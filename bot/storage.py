import os

from bot.api.domain import Chat
from bot.utils.attributeobject import DictionaryObject, AttributeObject


class Storage(AttributeObject):
    def __init__(self, base_dir):
        super().__init__("_base_dir", "_cache")
        self._base_dir = base_dir
        self._cache = {}

    def get_for_chat(self, chat: Chat):
        chat_path = os.path.join("chat", str(chat.id))
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

    def get_value(self, key, default_value=None):
        value_path = self.__get_value_path(key)
        if not os.path.isfile(value_path):
            return default_value
        return open(value_path).read()

    def set_value(self, key, value, append=False):
        value_path = self.__get_value_path(key)
        if value is None:
            if os.path.exists(value_path):
                os.remove(value_path)
        else:
            mode = "a" if append else "w"
            with open(value_path, mode) as f:
                f.write(value)

    def __get_value_path(self, key):
        return os.path.join(self._base_dir, key)


class Config(Storage):
    def __init__(self, config_dir):
        super().__init__(config_dir)

    def is_debug_enabled(self):
        return self.get_value("debug").lower() == "true"

    def get_value(self, key, default_value=None):
        value = super().get_value(key, default_value)
        if value is not None:
            value = value.strip()
        return value

    def set_value(self, key, value, append=False):
        # do not allow to modify config values
        pass


class State(Storage):
    def __init__(self, state_dir):
        super().__init__(state_dir)
        if not os.path.exists(self._base_dir):
            os.makedirs(self._base_dir)


class Cache(DictionaryObject):
    def get_for_chat(self, chat: Chat):
        return self.get_for("chat" + str(chat.id))

    def get_for(self, key):
        return self._dictionary.setdefault(key, Cache())
