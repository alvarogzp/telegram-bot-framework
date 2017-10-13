import time

from bot.api.api import Api
from bot.api.domain import Message


class MessageSender:
    def send(self, text):
        raise NotImplementedError()


class ReusableMessageSender(MessageSender):
    def __init__(self, api: Api, chat_id, separator: str = "\n"):
        self.api = api
        self.message = Message.create("", chat_id)
        self.separator = separator

    def send(self, text):
        if self.__is_new():
            self._send_new(text)
        else:
            self._send_edit(text)

    def __is_new(self):
        return self.message.message_id is None

    def _send_new(self, text):
        self.message.new_text(text)
        sent_message = self.api.send_message(self.message)
        self.message.set_message_id(sent_message.message_id)

    def _send_edit(self, text):
        self.message.new_text(self.message.text + self.separator + text)
        self.api.editMessageText(**self.message.data)

    def new(self):
        self.message.set_message_id(None)


class TimedReusableMessageSender(MessageSender):
    def __init__(self, sender: ReusableMessageSender, reuse_message_for_seconds: int = 60):
        self.sender = sender
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
