import collections

from bot.action import util
from bot.action.core.action import Action
from bot.action.core.command import UnderscoredCommandBuilder, CommandUsageMessage
from bot.action.userinfo import UserStorageHandler
from bot.action.util.format import UserFormatter, DateFormatter, TimeFormatter, SizeFormatter
from bot.action.util.textformat import FormattedText
from bot.api.domain import Message


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


class ListVoiceAction(Action):
    def process(self, event):
        action, action_param, help_args = self.parse_args(event.command_args.split())
        if action in ("length", "longest", "number", "size", "biggest", "smallest", "recent", "show"):
            voices = VoiceStorageHandler(event).get_voices()
            if voices.is_empty():
                response = self.get_response_empty()
            else:
                func = getattr(self, "get_response_" + action)
                response = func(event, voices, action_param)
        else:
            response = self.get_response_help(event, help_args)
        if response.chat_id is None:
            response.to_chat(message=event.message)
        if response.reply_to_message_id is None:
            response = response.reply_to_message(message=event.message)
        self.api.send_message(response)

    @staticmethod
    def parse_args(args):
        action = "help"
        action_param = 10
        help_args = args[1:]
        if len(args) == 0:
            action = "length"
        elif len(args) == 1:
            if args[0].isnumeric():
                action = "show"
                action_param = int(args[0])
            elif args[0] != "show":
                action = args[0]
        elif len(args) == 2:
            if args[1].isnumeric():
                action_param = int(args[1])
                action = args[0]
        return action, action_param, help_args

    @staticmethod
    def get_response_help(event, help_args):
        args = [
            "[length [number_of_users]]",
            "longest [number_of_audios]",
            "number [number_of_users]",
            "size [number_of_users]",
            "biggest [number_of_audios]",
            "smallest [number_of_audios]",
            "recent [number_of_audios]",
            "[show] message_id"
        ]
        description = "By default, display a ranking with the sum of audios length per user.\n\n" \
                      "Use *longest* for a list of the longest audios sent.\n\n" \
                      "Use *number* for a ranking with the number of audios per user.\n\n" \
                      "Use *size* for a ranking with the sum of audios size per user.\n\n" \
                      "Use *biggest* for a list of the audios with most size.\n\n" \
                      "Use *smallest* for a list of the audios with less size.\n\n" \
                      "Use *recent* for a list of the most recent audios sent.\n\n" \
                      "In all of the previous modes you can add a number to the end of the command to limit " \
                      "the number of audios or users to display (default is 10).\n\n" \
                      "You can also call the command with an audio message\\_id to see some info about it " \
                      "with a reply to the requested audio, so you can listen it again."
        return CommandUsageMessage.get_usage_message(event.command, args, description)

    @staticmethod
    def get_response_empty():
        return Message.create("I have not seen any audios here.\n"
                              "Send some of them and try again.")

    def get_response_length(self, event, voices, number_of_users_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        printable_voices = voices.grouped_by_length(number_of_users_to_display).printable_version(user_storage_handler)
        return self.__build_success_response_message(event, "Sum of audios length per user:", printable_voices)

    def get_response_longest(self, event, voices, number_of_voices_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        filtered_voices = voices.longest().limit(number_of_voices_to_display)
        printable_voices = filtered_voices.printable_version(event, user_storage_handler)
        return self.__build_success_response_message(event, "Longest audios:", printable_voices)

    def get_response_number(self, event, voices, number_of_users_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        printable_voices = voices.grouped_by_user(number_of_users_to_display).printable_version(user_storage_handler)
        return self.__build_success_response_message(event, "Number of audios sent per user:", printable_voices)

    def get_response_size(self, event, voices, number_of_users_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        printable_voices = voices.grouped_by_size(number_of_users_to_display).printable_version(user_storage_handler)
        return self.__build_success_response_message(event, "Sum of audios size per user:", printable_voices)

    def get_response_biggest(self, event, voices, number_of_voices_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        filtered_voices = voices.biggest().limit(number_of_voices_to_display)
        printable_voices = filtered_voices.printable_version(event, user_storage_handler)
        return self.__build_success_response_message(event, "Biggest audios:", printable_voices)

    def get_response_smallest(self, event, voices, number_of_voices_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        filtered_voices = voices.smallest().limit(number_of_voices_to_display)
        printable_voices = filtered_voices.printable_version(event, user_storage_handler)
        return self.__build_success_response_message(event, "Smallest audios:", printable_voices)

    def get_response_recent(self, event, voices, number_of_voices_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        filtered_voices = voices.most_recent().limit(number_of_voices_to_display)
        printable_voices = filtered_voices.printable_version(event, user_storage_handler)
        return self.__build_success_response_message(event, "Most recent audios:", printable_voices)

    def get_response_show(self, event, voices, message_id):
        voice = voices.get(message_id)
        if voice is None:
            return Message.create("No such audio with that message_id.")
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        return voice.full_printable_version(user_storage_handler)

    @staticmethod
    def __build_success_response_message(event, title, printable_voices, footer_text=None):
        header = FormattedText().normal(title).newline()
        footer = FormattedText().newline().newline()
        if footer_text is not None:
            footer.concat(footer_text)
        else:
            footer.normal("Write ").bold(event.command + " help").normal(" to see more options.")
        return FormattedText().concat(header).normal(printable_voices).concat(footer).build_message()


class Voice:
    def __init__(self, date, message_id, user_id, duration, file_size):
        self.date = date
        self.message_id = message_id
        self.user_id = user_id
        self.duration = int(duration)
        self.file_size = int(file_size)  # may be None

    def printable_version(self, event, user_storage_handler):
        formatted_user = UserFormatter.retrieve_and_format(self.user_id, user_storage_handler)
        formatted_date = DateFormatter.format(self.date)
        view_voice_command = UnderscoredCommandBuilder.build_command(event.command, self.message_id)
        return "{} → {} → {}".format(formatted_user, formatted_date, view_voice_command)

    def full_printable_version(self, user_storage_handler):
        formatted_user = UserFormatter.retrieve_and_format(self.user_id, user_storage_handler)
        formatted_date = DateFormatter.format_full(self.date)
        formatted_duration = TimeFormatter.format(self.duration)
        formatted_size = SizeFormatter.format(self.file_size)
        text = "Author: {}\n".format(formatted_user)
        text += "Date: {}\n".format(formatted_date)
        text += "Duration: {}\n".format(formatted_duration)
        text += "Size: {}".format(formatted_size)
        return Message.create(text).reply_to_message(message_id=self.message_id)

    def serialize(self):
        return "{} {} {} {} {}\n".format(self.date, self.message_id, self.user_id, self.duration, self.file_size)

    @staticmethod
    def deserialize(voice_data):
        return Voice(*voice_data.split(" "))


class VoiceList:
    def __init__(self, voices):
        self.voices = voices

    def is_empty(self):
        return len(self.voices) == 0

    def get(self, message_id):
        message_id = str(message_id)
        for voice in self.voices:
            if voice.message_id == message_id:
                return voice

    def grouped_by_user(self, max_to_return):
        voice_users = (voice.user_id for voice in self.voices)
        return VoiceGroup(collections.Counter(voice_users).most_common(max_to_return))

    def grouped_by_length(self, max_to_return):
        counter = collections.Counter()
        for voice in self.voices:
            counter.update({voice.user_id: voice.duration})
        return VoiceGroup(counter.most_common(max_to_return))

    def grouped_by_size(self, max_to_return):
        counter = collections.Counter()
        for voice in self.voices:
            counter.update({voice.user_id: voice.file_size})
        return VoiceGroup(counter.most_common(max_to_return))

    def limit(self, limit):
        return VoiceList(self.voices[:limit])

    def most_recent(self):
        # for now, assume they are already sorted by date, in descending order
        return VoiceList(list(reversed(self.voices)))

    def longest(self):
        return VoiceList(list(reversed(self.__get_voices_sorted_by(lambda x: x.duration))))

    def biggest(self):
        return VoiceList(list(reversed(self.__get_voices_sorted_by_file_size())))

    def smallest(self):
        return VoiceList(self.__get_voices_sorted_by_file_size())

    def __get_voices_sorted_by_file_size(self):
        return self.__get_voices_sorted_by(lambda x: x.file_size)

    def __get_voices_sorted_by(self, key):
        return sorted(self.voices, key=key)

    def printable_version(self, event, user_storage_handler):
        return "\n".join((voice.printable_version(event, user_storage_handler) for voice in self.voices))

    @staticmethod
    def deserialize(voices_data):
        return VoiceList([Voice.deserialize(voice) for voice in voices_data.splitlines()])


class VoiceGroup:
    def __init__(self, grouped_voices):
        self.grouped_voices = grouped_voices

    def printable_version(self, user_storage_handler):
        return "\n".join(("{} → {}".format(count, UserFormatter.retrieve_and_format(user_id, user_storage_handler))
                          for user_id, count in self.grouped_voices))


class VoiceStorageHandler:
    def __init__(self, event):
        self.event = event

    def get_voices(self):
        voices = self.event.state.voices
        if voices is None:
            voices = ""
        return VoiceList.deserialize(voices)

    def save_voice(self, voice):
        self.event.state.set_value("voices", voice.serialize(), append=True)
