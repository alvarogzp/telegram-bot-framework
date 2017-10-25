import queue

from bot.multithreading.worker.queue import QueueWorker


class LimitedLifespanQueueWorker(QueueWorker):
    def __init__(self, name: str, work_queue: queue.Queue, error_handler: callable, max_seconds_idle: int,
                 end_notify: callable):
        """
        :param max_seconds_idle: Max seconds to wait for a new work to appear before ending the execution.
            If it is None, it behaves as a QueueWorker, waiting forever.
        """
        super().__init__(name, work_queue, error_handler)
        self.max_seconds_idle = max_seconds_idle
        self.end_notify = end_notify

    def run(self):
        while self._get_and_execute():
            pass

    def _get_and_execute(self):
        """
        :return: True if it should continue running, False if it should end its execution.
        """
        try:
            work = self.queue.get(timeout=self.max_seconds_idle)
        except queue.Empty:
            # max_seconds_idle has been exhausted, exiting
            self.end_notify()
            return False
        else:
            self._work(work)
            self.queue.task_done()
            return True
