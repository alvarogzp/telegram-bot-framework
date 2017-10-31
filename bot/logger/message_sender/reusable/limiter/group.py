from bot.logger.message_sender.message_builder import MessageBuilder
from bot.logger.message_sender.reusable.limiter import ReusableMessageLimiter


class ReusableMessageLimiterGroup(ReusableMessageLimiter):
    def __init__(self, *limiters: ReusableMessageLimiter):
        self.limiters = limiters

    def should_issue_new_message_pre_add(self, new_text):
        return self.__any_limiter(lambda limiter: limiter.should_issue_new_message_pre_add(new_text))

    def should_issue_new_message_post_add(self, builder: MessageBuilder):
        return self.__any_limiter(lambda limiter: limiter.should_issue_new_message_post_add(builder))

    def __any_limiter(self, func: callable):
        return any((func(limiter) for limiter in self.limiters))

    def notify_new_message_issued(self):
        for limiter in self.limiters:
            limiter.notify_new_message_issued()

    def notify_about_to_send_message(self):
        for limiter in self.limiters:
            limiter.notify_about_to_send_message()
