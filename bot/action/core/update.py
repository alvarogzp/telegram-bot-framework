from bot.utils.attributeobject import DictionaryObject


class Event(DictionaryObject):
    pass


class Update(Event):
    def __init__(self, update, is_pending=False):
        super().__init__()
        self.update = update
        self.is_pending = is_pending
