from bot.action.core.action import Action
from bot.action.extra.pole import SavePoleAction, TimezoneStorageHandler
from bot.action.standard.toggle import FeatureStateHandler
from bot.api.domain import Message

SECONDS_IN_A_DAY = 86400
OFFSET_FROM_UTC_IN_SECONDS = 2 * 3600


class LegacyPoleAction(Action):
    def process(self, event):
        state = FeatureStateHandler(event, "pole").state
        if event.global_gap_detected:  # reset everything
            state.last_message_timestamp = None
            state.current_day_message_count = None
            state.current_day_first_messages = None

        current_message_timestamp = event.message.date
        previous_message_timestamp = state.last_message_timestamp
        state.last_message_timestamp = str(current_message_timestamp)
        if previous_message_timestamp is not None:
            if self.has_changed_day(event, int(previous_message_timestamp), current_message_timestamp):  # pole
                state.current_day_message_count = str(1)
                state.current_day_first_messages = self.get_formatted_message_to_store(event.message)
            else:
                current_day_message_count = state.current_day_message_count
                if current_day_message_count is not None:
                    current_day_message_count = int(current_day_message_count)
                    if current_day_message_count < 3:
                        current_day_message_count += 1
                        if current_day_message_count == 3:
                            chat = event.message.chat
                            pole_message, subpole_message = state.current_day_first_messages.splitlines()
                            subsubpole_message = event.message.message_id
                            self.send_message(chat, pole_message, "pole")
                            self.send_message(chat, subpole_message, "subpole")
                            self.send_message(chat, subsubpole_message, "subsubpole")
                            state.current_day_message_count = None
                        else:
                            state.current_day_message_count = str(current_day_message_count)
                            state.current_day_first_messages += "\n" + self.get_formatted_message_to_store(event.message)

    @staticmethod
    def has_changed_day(event, previous_timestamp, current_timestamp):
        state = TimezoneStorageHandler(event.state.get_for("pole")).get_timezone_state("main")
        return SavePoleAction.has_changed_day(state, previous_timestamp, current_timestamp)

    @staticmethod
    def get_formatted_message_to_store(message):
        return str(message.message_id)

    def send_message(self, chat, message_id, text):
        self.api.send_message(Message.create(text, chat.id), reply_to_message_id=message_id)
