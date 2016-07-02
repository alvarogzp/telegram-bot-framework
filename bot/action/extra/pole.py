from bot.action.core.action import Action
from bot.api.domain import Message, Chat

SECONDS_IN_A_DAY = 86400
OFFSET_FROM_UTC_IN_SECONDS = 2 * 3600


class PoleAction(Action):
    def process(self, event):
        if event.global_gap_detected:  # reset everything
            event.state.last_message_timestamp = None
            event.state.current_day_message_count = None
            event.state.current_day_first_messages = None

        current_message_timestamp = event.message.date
        previous_message_timestamp = event.state.last_message_timestamp
        event.state.last_message_timestamp = str(current_message_timestamp)
        if previous_message_timestamp is not None:
            current_message_day = self.get_day_number(current_message_timestamp)
            previous_message_day = self.get_day_number(int(previous_message_timestamp))

            if current_message_day != previous_message_day:  # day change: pole
                event.state.current_day_message_count = str(1)
                event.state.current_day_first_messages = self.get_formatted_message_to_store(event.message)
            else:
                current_day_message_count = event.state.current_day_message_count
                if current_day_message_count is not None:
                    current_day_message_count = int(current_day_message_count)
                    if current_day_message_count < 3:
                        current_day_message_count += 1
                        event.state.current_day_first_messages += "\n" + self.get_formatted_message_to_store(event.message)
                        event.state.current_day_message_count = str(current_day_message_count)
                        if current_day_message_count == 3:
                            chat = event.message.chat
                            pole_message, subpole_message, subsubpole_message = event.state.current_day_first_messages.splitlines()
                            self.send_message(chat, pole_message, "pole")
                            self.send_message(chat, subpole_message, "subpole")
                            self.send_message(chat, subsubpole_message, "subsubpole")
                            event.state.current_day_message_count = None

    def send_message(self, chat, message_id, text):
        self.api.send_message(Message.create(chat, text, reply_to_message_id=message_id))

    @staticmethod
    def get_day_number(timestamp):
        return (timestamp + OFFSET_FROM_UTC_IN_SECONDS) // SECONDS_IN_A_DAY

    @staticmethod
    def get_formatted_message_to_store(message):
        return str(message.message_id)
