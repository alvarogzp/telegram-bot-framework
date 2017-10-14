from bot.api.api import Api
from bot.logger.message_sender import MessageSender


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
