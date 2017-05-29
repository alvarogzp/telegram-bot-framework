class StoredMessageMapper:
    def from_api(self, message):
        data = message.data.copy()
        self.__replace_with_id_if_present(data, "from")
        self.__replace_with_id_if_present(data, "forward_from")
        self.__replace_with_id_if_present(data, "reply_to_message", "message_id")
        self.__delete_if_present(data, "chat")
        self.__delete_if_present(data, "message_id")
        self.__delete_if_present(data, "entities")
        self.__replace_list_with_item_with_biggest(data, "photo", "height")
        self.__delete_if_present(data.get("sticker"), "thumb")
        self.__delete_if_present(data.get("document"), "thumb")
        self.__delete_if_present(data.get("video_note"), "thumb")
        self.__delete_if_present(data.get("video"), "thumb")
        return data

    def __replace_with_id_if_present(self, dict, key, id_key="id"):
        if self.__is_present(dict, key):
            dict[key] = dict[key][id_key]

    @staticmethod
    def __delete_if_present(dict, key):
        if dict is not None:
            dict.pop(key, None)

    def __replace_list_with_item_with_biggest(self, dict, key, attr):
        if self.__is_present(dict, key):
            biggest = None
            for item in dict[key]:
                if biggest is None or item[attr] >= biggest[attr]:
                    biggest = item
            if biggest is not None:
                dict[key] = biggest

    @staticmethod
    def __is_present(dict, key):
        return dict.get(key) is not None
