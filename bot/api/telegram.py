import threading

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


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
        response = self.__get_session().send(request, timeout=60)
        self.__log_response(response)
        json_response = response.json()
        if not json_response["ok"]:
            raise TelegramBotApiException(json_response["description"])
        return json_response["result"]

    def __get_session(self):
        session = self.local.__dict__.get("session")
        if not session:
            session = self.__create_session()
            self.local.session = session
        return session

    def __create_session(self):
        session = requests.session()
        # Retry one time on read errors, as the connection could have been closed
        # by the remote side and its close notification might have been lost,
        # blocked by firewall or dropped by NAT.
        # In that case, the session will try to reuse the connection thinking it is
        # still alive just to fail with a read error when the remote sends the reset.
        #
        # So, by retrying in that case we avoid this error and do not lose that api
        # call, which could be translated in a message lost.
        # That way we try to get the same behavior as we had when not using sessions.
        #
        # The drawback is that we could also be masquerading some *real* read errors
        # and retrying a request already processed by the server, repeating some
        # action (eg. a duplicate message).
        # But, during a year of production use we never had any read error of this kind.
        retry = Retry(total=1, connect=0, read=1, status=0)
        # passing prefix lowered to work-around https://github.com/requests/requests/pull/4349
        session.mount(self.base_url.lower(), HTTPAdapter(max_retries=retry))
        return session

    def __log_request(self, request: requests.PreparedRequest):
        if self.debug:
            print(">> " + request.url)

    def __log_response(self, response: requests.Response):
        if self.debug:
            print("<< " + response.text)


class TelegramBotApiException(Exception):
    pass
