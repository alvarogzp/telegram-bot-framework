from bot import project_info
from bot.action.core.action import ActionGroup
from bot.action.core.command import CommandAction
from bot.action.core.filter import MessageAction, TextMessageAction, NoPendingAction, EditedMessageAction, \
    PendingAction, NoForwardedMessage, VoiceMessageAction
from bot.action.extra.audios import SaveVoiceAction, ListVoiceAction
from bot.action.extra.hashtags import SaveHashtagsAction, ListHashtagsAction
from bot.action.extra.legacypole import LegacyPoleAction
from bot.action.extra.message import ShowMessageAction
from bot.action.extra.messages import SaveMessageAction, ListMessageAction
from bot.action.extra.pole import SavePoleAction, ListPoleAction, ManagePoleTimezonesAction
from bot.action.extra.random import RandomChoiceAction
from bot.action.standard.about import AboutAction, VersionAction
from bot.action.standard.admin import RestartAction, EvalAction, AdminActionWithErrorMessage, AdminAction, HaltAction
from bot.action.standard.admin.config_status import ConfigStatusAction
from bot.action.standard.admin.fail import FailAction
from bot.action.standard.admin.instance import InstanceAction
from bot.action.standard.admin.state import StateAction
from bot.action.standard.answer import AnswerAction
from bot.action.standard.async import AsyncApiAction
from bot.action.standard.asynchronous import AsynchronousAction
from bot.action.standard.benchmark import BenchmarkAction, WorkersAction
from bot.action.standard.chatsettings.action import ChatSettingsAction
from bot.action.standard.enterexit import GreetAction, LeaveAction
from bot.action.standard.gapdetector import GlobalGapDetectorAction
from bot.action.standard.group_admin import GroupAdminAction
from bot.action.standard.info.action import ChatInfoAction, UserInfoAction
from bot.action.standard.internationalization import InternationalizationAction
from bot.action.standard.logger import LoggerAction
from bot.action.standard.perchat import PerChatAction
from bot.action.standard.silence import SilenceAction
from bot.action.standard.toggle import GetSetFeatureAction, ToggleableFeatureAction
from bot.action.standard.userinfo import SaveUserAction
from bot.bot import Bot


class BotManager:
    def __init__(self):
        self.bot = Bot(project_info.name)

    def setup_actions(self):
        self.bot.set_action(
            ActionGroup(
                LoggerAction().then(
                    AsyncApiAction().then(
                        GlobalGapDetectorAction().then(

                            # # ALWAYS (or SAVE) ACTIONS # #

                            MessageAction().then(
                                SaveUserAction(),

                                PerChatAction().then(
                                    NoForwardedMessage().then(
                                        VoiceMessageAction().then(
                                            SaveVoiceAction()
                                        )
                                    ),

                                    SaveMessageAction(),
                                    SavePoleAction(),

                                    ToggleableFeatureAction("pole").then(
                                        LegacyPoleAction()
                                    ),

                                    TextMessageAction().then(
                                        SaveHashtagsAction()
                                    )
                                )
                            ),

                            EditedMessageAction().then(
                                PerChatAction().then(
                                    SaveMessageAction()
                                )
                            ),

                            # # INTERACTIVE ACTIONS # #

                            NoPendingAction().then(
                                MessageAction().then(
                                    PerChatAction().then(
                                        InternationalizationAction().then(

                                            ToggleableFeatureAction("greet").then(
                                                GreetAction()
                                            ),
                                            ToggleableFeatureAction("leave").then(
                                                LeaveAction()
                                            ),

                                            TextMessageAction().then(

                                                CommandAction("start").then(
                                                    AnswerAction("Hello! I am " + self.bot.cache.bot_info.first_name + " and I am here to serve you.")
                                                ),

                                                CommandAction("about").then(
                                                    AboutAction(
                                                        project_info.name,
                                                        authors=project_info.authors_credits,
                                                        is_open_source=project_info.is_open_source,
                                                        url=project_info.url,
                                                        license_name=project_info.license_name,
                                                        license_url=project_info.license_url,
                                                        donation_addresses=project_info.donation_addresses
                                                    )
                                                ),

                                                CommandAction("version").then(
                                                    VersionAction(
                                                        project_info.name,
                                                        project_info.url + "/releases"
                                                    )
                                                ),

                                                CommandAction("benchmark").then(
                                                    AsynchronousAction("benchmark").then(
                                                        BenchmarkAction()
                                                    )
                                                ),

                                                CommandAction("ping").then(
                                                    AnswerAction("Up and running!")
                                                ),

                                                CommandAction("me", is_personal=True).then(
                                                    UserInfoAction(always_sender=True)
                                                ),

                                                CommandAction("user", is_personal=True).then(
                                                    UserInfoAction()
                                                ),

                                                CommandAction("chat").then(
                                                    ChatInfoAction()
                                                ),

                                                # ADMIN ACTIONS #

                                                CommandAction("restart").then(
                                                    AdminActionWithErrorMessage().then(
                                                        RestartAction()
                                                    )
                                                ),
                                                CommandAction("halt").then(
                                                    AdminActionWithErrorMessage().then(
                                                        HaltAction()
                                                    )
                                                ),
                                                CommandAction("eval").then(
                                                    AdminActionWithErrorMessage().then(
                                                        EvalAction()
                                                    )
                                                ),
                                                CommandAction("state").then(
                                                    AdminActionWithErrorMessage().then(
                                                        StateAction()
                                                    )
                                                ),
                                                CommandAction("config").then(
                                                    AdminActionWithErrorMessage().then(
                                                        ConfigStatusAction()
                                                    )
                                                ),
                                                CommandAction("instance").then(
                                                    AdminActionWithErrorMessage().then(
                                                        InstanceAction()
                                                    )
                                                ),
                                                CommandAction("workers").then(
                                                    AdminActionWithErrorMessage().then(
                                                        WorkersAction()
                                                    )
                                                ),
                                                CommandAction("fail").then(
                                                    AdminActionWithErrorMessage().then(
                                                        FailAction()
                                                    )
                                                ),

                                                # FEATURES #

                                                CommandAction("settings").then(
                                                    GroupAdminAction().then(
                                                        ChatSettingsAction()
                                                    )
                                                ),

                                                CommandAction("silence").then(
                                                    GroupAdminAction().then(
                                                        SilenceAction()
                                                    )
                                                ),

                                                CommandAction("hashtags").then(
                                                    ListHashtagsAction()
                                                ),

                                                CommandAction("feature").then(
                                                    GetSetFeatureAction()
                                                ),

                                                CommandAction("polestzman").then(
                                                    GroupAdminAction().then(
                                                        ManagePoleTimezonesAction()
                                                    )
                                                ),

                                                CommandAction("poles").then(
                                                    ListPoleAction("poles")
                                                ),

                                                CommandAction("subpoles").then(
                                                    ListPoleAction("subpoles")
                                                ),

                                                CommandAction("subsubpoles").then(
                                                    ListPoleAction("subsubpoles")
                                                ),

                                                CommandAction("messages").then(
                                                    ListMessageAction()
                                                ),

                                                CommandAction("message").then(
                                                    ShowMessageAction()
                                                ),

                                                CommandAction("audios").then(
                                                    ListVoiceAction()
                                                ),

                                                CommandAction("random").then(
                                                    RandomChoiceAction()
                                                )

                                            )

                                        )
                                    )
                                )
                            ),

                            # # PENDING ACTIONS # #

                            PendingAction().then(
                                MessageAction().then(
                                    PerChatAction().then(
                                        TextMessageAction().then(

                                            CommandAction("ping").then(
                                                AnswerAction("I'm back! Sorry for the delay...")
                                            ),

                                            AdminAction().then(
                                                CommandAction("restart").then(
                                                    RestartAction()
                                                ),
                                                CommandAction("halt").then(
                                                    HaltAction()
                                                )
                                            )

                                        )
                                    )
                                )
                            )

                        )
                    )
                )
            )
        )

    def run(self):
        self.bot.run()
