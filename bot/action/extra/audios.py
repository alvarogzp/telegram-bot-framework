from bot.action import util
from bot.action.core.action import Action


class SaveVoiceAction(Action):
    def process(self, event):
        storage_handler = VoiceStorageHandler(event)
        voice = self.build_voice_from_event(event)
        storage_handler.save_voice(voice)

    @staticmethod
    def build_voice_from_event(event):
        message = event.message
        voice = event.voice
        date = message.date
        message_id = message.message_id
        user_id = util.get_user_id_from_message(message)
        duration = voice.duration
        file_size = voice.file_size
        return Voice(date, message_id, user_id, duration, file_size)


class Voice:
    def __init__(self, date, message_id, user_id, duration, file_size):
        self.date = date
        self.message_id = message_id
        self.user_id = user_id
        self.duration = duration
        self.file_size = file_size  # may be None

    def serialize(self):
        return "{} {} {} {} {}\n".format(self.date, self.message_id, self.user_id, self.duration, self.file_size)


class VoiceStorageHandler:
    def __init__(self, event):
        self.event = event

    def save_voice(self, voice):
        self.event.state.set_value("voices", voice.serialize(), append=True)
