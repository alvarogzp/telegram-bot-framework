import requests

from bot.api.domain import ApiObject


class TelegramBotApi:
    def __init__(self, auth_token, debug: bool):
        self.base_url = "https://api.telegram.org/bot" + auth_token + "/"
        self.debug = debug

    def get_me(self):
        return self.__send_request("getMe")

    def send_message(self, **params):
        return self.__send_request("sendMessage", **params)

    def get_updates(self, offset=None, timeout=None):
        return self.__send_request("getUpdates", offset=offset, timeout=timeout)

    def __send_request(self, command, **params):
        request = requests.get(self.base_url + command, params=params, timeout=60)
        self.__log_request(request)
        response = request.json()
        self.__log_response(response)
        if not response["ok"]:
            raise TelegramBotApiException(response["description"])
        return ApiObject.wrap_api_object(response["result"])

    def __log_request(self, request):
        if self.debug:
            print(">> " + request.url)

    def __log_response(self, response):
        if self.debug:
            print("<< " + str(response))


class TelegramBotApiException(Exception):
    pass
