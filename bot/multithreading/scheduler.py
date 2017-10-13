import queue
import threading

from bot.multithreading.worker import Worker, Work


class SchedulerApi:
    def __init__(self, worker_error_handler: callable):
        self.worker_error_handler = worker_error_handler
        self.threads = []
        self.workers = []
        self.network_worker = self._new_worker("network")
        self.io_worker = self._new_worker("io")

    def _new_worker(self, name: str):
        worker = Worker(name, queue.Queue(), self.worker_error_handler)
        self.workers.append(worker)
        return worker

    def setup(self):
        self._start_workers()

    def _start_workers(self):
        for worker in self.workers:
            self._start_worker(worker)

    def _start_worker(self, worker):
        """Can be safely called multiple times on the same worker to start a new thread for it"""
        thread = threading.Thread(target=worker.run, name=worker.name)
        thread.start()
        self.threads.append(thread)

    def network(self, work: Work):
        self.network_worker.post(work)

    def io(self, work: Work):
        self.io_worker.post(work)

    def shutdown(self):
        for worker in self.workers:
            worker.shutdown()
        for thread in self.threads:
            thread.join()
