import os


class Config:
    def __init__(self, config_dir):
        self.config_dir = config_dir + "/"

    def get_auth_token(self):
        return self.__get_config_value("auth_token")

    def get_admin_user_id(self):
        return self.__get_config_value("admin_user_id")

    def is_debug_enabled(self):
        return self.__get_config_value("debug").lower() == "true"

    def __get_config_value(self, config_key):
        return open(self.config_dir + config_key).read().strip()


class State:
    def __init__(self, state_dir):
        self.state_dir = state_dir + "/"

    def get_next_update_id(self):
        return self.__get_state_value("next_update_id")

    def set_next_update_id(self, next_update_id):
        self.__set_state_value("next_update_id", next_update_id)

    def __get_state_value(self, state_key, default_value=None):
        state_file_path = self.state_dir + state_key
        if not os.path.isfile(state_file_path):
            return default_value
        return open(state_file_path).read()

    def __set_state_value(self, state_key, state_value):
        with open(self.state_dir + state_key, "w") as f:
            f.write(state_value)


class Cache:
    def __init__(self):
        self.cache = {}

    def __getattr__(self, item):
        return self.cache.get(item)

    def __setattr__(self, key, value):
        if key == "cache":
            super().__setattr__(key, value)
        else:
            self.cache[key] = value
