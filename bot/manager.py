from bot.action.admin import AdminAction, StopAction, EvalAction
from bot.action.answer import AnswerAction
from bot.action.core.action import ActionGroup
from bot.action.core.command import CommandAction
from bot.action.core.filter import MessageAction, TextMessageAction, NoPendingAction, EditedMessageAction
from bot.action.enterexit import GreetAction, LeaveAction
from bot.action.extra.hashtags import HashtagRecolectorAction, HashtagListAction
from bot.action.extra.messages import SaveMessageAction
from bot.action.extra.pole import SavePoleAction, ListPoleAction
from bot.action.gapdetector import GlobalGapDetectorAction
from bot.action.perchat import PerChatAction
from bot.action.toggle import GetSetFeatureAction, ToggleableFeatureAction
from bot.action.userinfo import SaveUserAction
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
                            PerChatAction().then(
                                ToggleableFeatureAction("greet").then(
                                    GreetAction()
                                ),
                                ToggleableFeatureAction("leave").then(
                                    LeaveAction()
                                )
                            )
                        )
                    ),

                    EditedMessageAction().then(
                        PerChatAction().then(
                            SaveMessageAction()
                        )
                    ),

                    MessageAction().then(
                        SaveUserAction(),

                        PerChatAction().then(
                            SaveMessageAction(),
                            SavePoleAction(),

                            TextMessageAction().then(
                                HashtagRecolectorAction(),

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

                                CommandAction("hashtags").then(
                                    HashtagListAction()
                                ),

                                CommandAction("feature").then(
                                    GetSetFeatureAction()
                                ),

                                CommandAction("poles").then(
                                    ListPoleAction()
                                )
                            )
                        )
                    )

                )
            )
        )

    def run(self):
        self.bot.run()
