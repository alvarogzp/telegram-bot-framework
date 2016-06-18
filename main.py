#!/usr/bin/env python3

import requests

AUTH_TOKEN = open("config/auth_token").read().strip()
USER_ID = open("config/user_id").read().strip()

BASE_URL = "https://api.telegram.org/bot" + AUTH_TOKEN + "/"


def send_request(command, **params):
    requests.get(BASE_URL + command, params=params)


def send_message(chat_id, text):
    send_request("sendMessage", chat_id=chat_id, text=text)


send_message(USER_ID, "test")
