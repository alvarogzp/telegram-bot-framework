from bot.api.domain import Message
from bot.api.telegram import TelegramBotApi, TelegramBotApiException
from bot.storage import State


LOCAL_PARAM_ERROR_CALLBACK = "__error_callback"
LOCAL_PARAMS = [LOCAL_PARAM_ERROR_CALLBACK]


class Api:
    def __init__(self, telegram_api: TelegramBotApi, state: State):
        self.telegram_api = telegram_api
        self.state = state

    def send_message(self, message: Message, **params):
        message_params = message.data.copy()
        message_params.update(params)
        return self.sendMessage(**message_params)

    def get_pending_updates(self):
        there_are_pending_updates = True
        while there_are_pending_updates:
            there_are_pending_updates = False
            for update in self.get_updates(timeout=0):
                there_are_pending_updates = True
                yield update

    def get_updates(self, timeout=45):
        updates = self.getUpdates(offset=self.__get_updates_offset(), timeout=timeout)
        for update in updates:
            self.__set_updates_offset(update.update_id)
            yield update

    def __get_updates_offset(self):
        return self.state.next_update_id

    def __set_updates_offset(self, last_update_id):
        self.state.next_update_id = str(last_update_id + 1)

    def __getattr__(self, item):
        return self.__get_api_call_hook_for(item)

    def __get_api_call_hook_for(self, api_call):
        return lambda **params: self.__api_call_hook(api_call, **params)

    def __api_call_hook(self, command, **params):
        api_func = self.telegram_api.__getattr__(command)
        local_params = self.__separate_local_params(params)
        try:
            return api_func(**params)
        except TelegramBotApiException as e:
            return self.__handle_api_error(e, local_params)

    @staticmethod
    def __separate_local_params(params):
        local_params = {}
        for local_param in LOCAL_PARAMS:
            if local_param in params:
                local_params[local_param] = params.pop(local_param)
        return local_params

    @staticmethod
    def __handle_api_error(e, local_params):
        error_callback = local_params.get(LOCAL_PARAM_ERROR_CALLBACK)
        if callable(error_callback):
            return error_callback(e)
        else:
            raise e
