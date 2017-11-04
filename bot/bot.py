import time

from bot.action.core.action import Action
from bot.action.core.update import Update
from bot.action.standard.admin.config_status import ConfigStatus
from bot.action.util.textformat import FormattedText
from bot.api.api import Api
from bot.api.async import AsyncApi
from bot.api.telegram import TelegramBotApi
from bot.logger.admin_logger import AdminLogger
from bot.logger.worker_logger import WorkerStartStopLogger
from bot.multithreading.scheduler import SchedulerApi
from bot.storage import Config, Cache
from bot.storage import State


CONFIG_DIR = "config"
STATE_DIR = "state"


class Bot:
    def __init__(self):
        self.config = Config(CONFIG_DIR)
        self.state = State(STATE_DIR)
        self.cache = Cache()
        debug = self.config.debug()
        telegram_api = TelegramBotApi(self.config.auth_token, self.config.reuse_connections(), debug)
        self.api = Api(telegram_api, self.state)
        self.cache.bot_info = self.api.getMe()
        self.logger = AdminLogger(self.api, self.config.admin_chat_id, debug, self.config.send_error_tracebacks())
        self.scheduler = self._create_scheduler()
        self.starting()
        if self.config.async():
            self.scheduler.setup()
            self.api.enable_async(AsyncApi(self.api, self.scheduler))
        self.action = Action()
        self.update_processor = UpdateProcessor(self.action, self.logger)

    def _create_scheduler(self):
        max_network_workers = int(self.config.max_network_workers)
        worker_logger = WorkerStartStopLogger(self.logger.logger)
        return SchedulerApi(
            max_network_workers, self.logger.work_error, worker_logger.worker_start, worker_logger.worker_stop
        )

    def set_action(self, action: Action):
        action.setup(self.api, self.config, self.state, self.cache, self.scheduler)
        self.action = action
        self.update_processor = UpdateProcessor(self.action, self.logger)

    def run(self):
        try:
            self.main_loop()
        except KeyboardInterrupt:
            self.logger.info("KeyboardInterrupt")
        except SystemExit as e:
            self.logger.info("SystemExit: " + str(e))
            raise e
        except BaseException as e:
            self.logger.error(e, "Fatal error")
            raise e
        finally:
            self.shutdown()

    def starting(self):
        self.logger.info_formatted_text(
            FormattedText().bold("Starting"),
            *ConfigStatus(self.config, self.state).get_config_status()
        )

    def main_loop(self):
        while True:
            self.process_pending_updates()
            self.process_normal_updates()

    def process_pending_updates(self):
        PendingUpdatesProcessor(self.api.get_pending_updates, self.logger, self.config, self.update_processor).run()

    def process_normal_updates(self):
        NormalUpdatesProcessor(self.api.get_updates, self.logger, self.config, self.update_processor).run()

    def shutdown(self):
        self.action.shutdown()
        self.scheduler.shutdown()
        self.logger.info("Finished")


class UpdateProcessor:
    def __init__(self, action: Action, logger: AdminLogger):
        self.action = action
        self.logger = logger

    def process_update(self, update: Update):
        try:
            self.action.process(update)
        except Exception as e:
            # As logger errors are probably API failures that the next updates may also get,
            # let them to be propagated so that no more updates are processed before waiting some time
            self.logger.error(e, "process_update")


class UpdatesProcessor:
    def __init__(self, get_updates_func: callable, logger: AdminLogger, config: Config,
                 update_processor: UpdateProcessor):
        self.get_updates_func = get_updates_func
        self.logger = logger
        self.config = config
        self.update_processor = update_processor
        self.last_error = None
        self.number_of_updates_processed = 0

    def run(self):
        self.processing_starting()
        try:
            self.__processing_loop()
        finally:
            self.processing_ended()
        self.processing_ended_successfully()

    def __processing_loop(self):
        while self.should_keep_processing_updates():
            self.__get_and_process_handling_errors()

    def __get_and_process_handling_errors(self):
        try:
            self.__get_and_process()
        except Exception as e:
            self.__handle_error(e)
            # notify there has been an error
            self.processing_error(e)
        else:
            # notify successful processing
            self.processing_successful()

    def __get_and_process(self):
        for update in self.get_updates_func():
            self.update_processor.process_update(update)
            self.number_of_updates_processed += 1

    def __handle_error(self, error: Exception):
        sleep_seconds = self.config.sleep_seconds_on_get_updates_error
        # we do not want to let non-fatal (eg. API) errors to escape from here
        self.safe_log_error(error, "get_and_process", "Sleeping for {seconds} seconds.".format(seconds=sleep_seconds))
        # there has been an error while getting updates, sleep a little to give a chance
        # for the server or the network to recover (if that was the case), and to not to flood the server
        time.sleep(int(sleep_seconds))

    def safe_log_error(self, error: Exception, *info: str):
        """Log error failing silently on error"""
        self.__do_safe(lambda: self.logger.error(error, *info))

    def safe_log_info(self, *info: str):
        """Log info failing silently on error"""
        self.__do_safe(lambda: self.logger.info(*info))

    @staticmethod
    def __do_safe(func: callable):
        try:
            return func()
        except Exception:
            pass

    def should_keep_processing_updates(self):
        raise NotImplementedError()

    def processing_successful(self):
        """Updates were processed successfully"""
        self.last_error = None

    def processing_error(self, error: Exception):
        """There has been an error while processing the last updates"""
        self.last_error = error

    def processing_starting(self):
        """Updates are about to start being processed"""
        pass

    def processing_ended(self):
        """Processing has ended, we don't know if successfully or caused by an error"""
        self.safe_log_info(
            "Ending",
            "Updates processed: {updates_processed_number}"
                .format(updates_processed_number=self.number_of_updates_processed)
        )

    def processing_ended_successfully(self):
        """Processing has ended successfully"""
        pass


class PendingUpdatesProcessor(UpdatesProcessor):
    def __init__(self, get_updates_func: callable, logger: AdminLogger, config: Config,
                 update_processor: UpdateProcessor):
        super().__init__(get_updates_func, logger, config, update_processor)
        # set to some value other than None to let the processing run the first time
        self.last_error = True

    def should_keep_processing_updates(self):
        # if there has been an error not all pending updates were processed
        # so try again until it ends without error
        was_error = self.last_error is not None
        if was_error and self.last_error is not True:
            self.safe_log_info("Restarting", "Recovered from error. Continue processing pending updates...")
        return was_error

    def processing_starting(self):
        self.safe_log_info("Pending", "Processing pending updates...")

    def processing_ended_successfully(self):
        self.safe_log_info("Continuing", "Pending updates successfully processed.")


class NormalUpdatesProcessor(UpdatesProcessor):
    def __init__(self, get_updates_func: callable, logger: AdminLogger, config: Config,
                 update_processor: UpdateProcessor):
        super().__init__(get_updates_func, logger, config, update_processor)
        self.last_successful_processing = time.time()

    def processing_successful(self):
        super().processing_successful()
        self.last_successful_processing = time.time()

    def should_keep_processing_updates(self):
        if self.last_error is None:
            # if last processing ended without error, keep going!
            return True
        error_seconds_in_normal_mode = time.time() - self.last_successful_processing
        max_error_seconds_allowed_in_normal_mode = int(self.config.max_error_seconds_allowed_in_normal_mode)
        if error_seconds_in_normal_mode > max_error_seconds_allowed_in_normal_mode:
            # it has happened too much time since last successful processing
            # although it does not mean no update have been processed, we are
            # having problems and updates are being delayed, so going back to
            # process pending updates mode
            self.safe_log_info(
                "Restarting",
                "Exceeded {max_seconds} maximum seconds with errors (current value: {seconds} seconds)"
                    .format(max_seconds=max_error_seconds_allowed_in_normal_mode,
                            seconds=int(error_seconds_in_normal_mode)),
                "Switching to pending updates mode."
            )
            return False
        else:
            self.safe_log_info(
                "Restarted",
                "Recovered from error (current error burst duration is {seconds} seconds of "
                "{max_seconds} maximum seconds allowed)"
                    .format(seconds=int(error_seconds_in_normal_mode),
                            max_seconds=max_error_seconds_allowed_in_normal_mode),
                "Continuing in normal updates mode."
            )
            return True

    def processing_starting(self):
        self.safe_log_info("Started", "Switched to normal updates mode.")
