from bot.action import chatsettings
from bot.action.chatsettings import ChatSettings
from bot.action.core.command.throttler import Throttler


class ShortlyRepeatedCommandThrottler(Throttler):
    def __init__(self):
        self.recent_commands = {}

    def should_execute(self, event):
        current_date = event.message.date
        self.__cleanup_recent_commands(current_date)
        command_key = CommandKey(event)
        if command_key not in self.recent_commands:
            throttling_state = CommandThrottlingState(event)
            if not throttling_state.has_expired(current_date):
                # it has not expired immediately, throttling is enabled
                self.recent_commands[command_key] = throttling_state
        else:
            throttling_state = self.recent_commands[command_key]
            throttling_state.add_invocation()
        return throttling_state.should_execute()

    def __cleanup_recent_commands(self, current_date):
        for key, state in self.recent_commands.copy().items():
            if state.has_expired(current_date):
                del self.recent_commands[key]


class CommandKey:
    def __init__(self, event):
        self.chat_id = event.chat.id
        self.command = event.command
        self.command_args = event.command_args
        self.__key = (self.chat_id, self.command, self.command_args)

    def __hash__(self):
        return hash(self.__key)

    def __eq__(self, other):
        return self.__key == other.__key


class CommandThrottlingState:
    def __init__(self, event):
        self.chat_settings = chatsettings.repository.get_for_event(event)
        self.first_invocation = event.message.date
        self.number_of_invocations = 1

    def add_invocation(self):
        self.number_of_invocations += 1

    def should_execute(self):
        return self.number_of_invocations <= 1

    def has_expired(self, current_date):
        throttling_seconds = self.chat_settings.get(ChatSettings.THROTTLING_SECONDS)
        expiration_date = current_date - throttling_seconds
        return self.first_invocation <= expiration_date
