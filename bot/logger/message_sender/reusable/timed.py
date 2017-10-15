import time

from bot.logger.message_sender import IntermediateMessageSender
from bot.logger.message_sender.reusable.reusable import ReusableMessageSender


class TimedReusableMessageSender(IntermediateMessageSender):
    def __init__(self, sender: ReusableMessageSender, reuse_message_for_seconds: int = 60):
        super().__init__(sender)
        self.reuse_message_for_seconds = reuse_message_for_seconds
        self.last_new_message_issued_at = time.time()

    def send(self, text):
        self.__issue_new_message_if_appropriate()
        self.sender.send(text)

    def __issue_new_message_if_appropriate(self):
        current_time = time.time()
        if self.__should_issue_new_message(current_time):
            self.sender.new()
            self.last_new_message_issued_at = current_time

    def __should_issue_new_message(self, current_time):
        return self.last_new_message_issued_at + self.reuse_message_for_seconds <= current_time
