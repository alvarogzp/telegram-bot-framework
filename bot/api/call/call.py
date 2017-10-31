from bot.api.call.params import ApiCallParams
from bot.api.domain import ApiObject
from bot.api.exception import ApiExceptionFactory
from bot.api.telegram import TelegramBotApiException
from bot.multithreading.work import Work


class ApiCall:
    def __init__(self, api_func: callable, name: str):
        self.api_func = api_func
        self.name = name

    def call(self, params: ApiCallParams):
        api_call = lambda: self.__do_api_call_and_handle_error(params)
        scheduler = params.scheduler
        if scheduler:
            scheduler(Work(api_call, "async_api_call:" + self.name))
        else:
            return api_call()

    def __do_api_call_and_handle_error(self, params: ApiCallParams):
        try:
            return self.__do_api_call(params)
        except TelegramBotApiException as e:
            exception = ApiExceptionFactory.from_telegram_bot_api_exception(e)
            return self.__handle_api_error(exception, params)

    def __do_api_call(self, params: ApiCallParams):
        return ApiObject.wrap_api_object(self.api_func(**params.send))

    @staticmethod
    def __handle_api_error(e, params: ApiCallParams):
        error_callback = params.error_callback
        if callable(error_callback):
            return error_callback(e)
        else:
            raise e
