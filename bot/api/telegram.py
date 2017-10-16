import requests


class TelegramBotApi:
    """This is a threading-safe API. Avoid breaking it by adding state."""

    def __init__(self, auth_token, debug: bool):
        self.base_url = "https://api.telegram.org/bot" + auth_token + "/"
        self.debug = debug

    def __getattr__(self, item):
        return self.__get_request_from_function_name(item)

    def __get_request_from_function_name(self, function_name):
        return lambda **params: self.__send_request(function_name, params)

    def __send_request(self, command, params):
        request = requests.get(self.base_url + command, params=params, timeout=60)
        self.__log_request(request)
        response = request.json()
        self.__log_response(response)
        if not response["ok"]:
            raise TelegramBotApiException(response["description"])
        return response["result"]

    def __log_request(self, request):
        if self.debug:
            print(">> " + request.url)

    def __log_response(self, response):
        if self.debug:
            print("<< " + str(response))


class TelegramBotApiException(Exception):
    pass
