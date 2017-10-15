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
