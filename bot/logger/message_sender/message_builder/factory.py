from bot.logger.message_sender.message_builder.formatted import FormattedTextBuilder
from bot.logger.message_sender.message_builder.plain import PlainTextBuilder


class MessageBuilderFactory:
    @classmethod
    def get(cls, builder_type: str):
        if builder_type == "formatted":
            return cls.get_formatted()
        elif builder_type == "plain":
            return cls.get_plain()
        else:
            raise Exception("Unknown MessageBuilder requested (" + builder_type + ")")

    @staticmethod
    def get_formatted():
        return FormattedTextBuilder()

    @staticmethod
    def get_plain():
        return PlainTextBuilder()
