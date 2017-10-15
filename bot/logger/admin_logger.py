import traceback

from bot.action.util.textformat import FormattedText
from bot.api.api import Api
from bot.logger.logger import FormattedTextLogger
from bot.logger.message_sender.message_builder.formatted import FormattedTextBuilder
from bot.logger.message_sender.reusable.reusable import ReusableMessageSender
from bot.logger.message_sender.reusable.same import SameMessageSender
from bot.logger.message_sender.reusable.timed import TimedReusableMessageSender
from bot.logger.message_sender.synchronized import SynchronizedMessageSender
from bot.multithreading.work import Work
from bot.multithreading.worker import Worker


ERROR_TAG = FormattedText().bold("ERROR")
INFO_TAG = FormattedText().normal("INFO")


class AdminLogger:
    def __init__(self, api: Api, admin_chat_id: str, debug: bool):
        sender = \
            SynchronizedMessageSender(
                TimedReusableMessageSender(
                    ReusableMessageSender(
                        SameMessageSender(api, admin_chat_id),
                        FormattedTextBuilder(),
                        max_length=1000
                    ),
                    reuse_message_for_seconds=1
                )
            )
        self.logger = FormattedTextLogger(sender)
        self.debug = debug

    def work_error(self, error: BaseException, work: Work, worker: Worker):
        self.__error(
            FormattedText().normal("Worker: {worker}").start_format().bold(worker=worker.name).end_format(),
            FormattedText().normal("Work: {work}").start_format().bold(work=work.name).end_format(),
            FormattedText().bold(str(error))
        )

    def error(self, error: BaseException, action: str, *additional_info: str):
        self.__error(
            FormattedText().normal("Action: {action}").start_format().bold(action=action).end_format(),
            FormattedText().bold(str(error)),
            *[FormattedText().normal(info) for info in additional_info]
        )

    def __error(self, *texts: FormattedText):
        self.__print_traceback()
        self.logger.log(ERROR_TAG, *texts)

    def __print_traceback(self):
        if self.debug:
            traceback.print_exc()

    def info(self, info_text: str, *additional_info: str):
        self.__info(
            FormattedText().bold(info_text),
            *[FormattedText().normal(info) for info in additional_info]
        )

    def __info(self, *texts: FormattedText):
        self.logger.log(INFO_TAG, *texts)
