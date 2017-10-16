from bot.api.domain import Message


class MessageBuilder:
    def __init__(self, separator):
        self.separator = separator

    def add(self, text):
        if self.get_length() > 0:
            self._add(self.separator)
        self._add(text)

    def _add(self, text):
        raise NotImplementedError()

    def get_length(self):
        """:rtype: int"""
        raise NotImplementedError()

    def get_message(self):
        """:rtype: Message"""
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()
