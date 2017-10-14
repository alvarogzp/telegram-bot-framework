from bot.api.api import Api
from bot.api.domain import Message
from bot.logger.message_sender import MessageSender


class ApiMessageSender(MessageSender):
    def __init__(self, api: Api, chat_id):
        self.api = api
        self.chat_id = chat_id

    def send(self, message: Message):
        """
        :rtype: int
        :return message_id
        """
        self.__add_chat_id(message)
        return self.api.send_message(message).message_id

    def edit(self, message: Message, message_id):
        self.__add_chat_id(message)
        message.set_message_id(message_id)
        self.api.editMessageText(**message.data)

    def __add_chat_id(self, message: Message):
        message.to_chat(chat_id=self.chat_id)
