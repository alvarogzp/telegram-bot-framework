from bot.action.core.action import IntermediateAction
from bot.logger.logger import LoggerFactory
from bot.logger.message_sender.factory import MessageSenderFactory
from bot.logger.worker_logger import WorkerStartStopLogger


class LoggerAction(IntermediateAction):
    def __init__(self, logger_type: str = "formatted", reuse_max_length: int = 4000, reuse_max_time: int = 60,
                 async: bool = True):
        """
        :param logger_type: Either `formatted` or `plain`. Indicates the type of input that the logger accepts.
            If `formatted`, it accepts FormattedText, and if `plain`, it accepts str.
        """
        super().__init__()
        self.logger_type = logger_type
        self.sender_builder = MessageSenderFactory.get_synchronized_timed_and_length_limited_reusable_builder()\
            .with_message_builder_type(logger_type)\
            .with_reuse_max_length(reuse_max_length)\
            .with_reuse_max_time(reuse_max_time)
        self.async = async
        self.logger = None

    def post_setup(self):
        self.sender_builder.with_api(self.api)
        self.logger = self.new_logger(self.config.log_chat_id)
        should_use_this_logger_for_scheduler_events = self.config.scheduler_events_on_log_chat()
        if should_use_this_logger_for_scheduler_events:
            self.__update_scheduler_callbacks()

    def __update_scheduler_callbacks(self):
        # update scheduler callbacks to use this logger instead of the admin one
        worker_logger = WorkerStartStopLogger(self.logger)
        self.scheduler.set_callbacks(worker_logger.worker_start, worker_logger.worker_stop, are_async=self.async)

    def new_logger(self, chat_id, logger_type: str = None, reuse_max_length: int = None, reuse_max_time: int = None,
                   async: bool = None, use_worker_pool: bool = True):
        if chat_id is None:
            return LoggerFactory.get_no_logger()
        sender_builder = self.sender_builder.copy().with_chat_id(chat_id)
        if logger_type is not None:
            sender_builder.with_message_builder_type(logger_type)
        else:
            logger_type = self.logger_type
        if reuse_max_length is not None:
            sender_builder.with_reuse_max_length(reuse_max_length)
        if reuse_max_time is not None:
            sender_builder.with_reuse_max_time(reuse_max_time)
        if async is None:
            async = self.async
        if async:
            new_worker_func = self.scheduler.new_worker_pool if use_worker_pool else self.scheduler.new_worker
            worker = new_worker_func("logger@" + str(chat_id))
            sender_builder.with_worker(worker)
        return LoggerFactory.get(logger_type, sender_builder.build())

    def process(self, event):
        event.log = self.logger.log
        event.logger = self.logger
        event.new_logger = self.new_logger
        self._continue(event)
