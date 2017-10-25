import queue

from bot.multithreading.work import Work
from bot.multithreading.worker.queue import QueueWorker
from bot.multithreading.worker.pool.name_generator import WorkerPoolNameGenerator
from bot.multithreading.worker.pool.spawner import WorkerSpawner


class QueueWorkerPool(QueueWorker):
    def __init__(self, base_name: str, work_queue: queue.Queue, error_handler: callable, worker_starter: callable,
                 min_workers: int, max_workers: int, max_seconds_idle: int):
        """
        :param min_workers: Minimum number of workers that must be running at every time ready to accept works.
        :param max_workers: Maximum number of workers that can be spawned on heavy workload situations.
        :param max_seconds_idle: Maximum number of seconds that the additional workers over min_workers
            that were spawned will remain alive without processing works (ie. in idle state).
        """
        super().__init__(base_name, work_queue, error_handler)
        name_generator = WorkerPoolNameGenerator(base_name, max_workers, max_seconds_idle)
        self.spawner = WorkerSpawner(
            name_generator, self.queue, error_handler, worker_starter,
            min_workers, max_workers, max_seconds_idle
        )

    def start(self):
        # called from main thread
        self.spawner.spawn_initial_workers()

    def run(self):
        # this worker is not meant to be run, it only spawns workers when needed
        pass

    def post(self, work: Work):
        # put on the queue
        super().post(work)
        # this should be quick and performs no I/O, so posting it to another worker would be inefficient
        self.spawner.spawn_worker_if_needed()
