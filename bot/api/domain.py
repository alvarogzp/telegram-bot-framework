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


class Message(ApiObject):
    def replying_to(self, message):
        self.data["chat_id"] = message.chat.id
        self.data["reply_to_message_id"] = message.message_id
        return self

    @staticmethod
    def create(text, chat_id=None, **kwargs):
        return Message(_type=Message, text=text, chat_id=chat_id, **kwargs)

    @staticmethod
    def create_reply(message, reply_text):
        return Message.create(reply_text).replying_to(message)


class Chat(ApiObject):
    pass


class MessageEntityParser:
    def __init__(self, message):
        self.text_as_utf16_bytes = message.text.encode("utf-16")

    def get_entity_text(self, entity):
        start_byte = 2 + entity.offset * 2  # BOM + characters * 2 bytes
        end_byte = start_byte + entity.length * 2
        return self.text_as_utf16_bytes[start_byte:end_byte].decode("utf-16")
