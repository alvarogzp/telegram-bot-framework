import queue

from bot.multithreading.work import Work


class Worker:
    def run(self):
        raise NotImplementedError()

    def post(self, work: Work):
        raise NotImplementedError()

    def shutdown(self):
        raise NotImplementedError()


class AbstractWorker(Worker):
    def __init__(self, name: str, error_handler: callable):
        self.name = name
        self.error_handler = error_handler

    def _work(self, work: Work):
        try:
            work.do_work()
        except BaseException as e:
            self._error(e, work)

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


class QueueWorker(AbstractWorker):
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


class ImmediateWorker(AbstractWorker):
    def __init__(self, error_handler: callable):
        super().__init__("immediate", error_handler)

    def run(self):
        pass

    def post(self, work: Work):
        self._work(work)

    def shutdown(self):
        pass
