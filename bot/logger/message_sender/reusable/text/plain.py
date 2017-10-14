from bot.api.api import Api
from bot.api.domain import Message
from bot.logger.message_sender.reusable import ReusableMessageSender


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
