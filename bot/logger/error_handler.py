import traceback

from bot.api.api import Api
from bot.logger.logger import Logger
from bot.logger.reusable_message_sender import TimedReusableMessageSender, ReusableMessageSender
from bot.multithreading.worker import Work, Worker


class ErrorHandler:
    def __init__(self, api: Api, error_chat_id: str, debug: bool):
        sender = TimedReusableMessageSender(ReusableMessageSender(api, error_chat_id))
        self.logger = Logger(sender, tag="ERROR")
        self.debug = debug

    def handle_work_error(self, error: Exception, work: Work, worker: Worker):
        if self.debug:
            traceback.print_exc()
        text = "Worker: {worker} | Work: {work} | {description}"\
            .format(worker=worker.name, work=work.name, description=str(error))
        self.logger.log(text)
