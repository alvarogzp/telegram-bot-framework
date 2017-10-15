from bot.api.api import Api
from bot.logger.message_sender.message_builder import MessageBuilder
from bot.logger.message_sender.reusable.reusable import ReusableMessageSender
from bot.logger.message_sender.reusable.same import SameMessageSender
from bot.logger.message_sender.reusable.timed import TimedReusableMessageSender
from bot.logger.message_sender.synchronized import SynchronizedMessageSender


class MessageSenderFactory:
    @staticmethod
    def get_synchronized_timed_reusable_builder():
        return SynchronizedTimedReusableMessageSenderBuilder()


class SynchronizedTimedReusableMessageSenderBuilder:
    def __init__(self):
        self.api = None
        self.chat_id = None
        self.message_builder = None
        self.reuse_max_length = None
        self.reuse_max_time = None

    def with_api(self, api: Api):
        self.api = api
        return self

    def with_chat_id(self, chat_id):
        self.chat_id = chat_id
        return self

    def with_message_builder(self, message_builder: MessageBuilder):
        self.message_builder = message_builder
        return self

    def with_reuse_max_length(self, reuse_max_length: int):
        self.reuse_max_length = reuse_max_length
        return self

    def with_reuse_max_time(self, reuse_max_time: int):
        self.reuse_max_time = reuse_max_time
        return self

    def build(self):
        self.__check_not_none(self.api, self.chat_id, self.message_builder, self.reuse_max_length, self.reuse_max_time)
        return \
            SynchronizedMessageSender(
                TimedReusableMessageSender(
                    ReusableMessageSender(
                        SameMessageSender(self.api, self.chat_id),
                        self.message_builder,
                        max_length=self.reuse_max_length
                    ),
                    reuse_message_for_seconds=self.reuse_max_time
                )
            )

    @staticmethod
    def __check_not_none(*args):
        for arg in args:
            assert arg is not None

    def copy(self):
        return self.__class__()\
            .with_api(self.api)\
            .with_chat_id(self.chat_id)\
            .with_message_builder(self.message_builder)\
            .with_reuse_max_length(self.reuse_max_length)\
            .with_reuse_max_time(self.reuse_max_time)
