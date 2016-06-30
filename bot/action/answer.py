from bot.action.core.action import Action
from bot.api.domain import Message


class AnswerAction(Action):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def process(self, event):
        self.api.send_message(Message.create_reply(event.message, self.text))
