import traceback

from bot.api.api import Api
from bot.logger.logger import Logger
from bot.logger.reusable_message_sender import TimedReusableMessageSender, ReusableMessageSender
from bot.multithreading.worker import Worker
from bot.multithreading.work import Work


class AdminLogger:
    def __init__(self, api: Api, admin_chat_id: str, debug: bool):
        sender = TimedReusableMessageSender(ReusableMessageSender(api, admin_chat_id), reuse_message_for_seconds=5)
        self.logger = Logger(sender)
        self.debug = debug

    def work_error(self, error: BaseException, work: Work, worker: Worker):
        text = "Worker: {worker} | Work: {work} | {error}"\
            .format(worker=worker.name, work=work.name, error=str(error))
        self.__error(text)

    def error(self, error: BaseException, action: str):
        text = "Action: {action} | {error}".format(action=action, error=str(error))
        self.__error(text)

    def __error(self, text):
        self.__print_traceback()
        self.logger.log("ERROR", text)

    def __print_traceback(self):
        if self.debug:
            traceback.print_exc()

    def info(self, info_text: str):
        self.__info(info_text)

    def __info(self, text):
        self.logger.log("INFO", text)
