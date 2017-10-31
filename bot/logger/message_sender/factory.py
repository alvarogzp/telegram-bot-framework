from bot.api.api import Api
from bot.logger.message_sender.asynchronous import AsynchronousMessageSender
from bot.logger.message_sender.message_builder.factory import MessageBuilderFactory
from bot.logger.message_sender.reusable.limiter.group import ReusableMessageLimiterGroup
from bot.logger.message_sender.reusable.limiter.length import LengthReusableMessageLimiter
from bot.logger.message_sender.reusable.limiter.number import NumberReusableMessageLimiter
from bot.logger.message_sender.reusable.limiter.timed import TimedReusableMessageLimiter
from bot.logger.message_sender.reusable.reusable import ReusableMessageSender
from bot.logger.message_sender.reusable.same import SameMessageSender
from bot.logger.message_sender.synchronized import SynchronizedMessageSender
from bot.multithreading.worker import Worker


class MessageSenderFactory:
    @classmethod
    def get_builder(cls):
        return cls.get_synchronized_length_time_and_number_limited_reusable_builder()

    @staticmethod
    def get_synchronized_length_time_and_number_limited_reusable_builder():
        return SynchronizedLengthTimeAndNumberLimitedReusableMessageSenderBuilder()


class SynchronizedLengthTimeAndNumberLimitedReusableMessageSenderBuilder:
    def __init__(self):
        self.api = None
        self.chat_id = None
        self.message_builder_type = None
        self.reuse_max_length = None
        self.reuse_max_time = None
        self.reuse_max_number = None
        self.worker = None

    def with_api(self, api: Api):
        self.api = api
        return self

    def with_chat_id(self, chat_id):
        self.chat_id = chat_id
        return self

    def with_message_builder_type(self, message_builder_type: str):
        self.message_builder_type = message_builder_type
        return self

    def with_reuse_max_length(self, reuse_max_length: int):
        self.reuse_max_length = reuse_max_length
        return self

    def with_reuse_max_time(self, reuse_max_time: int):
        self.reuse_max_time = reuse_max_time
        return self

    def with_reuse_max_number(self, reuse_max_number: int):
        self.reuse_max_number = reuse_max_number
        return self

    def with_worker(self, worker: Worker):
        self.worker = worker
        return self

    def build(self):
        self.__check_not_none(self.api, self.chat_id, self.message_builder_type, self.reuse_max_length,
                              self.reuse_max_time, self.reuse_max_number)
        sender = \
            SynchronizedMessageSender(
                ReusableMessageSender(
                    SameMessageSender(self.api, self.chat_id),
                    MessageBuilderFactory.get(self.message_builder_type),
                    ReusableMessageLimiterGroup(
                        LengthReusableMessageLimiter(self.reuse_max_length),
                        TimedReusableMessageLimiter(self.reuse_max_time),
                        NumberReusableMessageLimiter(self.reuse_max_number)
                    )
                )
            )
        if self.worker:
            sender = AsynchronousMessageSender(sender, self.worker)
        return sender

    @staticmethod
    def __check_not_none(*args):
        for arg in args:
            assert arg is not None

    def copy(self):
        return self.__class__()\
            .with_api(self.api)\
            .with_chat_id(self.chat_id)\
            .with_message_builder_type(self.message_builder_type)\
            .with_reuse_max_length(self.reuse_max_length)\
            .with_reuse_max_time(self.reuse_max_time)\
            .with_reuse_max_number(self.reuse_max_number)\
            .with_worker(self.worker)
