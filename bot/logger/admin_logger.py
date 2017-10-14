import traceback

from bot.action.util.textformat import FormattedText
from bot.api.api import Api
from bot.logger.logger import FormattedTextLogger
from bot.logger.message_sender.api import ApiMessageSender
from bot.logger.message_sender.message_builder.formatted import FormattedTextBuilder
from bot.logger.message_sender.reusable import ReusableMessageSender
from bot.logger.message_sender.reusable.timed import TimedReusableMessageSender
from bot.logger.message_sender.synchronized import SynchronizedMessageSender
from bot.multithreading.work import Work
from bot.multithreading.worker import Worker


class AdminLogger:
    def __init__(self, api: Api, admin_chat_id: str, debug: bool):
        sender = \
            SynchronizedMessageSender(
                TimedReusableMessageSender(
                    ReusableMessageSender(
                        ApiMessageSender(api, admin_chat_id),
                        FormattedTextBuilder(),
                        max_length=1000
                    ),
                    reuse_message_for_seconds=1
                )
            )
        self.logger = FormattedTextLogger(sender)
        self.debug = debug

    def work_error(self, error: BaseException, work: Work, worker: Worker):
        text = FormattedText().normal("Worker: {worker} | Work: {work} | {error}")\
            .start_format().bold(worker=worker.name, work=work.name, error=str(error)).end_format()
        self.__error(text)

    def error(self, error: BaseException, action: str):
        text = FormattedText().normal("Action: {action} | {error}")\
            .start_format().bold(action=action, error=str(error)).end_format()
        self.__error(text)

    def __error(self, text):
        self.__print_traceback()
        self.logger.log("ERROR", text)

    def __print_traceback(self):
        if self.debug:
            traceback.print_exc()

    def info(self, info_text: str):
        self.__info(FormattedText().bold(info_text))

    def __info(self, text):
        self.logger.log("INFO", text)
