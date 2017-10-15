import threading

from bot.logger.message_sender import MessageSender, IntermediateMessageSender


class SynchronizedMessageSender(IntermediateMessageSender):
    """
    Thread-safe message sender.

    Wrap your `MessageSender` with this class and its :func:`send` function will be called in a synchronized way,
    only by one thread at the same time.
    """

    def __init__(self, sender: MessageSender):
        super().__init__(sender)
        self.lock = threading.Lock()

    def send(self, text):
        with self.lock:
            self.sender.send(text)
