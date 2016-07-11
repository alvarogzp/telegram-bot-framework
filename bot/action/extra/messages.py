import collections
import json

from bot.action.core.action import Action
from bot.action.core.command import CommandUsageMessage
from bot.action.userinfo import UserStorageHandler
from bot.action.util.format import UserFormatter, DateFormatter
from bot.api.domain import Message, ApiObject


class SaveMessageAction(Action):
    def process(self, event):
        MessageStorageHandler(event).save_message(event.message)


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
        else:
            response = self.get_response_help(event, help_args)
        if response.reply_to_message_id is None:
            response = response.replying_to(event.message)
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
                action = "recent"
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
        args = ["[number_of_messages]", "show message_id", "ranking [number_of_users]"]
        description = "By default, display a list with information about last messages.\n" \
                      "You can add a number to modify the number of messages to list (default is 10).\n\n" \
                      "Use *show* along with a message\\_id to view that particular message.\n\n" \
                      "Use *ranking* to display a ranking of the users who wrote most recent messages" \
                      " (approximately last 1000 messages are counted).\n" \
                      "You can add a number to modify the number of top users to display (default is 10)."
        return CommandUsageMessage.get_usage_message(event.command, args, description)

    @staticmethod
    def get_response_empty():
        return Message.create("I have not seen any messages here.\n"
                              "Write some messages and try again.")

    def get_response_recent(self, event, messages, number_of_messages_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        sorted_messages = messages.most_recent(number_of_messages_to_display)
        printable_messages = sorted_messages.printable_info(user_storage_handler)
        return self.__build_success_response_message(event, "Most recent messages:", printable_messages)

    def get_response_show(self, event, messages, message_id):
        message = messages.get(message_id)
        if message is None:
            return Message.create("Invalid message_id.\nUse " + event.command + " to get valid message_ids.")
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        return message.printable_full_message(user_storage_handler)

    def get_response_ranking(self, event, messages, number_of_users_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        printable_messages = messages.grouped_by_user(number_of_users_to_display).printable_info(user_storage_handler)
        return self.__build_success_response_message(event, "Ranking of users:", printable_messages)

    @staticmethod
    def __build_success_response_message(event, title, printable_messages):
        footer = "\n\nUse *" + event.command + " help* to see more options."
        return Message.create(title + "\n" + printable_messages + footer, parse_mode="Markdown")


class StoredMessage:
    def __init__(self, message_id, message, *edited_messages):
        self.message_id = message_id
        self.message = message
        self.edited_messages = edited_messages

    @property
    def user_id(self):
        return self.message.from_

    def printable_info(self, user_storage_handler):
        formatted_user = UserFormatter.retrieve_and_format(self.message.from_, user_storage_handler)
        formatted_date = DateFormatter.format(self.message.date)
        edits_info = (" (%s edits)" % len(self.edited_messages)) if len(self.edited_messages) > 0 else ""
        return "\\[*%s*] at *%s* by %s%s" % (self.message_id, formatted_date, formatted_user, edits_info)

    def printable_full_message(self, user_storage_handler):
        formatted_date = DateFormatter.format_full(self.message.date)
        formatted_user = UserFormatter.retrieve_and_format(self.message.from_, user_storage_handler)
        text = "Message %s sent on %s by %s.\n" % (self.message_id, formatted_date, formatted_user)
        if len(self.edited_messages) > 0:
            text += "This message has been edited %s times.\n" % len(self.edited_messages)
        text += "\n"
        if self.message.text is None:
            text += "This is a non-text message. They are not supported yet :("
        else:
            text += "Text:\n"
            text += self.message.text
        for index, edited_message in enumerate(self.edited_messages):
            formatted_date = DateFormatter.format_full(edited_message.edit_date)
            text += "\n\n"
            text += "· Edit %s, done at %s." % (index+1, formatted_date)
            text += "\n  New text:\n"
            text += edited_message.text
        return Message.create(text)

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
            int_ids = [int(id_) for id_ in self.ids]
            int_ids.sort(reverse=True)
            int_ids = int_ids[:limit]
            ids = [str(id_) for id_ in int_ids]
        return MessageList(ids, self.storage)

    def printable_info(self, user_storage_handler):
        return "\n".join((message.printable_info(user_storage_handler) for message in self.__get_messages()))

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
        return "\n".join(("%s -> %s" % (count, UserFormatter.retrieve_and_format(user_id, user_storage_handler))
                          for user_id, count in self.grouped_messages))


class MessageStorageHandler:
    def __init__(self, event):
        self.state = event.state.get_for("messages")

    def get_stored_messages(self):
        return MessageList(self.state.list_keys(), self.state)

    def save_message(self, message):
        data = message.data.copy()
        self.__replace_with_id_if_present(data, "from")
        self.__replace_with_id_if_present(data, "forward_from")
        self.__delete_if_present(data, "chat")
        self.__delete_if_present(data, "message_id")
        self.__delete_if_present(data, "entities")
        dump = json.dumps(data)
        self.state.set_value(str(message.message_id), dump + "\n", append=True)

    @staticmethod
    def __replace_with_id_if_present(dict, key):
        if dict.get(key) is not None:
            dict[key] = dict[key]["id"]

    @staticmethod
    def __delete_if_present(dict, key):
        dict.pop(key, None)