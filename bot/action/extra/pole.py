import collections
import datetime

import pytz

from bot.action.core.action import Action
from bot.action.core.command import UnderscoredCommandBuilder
from bot.action.core.command.usagemessage import CommandUsageMessage
from bot.action.standard.userinfo import UserStorageHandler
from bot.action.util.format import DateFormatter, UserFormatter
from bot.action.util.textformat import FormattedText
from bot.api.domain import Message

I18N_DOMAIN = "pole"

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
            previous_message_timestamp = int(previous_message_timestamp)
            timezone_states = self.get_timezone_states(state)
            for timezone_state in timezone_states:
                self.handle_pole_for_timezone(event, timezone_state, previous_message_timestamp, current_message_timestamp)

    @staticmethod
    def get_timezone_states(state):
        handler = TimezoneStorageHandler(state)
        timezones = handler.get_timezones()
        return (handler.get_timezone_state(timezone) for timezone in timezones)

    def handle_pole_for_timezone(self, event, state, previous_timestamp, current_timestamp):
        if self.has_changed_day(state, previous_timestamp, current_timestamp):  # pole
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

    @classmethod
    def has_changed_day(cls, state, previous_timestamp, current_timestamp):
        current_day = cls.get_day_number(state, current_timestamp)
        previous_day = cls.get_day_number(state, previous_timestamp)
        return current_day != previous_day

    @staticmethod
    def get_day_number(state, timestamp):
        offset_seconds = state.get_value("offset_seconds", 0)  # TODO check number on set
        if offset_seconds:
            timestamp -= int(offset_seconds)
        timezone_name = state.get_value("timezone", DEFAULT_TIMEZONE)
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


class ManagePoleTimezonesAction(Action):
    def process(self, event):
        action, action_params = self.parse_args(event.command_args.split())
        function_name = "get_response_" + action
        func = getattr(self, function_name, None)
        if callable(func):
            handler = TimezoneStorageHandler(event.state.get_for("pole"))
            response = func(event, action_params, handler)
        else:
            response = self._get_response_help(event, action_params)
        if response.chat_id is None:
            response.to_chat(message=event.message)
        if response.reply_to_message_id is None:
            response = response.reply_to_message(message=event.message)
        self.api.send_message(response)

    @staticmethod
    def parse_args(args):
        action = "help"
        action_params = args[1:]
        if len(args) == 0 or (len(args) == 1 and args[0] == "list"):
            action = "list"
        elif len(args) == 2 and (args[0] == "info" or args[0] == "del"):
            action = args[0]
        elif 2 <= len(args) <= 4 and args[0] in ("add", "mod"):
            action = args[0]
        return action, action_params

    @staticmethod
    def _get_response_help(event, help_args):
        args = [
            "[list]",
            "info timezone_alias",
            "add timezone_alias timezone_name [offset_in_seconds]",
            "mod timezone_alias [timezone_name] [offset_in_seconds]",
            "del timezone_alias"
        ]
        description = (
            "By default, list current pole timezones.\n"
            "\n"
            "Use *info* with a timezone alias to view the info of that alias.\n"
            "\n"
            "Use *add* to add a new timezone.\n"
            "Give it:\n"
            "· an `alias` to refer to it,\n"
            "· the `timezone_name` for this pole using the non daylight-saving abbreviation"
            " (you can use this URL to find yours:"
            " [https://en.wikipedia.org/wiki/List_of_time_zone_abbreviations]),\n"
            "· an optional `offset_in_seconds` to add (if positive) or subtract (if negative) to the moment"
            " when the day changes in that timezone.\n"
            "\n"
            "Use *mod* to modify an already added timezone.\n"
            "You can change both the `timezone_name` and the `offset_in_seconds`.\n"
            "\n"
            "Use *del* to remove a previously added timezone by indicating its alias.\n"
            "Poles in that timezone remain in case you later re-enable it (you must use the same alias).\n\n"
            "Only group admins can use this command."
        )
        return CommandUsageMessage.get_usage_message(event.command, args, description)

    @staticmethod
    def get_response_list(event, action_params, handler):
        text = FormattedText().normal("List of pole timezones:").newline()
        for alias in handler.get_timezones():
            state = handler.get_timezone_state(alias)
            name = state.get_value("timezone", DEFAULT_TIMEZONE)
            text.bold(alias).normal(" → ").bold(name)
            offset_seconds = state.offset_seconds
            if offset_seconds is not None:
                text.normal(" (with ").bold(offset_seconds).normal(" seconds offset)")
            text.newline()
        return text.build_message()

    def get_response_info(self, event, action_params, handler):
        alias = action_params[0]
        return FormattedText().normal("Information for ").bold(alias).normal(" timezone:").newline()\
            .concat(self.get_timezone_info_text(handler.get_timezone_state(alias)))\
            .build_message()

    @staticmethod
    def get_timezone_info_text(state):
        name = state.get_value("timezone", DEFAULT_TIMEZONE)
        offset_seconds = state.offset_seconds
        text = FormattedText().normal("Timezone abbreviation: ").bold(name).newline()
        if offset_seconds is None:
            text.bold("No").normal(" offset set.")
        else:
            text.bold(offset_seconds).normal(" seconds of offset.")
        return text

    def get_response_add(self, event, action_params, handler):
        timezone_alias = action_params[0]
        if timezone_alias in handler.get_timezones():
            return FormattedText().bold("ERROR").normal(", a timezone called ").bold(timezone_alias)\
                .normal(" already exists. Modify it instead of trying to add it again.")\
                .build_message()
        success = self.set_timezone_data(action_params, handler)
        if not success:
            return FormattedText().bold("ERROR while adding timezone").normal(", check name and offset are valid.")\
                .normal(" See help for more info")\
                .build_message()
        handler.add_timezone(timezone_alias)
        return FormattedText().bold("New timezone added!").newline().newline()\
            .normal("Alias: ").bold(timezone_alias).newline()\
            .concat(self.get_timezone_info_text(handler.get_timezone_state(timezone_alias)))\
            .build_message()

    def get_response_mod(self, event, action_params, handler):
        alias = action_params[0]
        success = self.set_timezone_data(action_params, handler)
        if not success:
            return FormattedText().bold("ERROR while modifying timezone").normal(", check name and offset are valid.")\
                .normal(" See help for more info")\
                .build_message()
        return FormattedText().normal("Timezone ").bold(alias).normal(" updated!").newline().newline()\
            .concat(self.get_timezone_info_text(handler.get_timezone_state(alias)))\
            .build_message()

    @staticmethod
    def get_response_del(event, action_params, handler):
        alias = action_params[0]
        if alias not in handler.get_timezones():
            return FormattedText().bold("ERROR").normal(", no ").bold(alias).normal(" timezone found.")\
                .build_message()
        if alias == "main":
            return FormattedText().normal("Sorry, main timezone cannot be removed")\
                .build_message()
        handler.del_timezone(alias)
        return FormattedText().normal("Timezone ").bold(alias).normal(" removed.").newline().newline()\
            .normal("Ranking in that timezone is still accessible, but no new poles will be added.").newline()\
            .normal("If you add a timezone with the same alias in the future,"
                    " new poles will be added to the ranking again.").newline()\
            .normal("Contact the bot admin if you want the ranking to be wiped.")\
            .build_message()

    @classmethod
    def set_timezone_data(cls, action_params, handler):
        timezone_alias = action_params[0]
        timezone_name = action_params[1] if len(action_params) > 1 else None
        offset_seconds = action_params[2] if len(action_params) > 2 else None
        if cls.is_valid_timezone_name(timezone_name) and cls.is_valid_offset_seconds(offset_seconds):
            state = handler.get_timezone_state(timezone_alias)
            state.timezone = timezone_name
            state.offset_seconds = offset_seconds
            return True
        return False

    @staticmethod
    def is_valid_timezone_name(name):
        if name is None:
            return True
        try:
            pytz.timezone(name)
        except:
            return False
        else:
            return True

    @staticmethod
    def is_valid_offset_seconds(offset_seconds):
        if offset_seconds is None:
            return True
        try:
            int(offset_seconds)
        except:
            return False
        else:
            return True


class ListPoleAction(Action):
    def __init__(self, kind="poles"):
        super().__init__()
        self.kind = kind
        self.pole_format_dict = {"poles": self.kind, "pole": self.kind[:-1]}

    def process(self, event):
        event.i18n.enable(I18N_DOMAIN)
        action, action_param, help_args, timezone = self.parse_args(event.command_args.split())
        original_command = event.command
        if timezone != "main":
            event.command = UnderscoredCommandBuilder.build_command(original_command, "tz", timezone)
        if action in ("recent", "ranking", "last"):
            state = TimezoneStorageHandler(event.state.get_for("pole")).get_timezone_state(timezone)
            poles = PoleStorageHandler(state).get_stored_poles(self.kind)
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
        event.command = original_command

    @staticmethod
    def parse_args(args):
        timezone = "main"
        if len(args) > 1 and args[0] == "tz":
            timezone = args[1]
            args = args[2:]
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
        return action, action_param, help_args, timezone

    def get_response_help(self, event, help_args):
        args = self.__formatted("[ranking number_of_users]", "recent [number_of_{poles}]", "[last] {pole}_number")
        description = self.__formatted(_(
            "By default, display users with most {poles} (the ranking).\n\n"
            "Use *recent* to show recent {poles}.\n\n"
            "You can also add a number to the end in both modes to limit the users or {poles} to display"
            " (default is 10).\n\n"
            "Use *last* to show last {pole}, or previous ones adding a number (starting with 1).\n\n"
            "Use: `/poles tz timezone_name` to view rankings of poles in another timezone"
            " (they can be managed with `/polestzman`)"
        ))
        return CommandUsageMessage.get_usage_message(event.command, args, description)

    def get_response_empty(self):
        return Message.create(self.__formatted(_("I have not seen any {poles} here.\n"
                                                 "Wait until next day start, make a {pole} and try again.")))

    def get_response_recent(self, event, poles, number_of_poles_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        sorted_poles = poles.most_recent(number_of_poles_to_display)
        printable_poles = sorted_poles.printable_version(event, user_storage_handler)
        return self.__build_success_response_message(event, self.__formatted(_("Most recent {poles}:")), printable_poles)

    def get_response_ranking(self, event, poles, number_of_users_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        printable_poles = poles.grouped_by_user(number_of_users_to_display).printable_version(user_storage_handler)
        recent_poles_command = UnderscoredCommandBuilder.build_command(event.command, "recent")
        recent_poles_text = FormattedText().normal(_("Write {0} to see recent {poles}."))\
            .start_format().normal(recent_poles_command).normal(**self.pole_format_dict).end_format()
        return self.__build_success_response_message(event, self.__formatted(_("Ranking of {poles}:")), printable_poles, recent_poles_text)

    def get_response_last(self, event, poles, number_of_pole_to_display):
        pole = poles.get(-number_of_pole_to_display)
        if pole is None:
            return Message.create(self.__formatted(_("Invalid {pole} number. Range [1,total_{poles}]")))
        text = _("This is the {0} last {pole}").format(number_of_pole_to_display, **self.pole_format_dict)
        return Message.create(text, chat_id=event.message.chat.id, reply_to_message_id=pole.message_id)\
            .with_error_callback(lambda e: self.__deleted_pole_handler(0, pole, event, number_of_pole_to_display))

    def __deleted_pole_handler(self, tries, pole, event, pole_number):
        text = FormattedText().normal(_("Oops, the {0} last {pole} seems to be deleted.")).newline().newline()\
            .start_format().normal(pole_number, **self.pole_format_dict).end_format()
        reply_to_message_id = int(pole.message_id) + tries + 1
        if tries == 0:
            text.normal(_("It was above this message."))
        elif tries < 5:
            text.concat(FormattedText()
                        .normal(_("It was above this message, along with other {0} message(s) deleted or "
                                  "inaccessible to me (maybe from another bot)."))
                        .start_format().normal(tries).end_format()
                        )
        else:
            text.concat(FormattedText()
                        .normal(_("And at least the next {0} messages are also deleted or inaccessible to me (maybe "
                                  "because they are from another bot), so I cannot find where the {pole} was."))
                        .start_format().normal(tries, **self.pole_format_dict).end_format()
                        )
            reply_to_message_id = None
        message = text.build_message().to_chat(event.message.chat)
        if reply_to_message_id:
            message.reply_to_message(message_id=reply_to_message_id)
            message.with_error_callback(lambda e: self.__deleted_pole_handler(tries + 1, pole, event, pole_number))
        return self.api.send_message(message)

    @staticmethod
    def __build_success_response_message(event, title, printable_poles, footer_text=None):
        # header
        text = FormattedText().normal(title).newline()
        # body
        if isinstance(printable_poles, FormattedText):
            text.concat(printable_poles)
        else:
            text.normal(printable_poles)
        # footer
        text.newline().newline()
        if footer_text is not None:
            text.concat(footer_text)
        else:
            text.normal(_("Write {0} to see more options."))\
                .start_format().bold(event.command + " help").end_format()
        return text.build_message()

    def __formatted(self, *text):
        if len(text) == 1:
            return text[0].format(**self.pole_format_dict)
        return [t.format(**self.pole_format_dict) for t in text]


class Pole:
    def __init__(self, user_id, date, message_id):
        self.user_id = user_id
        self.date = date
        self.message_id = message_id

    def printable_version(self, event, user_storage_handler, index):
        formatted_user = UserFormatter.retrieve_and_format(self.user_id, user_storage_handler)
        formatted_date = DateFormatter.format(self.date)
        view_pole_command = UnderscoredCommandBuilder.build_command(event.command, str(index+1))
        return _("{date} → {user} → {view_pole_command}")\
            .format(date=formatted_date, user=formatted_user, view_pole_command=view_pole_command)

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
        return PoleGroupPrintableVersionHelper(self.grouped_poles, user_storage_handler).printable_version()


class PoleGroupPrintableVersionHelper:
    def __init__(self, grouped_poles, user_storage_handler):
        self.grouped_poles = grouped_poles
        self.user_storage_handler = user_storage_handler
        self.printable_poles = []

    def printable_version(self):
        self.printable_poles = []
        if len(self.grouped_poles) > 0:
            self.__add_grouped_pole(_("FIRST: {user} → {pole_count}"), self.grouped_poles[0])
        if len(self.grouped_poles) > 1:
            self.__add_grouped_pole(_("SECOND: {user} → {pole_count}"), self.grouped_poles[1])
        if len(self.grouped_poles) > 2:
            self.__add_grouped_pole(_("THIRD: {user} → {pole_count}"), self.grouped_poles[2])
        if len(self.grouped_poles) > 3:
            for grouped_pole in self.grouped_poles[3:]:
                self.__add_grouped_pole(_("{user} → {pole_count}"), grouped_pole)
        return FormattedText().newline().join(self.printable_poles)

    def __add_grouped_pole(self, text, grouped_pole):
        user_id, count = grouped_pole
        formatted_user = UserFormatter.retrieve_and_format(user_id, self.user_storage_handler)
        formatted_grouped_pole = FormattedText().normal(text).start_format()\
            .bold(user=formatted_user).normal(pole_count=count).end_format()
        self.printable_poles.append(formatted_grouped_pole)


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


class TimezoneStorageHandler:
    def __init__(self, state):
        self.state = state

    def get_timezones(self):
        timezones_raw_data = self.state.timezones
        if timezones_raw_data is None:
            timezones_raw_data = ""
        timezones = timezones_raw_data.splitlines()
        if "main" not in timezones:
            timezones.insert(0, "main")
        return timezones

    def get_timezone_state(self, timezone_name):
        if timezone_name == "main" and self.state.exists_value("poles"):
            # backward compatibility with existing poles
            return self.state
        else:
            return self.state.get_for(timezone_name)

    def add_timezone(self, name):
        self.state.set_value("timezones", name + "\n", append=True)

    def del_timezone(self, name):
        timezones = self.state.timezones.splitlines()
        timezones.remove(name)
        if len(timezones) == 0:
            self.state.timezones = None
        else:
            self.state.timezones = "\n".join(timezones) + "\n"
