from bot.action.util.textformat import FormattedText
from bot.logger.message_sender.message_builder import MessageBuilder


class FormattedTextBuilder(MessageBuilder):
    def __init__(self, separator: FormattedText = FormattedText().newline().newline()):
        super().__init__(separator)
        self.formatted_text = FormattedText()

    def _add(self, formatted_text: FormattedText):
        self.formatted_text.concat(formatted_text)

    def get_length(self):
        return self.formatted_text.length()

    def get_message(self):
        return self.formatted_text.build_message()

    def clear(self):
        self.formatted_text.clear()
