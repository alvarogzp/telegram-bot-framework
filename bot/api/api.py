from bot.action.core.update import Update
from bot.api.call.call import ApiCall
from bot.api.call.params import ApiCallParams
from bot.api.domain import Message, Photo, Sticker, Document, Voice, VideoNote, Audio, Video, Location, Contact
from bot.api.telegram import TelegramBotApi
from bot.storage import State


class Api:
    def __init__(self, telegram_api: TelegramBotApi, state: State):
        self.telegram_api = telegram_api
        self.state = state
        self.async = self

    def enable_async(self, async_api):
        self.async = async_api

    def send_message(self, message: Message, **params):
        message_params = message.data.copy()
        message_params.update(params)
        if self.__should_send_message(message_params):
            send_func = self.__get_send_func(message.get_type())
            return send_func(**message_params)

    def __should_send_message(self, message_params):
        chat_id = message_params.get("chat_id")
        if chat_id:
            chat_state = self.state.get_for_chat_id(chat_id)
            is_silenced = chat_state.silenced
            if is_silenced:
                return False
        return True

    def __get_send_func(self, message_type):
        if message_type == Photo:
            return self.sendPhoto
        elif message_type == Sticker:
            return self.sendSticker
        elif message_type == Document:
            return self.sendDocument
        elif message_type == Voice:
            return self.sendVoice
        elif message_type == VideoNote:
            return self.sendVideoNote
        elif message_type == Audio:
            return self.sendAudio
        elif message_type == Video:
            return self.sendVideo
        elif message_type == Location:
            return self.sendLocation
        elif message_type == Contact:
            return self.sendContact
        else:
            # fallback to sendMessage
            return self.sendMessage

    def get_pending_updates(self):
        there_are_pending_updates = True
        while there_are_pending_updates:
            there_are_pending_updates = False
            for update in self.get_updates(timeout=0):
                there_are_pending_updates = True
                update.is_pending = True
                yield update

    def get_updates(self, timeout=45):
        updates = self.getUpdates(offset=self.__get_updates_offset(), timeout=timeout)
        for update in updates:
            self.__set_updates_offset(update.update_id)
            yield Update(update)

    def __get_updates_offset(self):
        return self.state.next_update_id

    def __set_updates_offset(self, last_update_id):
        self.state.next_update_id = str(last_update_id + 1)

    def __getattr__(self, item):
        return self.__get_api_call_hook_for(item)

    def __get_api_call_hook_for(self, api_call):
        api_func = self.telegram_api.__getattr__(api_call)
        call = ApiCall(api_func, api_call)
        return lambda **params: self.__api_call_hook(call, params)

    @staticmethod
    def __api_call_hook(call: ApiCall, params: dict):
        return call.call(ApiCallParams(params))
