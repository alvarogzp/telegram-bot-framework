import collections

import datetime
import pytz

from bot.action.core.action import Action
from bot.action.core.command import CommandUsageMessage, UnderscoredCommandBuilder
from bot.action.userinfo import UserStorageHandler
from bot.action.util.format import DateFormatter, UserFormatter
from bot.action.util.textformat import FormattedText
from bot.api.domain import Message

DEFAULT_TIMEZONE = "CET"


class SavePoleAction(Action):
    def process(self, event):
        state = event.state.get_for("pole")
        if event.global_gap_detected:  # reset everything
            # FIXME https://github.com/alvarogzp/telegram-bot/issues/23
            state.last_message_timestamp = None
            state.current_day_message_count = None

        current_message_timestamp = event.message.date
        previous_message_timestamp = state.last_message_timestamp
        state.last_message_timestamp = str(current_message_timestamp)
        if previous_message_timestamp is not None:
            if self.has_changed_day(event.state, state, int(previous_message_timestamp), current_message_timestamp):  # pole
                self.build_pole_and_save_to(state, "poles", event.message)
                state.current_day_message_count = str(1)
            else:
                current_day_message_count = state.current_day_message_count
                if current_day_message_count is not None:
                    current_day_message_count = int(current_day_message_count)
                    if current_day_message_count < 3:
                        current_day_message_count += 1
                        if current_day_message_count == 2:
                            self.build_pole_and_save_to(state, "subpoles", event.message)
                            state.current_day_message_count = str(current_day_message_count)
                        elif current_day_message_count == 3:
                            self.build_pole_and_save_to(state, "subsubpoles", event.message)
                            state.current_day_message_count = None

    def has_changed_day(self, chat_state, feature_state, previous_timestamp, current_timestamp):
        current_day = self.get_day_number(chat_state, feature_state, current_timestamp)
        previous_day = self.get_day_number(chat_state, feature_state, previous_timestamp)
        return current_day != previous_day

    @staticmethod
    def get_day_number(chat_state, feature_state, timestamp):
        offset_seconds = feature_state.get_value("offset_seconds", 0)  # TODO check number on set
        if offset_seconds:
            timestamp += int(offset_seconds)
        timezone_name = chat_state.get_value("timezone", DEFAULT_TIMEZONE)
        timezone = pytz.timezone(timezone_name)  # TODO catch exceptions on set
        return datetime.datetime.fromtimestamp(timestamp, tz=timezone).date().toordinal()

    def build_pole_and_save_to(self, state, storage, message):
        pole = self.build_pole_from_message(message)
        self.save_pole_to(state, storage, pole)

    @staticmethod
    def build_pole_from_message(message):
        user_id = message.from_.id if message.from_ is not None else "-"
        return Pole(user_id, message.date, message.message_id)

    @staticmethod
    def save_pole_to(state, storage, pole):
        PoleStorageHandler(state).save_pole_to(storage, pole)


class ListPoleAction(Action):
    def process(self, event):
        action, action_param, help_args = self.parse_args(event.command_args.split())
        if action in ("recent", "ranking", "last"):
            poles = PoleStorageHandler(event.state.get_for("pole")).get_stored_poles("poles")
            if poles.is_empty():
                response = self.get_response_empty()
            elif action == "recent":
                response = self.get_response_recent(event, poles, action_param)
            elif action == "ranking":
                response = self.get_response_ranking(event, poles, action_param)
            else:
                response = self.get_response_last(event, poles, action_param)
        else:
            response = self.get_response_help(event, help_args)
        if response.reply_to_message_id is None:
            response = response.to_chat_replying(event.message)
        self.api.send_message(response)

    @staticmethod
    def parse_args(args):
        action = "help"
        action_param = 10
        help_args = args[1:]
        if len(args) == 0:
            action = "ranking"
        elif len(args) == 1:
            if args[0].isnumeric():
                action = "last"
                action_param = int(args[0])
            else:
                action = args[0]
                if action == "last":
                    action_param = 1
        elif len(args) == 2:
            if args[1].isnumeric():
                action_param = int(args[1])
                action = args[0]
        return action, action_param, help_args

    @staticmethod
    def get_response_help(event, help_args):
        args = ["[ranking number_of_users]", "recent [number_of_poles]", "[last] pole_number"]
        description = "By default, display users with most poles (the ranking).\n\n" \
                      "Use *recent* to show recent poles.\n\n" \
                      "You can also add a number to the end in both modes to limit the users or poles to display" \
                      " (default is 10).\n\n" \
                      "Use *last* to show last pole, or previous ones adding a number (starting with 1)."
        return CommandUsageMessage.get_usage_message(event.command, args, description)

    @staticmethod
    def get_response_empty():
        return Message.create("I have not seen any poles here.\n"
                              "Wait until next day start, make a pole and try again.")

    def get_response_recent(self, event, poles, number_of_poles_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        sorted_poles = poles.most_recent(number_of_poles_to_display)
        printable_poles = sorted_poles.printable_version(event, user_storage_handler)
        return self.__build_success_response_message(event, "Most recent poles:", printable_poles)

    def get_response_ranking(self, event, poles, number_of_users_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        printable_poles = poles.grouped_by_user(number_of_users_to_display).printable_version(user_storage_handler)
        recent_poles_command = UnderscoredCommandBuilder.build_command(event.command, "recent")
        recent_poles_text = FormattedText().normal("Write ").normal(recent_poles_command).normal(" to see recent poles.")
        return self.__build_success_response_message(event, "Ranking of poles:", printable_poles, recent_poles_text)

    @staticmethod
    def get_response_last(event, poles, number_of_pole_to_display):
        pole = poles.get(-number_of_pole_to_display)
        if pole is None:
            return Message.create("Invalid number. Range [1,total_poles]")
        text = "\U0001f446 Here is the " + str(number_of_pole_to_display) + " last pole"
        return Message.create(text, chat_id=event.message.chat.id, reply_to_message_id=pole.message_id)

    @staticmethod
    def __build_success_response_message(event, title, printable_poles, footer_text=None):
        header = FormattedText().normal(title).newline()
        footer = FormattedText().newline().newline()
        if footer_text is not None:
            footer.concat(footer_text)
        else:
            footer.normal("Write ").bold(event.command + " help").normal(" to see more options.")
        return FormattedText().concat(header).normal(printable_poles).concat(footer).build_message()


class Pole:
    def __init__(self, user_id, date, message_id):
        self.user_id = user_id
        self.date = date
        self.message_id = message_id

    def printable_version(self, event, user_storage_handler, index):
        formatted_user = UserFormatter.retrieve_and_format(self.user_id, user_storage_handler)
        formatted_date = DateFormatter.format(self.date)
        view_pole_command = UnderscoredCommandBuilder.build_command(event.command, str(index+1))
        return "%s → %s → %s" % (formatted_date, formatted_user, view_pole_command)

    def serialize(self):
        return "%s %s %s\n" % (self.user_id, self.date, self.message_id)

    @staticmethod
    def deserialize(pole_data):
        return Pole(*pole_data.split(" "))


class PoleList:
    def __init__(self, poles):
        self.poles = poles

    def is_empty(self):
        return len(self.poles) == 0

    def get(self, index):
        try:
            return self.poles[index]
        except IndexError:
            return None

    def grouped_by_user(self, max_to_return):
        pole_users = (pole.user_id for pole in self.poles)
        return PoleGroup(collections.Counter(pole_users).most_common(max_to_return))

    def most_recent(self, limit):
        if limit <= 0:
            return PoleList([])
        # for now, assume they are already sorted by date
        return PoleList(reversed(self.poles[-limit:]))

    def printable_version(self, event, user_storage_handler):
        return "\n".join((pole.printable_version(event, user_storage_handler, index)
                          for index, pole in enumerate(self.poles)))

    @staticmethod
    def deserialize(poles_data):
        return PoleList([Pole.deserialize(pole) for pole in poles_data.splitlines()])


class PoleGroup:
    def __init__(self, grouped_poles):
        self.grouped_poles = grouped_poles

    def printable_version(self, user_storage_handler):
        return "\n".join(("%s → %s" % (count, UserFormatter.retrieve_and_format(user_id, user_storage_handler))
                          for user_id, count in self.grouped_poles))


class PoleStorageHandler:
    def __init__(self, state):
        self.state = state

    def get_stored_poles(self, storage_name):
        poles = self.state.get_value(storage_name)
        if poles is None:
            poles = ""
        return PoleList.deserialize(poles)

    def save_pole_to(self, storage_name, pole: Pole):
        self.state.set_value(storage_name, pole.serialize(), append=True)
