import time

from bot.action.util.textformat import FormattedText
from bot.logger.message_sender import MessageSender


LOG_ENTRY_FORMAT = "{time} [{tag}] {text}"
TEXT_SEPARATOR = " | "


class Logger:
    def __init__(self, sender: MessageSender):
        self.sender = sender

    def log(self, tag, *texts):
        text = self._get_text_to_send(tag, *texts)
        self.sender.send(text)

    def _get_text_to_send(self, tag, *texts):
        raise NotImplementedError()


class PlainTextLogger(Logger):
    def _get_text_to_send(self, tag: str, *texts: str):
        text = TEXT_SEPARATOR.join(texts)
        return LOG_ENTRY_FORMAT.format(time=time.strftime("%X"), tag=tag, text=text)


class FormattedTextLogger(Logger):
    def _get_text_to_send(self, tag: FormattedText, *texts: FormattedText):
        text = FormattedText().normal(TEXT_SEPARATOR).join(texts)
        return FormattedText().normal(LOG_ENTRY_FORMAT).start_format()\
            .normal(time=time.strftime("%X")).concat(tag=tag).concat(text=text).end_format()


class NoLogger(Logger):
    def __init__(self):
        super().__init__(None)

    def log(self, tag, *texts):
        pass

    def _get_text_to_send(self, tag, *texts):
        pass


class LoggerFactory:
    @classmethod
    def get(cls, logger_type: str, sender: MessageSender):
        if logger_type == "formatted":
            return cls.get_formatted(sender)
        elif logger_type == "plain":
            return cls.get_plain(sender)
        elif logger_type == "none":
            return cls.get_no_logger()
        else:
            raise Exception("Unknown Logger requested (" + logger_type + ")")

    @staticmethod
    def get_formatted(sender: MessageSender):
        return FormattedTextLogger(sender)

    @staticmethod
    def get_plain(sender: MessageSender):
        return PlainTextLogger(sender)

    @staticmethod
    def get_no_logger():
        return NoLogger()
