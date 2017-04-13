from bot.api.domain import Message


class CommandUsageMessage:
    @classmethod
    def get_usage_message(cls, command, args=None, description=""):
        message = "*Usage*\n"
        if type(args) is list:
            message += "\n".join((cls.__get_command_with_args(command, arg) for arg in args))
        else:
            message += cls.__get_command_with_args(command, args)
        if description:
            message += "\n\n" + description
        return Message.create(message, parse_mode="Markdown", disable_web_page_preview=True)

    @staticmethod
    def __get_command_with_args(command, args):
        text = "`" + command
        if args:
            text += " " + args
        text += "`"
        return text
