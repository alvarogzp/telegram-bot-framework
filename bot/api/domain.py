from bot.api import api


class ApiObject:
    def __init__(self, _type=None, **data):
        self._type = _type
        self.data = data

    def get_or_fail(self, key):
        value = self.data[key]
        return self.wrap_api_object(value)

    def get_or_default(self, key, default=None):
        value = self.data.get(key, default)
        return self.wrap_api_object(value)

    def __getattr__(self, item):
        if len(item) > 1 and item[-1] == "_":
            item = item[:-1]
        return self.get_or_default(item)

    @staticmethod
    def wrap_api_object(data):
        if type(data) is dict:
            return ApiObject(**data)
        elif type(data) is list:
            return ApiObjectList(data)
        else:
            return data


class ApiObjectList:
    def __init__(self, data_list: list):
        self.data_list = data_list

    def __iter__(self):
        return self.__wrapped_api_objects()

    def __wrapped_api_objects(self):
        for data in self.data_list:
            yield ApiObject.wrap_api_object(data)


class OutApiObject(ApiObject):
    def with_error_callback(self, func):
        self.data[api.LOCAL_PARAM_ERROR_CALLBACK] = func
        return self


class Message(OutApiObject):
    def to_chat(self, chat=None, message=None, chat_id=None):
        if message is not None:
            chat = message.chat
        if chat is not None:
            chat_id = chat.id
        self.data["chat_id"] = chat_id
        return self

    def reply_to_message(self, message=None, message_id=None):
        if message is not None:
            message_id = message.message_id
        self.data["reply_to_message_id"] = message_id
        return self

    def to_chat_replying(self, message):
        self.to_chat(message=message)
        self.reply_to_message(message)
        return self

    @staticmethod
    def create(text, chat_id=None, **kwargs):
        return Message(_type=Message, text=text, chat_id=chat_id, **kwargs)

    @staticmethod
    def create_reply(message, reply_text):
        return Message.create(reply_text).to_chat(message=message).reply_to_message(message)


class MessageEntityParser:
    def __init__(self, message):
        self.text_as_utf16_bytes = message.text.encode("utf-16")

    def get_entity_text(self, entity):
        start_byte = 2 + entity.offset * 2  # BOM + characters * 2 bytes
        end_byte = start_byte + entity.length * 2
        return self.text_as_utf16_bytes[start_byte:end_byte].decode("utf-16")

    def get_text_after_entity(self, entity):
        start_byte = 2 + (entity.offset + entity.length) * 2
        return self.text_as_utf16_bytes[start_byte:].decode("utf-16")
