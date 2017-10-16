from bot.api.domain import Message
from bot.logger.message_sender.message_builder import MessageBuilder


class PlainTextBuilder(MessageBuilder):
    def __init__(self, separator: str = "\n\n"):
        super().__init__(separator)
        self.text = ""

    def _add(self, text):
        self.text += text

    def get_length(self):
        return len(self.text)

    def get_message(self):
        return Message.create(self.text)

    def clear(self):
        self.text = ""
