from bot.action.core.action import Action
from bot.action.standard.userinfo import UserStorageHandler
from bot.action.util.format import ChatFormatter
from bot.action.util.textformat import FormattedText
from bot.storage import State, Config


class ConfigStatusAction(Action):
    def process(self, event):
        response = FormattedText().newline().join(ConfigStatus(self.config, self.state).get_config_status())
        response.newline().newline()\
            .italic("These are the current values read from storage.").newline()\
            .italic("But please, note that most of them are being cached at startup and "
                    "changing them will not modify bot behavior until it is restarted.")
        self.api.send_message(response.build_message().to_chat_replying(event.message))


class ConfigStatus:
    def __init__(self, config: Config, state: State):
        """
        :param state: Used to resolve chat ids to names
        """
        self.config = config
        self.user_storage_handler = UserStorageHandler.get_instance(state)

    def get_config_status(self):
        admin_user = FormattedText()\
            .normal("Admin user: {user}").start_format()\
            .bold(user=self.__formatted_chat(self.config.admin_user_id)).end_format()
        admin_chat = FormattedText()\
            .normal("Admin chat: {chat}").start_format()\
            .bold(chat=self.__formatted_chat(self.config.admin_chat_id)).end_format()
        log_chat = FormattedText()\
            .normal("Log chat: {chat}").start_format()\
            .bold(chat=self.__formatted_chat(self.config.log_chat_id)).end_format()
        async = FormattedText()\
            .normal("Async enabled: {bool}").start_format()\
            .bold(bool=self.config.async()).end_format()
        reuse_connections = FormattedText()\
            .normal("Reuse connections: {bool}").start_format()\
            .bold(bool=self.config.reuse_connections()).end_format()
        debug = FormattedText()\
            .normal("Debug on stdout: {bool}").start_format()\
            .bold(bool=self.config.debug()).end_format()
        error_tracebacks = FormattedText()\
            .normal("Send traceback on error: {bool}").start_format()\
            .bold(bool=self.config.send_error_tracebacks()).end_format()
        scheduler_events_on_log_chat = FormattedText()\
            .normal("Scheduler events on log chat: {bool}").start_format()\
            .bold(bool=self.config.scheduler_events_on_log_chat()).end_format()
        sleep_time_on_get_updates_error = FormattedText()\
            .normal("Sleep on get_updates error: {seconds} seconds").start_format()\
            .bold(seconds=self.config.sleep_seconds_on_get_updates_error).end_format()
        max_error_time_in_normal_mode = FormattedText()\
            .normal("Max error time in normal mode: {seconds} seconds").start_format()\
            .bold(seconds=self.config.max_error_seconds_allowed_in_normal_mode).end_format()
        max_network_workers = FormattedText()\
            .normal("Max network workers: {number}").start_format()\
            .bold(number=self.config.max_network_workers).end_format()
        instance_name = FormattedText()\
            .normal("Instance name: {name}").start_format()\
            .bold(name=self.config.instance_name).end_format()
        return (
            admin_user,
            admin_chat,
            log_chat,
            async,
            reuse_connections,
            debug,
            error_tracebacks,
            scheduler_events_on_log_chat,
            sleep_time_on_get_updates_error,
            max_error_time_in_normal_mode,
            max_network_workers,
            instance_name
        )

    def __formatted_chat(self, chat_id):
        if chat_id:
            chat = self.user_storage_handler.get(chat_id)
            return ChatFormatter.format_group_or_user(chat)
        else:
            return "<Not set (disabled)>"
