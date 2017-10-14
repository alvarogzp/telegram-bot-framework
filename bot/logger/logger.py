import time

from bot.action.util.textformat import FormattedText
from bot.logger.message_sender import MessageSender


LOG_ENTRY_FORMAT = "{time} [{tag}] {text}"


class Logger:
    def __init__(self, sender: MessageSender):
        self.sender = sender

    def log(self, tag, text):
        text = self._get_text_to_send(tag, text)
        self.sender.send(text)

    def _get_text_to_send(self, tag, text):
        raise NotImplementedError()


class PlainTextLogger(Logger):
    def _get_text_to_send(self, tag: str, text: str):
        return LOG_ENTRY_FORMAT.format(time=time.strftime("%X"), tag=tag, text=text)


class FormattedTextLogger(Logger):
    def _get_text_to_send(self, tag: FormattedText, text: FormattedText):
        return FormattedText().normal(LOG_ENTRY_FORMAT).start_format()\
            .normal(time=time.strftime("%X")).concat(tag=tag).concat(text=text).end_format()
