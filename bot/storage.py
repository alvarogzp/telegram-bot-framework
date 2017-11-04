import os
import shutil

from bot.utils.attributeobject import DictionaryObject, AttributeObject


class Storage(AttributeObject):
    def __init__(self, base_dir):
        super().__init__("_base_dir", "_cache")
        self._base_dir = base_dir
        self._cache = {}

    def get_for_chat_id(self, chat_id):
        chat_path = os.path.join("chat", str(chat_id))
        return self.get_for(chat_path)

    def get_for(self, key):
        if key not in self._cache:
            instance = self.__class__.__new__(self.__class__)
            instance.__init__(os.path.join(self._base_dir, key))
            self._cache[key] = instance
        return self._cache[key]

    def _getattr(self, key):
        return self.get_value(key)

    def _setattr(self, key, value):
        self.set_value(key, value)

    def exists_value(self, key):
        value_path = self.__get_value_path(key)
        return os.path.exists(value_path)

    def get_value(self, key, default_value=None):
        value_path = self.__get_value_path(key)
        if not os.path.isfile(value_path):
            return default_value
        with open(value_path) as f:
            return f.read()

    def set_value(self, key, value, append=False):
        value_path = self.__get_value_path(key)
        if value is None:
            self.__remove(value_path)
        else:
            self.__create_dirs_if_needed()
            mode = "a" if append else "w"
            with open(value_path, mode) as f:
                f.write(value)

    def list_keys(self):
        if not os.path.isdir(self._base_dir):
            return []
        return os.listdir(self._base_dir)

    def __get_value_path(self, key):
        return os.path.join(self._base_dir, key)

    def __create_dirs_if_needed(self):
        if not os.path.exists(self._base_dir):
            os.makedirs(self._base_dir)

    @staticmethod
    def __remove(value_path):
        if os.path.isdir(value_path):
            shutil.rmtree(value_path)
        elif os.path.isfile(value_path):
            os.remove(value_path)


class Config(Storage):
    DEFAULT_VALUES = {
        "debug": "true",
        "send_error_tracebacks": "true",
        "async": "true",
        "reuse_connections": "true",
        "scheduler_events_on_log_chat": "true",
        "sleep_seconds_on_get_updates_error": "60",
        "max_error_seconds_allowed_in_normal_mode": "3600",
        "max_network_workers": "4",
        "instance_name": ""
    }

    TRUE_VALUES = ("true", "yes", "on", "1")

    def __init__(self, config_dir):
        super().__init__(config_dir)

    def debug(self):
        return self.__is_true("debug")

    def send_error_tracebacks(self):
        return self.__is_true("send_error_tracebacks")

    def async(self):
        return self.__is_true("async")

    def reuse_connections(self):
        return self.__is_true("reuse_connections")

    def scheduler_events_on_log_chat(self):
        return self.__is_true("scheduler_events_on_log_chat")

    def __is_true(self, key):
        value = self._getattr(key)
        return value.lower() in self.TRUE_VALUES

    def _getattr(self, key):
        return self.get_value(key, self._get_default_value(key))

    def _get_default_value(self, key, default_value=None):
        return self.DEFAULT_VALUES.get(key, default_value)

    def get_value(self, key, default_value=None):
        value = super().get_value(key, default_value)
        if value is not None:
            value = value.strip()
        return value

    def set_value(self, key, value, append=False):
        # do not allow to modify config values
        raise Exception("config values cannot be modified")


class State(Storage):
    def __init__(self, state_dir):
        super().__init__(state_dir)


class Cache(DictionaryObject):
    def get_for_chat_id(self, chat_id):
        return self.get_for("chat" + str(chat_id))

    def get_for(self, key):
        return self._dictionary.setdefault(key, Cache())
