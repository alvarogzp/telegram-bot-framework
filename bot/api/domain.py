

class Response:
    def __init__(self, response: dict):
        self.response = response

    def get_or_fail(self, key):
        value = self.response[key]
        return self.wrap_response(value)

    def get_or_default(self, key, default=None):
        value = self.response.get(key, default)
        return self.wrap_response(value)

    @staticmethod
    def wrap_response(response):
        if type(response) is dict:
            return Response(response)
        elif type(response) is list:
            return ResponseList(response)
        else:
            return response


class ResponseList:
    def __init__(self, responses: list):
        self.responses = responses

    def __iter__(self):
        return self.__wrapped_responses()

    def __wrapped_responses(self):
        for response in self.responses:
            yield Response.wrap_response(response)
