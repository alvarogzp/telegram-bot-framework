import queue

from bot.multithreading.work import Work
from bot.multithreading.worker.abstract import AbstractWorker


class QueueWorker(AbstractWorker):
    """
    Instances of this worker are safe to be running on more than one thread at the same time.
    The only limitation is that in error handling you will not be able to distinguish between them.
    """

    def __init__(self, name: str, work_queue: queue.Queue, error_handler: callable):
        super().__init__(name, error_handler)
        self.queue = work_queue

    def run(self):
        while True:
            work = self.queue.get()
            self._work(work)
            self.queue.task_done()

    def post(self, work: Work):
        self.queue.put(work)

    def shutdown(self):
        self.queue.join()
