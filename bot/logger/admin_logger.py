import traceback

from bot.action.util.textformat import FormattedText
from bot.api.api import Api
from bot.logger.logger import LoggerFactory
from bot.logger.message_sender.factory import MessageSenderFactory
from bot.multithreading.work import Work
from bot.multithreading.worker import Worker


ERROR_TAG = FormattedText().bold("ERROR")
INFO_TAG = FormattedText().normal("INFO")


class AdminLogger:
    def __init__(self, api: Api, admin_chat_id: str, debug: bool):
        sender = MessageSenderFactory\
            .get_synchronized_timed_and_length_limited_reusable_builder()\
            .with_api(api)\
            .with_chat_id(admin_chat_id)\
            .with_message_builder_type("formatted")\
            .with_reuse_max_length(1000)\
            .with_reuse_max_time(1)\
            .build()
        self.logger = LoggerFactory.get("formatted", sender)
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
