from bot.action.util.codecs import Codecs


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
