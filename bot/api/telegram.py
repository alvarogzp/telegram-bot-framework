import threading

import requests


class TelegramBotApi:
    """This is a threading-safe API. Avoid breaking it by adding state."""

    def __init__(self, auth_token, debug: bool):
        self.base_url = "https://api.telegram.org/bot" + auth_token + "/"
        self.debug = debug
        self.local = threading.local()

    def __getattr__(self, item):
        return self.__get_request_from_function_name(item)

    def __get_request_from_function_name(self, function_name):
        return lambda **params: self.__send_request(function_name, params)

    def __send_request(self, command, params):
        request = requests.Request("GET", self.base_url + command, params=params).prepare()
        self.__log_request(request)
        response = self.__get_session().send(request, timeout=60).json()
        self.__log_response(response)
        if not response["ok"]:
            raise TelegramBotApiException(response["description"])
        return response["result"]

    def __get_session(self):
        session = self.local.__dict__.get("session")
        if not session:
            session = requests.session()
            self.local.session = session
        return session

    def __log_request(self, request):
        if self.debug:
            print(">> " + request.url)

    def __log_response(self, response):
        if self.debug:
            print("<< " + str(response))


class TelegramBotApiException(Exception):
    pass
