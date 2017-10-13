import queue

from bot.multithreading.work import Work


class Worker:
    def __init__(self, name: str, work_queue: queue.Queue, error_handler: callable):
        self.name = name
        self.queue = work_queue
        self.error_handler = error_handler

    def run(self):
        while True:
            work = self.queue.get()
            self._work(work)
            self.queue.task_done()

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
        self.queue.join()
