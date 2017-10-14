import time

from bot.action.util.textformat import FormattedText
from bot.api.api import Api
from bot.api.domain import Message


class MessageSender:
    def send(self, text):
        raise NotImplementedError()


class ReusableMessageSender(MessageSender):
    def __init__(self, api: Api, separator):
        self.api = api
        self.separator = separator

    def send(self, text):
        if self._is_new():
            self._send_new(text)
        else:
            self._send_edit(text)

    def _is_new(self):
        raise NotImplementedError()

    def _send_new(self, text):
        raise NotImplementedError()

    def _send_edit(self, text):
        raise NotImplementedError()

    def new(self):
        raise NotImplementedError()


class PlainTextReusableMessageSender(ReusableMessageSender):
    def __init__(self, api: Api, chat_id, separator: str = "\n\n"):
        super().__init__(api, separator)
        self.message = Message.create("", chat_id)

    def _is_new(self):
        return self.message.message_id is None

    def _send_new(self, text: str):
        self.message.new_text(text)
        sent_message = self.api.send_message(self.message)
        self.message.set_message_id(sent_message.message_id)

    def _send_edit(self, text: str):
        self.message.new_text(self.message.text + self.separator + text)
        self.api.editMessageText(**self.message.data)

    def new(self):
        self.message.set_message_id(None)


class FormattedTextReusableMessageSender(ReusableMessageSender):
    def __init__(self, api: Api, chat_id, separator: FormattedText = FormattedText().newline().newline()):
        super().__init__(api, separator)
        self.chat_id = chat_id
        self.message_id = None
        self.formatted_text = FormattedText()

    def _is_new(self):
        return self.message_id is None

    def _send_new(self, formatted_text: FormattedText):
        message = self.formatted_text.concat(formatted_text).build_message().to_chat(chat_id=self.chat_id)
        sent_message = self.api.send_message(message)
        self.message_id = sent_message.message_id

    def _send_edit(self, formatted_text: FormattedText):
        message = self.formatted_text.concat(self.separator).concat(formatted_text)\
            .build_message().to_chat(chat_id=self.chat_id)
        message.set_message_id(self.message_id)
        self.api.editMessageText(**message.data)

    def new(self):
        self.formatted_text = FormattedText()
        self.message_id = None


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
