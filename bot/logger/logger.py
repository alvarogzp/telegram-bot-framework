import time

from bot.logger.reusable_message_sender import MessageSender


class Logger:
    def __init__(self, sender: MessageSender, tag: str = ""):
        self.sender = sender
        self.tag = tag

    def log(self, text):
        text = self.__get_formatted_text(text)
        self.sender.send(text)

    def __get_formatted_text(self, text):
        return "{time} [{tag}] {text}".format(time=time.strftime("%X"), tag=self.tag, text=text)
