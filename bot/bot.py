import time

from bot.action.core.action import Action
from bot.action.core.update import Update
from bot.api.api import Api
from bot.api.telegram import TelegramBotApi
from bot.logger.admin_logger import AdminLogger
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
        telegram_api = TelegramBotApi(self.config.auth_token, debug)
        self.api = Api(telegram_api, self.state)
        self.logger = AdminLogger(self.api, self.config.admin_chat_id, debug)
        self.scheduler = SchedulerApi(self.logger.work_error)
        if self.config.async():
            self.scheduler.setup()
            self.api.enable_async(self.scheduler)
        self.cache.bot_info = self.api.getMe()
        self.action = Action()

    def set_action(self, action: Action):
        action.setup(self.api, self.config, self.state, self.cache, self.scheduler)
        self.action = action

    def run(self):
        self.logger.info(
            "Started",
            "async: {async}".format(async=self.config.async()),
            "debug: {debug}".format(debug=self.config.debug())
        )
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

    def main_loop(self):
        self.get_and_process_updates(self.api.get_pending_updates)
        while True:
            self.get_and_process_updates(self.api.get_updates)

    def get_and_process_updates(self, get_updates_func: callable):
        try:
            for update in get_updates_func():
                self.process_update(update)
        except Exception as e:
            sleep_seconds = self.config.sleep_seconds_on_get_updates_error
            # we do not want to let non-fatal (eg. API) errors to escape from here
            self.__safe_log_error(e, "get_updates", "Sleeping for {seconds} seconds".format(seconds=sleep_seconds))
            # there has been an error while getting updates, sleep a little to give a chance
            # for the server or the network to recover (if that was the case), and to not to flood the server
            time.sleep(int(sleep_seconds))

    def __safe_log_error(self, error: Exception, *info: str):
        """Log error failing silently on error"""
        try:
            self.logger.error(error, *info)
        except:
            pass

    def process_update(self, update: Update):
        try:
            self.action.process(update)
        except Exception as e:
            self.logger.error(e, "process_update")

    def shutdown(self):
        if self.config.async():
            self.scheduler.shutdown()
        self.logger.info("Finished")
