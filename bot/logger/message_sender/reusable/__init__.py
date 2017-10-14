from bot.api.domain import Message
from bot.logger.message_sender import MessageSender
from bot.logger.message_sender.api import ApiMessageSender
from bot.logger.message_sender.message_builder import MessageBuilder


class ReusableMessageSender(MessageSender):
    def __init__(self, sender: ApiMessageSender, builder: MessageBuilder, max_length: int = 4000):
        self.sender = sender
        self.builder = builder
        self.max_length = max_length
        self.message_id = None

    def send(self, text):
        message = self._get_message_for(text)
        self._get_send_func()(message)

    def _get_message_for(self, text):
        self.builder.add(text)
        self.__check_length(text)
        return self.builder.get_message()

    def __check_length(self, text):
        if self.builder.get_length() > self.max_length:
            self.new()
            # if length is still greater than max_length, let it fail, otherwise we would enter on infinite loop
            self.builder.add(text)

    def _get_send_func(self):
        return self.__send_standalone_message if self.message_id is None else self.__send_edited_message

    def __send_standalone_message(self, message: Message):
        try:
            self.message_id = self.sender.send(message)
        finally:
            if self.message_id is None:
                # Discard current message, as there has been a problem with the message_id retrieval and we
                # don't know if it was properly sent or not, so we threat it as corrupt and start a new one.
                # That way, the next send:
                #  - Will not fail if the problem was with this message content
                #  - Won't have repeated content if this message was really sent but the request was interrupted
                #    by some event (like a KeyboardInterrupt)
                self.new()

    def __send_edited_message(self, message: Message):
        self.sender.edit(message, self.message_id)

    def new(self):
        self.builder.clear()
        self.message_id = None
