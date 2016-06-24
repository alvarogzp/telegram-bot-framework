

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
        if len(item) > 1 and item[0] == "_" and item[1] != "_":
            item = item[1:]
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


class Message:
    @staticmethod
    def create(chat, text):
        return ApiObject(_type=Message, chat=chat, text=text)

    @staticmethod
    def create_reply(message, reply_text):
        return Message.create(message.chat, reply_text)


class Chat(ApiObject):
    @staticmethod
    def create(id):
        return ApiObject(_type=Chat, id=id)
