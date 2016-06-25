from bot.actions.filter import NoPendingAction, MessageAction
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
        self.bot.add_action(no_pending_message_actions)

    def run(self):
        self.bot.run()
