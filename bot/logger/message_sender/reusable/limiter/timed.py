import time

from bot.logger.message_sender.reusable.limiter import ReusableMessageLimiter


class TimedReusableMessageLimiter(ReusableMessageLimiter):
    def __init__(self, reuse_message_for_seconds: int = 60):
        self.reuse_message_for_seconds = reuse_message_for_seconds
        # initialized to 0 to avoid the first message to use this time as its issue time,
        # forcing it to be issued again.
        self.last_new_message_issued_at = 0

    def should_issue_new_message_pre_add(self, new_text):
        return self.__should_issue_new_message(time.time())

    def __should_issue_new_message(self, current_time):
        return self.last_new_message_issued_at + self.reuse_message_for_seconds <= current_time

    def notify_new_message_issued(self):
        self.last_new_message_issued_at = time.time()
