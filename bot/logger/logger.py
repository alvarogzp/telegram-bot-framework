import time

from bot.logger.reusable_message_sender import MessageSender


class Logger:
    def __init__(self, sender: MessageSender):
        self.sender = sender

    def log(self, tag, text):
        text = self.__get_formatted_text(tag, text)
        self.sender.send(text)

    @staticmethod
    def __get_formatted_text(tag, text):
        return "{time} [{tag}] {text}".format(time=time.strftime("%X"), tag=tag, text=text)
