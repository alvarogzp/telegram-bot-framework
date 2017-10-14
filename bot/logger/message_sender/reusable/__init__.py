from bot.api.domain import Message
from bot.logger.message_sender import MessageSender
from bot.logger.message_sender.api import ApiMessageSender
from bot.logger.message_sender.message_builder import MessageBuilder


class ReusableMessageSender(MessageSender):
    def __init__(self, sender: ApiMessageSender, builder: MessageBuilder, max_length: int = 4000):
        self.sender = sender
        self.builder = builder
        self.max_length = max_length

    def send(self, text):
        message = self._get_message_for(text)
        self._send(message)

    def _get_message_for(self, text):
        self.builder.add(text)
        self.__check_length(text)
        return self.builder.get_message()

    def __check_length(self, text):
        if self.builder.get_length() > self.max_length:
            self.new()
            # if length is still greater than max_length, let it fail, otherwise we would enter on infinite loop
            self.builder.add(text)

    def _send(self, message: Message):
        try:
            self.sender.send(message)
        finally:
            if self.sender.will_send_new_message():
                # There has been a problem and the sender cannot reuse the message, either because it was the
                # initial one and the message_id could not be retrieved (by some error or interruption), or
                # because the message failed to edit (it could have reached its max length).
                # The best thing we can do here is to start a new message, discarding the current text.
                # Doing so, we ensure the next send:
                #  - Will not fail if the problem was with the message content
                #  - Won't have repeated content if the message was really sent but the request was interrupted
                #    by some event (like a KeyboardInterrupt)
                self.new()

    def new(self):
        self.sender.new()
        self.builder.clear()
