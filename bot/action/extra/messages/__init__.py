from bot.action.core.action import Action
from bot.action.core.command.usagemessage import CommandUsageMessage
from bot.action.extra.messages import analyzer
from bot.action.extra.messages.mapper import StoredMessageMapper
from bot.action.extra.messages.operations import MessageGroup, MessageList, MessageIdOperations
from bot.action.extra.messages.opt_out import OptOutManager
from bot.action.extra.messages.storage import MessageStorageHandler
from bot.action.extra.messages.stored_message import StoredMessage
from bot.action.standard.chatsettings import ChatSettings
from bot.action.standard.userinfo import UserStorageHandler
from bot.action.util.format import UserFormatter
from bot.action.util.textformat import FormattedText
from bot.api.domain import Message


def is_store_messages_enabled(event):
    return event.settings.get(ChatSettings.STORE_MESSAGES) == "on"


class SaveMessageAction(Action):
    def process(self, event):
        if is_store_messages_enabled(event):
            storage_handler = MessageStorageHandler(event)
            storage_handler.save_message(event.message)
            storage_handler.delete_old_messages()


class ListMessageAction(Action):
    def process(self, event):
        action, action_param, help_args = self.parse_args(event.command_args.split(), event.message.reply_to_message)
        if action in ("recent", "from", "show", "ranking"):
            if not is_store_messages_enabled(event):
                response = self.get_response_disabled()
            else:
                messages = MessageStorageHandler(event).get_stored_messages()
                if messages.is_empty():
                    response = self.get_response_empty()
                elif action == "recent":
                    response = self.get_response_recent(event, messages, action_param)
                elif action == "from":
                    response = self.get_response_from(event, messages, *action_param)
                elif action == "show":
                    response = self.get_response_show(event, messages, action_param)
                else:
                    response = self.get_response_ranking(event, messages, action_param)
        elif action == "whereis":
            response = self.get_response_whereis(event, action_param)
        elif action == "opt-out":
            response = self.get_response_opt_out(event, action_param)
        else:
            response = self.get_response_help(event, help_args)
        if type(response) is not list:
            response = [response]
        last_message = event.message
        for message in response:
            message.to_chat(message=last_message)
            if message.reply_to_message_id is None:
                message.reply_to_message(last_message)
            last_message = self.api.send_message(message)

    @staticmethod
    def parse_args(args, reply_to_message):
        action = "help"
        action_param = 10
        help_args = args[1:]
        if len(args) == 0:
            action = "recent"
        elif len(args) == 1:
            if args[0].isnumeric():
                action = "show"
                action_param = int(args[0])
            elif args[0] not in ("show", "whereis", "from"):
                action = args[0]
            elif args[0] == "from" and reply_to_message is not None:
                action = args[0]
                action_param = (reply_to_message.message_id, action_param)
        elif len(args) == 2:
            if args[0] == "opt-out":
                action = args[0]
                action_param = args[1]
            elif args[1].isnumeric():
                action = args[0]
                action_param = int(args[1])
            if args[0] == "from":
                if reply_to_message is None:
                    action_param = (action_param, 10)
                else:
                    action_param = (reply_to_message.message_id, action_param)
        elif len(args) == 3:
            if args[0] == "from" and reply_to_message is None and args[1].isnumeric() and args[2].isnumeric():
                action = args[0]
                action_param = (int(args[1]), int(args[2]))
        return action, action_param, help_args

    @staticmethod
    def get_response_help(event, help_args):
        args = ["[recent number_of_messages]",
                "from [message_id] [number_of_messages]",
                "[show] message_id",
                "ranking [number_of_users]",
                "whereis message_id",
                "opt-out [action]"]
        description = "_Have you ever wondered that, like in WhatsApp, Telegram messages could not be deleted or" \
                      " edited once sent?_\n" \
                      "Then this is for you! It allows you to recover deleted messages content, or original text"\
                      " of edited messages.\n\n" \
                      "There is a way to opt-out to avoid your messages being recovered (see at the end of this"\
                      " message). Keep in mind that group admins can still configure the group to override opt-out"\
                      " on that specific group (by setting `override_messages_opt_out` to `off` in `/settings`).\n\n" \
                      "Group admins can also disable completely this feature on the group. That will disable" \
                      " message storing and retrieving via this command. To do it, set `store_messages`" \
                      " to `off` using the `/settings` command.\n\n" \
                      "By default, this command displays a list with information about last messages.\n" \
                      "You can use *recent* with a number to modify the number of messages to list" \
                      " (default is 10).\n\n" \
                      "Use *from* to get a list of messages sent after a specific one.\n" \
                      "The message you want to use as a reference can be specified by its `message_id`, or by sending" \
                      " this command as a reply to the message you want to use as reference.\n" \
                      "You can also add the `number_of_messages` you want to be listed. If using this command by "\
                      "replying a message, this is the only parameter accepted.\n\n" \
                      "Use *show* along with a `message_id` to view that particular message.\n\n" \
                      "Use *ranking* to display a ranking of the users who wrote most recent messages" \
                      " (approximately last 1000 messages are counted).\n" \
                      "You can add a number to modify the number of top users to display (default is 10).\n\n" \
                      "Use *whereis* followed by a `message_id` to locate a particular message.\n\n" \
                      "Use *opt-out* followed by *add-me* or *remove-me* to be added or removed from the opt-out list" \
                      " of this feature. Use *get-status* or nothing to query your status on the list.\n" \
                      "While you are in the opt-out list, nobody but you can show the content of your messages using" \
                      " this feature, in any group."
        return CommandUsageMessage.get_usage_message(event.command, args, description)

    @staticmethod
    def get_response_disabled():
        return FormattedText().bold("Sorry, this feature is disabled on this chat. 😕").newline().newline()\
            .normal("Group admins can enable it using the following command:").newline()\
            .code_inline("/settings set store_messages on")\
            .build_message()

    @staticmethod
    def get_response_empty():
        return Message.create("I have not seen any messages here.\n"
                              "Write some messages and try again.")

    def get_response_recent(self, event, messages, number_of_messages_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        sorted_messages = messages.most_recent(number_of_messages_to_display)
        printable_messages = sorted_messages.printable_info(event, user_storage_handler)
        return self.__build_success_response_message(event, "Most recent messages:", printable_messages)

    def get_response_from(self, event, messages, from_message_id, number_of_messages_to_display):
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        sorted_messages = messages.slice_from(from_message_id, number_of_messages_to_display)
        printable_messages = sorted_messages.printable_info(event, user_storage_handler)
        title = FormattedText().normal("Messages from {0}:").start_format().bold(from_message_id).end_format()
        return self.__build_success_response_message(event, title, printable_messages)

    def get_response_show(self, event, messages, message_id):
        message = messages.get(message_id)
        if message is None:
            return Message.create("Invalid message_id.\nUse " + event.command + " to get valid message_ids.")
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        if not OptOutManager(self.state).should_display_message(event, message.user_id):
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
        if not isinstance(title, FormattedText):
            title = FormattedText().normal(title)
        return FormattedText().concat(title).newline().concat(printable_messages).concat(footer).build_message()

    def get_response_whereis(self, event, message_id):
        return FormattedText().bold("👆 Here is message ").code_inline(message_id).bold(".")\
            .build_message().reply_to_message(message_id=message_id)\
            .with_error_callback(lambda e: self.api.send_message(
                FormattedText().bold("❌ Sorry, message ").code_inline(message_id).bold(" cannot be located.")
                .newline().newline().normal("Possible causes:").newline()
                .normal("· The message may have been deleted.").newline()
                .normal("· The message ID you entered may not be valid. They should be positive numbers.").newline()
                .normal("· If you recently converted the group to a supergroup, messages sent before the conversion"
                        " took place cannot be replied to.")
                .build_message().to_chat_replying(event.message)))

    def get_response_opt_out(self, event, action):
        manager = OptOutManager(self.state)
        user_id = event.message.from_.id
        had_user_opted_out = manager.has_user_opted_out(user_id)
        if action == "add-me":
            if had_user_opted_out:
                response = FormattedText().bold("❌ You had already opted-out.")
            else:
                manager.add_user(user_id)
                response = FormattedText().bold("✅ You have been added to the opt-out list of this feature.")
        elif action == "remove-me":
            if not had_user_opted_out:
                response = FormattedText().bold("❌ You are not currently on the list.")
            else:
                manager.remove_user(user_id)
                response = FormattedText().bold("✅ You have been removed from the opt-out list of this feature.")
        else:
            if had_user_opted_out:
                response = FormattedText().bold("🙃 You are in the opt-out list.")
            else:
                response = FormattedText().bold("🙂 You are NOT in the opt-out list.")
        if manager.is_override_enabled_on_chat(event):
            response.newline().newline()\
                .bold("⚠️ Opt-out override is currently enabled on this chat ⚠️").newline()\
                .normal("Opt-out list is not in effect here while override is enabled.")
        return response.build_message()
