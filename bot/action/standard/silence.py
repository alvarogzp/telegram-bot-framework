from bot.action.core.action import Action
from bot.action.core.command import UnderscoredCommandBuilder
from bot.action.core.command.usagemessage import CommandUsageMessage
from bot.action.util.textformat import FormattedText


class SilenceAction(Action):
    def process(self, event):
        action = self._get_action(event.command_args.split())
        function_name = "do_" + action
        func = getattr(self, function_name, None)
        if not callable(func):
            func = self.do_help
        response = func(event)
        if response.chat_id is None:
            response.to_chat(message=event.message)
        if response.reply_to_message_id is None:
            response = response.reply_to_message(message=event.message)
        self.api.send_message(response)

    @staticmethod
    def _get_action(args):
        action = "help"
        if len(args) == 0:
            action = "enable"
        elif len(args) == 1:
            arg = args[0]
            if arg == "off":
                action = "disable"
            elif arg == "on":
                action = "enable"
        return action

    @staticmethod
    def do_help(event):
        return CommandUsageMessage.get_usage_message(event.command, ["[on]", "off"], "Silences bot in the current chat.")

    def do_enable(self, event):
        disable_command = UnderscoredCommandBuilder.build_command(event.command, "off")
        message = FormattedText().normal("Activating #silence mode. I won't send anything here until you ")\
            .normal(disable_command).normal(" me.")\
            .build_message()
        # sending reply before activating silence mode, so that it is actually sent
        message.to_chat_replying(event.message)
        self.api.send_message(message)
        event.state.silenced = "yes"
        # returning a message to avoid caller failing, but message should not be sent, as silence mode is now enabled
        return message

    @staticmethod
    def do_disable(event):
        event.state.silenced = None
        return FormattedText().normal("#silence mode disabled").build_message()
