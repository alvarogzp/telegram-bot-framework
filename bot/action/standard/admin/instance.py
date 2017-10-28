from bot.action.core.action import Action
from bot.action.util.textformat import FormattedText


class InstanceAction(Action):
    def process(self, event):
        response = FormattedText().normal("Bot instance: {instance_name}")\
            .start_format().bold(instance_name=self.config.instance_name).end_format()
        self.api.send_message(response.build_message().to_chat_replying(event.message))
