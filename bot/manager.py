from bot.actions.admin import AdminAction, StopAction
from bot.actions.answer import AnswerAction
from bot.actions.command import CommandAction
from bot.actions.filter import NoPendingAction, MessageAction, TextMessageAction
from bot.actions.greet import GreetAction
from bot.actions.leave import LeaveAction
from bot.bot import Bot


class BotManager:
    def __init__(self):
        self.bot = Bot()

    def setup_actions(self):
        no_pending_message_actions = NoPendingAction().then(
            MessageAction().then(
                GreetAction(),
                LeaveAction(),
            )
        )
        message_actions = MessageAction().then(
            TextMessageAction().then(
                CommandAction("start").then(
                    AnswerAction("Hello! I am " + self.bot.cache.bot_info.first_name + " and I am here to serve you.\nSorry if I cannot do too much for you now, I am still under construction.")
                ),
                AdminAction().then(
                    CommandAction("shutdown").then(
                        StopAction()
                    )
                )
            )
        )
        self.bot.add_action(no_pending_message_actions)
        self.bot.add_action(message_actions)

    def run(self):
        self.bot.run()
