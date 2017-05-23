from bot.action.core.action import Action
from bot.action.core.command.usagemessage import CommandUsageMessage
from bot.action.util.codecs import Codecs
from bot.action.util.textformat import FormattedText


class ChatSettingsAction(Action):
    def process(self, event):
        action, key, new_value = self.parse_args(event.command_args.split(" "))
        if key is not None and self.is_valid_key(key):
            settings = event.settings
            if action == "list":
                response = self.list_settings(settings)
            elif action == "get":
                response = self.get_current_value(settings, key)
            elif action == "set":
                response = self.set_new_value(settings, key, new_value)
            elif action == "del":
                response = self.set_new_value(settings, key, None)
            else:
                response = self.get_usage(event)
        else:
            response = self.get_usage(event)
        response.to_chat_replying(event.message)
        self.api.send_message(response)

    @staticmethod
    def parse_args(args):
        action = "get"
        key = None
        new_value = None
        if len(args) == 1 and args[0] != "":
            key = args[0]
            if key == "list":
                action = key
        elif len(args) > 1:
            action = args[0]
            key = args[1]
            new_value = " ".join(args[2:])
        return action, key, new_value

    @staticmethod
    def is_valid_key(key):
        return key.replace("_", "").isalnum()

    @staticmethod
    def list_settings(settings):
        keys = settings.list()
        response = FormattedText().normal("Settings status for this chat:").newline()
        for setting_name, value, default_value, is_set, is_supported in keys:
            response.newline()
            if not is_supported:
                response.code_inline(setting_name)
            elif is_set:
                response.bold(setting_name)
            else:
                response.normal(setting_name)
            response.normal(" → ").code_inline(value)
            if is_set and is_supported:
                response.normal(" (default: ").code_inline(default_value).normal(")")
        return response.build_message()

    def get_current_value(self, settings, key):
        value = self.__get_current_value(settings, key)
        response = FormattedText().bold("Setting").normal(":").newline().code_block(key).newline().newline()\
            .bold("Value").normal(":").newline().concat(value)
        is_supported = settings.is_supported(key)
        response.newline().newline()\
            .bold("Supported?").newline().code_block("yes" if is_supported else "no")
        if is_supported and settings.is_set(key):
            response.newline().newline()\
                .bold("Default value").normal(":").newline().code_block(settings.get_default_value(key))
        return response.build_message()

    def set_new_value(self, settings, key, new_value):
        previous_value = self.__get_current_value(settings, key)
        try:
            settings.set(key, new_value)
        except Exception as e:
            return FormattedText().bold("Setting could not be updated").newline().newline()\
                .normal("Please, input a valid value.").newline().newline()\
                .normal("Error was: ").code_inline(e)\
                .build_message()
        current_value = self.__get_current_value(settings, key)
        return FormattedText().bold("Setting updated!").newline().newline()\
            .bold("Name").normal(":").newline().code_block(key).newline().newline()\
            .bold("Previous value").normal(":").newline().concat(previous_value).newline().newline()\
            .bold("Current value").normal(":").newline().concat(current_value)\
            .build_message()

    @staticmethod
    def __get_current_value(settings, key):
        text = FormattedText()
        value = settings.get(key)
        if value is None:
            text.italic("No value")
        else:
            text.code_block(value)
        if not settings.is_set(key):
            text.newline().italic("(default)")
        return text

    @staticmethod
    def get_usage(event):
        return CommandUsageMessage.get_usage_message(event.command, ["list", "[get] <key>", "set <key> <value>", "del <key>"])


_SETTINGS = []
_DEFAULT_VALUES = {}
_CODECS = {}


def add_setting(name, default_value, codec=None):
    _SETTINGS.append(name)
    _DEFAULT_VALUES[name] = default_value
    if codec is not None:
        _CODECS[name] = codec
    return name


class ChatSettings:
    # List of chat settings
    # To add one: SETTING = add_setting("name", "default_value")
    LANGUAGE = add_setting("language", "en")
    STORE_MESSAGES = add_setting("store_messages", "on")
    OVERRIDE_MESSAGES_OPT_OUT = add_setting("override_messages_opt_out", "off")
    THROTTLING_SECONDS = add_setting("throttling_seconds", 60, Codecs.INT)

    def __init__(self, settings_state):
        self.settings_state = settings_state

    def get(self, name):
        value = self.settings_state.get_value(name)
        if value is None:
            value = self.get_default_value(name)
        elif name in _CODECS:
            value = _CODECS[name].decode(value)
        return value

    def set(self, name, value):
        if name in _CODECS:
            # decode to check if value is valid
            _CODECS[name].decode(value)
        self.settings_state.set_value(name, value)

    def list(self):
        """
        :rtype: list(setting_name, value, default_value, is_set, is_supported)
        """
        settings = []
        for setting in _SETTINGS:
            value = self.get(setting)
            is_set = self.is_set(setting)
            default_value = self.get_default_value(setting)
            is_supported = True
            settings.append((setting, value, default_value, is_set, is_supported))
        for setting in sorted(self.settings_state.list_keys()):
            if not self.is_supported(setting):
                value = self.get(setting)
                default_value = None
                is_set = True
                is_supported = False
                settings.append((setting, value, default_value, is_set, is_supported))
        return settings

    @staticmethod
    def get_default_value(name):
        return _DEFAULT_VALUES.get(name)

    def is_set(self, name):
        return self.settings_state.exists_value(name)

    @staticmethod
    def is_supported(name):
        return name in _SETTINGS


class ChatSettingsRepository:
    def __init__(self):
        self.cache = {}

    def get_for_event(self, event):
        chat_id = event.chat.id
        if self.__is_cached(chat_id):
            return self.__get_cached(chat_id)
        return self.__get_new_and_add_to_cache(event.state, chat_id)

    def get_for_chat_id(self, global_state, chat_id):
        if self.__is_cached(chat_id):
            return self.__get_cached(chat_id)
        chat_state = global_state.get_for_chat_id(chat_id)
        return self.__get_new_and_add_to_cache(chat_state, chat_id)

    def __is_cached(self, chat_id):
        return chat_id in self.cache

    def __get_cached(self, chat_id):
        return self.cache[chat_id]

    def __get_new_and_add_to_cache(self, chat_state, chat_id):
        settings_state = chat_state.get_for("settings")
        chat_settings = ChatSettings(settings_state)
        self.__add_to_cache(chat_id, chat_settings)
        return chat_settings

    def __add_to_cache(self, chat_id, value):
        assert chat_id not in self.cache
        self.cache[chat_id] = value


repository = ChatSettingsRepository()
