from typing import Union

from bot.api.domain import ApiObject
from bot.api.telegram import TelegramBotApiException


class ApiException(Exception):
    def __init__(self, error_code: int, description: str, parameters: Union[ApiObject, None]):
        self.error_code = error_code
        self.description = description
        self.parameters = parameters
        super().__init__(description)


class TooManyRequestsApiException(ApiException):
    def __init__(self, error_code: int, description: str, parameters: Union[ApiObject, None], retry_after: int):
        super().__init__(error_code, description, parameters)
        self.retry_after = retry_after


class ApiExceptionFactory:
    @staticmethod
    def from_telegram_bot_api_exception(exception: TelegramBotApiException):
        error_code = exception.error_code
        description = exception.description
        parameters = ApiObject.wrap_api_object(exception.parameters)
        if parameters is not None:
            retry_after = parameters.retry_after
            if retry_after is not None:
                return TooManyRequestsApiException(error_code, description, parameters, retry_after)
        return ApiException(error_code, description, parameters)
