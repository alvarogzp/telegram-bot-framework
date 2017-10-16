from bot.logger.message_sender.message_builder import MessageBuilder
from bot.logger.message_sender.reusable.limiter import ReusableMessageLimiter


class LengthReusableMessageLimiter(ReusableMessageLimiter):
    def __init__(self, max_length: int = 4000):
        self.max_length = max_length

    def should_issue_new_message_post_add(self, builder: MessageBuilder):
        return self.__should_issue_new_message(builder.get_length())

    def __should_issue_new_message(self, current_length):
        return current_length > self.max_length
