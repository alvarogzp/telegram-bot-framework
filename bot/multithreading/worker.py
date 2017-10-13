import queue
import threading


class Worker:
    def __init__(self, name: str, work_queue: queue.Queue, error_handler: callable):
        self.name = name
        self.queue = work_queue
        # using an event instead of a boolean flag to avoid race conditions between threads
        self.end = threading.Event()
        self.error_handler = error_handler

    def run(self):
        while self._should_run():
            work = self.queue.get()
            self._work(work)

    def _should_run(self):
        return not self.end.is_set()

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

    def post(self, work: Work):
        self.queue.put(work)

    def shutdown(self):
        self.end.set()


class Work:
    def __init__(self, func: callable, name: str):
        self.func = func
        self.name = name

    def do_work(self):
        self.func()
