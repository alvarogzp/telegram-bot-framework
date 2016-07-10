import collections

from bot.action.core.action import Action
from bot.action.core.command import CommandUsageMessage
from bot.action.userinfo import UserStorageHandler
from bot.action.util.format import DateFormatter, UserFormatter
from bot.api.domain import Message

SECONDS_IN_A_DAY = 86400
OFFSET_FROM_UTC_IN_SECONDS = 2 * 3600


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
            if self.has_changed_day(int(previous_message_timestamp), current_message_timestamp):  # pole
                self.build_pole_and_add_to(state, "poles", event.message)
                state.current_day_message_count = str(1)
            else:
                current_day_message_count = state.current_day_message_count
                if current_day_message_count is not None:
                    current_day_message_count = int(current_day_message_count)
                    if current_day_message_count < 3:
                        current_day_message_count += 1
                        if current_day_message_count == 2:
                            self.build_pole_and_add_to(state, "subpoles", event.message)
                            state.current_day_message_count = str(current_day_message_count)
                        elif current_day_message_count == 3:
                            self.build_pole_and_add_to(state, "subsubpoles", event.message)
                            state.current_day_message_count = None

    def has_changed_day(self, previous_timestamp, current_timestamp):
        current_day = self.get_day_number(current_timestamp)
        previous_day = self.get_day_number(previous_timestamp)
        return current_day != previous_day

    @staticmethod
    def get_day_number(timestamp):
        return (timestamp + OFFSET_FROM_UTC_IN_SECONDS) // SECONDS_IN_A_DAY

    def build_pole_and_add_to(self, state, key, message):
        pole = self.build_pole_from_message(message)
        self.add_pole_to(state, key, pole)

    @staticmethod
    def add_pole_to(state, key, pole):
        state.set_value(key, pole.serialize(), append=True)

    @staticmethod
    def build_pole_from_message(message):
        user_id = message.from_.id if message.from_ is not None else "-"
        return Pole(user_id, message.date, message.message_id)


class ListPoleAction(Action):
    def process(self, event):
        action, number_of_poles_to_display, help_args = self.parse_args(event.command_args.split())
        if action in ("recent", "ranking", "last"):
            poles = PoleStorageHandler(event.state.get_for("pole")).get_stored_poles("poles")
            if poles.is_empty():
                response = self.get_response_empty()
            elif action == "recent":
                response = self.get_response_recent(event, poles, number_of_poles_to_display)
            elif action == "ranking":
                response = self.get_response_ranking(event, poles, number_of_poles_to_display)
            else:
                response = self.get_response_last(event, poles, number_of_poles_to_display)
        else:
            response = self.get_response_help(event, help_args)
        if response.reply_to_message_id is None:
            response = response.replying_to(event.message)
        self.api.send_message(response)

    @staticmethod
    def parse_args(args):
        action = "help"
        number_of_poles_to_display = 10
        help_args = args[1:]
        if len(args) == 0:
            action = "recent"
        elif len(args) == 1:
            if args[0].isnumeric():
                action = "recent"
                number_of_poles_to_display = int(args[0])
            else:
                action = args[0]
                if action == "last":
                    number_of_poles_to_display = 1
        elif len(args) == 2:
            if args[1].isnumeric():
                number_of_poles_to_display = int(args[1])
                action = args[0]
        return action, number_of_poles_to_display, help_args

    @staticmethod
    def get_response_help(event, help_args):
        args = "[number_of_poles]|[ranking [number_of_users]]|[last [pole_number]]"
        description = "By default, display recent poles.\n" \
                      "Use *ranking* to show users with most poles.\n" \
                      "You can also add a number to the end in both modes to limit the poles or users to display" \
                      " (default is 10).\n" \
                      "Use *last* to show last pole, or previous ones adding a number.\n"
        return CommandUsageMessage.get_usage_message(event.command, args, description)

    @staticmethod
    def get_response_empty():
        return Message.create("I have not seen any poles here.\n"
                              "Wait until next day start, make a pole and try again.")

    def get_response_recent(self, event, poles, number_of_poles_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        sorted_poles = poles.most_recent(number_of_poles_to_display)
        printable_poles = sorted_poles.printable_version(user_storage_handler)
        return self.__build_success_response_message(event, "Most recent poles:", printable_poles)

    def get_response_ranking(self, event, poles, number_of_poles_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        printable_poles = poles.grouped_by_user(number_of_poles_to_display).printable_version(user_storage_handler)
        return self.__build_success_response_message(event, "Ranking of poles:", printable_poles)

    @staticmethod
    def get_response_last(event, poles, number_of_pole_to_display):
        pole = poles.get(-number_of_pole_to_display)
        if pole is None:
            return Message.create("Invalid number. Range [1,total_poles]")
        text = "\U0001f446 Here is the " + str(number_of_pole_to_display) + " last pole"
        return Message.create(text, chat_id=event.message.chat.id, reply_to_message_id=pole.message_id)

    @staticmethod
    def __build_success_response_message(event, title, printable_poles):
        footer = "\n\nUse *" + event.command + " help* to see more options."
        return Message.create(title + "\n" + printable_poles + footer, parse_mode="Markdown")


class Pole:
    def __init__(self, user_id, date, message_id):
        self.user_id = user_id
        self.date = date
        self.message_id = message_id

    def printable_version(self, user_storage_handler):
        formatted_user = UserFormatter.retrieve_and_format(self.user_id, user_storage_handler)
        formatted_date = DateFormatter.format(self.date)
        return "%s -> %s" % (formatted_date, formatted_user)

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

    def printable_version(self, user_storage_handler):
        return "\n".join((pole.printable_version(user_storage_handler) for pole in self.poles))

    @staticmethod
    def deserialize(poles_data):
        return PoleList([Pole.deserialize(pole) for pole in poles_data.splitlines()])


class PoleGroup:
    def __init__(self, grouped_poles):
        self.grouped_poles = grouped_poles

    def printable_version(self, user_storage_handler):
        return "\n".join(("%s -> %s" % (count, UserFormatter.retrieve_and_format(user_id, user_storage_handler))
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
