from bot.multithreading.work import Work
from bot.multithreading.worker.abstract import AbstractWorker


class ImmediateWorker(AbstractWorker):
    def __init__(self, error_handler: callable):
        super().__init__("immediate", error_handler)

    def run(self):
        pass

    def post(self, work: Work):
        self._work(work)

    def shutdown(self):
        pass
