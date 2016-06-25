from bot.actions.action import Action
from bot.api.domain import Message


class AnswerAction(Action):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def process_message(self, message):
        self.api.send_message(Message.create_reply(message, self.text))
