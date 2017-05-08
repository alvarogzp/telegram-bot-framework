import collections
import json

from bot.action.chatsettings import ChatSettings
from bot.action.core.action import Action
from bot.action.core.command import UnderscoredCommandBuilder
from bot.action.core.command.usagemessage import CommandUsageMessage
from bot.action.extra.messages import analyzer
from bot.action.userinfo import UserStorageHandler
from bot.action.util.format import UserFormatter, DateFormatter
from bot.action.util.textformat import FormattedText
from bot.api.domain import Message, ApiObject

MIN_MESSAGES_TO_KEEP = 5000
MAX_MESSAGES_TO_KEEP = 15000


class SaveMessageAction(Action):
    def process(self, event):
        if event.settings.get(ChatSettings.STORE_MESSAGES) == "on":
            storage_handler = MessageStorageHandler(event)
            storage_handler.save_message(event.message)
            storage_handler.delete_old_messages()


class ListMessageAction(Action):
    def process(self, event):
        action, action_param, help_args = self.parse_args(event.command_args.split())
        if action in ("recent", "show", "ranking"):
            messages = MessageStorageHandler(event).get_stored_messages()
            if messages.is_empty():
                response = self.get_response_empty()
            elif action == "recent":
                response = self.get_response_recent(event, messages, action_param)
            elif action == "show":
                response = self.get_response_show(event, messages, action_param)
            else:
                response = self.get_response_ranking(event, messages, action_param)
        elif action == "opt-out":
            response = self.get_response_opt_out(event, action_param)
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
            action = "recent"
        elif len(args) == 1:
            if args[0].isnumeric():
                action = "show"
                action_param = int(args[0])
            elif args[0] != "show":
                action = args[0]
        elif len(args) == 2:
            if args[1].isnumeric() or args[0] == "opt-out":
                action_param = int(args[1]) if args[0] != "opt-out" else args[1]
                action = args[0]
        return action, action_param, help_args

    @staticmethod
    def get_response_help(event, help_args):
        args = ["[recent number_of_messages]", "[show] message_id", "ranking [number_of_users]", "opt-out [action]"]
        description = "By default, display a list with information about last messages.\n" \
                      "You can use *recent* with a number to modify the number of messages to list" \
                      " (default is 10).\n\n" \
                      "Use *show* along with a message\\_id to view that particular message.\n\n" \
                      "Use *ranking* to display a ranking of the users who wrote most recent messages" \
                      " (approximately last 1000 messages are counted).\n" \
                      "You can add a number to modify the number of top users to display (default is 10).\n\n" \
                      "Use *opt-out* followed by *add-me* or *remove-me* to be added or removed from the opt-out list" \
                      " of this feature. Use *get-status* or nothing to query your status on the list.\n" \
                      "While you are in the opt-out list, nobody but you can show the content of your messages using" \
                      " this feature, in any group."
        return CommandUsageMessage.get_usage_message(event.command, args, description)

    @staticmethod
    def get_response_empty():
        return Message.create("I have not seen any messages here.\n"
                              "Write some messages and try again.")

    def get_response_recent(self, event, messages, number_of_messages_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        sorted_messages = messages.most_recent(number_of_messages_to_display)
        printable_messages = sorted_messages.printable_info(event, user_storage_handler)
        return self.__build_success_response_message(event, "Most recent messages:", printable_messages)

    def get_response_show(self, event, messages, message_id):
        message = messages.get(message_id)
        if message is None:
            return Message.create("Invalid message_id.\nUse " + event.command + " to get valid message_ids.")
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        if OptOutManager(self.state).has_user_opted_out(message.user_id) and message.user_id != event.message.from_.id:
            user = UserFormatter.retrieve_and_format(message.user_id, user_storage_handler)
            return FormattedText().normal("🙁 Sorry, ").bold(user).normal(" has opted-out from this feature.").build_message()
        return message.printable_full_message(user_storage_handler)

    def get_response_ranking(self, event, messages, number_of_users_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        printable_messages = messages.grouped_by_user(number_of_users_to_display).printable_info(user_storage_handler)
        return self.__build_success_response_message(event, "Ranking of users:", printable_messages)

    @staticmethod
    def __build_success_response_message(event, title, printable_messages):
        footer = FormattedText().normal("\n\nWrite ").bold(event.command + " help").normal(" to see more options.")
        return FormattedText().normal(title + "\n").concat(printable_messages).concat(footer).build_message()

    def get_response_opt_out(self, event, action):
        manager = OptOutManager(self.state)
        user_id = event.message.from_.id
        had_user_opted_out = manager.has_user_opted_out(user_id)
        if action == "add-me":
            if had_user_opted_out:
                response = FormattedText().normal("❌ You had already opted-out.")
            else:
                manager.add_user(user_id)
                response = FormattedText().normal("✅ You have been added to the opt-out list of this feature.")
        elif action == "remove-me":
            if not had_user_opted_out:
                response = FormattedText().normal("❌ You are not currently on the list.")
            else:
                manager.remove_user(user_id)
                response = FormattedText().normal("✅ You have been removed from the opt-out list of this feature.")
        else:
            if had_user_opted_out:
                response = FormattedText().normal("🙃 You are in the opt-out list.")
            else:
                response = FormattedText().normal("🙂 You are NOT in the opt-out list.")
        return response.build_message()


class StoredMessage:
    def __init__(self, message_id, message, *edited_messages):
        self.message_id = message_id
        self.message = message
        self.edited_messages = edited_messages

    @property
    def user_id(self):
        return self.message.from_

    def printable_info(self, event, user_storage_handler):
        show_command = UnderscoredCommandBuilder.build_command(event.command, self.message_id)
        return analyzer.get_short_info(user_storage_handler, self, show_command)

    def printable_full_message(self, user_storage_handler):
        return analyzer.get_full_content(user_storage_handler, self)

    @staticmethod
    def deserialize(message_id, data):
        messages = []
        for line in data.splitlines():
            message_data = json.loads(line)
            message = ApiObject.wrap_api_object(message_data)
            messages.append(message)
        return StoredMessage(message_id, *messages)


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
            ids = MessageIdSorter.sorted(self.ids, reverse=True, keep_only_first=limit)
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


class MessageIdSorter:
    @staticmethod
    def sorted(ids, reverse=False, keep_only_first=None):
        int_ids = [int(id_) for id_ in ids]
        int_ids.sort(reverse=reverse)
        if keep_only_first is not None:
            int_ids = int_ids[:keep_only_first]
        return [str(id_) for id_ in int_ids]


class OptOutManager:
    def __init__(self, global_state):
        self.state = global_state

    def has_user_opted_out(self, user_id):
        return str(user_id) in self.state.opted_out_from_messages_feature.splitlines()

    def add_user(self, user_id):
        self.state.set_value("opted_out_from_messages_feature", str(user_id) + "\n", append=True)

    def remove_user(self, user_id):
        users = self.state.opted_out_from_messages_feature.splitlines()
        users.remove(str(user_id))
        self.state.opted_out_from_messages_feature = "\n".join(users)


class MessageStorageHandler:
    def __init__(self, event):
        self.state = event.state.get_for("messages")

    def get_stored_messages(self):
        return MessageList(self.state.list_keys(), self.state)

    def save_message(self, message):
        data = message.data.copy()
        self.__replace_with_id_if_present(data, "from")
        self.__replace_with_id_if_present(data, "forward_from")
        self.__replace_with_id_if_present(data, "reply_to_message", "message_id")
        self.__delete_if_present(data, "chat")
        self.__delete_if_present(data, "message_id")
        self.__delete_if_present(data, "entities")
        dump = json.dumps(data)
        self.state.set_value(str(message.message_id), dump + "\n", append=True)

    @staticmethod
    def __replace_with_id_if_present(dict, key, id_key="id"):
        if dict.get(key) is not None:
            dict[key] = dict[key][id_key]

    @staticmethod
    def __delete_if_present(dict, key):
        dict.pop(key, None)

    def delete_old_messages(self):
        stored_ids = self.state.list_keys()
        if len(stored_ids) > MAX_MESSAGES_TO_KEEP:
            number_of_messages_to_delete = len(stored_ids) - MIN_MESSAGES_TO_KEEP
            ids_to_delete = MessageIdSorter.sorted(stored_ids, keep_only_first=number_of_messages_to_delete)
            self.__delete_messages(ids_to_delete)

    def __delete_messages(self, message_ids_to_delete):
        for message_id in message_ids_to_delete:
            self.state.set_value(message_id, None)
