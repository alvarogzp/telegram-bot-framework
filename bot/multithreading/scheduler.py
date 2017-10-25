import queue
import threading

from bot.multithreading.worker import Worker
from bot.multithreading.worker.immediate import ImmediateWorker
from bot.multithreading.worker.queue import QueueWorker
from bot.multithreading.work import Work
from bot.multithreading.worker.pool.workers.main import QueueWorkerPool


class SchedulerApi:
    def __init__(self, worker_error_handler: callable):
        self.worker_error_handler = worker_error_handler
        self.workers = []
        self.worker_pools = []
        self.running = False
        self.immediate_worker = ImmediateWorker(worker_error_handler)
        self.network_worker = self._new_worker("network")
        self.io_worker = self._new_worker("io")

    def _new_worker(self, name: str):
        worker = QueueWorker(name, queue.Queue(), self.worker_error_handler)
        self.workers.append(worker)
        return worker

    def _new_worker_pool(self, name: str, min_workers: int, max_workers: int, max_seconds_idle: int):
        return QueueWorkerPool(name, queue.Queue(), self.worker_error_handler, self._start_worker,
                               min_workers, max_workers, max_seconds_idle)

    def setup(self):
        self._start_workers()
        self.running = True

    def _start_workers(self):
        for worker in self.workers:
            self._start_worker(worker)

    @staticmethod
    def _start_worker(worker):
        """Can be safely called multiple times on the same worker to start a new thread for it"""
        thread = threading.Thread(target=worker.run, name=worker.name)
        thread.daemon = True
        thread.start()

    def _start_worker_pool(self, worker: QueueWorkerPool):
        self.worker_pools.append(worker)
        worker.start()

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

    def new_worker_pool(self, name: str, min_workers: int, max_workers: int, max_seconds_idle: int):
        """
        Creates a new worker pool and starts it.
        Returns the Worker that schedules works to the pool.
        """
        if not self.running:
            return self.immediate_worker
        worker = self._new_worker_pool(name, min_workers, max_workers, max_seconds_idle)
        self._start_worker_pool(worker)
        return worker

    def shutdown(self):
        for worker in self.worker_pools:
            worker.shutdown()
        for worker in self.workers:
            worker.shutdown()
