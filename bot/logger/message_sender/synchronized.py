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
        # Using a reentrant lock to play safe in case the send function somewhat invokes this send function again
        # maybe because a send triggers another send on the same message sender.
        # Note that if this send throws an exception the lock is released when dealing with it from outside,
        # so this is not a problem.
        # But if the exception is handled inside this send call, the lock is still hold.
        self.lock = threading.RLock()

    def send(self, text):
        with self.lock:
            self.sender.send(text)
