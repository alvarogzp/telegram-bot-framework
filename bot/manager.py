from bot.action.admin import AdminAction, StopAction, EvalAction
from bot.action.answer import AnswerAction
from bot.action.core.action import ActionGroup
from bot.action.core.command import CommandAction
from bot.action.core.filter import MessageAction, TextMessageAction, NoPendingAction
from bot.action.extra.hashtags import HashtagRecolectorAction, HashtagListAction
from bot.action.extra.pole import PoleAction
from bot.action.gapdetector import GlobalGapDetectorAction
from bot.action.perchat import PerChatAction
from bot.action.toggle import GetSetFeatureAction, ToggleableFeatureAction
from bot.bot import Bot


class BotManager:
    def __init__(self):
        self.bot = Bot()

    def setup_actions(self):
        self.bot.set_action(
            ActionGroup(
                GlobalGapDetectorAction().then(

                    NoPendingAction().then(
                        MessageAction().then(
                            # GreetAction(),
                            # LeaveAction(),
                        )
                    ),

                    MessageAction().then(
                        PerChatAction().then(
                            ToggleableFeatureAction("pole").then(
                                PoleAction()
                            ),

                            TextMessageAction().then(
                                CommandAction("start").then(
                                    AnswerAction(
                                        "Hello! I am " + self.bot.cache.bot_info.first_name + " and I am here to serve you.\nSorry if I cannot do too much for you now, I am still under construction.")
                                ),
                                AdminAction().then(
                                    CommandAction("shutdown").then(
                                        StopAction()
                                    ),
                                    CommandAction("eval").then(
                                        EvalAction()
                                    )
                                ),

                                HashtagRecolectorAction(),
                                CommandAction("hashtags").then(
                                    HashtagListAction()
                                ),

                                CommandAction("feature").then(
                                    GetSetFeatureAction()
                                )
                            )
                        )
                    )

                )
            )
        )

    def run(self):
        self.bot.run()
