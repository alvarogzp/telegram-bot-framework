import traceback

from bot.action.util.textformat import FormattedText
from bot.api.api import Api
from bot.api.exception import ApiException
from bot.logger.formatter.exception import ExceptionFormatter
from bot.logger.logger import LoggerFactory
from bot.logger.message_sender.factory import MessageSenderFactory
from bot.multithreading.work import Work
from bot.multithreading.worker import Worker


ERROR_TAG = FormattedText().bold("ERROR")
TRACEBACK_TAG = FormattedText().code_inline("TRACEBACK")

INFO_TAG = FormattedText().normal("INFO")


class AdminLogger:
    def __init__(self, api: Api, admin_chat_id: str, print_tracebacks: bool, send_tracebacks: bool):
        sender = MessageSenderFactory\
            .get_builder()\
            .with_api(api)\
            .with_chat_id(admin_chat_id)\
            .with_message_builder_type("formatted")\
            .with_reuse_max_length(1000)\
            .with_reuse_max_time(1)\
            .with_reuse_max_number(10)\
            .build()
        self.logger = LoggerFactory.get("formatted", sender)
        self.print_tracebacks = print_tracebacks
        self.send_tracebacks = send_tracebacks

    def work_error(self, error: BaseException, work: Work, worker: Worker):
        self.__error(
            FormattedText().bold(ExceptionFormatter.format(error)),
            FormattedText().normal("Work: {work}").start_format().bold(work=work.name).end_format(),
            FormattedText().normal("Worker: {worker}").start_format().bold(worker=worker.name).end_format()
        )

    def error(self, error: BaseException, action: str, *additional_info: str):
        self.__error(
            FormattedText().bold(ExceptionFormatter.format(error)),
            FormattedText().normal("Action: {action}").start_format().bold(action=action).end_format(),
            *[FormattedText().normal(info) for info in additional_info]
        )

    def __error(self, *texts: FormattedText):
        if self.print_tracebacks:
            self.__print_traceback()
        self.logger.log(ERROR_TAG, *texts)
        if self.send_tracebacks:
            self.__send_traceback()

    @staticmethod
    def __print_traceback():
        traceback.print_exc()

    def __send_traceback(self):
        try:
            self.logger.log(TRACEBACK_TAG, FormattedText().code_block(traceback.format_exc()))
        except ApiException:
            # tracebacks can be very long and reach message length limit
            # retry with a shorter traceback
            self.logger.log(TRACEBACK_TAG, FormattedText().code_block(traceback.format_exc(limit=1)))

    def info(self, info_text: str, *additional_info: str):
        self.__info(
            FormattedText().bold(info_text),
            *[FormattedText().normal(info) for info in additional_info]
        )

    def info_formatted_text(self, *info_texts: FormattedText):
        self.__info(*info_texts)

    def __info(self, *texts: FormattedText):
        self.logger.log(INFO_TAG, *texts)
