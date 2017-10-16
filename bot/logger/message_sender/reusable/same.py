from bot.api.api import Api
from bot.api.domain import Message
from bot.logger.message_sender import MessageSender


class SameMessageSender(MessageSender):
    def __init__(self, api: Api, chat_id):
        self.api = api
        self.chat_id = chat_id
        self.message_id = None

    def send(self, message: Message):
        message.to_chat(chat_id=self.chat_id)
        send_func = self._send if self._should_send_new_message() else self._edit
        try:
            send_func(message)
        except:
            # If the message could not be sent properly, discard it to start with a new one
            self.new()
            raise

    def _should_send_new_message(self):
        return self.message_id is None

    def _send(self, message: Message):
        self.message_id = self.api.send_message(message).message_id

    def _edit(self, message: Message):
        message.set_message_id(self.message_id)
        self.api.editMessageText(**message.data)

    def will_send_new_message(self):
        return self._should_send_new_message()

    def new(self):
        self.message_id = None
