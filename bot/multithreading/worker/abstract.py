from bot.multithreading.work import Work
from bot.multithreading.worker import Worker


class AbstractWorker(Worker):
    def __init__(self, name: str, error_handler: callable):
        super().__init__(name)
        self.error_handler = error_handler

    def _work(self, work: Work):
        try:
            self._do_work(work)
        except BaseException as e:
            self._error(e, work)

    def _do_work(self, work: Work):
        work.do_work()

    def _error(self, e: BaseException, work: Work):
        try:
            self.error_handler(e, work, self)
        except:
            pass

    def run(self):
        raise NotImplementedError()

    def post(self, work: Work):
        raise NotImplementedError()

    def shutdown(self):
        raise NotImplementedError()
