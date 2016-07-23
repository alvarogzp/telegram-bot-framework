from bot.action.admin import RestartAction, EvalAction, AdminActionWithErrorMessage, AdminAction
from bot.action.answer import AnswerAction
from bot.action.core.action import ActionGroup
from bot.action.core.command import CommandAction
from bot.action.core.filter import MessageAction, TextMessageAction, NoPendingAction, EditedMessageAction, PendingAction
from bot.action.enterexit import GreetAction, LeaveAction
from bot.action.extra.hashtags import SaveHashtagsAction, ListHashtagsAction
from bot.action.extra.legacypole import LegacyPoleAction
from bot.action.extra.messages import SaveMessageAction, ListMessageAction
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
                                ),

                                TextMessageAction().then(

                                    CommandAction("start").then(
                                        AnswerAction(
                                            "Hello! I am " + self.bot.cache.bot_info.first_name + " and I am here to serve you.\nSorry if I cannot do too much for you now, I am still under construction.")
                                    ),

                                    CommandAction("restart").then(
                                        AdminActionWithErrorMessage().then(
                                            RestartAction()
                                        )
                                    ),
                                    CommandAction("eval").then(
                                        AdminActionWithErrorMessage().then(
                                            EvalAction()
                                        )
                                    ),

                                    CommandAction("hashtags").then(
                                        ListHashtagsAction()
                                    ),

                                    CommandAction("feature").then(
                                        GetSetFeatureAction()
                                    ),

                                    CommandAction("poles").then(
                                        ListPoleAction()
                                    ),

                                    CommandAction("messages").then(
                                        ListMessageAction()
                                    )

                                )
                            )
                        )
                    ),

                    PendingAction().then(
                        MessageAction().then(
                            PerChatAction().then(
                                TextMessageAction().then(
                                    AdminAction().then(
                                        CommandAction("restart").then(
                                            RestartAction()
                                        )
                                    )
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

                            ToggleableFeatureAction("pole").then(
                                LegacyPoleAction()
                            ),

                            TextMessageAction().then(
                                SaveHashtagsAction()
                            )
                        )
                    )

                )
            )
        )

    def run(self):
        self.bot.run()
