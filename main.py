#!/usr/bin/env python3

import requests

CONFIG_DIR = "config"


class Bot:
    def __init__(self):
        self.config = Config(CONFIG_DIR)
        self.api = TelegramBotApi(self.config.get_auth_token())

    def run(self):
        self.api.send_message(self.config.get_admin_user_id(), "test")


class TelegramBotApi:
    def __init__(self, auth_token):
        self.base_url = "https://api.telegram.org/bot" + auth_token + "/"

    def send_message(self, chat_id, text):
        self.__send_request("sendMessage", chat_id=chat_id, text=text)

    def __send_request(self, command, **params):
        requests.get(self.base_url + command, params=params)


class Config:
    def __init__(self, config_dir):
        self.config_dir = config_dir + "/"

    def get_auth_token(self):
        return self.__get_config_value("auth_token")

    def get_admin_user_id(self):
        return self.__get_config_value("admin_user_id")

    def __get_config_value(self, config_key):
        return open(self.config_dir + config_key).read().strip()


if __name__ == "__main__":
    Bot().run()
