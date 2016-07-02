import collections

from bot.action.core.action import Action
from bot.api.domain import Message


class HashtagRecolectorAction(Action):
    def process(self, event):
        hashtag_entities = self.get_hashtag_entities(event.message.entities)
        if len(hashtag_entities) > 0:
            new_hashtags = self.get_message_hashtags(event.message, hashtag_entities)
            if not new_hashtags.is_empty():
                HashtagStorageHandler(event).save_new_hashtags(new_hashtags)

    @staticmethod
    def get_hashtag_entities(entities):
        return [entity for entity in entities if entity.type == "hashtag"] if entities is not None else []

    def get_message_hashtags(self, message, hashtag_entities):
        hashtags = HashtagList([])
        for entity in hashtag_entities:
            hashtag = self.get_hashtag_from_entity(message, entity)
            hashtags.add(hashtag)
        return hashtags

    @staticmethod
    def get_hashtag_from_entity(message, entity):
        start = entity.offset
        end = start + entity.length
        hashtag = message.text[start:end]
        user_id = message.from_.id if message.from_ is not None else "-"
        return Hashtag(hashtag, message.date, user_id)


class HashtagListAction(Action):
    def process(self, event):
        hashtags = HashtagStorageHandler(event).get_stored_hashtags()
        response = self.get_response_message(hashtags)
        self.api.send_message(Message.create_reply(event.message, response))

    @staticmethod
    def get_response_message(hashtags):
        if hashtags.is_empty():
            return "I have not seen any hashtag in this chat.\nWrite some and try again (hint: #ThisIsAHashTag)."
        formatted_hashtags = ("%s -> %s" % (count, hashtag) for hashtag, count in hashtags.counted_by_popularity())
        return "\n".join(formatted_hashtags)


class Hashtag:
    def __init__(self, hashtag, date=None, user_id=None):
        self.hashtag = hashtag
        self.date = date
        self.user_id = user_id

    def serialize(self):
        return "%s %s %s\n" % (self.hashtag, self.date, self.user_id)

    @staticmethod
    def deserialize(hashtag_data):
        return Hashtag(*hashtag_data.split(" "))


class HashtagList:
    def __init__(self, hashtags):
        self.hashtags = hashtags

    def add(self, hashtag: Hashtag):
        self.hashtags.append(hashtag)

    def is_empty(self):
        return len(self.hashtags) == 0

    def counted_by_popularity(self):
        hashtags_names = (hashtag.hashtag for hashtag in self.hashtags)
        return collections.Counter(hashtags_names).most_common()

    def serialize(self):
        return "".join((hashtag.serialize() for hashtag in self.hashtags))

    @staticmethod
    def deserialize(hashtags_data):
        return HashtagList([Hashtag.deserialize(hashtag) for hashtag in hashtags_data.splitlines()])


class HashtagStorageHandler:
    def __init__(self, event):
        self.event = event

    def get_stored_hashtags(self):
        hashtags = self.event.state.hashtags
        if hashtags is None:
            hashtags = ""
        return HashtagList.deserialize(hashtags)

    def save_new_hashtags(self, hashtags: HashtagList):
        self.event.state._set_value("hashtags", hashtags.serialize(), append=True)
