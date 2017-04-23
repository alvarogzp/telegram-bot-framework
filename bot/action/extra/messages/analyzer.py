from bot.action.util.format import TextSummarizer
from bot.action.util.textformat import FormattedText
from bot.api import domain


class MessageAnalyzer:
    def __init__(self, message_data):
        self.message_data = message_data

    def get_summary(self):
        """:rtype: FormattedText"""
        raise NotImplementedError()

    def get_full_content(self):
        """:rtype: list[domain.Message]"""
        raise NotImplementedError()


class UnknownMessageAnalyzer(MessageAnalyzer):
    def get_summary(self):
        return FormattedText().bold("❓ Unknown")

    def get_full_content(self):
        pass


class TextMessageAnalyzer(MessageAnalyzer):
    def get_summary(self):
        summarized_text = TextSummarizer.summarize(self.message_data.text, max_number_of_characters=15)
        return FormattedText().normal("✍️ [ ").italic(summarized_text).normal(" ]")

    def get_full_content(self):
        pass


class PhotoMessageAnalyzer(MessageAnalyzer):
    def get_summary(self):
        return FormattedText().bold("🌅 Photo")

    def get_full_content(self):
        pass


class StickerMessageAnalyzer(MessageAnalyzer):
    def get_summary(self):
        summary = FormattedText()
        emoji = self.message_data.sticker.emoji
        if emoji:
            summary.normal(emoji)
        else:
            summary.normal("📃")
        summary.bold(" Sticker")
        return summary

    def get_full_content(self):
        pass


class DocumentMessageAnalyzer(MessageAnalyzer):
    def get_summary(self):
        return FormattedText().bold("📄 Document")

    def get_full_content(self):
        pass


class VoiceMessageAnalyzer(MessageAnalyzer):
    def get_summary(self):
        return FormattedText().bold("🎤 Voice")

    def get_full_content(self):
        pass


class MessageAnalyzerResolver:
    @staticmethod
    def get_analyzer(message_data):
        message_type = UnknownMessageAnalyzer
        if message_data.text is not None:
            message_type = TextMessageAnalyzer
        elif message_data.photo:
            message_type = PhotoMessageAnalyzer
        elif message_data.sticker:
            message_type = StickerMessageAnalyzer
        elif message_data.document:
            message_type = DocumentMessageAnalyzer
        elif message_data.voice:
            message_type = VoiceMessageAnalyzer
        return message_type(message_data)


# Following is the public API that is supposed to be used

def get_summary(message_data):
    return MessageAnalyzerResolver.get_analyzer(message_data).get_summary()


def get_full_content(message_data):
    return MessageAnalyzerResolver.get_analyzer(message_data).get_full_content()
