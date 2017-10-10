from bot.action.core.action import Action
from bot.action.core.command.usagemessage import CommandUsageMessage
from bot.action.extra.messages.opt_out import OptOutManager
from bot.action.extra.messages.storage import MessageStorageHandler
from bot.action.extra.messages.stored_message import StoredMessage
from bot.action.standard.userinfo import UserStorageHandler
from bot.action.util.textformat import FormattedTextFactory


class ShowMessageAction(Action):
    def process(self, event):
        replied_message = event.message.reply_to_message
        if replied_message is None:
            response = self.get_response_help(event)
        else:
            response = self.get_response_show(event, replied_message)
        self.send_response(event, response)

    @staticmethod
    def get_response_help(event):
        description = FormattedTextFactory.get_new_markdown()\
            .normal("Reply to a message with the command to display all the information available for that message.")\
            .newline().newline()\
            .bold("NOTE")\
            .normal(": I cannot read messages from other bots, only messages from users or from me will work.")
        return CommandUsageMessage.get_usage_message(event.command, description=description)

    def get_response_show(self, event, replied_message):
        message = self.__get_message(event, replied_message)
        user_storage_handler = UserStorageHandler.get_instance(self.state)
        return message.printable_full_message(user_storage_handler)

    def __get_message(self, event, replied_message):
        message = self.__get_message_from_storage(event, replied_message.message_id)
        if message is None:
            message = StoredMessage.from_message(replied_message)
        return message

    def __get_message_from_storage(self, event, message_id):
        message = MessageStorageHandler(event).get_stored_messages().get(message_id)
        if message is not None:
            if not OptOutManager(self.state).should_display_message(event, message.user_id):
                # user disallows viewing their stored messages, treating as if it were not stored
                message = None
        return message

    def send_response(self, event, response):
        if type(response) is not list:
            response = [response]
        last_message = event.message
        for message in response:
            message.to_chat(message=last_message)
            if message.reply_to_message_id is None:
                message.reply_to_message(last_message)
            last_message = self.api.send_message(message)
