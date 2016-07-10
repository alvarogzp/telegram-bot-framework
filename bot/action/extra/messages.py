import json

from bot.action.core.action import Action


class SaveMessageAction(Action):
    def process(self, event):
        message = event.message
        state = event.state.get_for("messages")
        dump = json.dumps(message.data)
        state.set_value(str(message.message_id), dump + "\n", append=True)
