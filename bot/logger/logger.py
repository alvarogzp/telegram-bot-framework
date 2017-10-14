import time

from bot.action.util.textformat import FormattedText
from bot.logger.reusable_message_sender import MessageSender


class Logger:
    def __init__(self, sender: MessageSender):
        self.sender = sender

    def log(self, tag: str, text: FormattedText):
        text = self.__get_formatted_text(tag, text)
        self.sender.send(text)

    @staticmethod
    def __get_formatted_text(tag: str, text: FormattedText):
        return FormattedText().normal("{time} [{tag}] {text}").start_format()\
            .normal(time=time.strftime("%X")).bold(tag=tag).concat(text=text).end_format()
