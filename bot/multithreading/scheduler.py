import queue
import threading

from bot.multithreading.worker import Worker, ImmediateWorker, QueueWorker
from bot.multithreading.work import Work


class SchedulerApi:
    def __init__(self, worker_error_handler: callable):
        self.worker_error_handler = worker_error_handler
        self.workers = []
        self.running = False
        self.immediate_worker = ImmediateWorker(worker_error_handler)
        self.network_worker = self._new_worker("network")
        self.io_worker = self._new_worker("io")

    def _new_worker(self, name: str):
        worker = QueueWorker(name, queue.Queue(), self.worker_error_handler)
        self.workers.append(worker)
        return worker

    def setup(self):
        self._start_workers()
        self.running = True

    def _start_workers(self):
        for worker in self.workers:
            self._start_worker(worker)

    @staticmethod
    def _start_worker(worker):
        """Can be safely called multiple times on the same worker to start a new thread for it"""
        thread = threading.Thread(target=worker.run, name=worker.name, daemon=True)
        thread.start()

    def network(self, work: Work):
        self._get_worker(self.network_worker).post(work)

    def io(self, work: Work):
        self._get_worker(self.io_worker).post(work)

    def _get_worker(self, worker: Worker):
        if not self.running:
            return self.immediate_worker
        return worker

    def new_worker(self, name: str):
        """Creates a new Worker and start a new Thread with it. Returns the Worker."""
        if not self.running:
            return self.immediate_worker
        worker = self._new_worker(name)
        self._start_worker(worker)
        return worker

    def shutdown(self):
        for worker in self.workers:
            worker.shutdown()
