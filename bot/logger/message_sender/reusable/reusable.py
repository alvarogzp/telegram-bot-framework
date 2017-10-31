from bot.api.domain import Message
from bot.logger.message_sender import IntermediateMessageSender
from bot.logger.message_sender.message_builder import MessageBuilder
from bot.logger.message_sender.reusable.limiter import ReusableMessageLimiter
from bot.logger.message_sender.reusable.same import SameMessageSender


class ReusableMessageSender(IntermediateMessageSender):
    def __init__(self, sender: SameMessageSender, builder: MessageBuilder, limiter: ReusableMessageLimiter):
        super().__init__(sender)
        self.builder = builder
        self.limiter = limiter

    def send(self, text):
        message = self._get_message_for(text)
        self.limiter.notify_about_to_send_message()
        self._send(message)

    def _get_message_for(self, text):
        self.__pre_add_limiter_hook(text)
        self.builder.add(text)
        self.__post_add_limiter_hook(text)
        return self.builder.get_message()

    def __pre_add_limiter_hook(self, text):
        if self.limiter.should_issue_new_message_pre_add(text):
            self.new()

    def __post_add_limiter_hook(self, text):
        if self.limiter.should_issue_new_message_post_add(self.builder):
            self.new()
            # add text again to the new message
            # no hooks are run this time as we could enter in infinite loop
            self.builder.add(text)

    def _send(self, message: Message):
        try:
            self.sender.send(message)
        finally:
            if self.sender.will_send_new_message():
                # There has been a problem and the sender cannot reuse the message, either because it was the
                # initial one and the message_id could not be retrieved (by some error or interruption), or
                # because the message failed to edit (it could have reached its max length).
                # The best thing we can do here is to start a new message, discarding the current text.
                # Doing so, we ensure the next send:
                #  - Will not fail if the problem was with the message content
                #  - Won't have repeated content if the message was really sent but the request was interrupted
                #    by some event (like a KeyboardInterrupt)
                self.new()

    def new(self):
        self.sender.new()
        self.builder.clear()
        self.limiter.notify_new_message_issued()
