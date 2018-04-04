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
        return (
            self._item("Admin user", self.__formatted_chat(self.config.admin_user_id)),
            self._item("Admin chat", self.__formatted_chat(self.config.admin_chat_id)),
            self._item("Log chat", self.__formatted_chat(self.config.log_chat_id)),
            self._item("Traceback chat", self.__formatted_chat(self.config.traceback_chat_id())),
            self._item("Async enabled", self.config.async()),
            self._item("Reuse connections", self.config.reuse_connections()),
            self._item("Debug on stdout", self.config.debug()),
            self._item("Send traceback on error (deprecated)", self.config.send_error_tracebacks()),
            self._item("Scheduler events on log chat", self.config.scheduler_events_on_log_chat()),
            self._item("Sleep on get_updates error", self.config.sleep_seconds_on_get_updates_error, "seconds"),
            self._item("Max error time in normal mode", self.config.max_error_seconds_allowed_in_normal_mode, "seconds"),
            self._item("Max network workers", self.config.max_network_workers),
            self._item("Instance name", self.config.instance_name)
        )

    @staticmethod
    def _item(label: str, value, additional_text: str = ""):
        text = FormattedText()\
            .normal("{label}: {value}")\
            .start_format()\
            .normal(label=label)\
            .bold(value=value)\
            .end_format()
        if additional_text:
            text.normal(" ").normal(additional_text)
        return text

    def __formatted_chat(self, chat_id):
        if chat_id:
            chat = self.user_storage_handler.get(chat_id)
            return ChatFormatter.format_group_or_user(chat)
        else:
            return "<Not set (disabled)>"
