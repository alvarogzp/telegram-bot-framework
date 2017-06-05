import collections

from bot.action.extra.messages.stored_message import StoredMessage
from bot.action.util.format import UserFormatter
from bot.action.util.textformat import FormattedText


class MessageList:
    def __init__(self, ids, storage):
        self.ids = ids
        self.storage = storage
        self.cached_messages = None

    def is_empty(self):
        return len(self.ids) == 0

    def get(self, id_):
        str_id = str(id_)
        if str_id not in self.ids:
            return None
        return self.__get_message(str_id)

    def grouped_by_user(self, max_to_return):
        message_users = (message.user_id for message in self.__get_messages())
        return MessageGroup(collections.Counter(message_users).most_common(max_to_return))

    def most_recent(self, limit):
        if limit <= 0:
            ids = []
        else:
            ids = reversed(MessageIdOperations.sorted(self.ids, reverse=True, keep_only_first=limit))
        return MessageList(ids, self.storage)

    def slice_from(self, from_id, limit):
        if limit <= 0:
            ids = []
        else:
            ids = MessageIdOperations.sliced(self.ids, from_id=from_id, keep_only_first=limit)
        return MessageList(ids, self.storage)

    def printable_info(self, event, user_storage_handler):
        return FormattedText().normal("\n")\
            .join((message.printable_info(event, user_storage_handler) for message in self.__get_messages()))

    def __get_messages(self):
        if self.cached_messages is None:
            self.cached_messages = [self.__get_message(id_) for id_ in self.ids]
        return self.cached_messages

    def __get_message(self, id_):
        return StoredMessage.deserialize(id_, self.storage.get_value(id_))


class MessageGroup:
    def __init__(self, grouped_messages):
        self.grouped_messages = grouped_messages

    def printable_info(self, user_storage_handler):
        return FormattedText().normal("\n".join(
            ("%s → %s" % (count, UserFormatter.retrieve_and_format(user_id, user_storage_handler))
             for user_id, count in self.grouped_messages)))


class MessageIdOperations:
    @classmethod
    def sorted(cls, ids, reverse=False, keep_only_first=None):
        int_ids = cls.__to_int(ids)
        int_ids.sort(reverse=reverse)
        int_ids = cls.keep_only_first(int_ids, keep_only_first)
        return cls.__to_str(int_ids)

    @classmethod
    def sliced(cls, ids, from_id, keep_only_first=None):
        int_ids = cls.__to_int(ids)
        int_ids.sort()
        if len(int_ids) == 0 or from_id > int_ids[-1]:
            return []
        min_id = int_ids[0]
        from_id = from_id if from_id > min_id else min_id
        while from_id not in int_ids:
            from_id += 1
        index = int_ids.index(from_id)
        int_ids = int_ids[index:]
        int_ids = cls.keep_only_first(int_ids, keep_only_first)
        return cls.__to_str(int_ids)

    @classmethod
    def __to_int(cls, ids):
        return cls.__to(int, ids)

    @classmethod
    def __to_str(cls, ids):
        return cls.__to(str, ids)

    @staticmethod
    def __to(func, ids):
        return [func(id_) for id_ in ids]

    @staticmethod
    def keep_only_first(ids, number_of_elements_to_keep):
        if number_of_elements_to_keep is not None:
            ids = ids[:number_of_elements_to_keep]
        return ids
