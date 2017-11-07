import queue
import threading
from typing import Union

from bot.multithreading.worker import Worker
from bot.multithreading.worker.immediate import ImmediateWorker
from bot.multithreading.worker.queue import QueueWorker
from bot.multithreading.work import Work
from bot.multithreading.worker.pool.workers.main import QueueWorkerPool


# Default max_seconds_idle value for temporal workers in worker pools.
# The value is based on the 900 seconds that Telegram bot API servers
# currently maintain idle connections, giving some margin to avoid
# close notification having to open a new connection.
DEFAULT_WORKER_POOL_MAX_SECONDS_IDLE = 850

# Value to indicate that temporal spawned workers on a worker pool
# should be kept alive forever, ie. once a worker is spawned, it
# will never end.
# Use it to get lazy spawning of perpetual workers.
WORKER_POOL_KEEP_WORKERS_FOREVER = None


class SchedulerApi:
    def __init__(self, max_network_workers: int, worker_error_handler: callable, worker_start_callback: callable, worker_end_callback: callable):
        self.worker_error_handler = worker_error_handler

        # Defining here to avoid IDE from complaining about defining variables outside __init__
        self.worker_start_callback = worker_start_callback
        self.worker_end_callback = worker_end_callback
        # Set the real callbacks
        self.set_callbacks(worker_start_callback, worker_end_callback)

        # This list is modified by multiple threads, and although lists shouldn't go corrupt
        # (https://stackoverflow.com/questions/6319207/are-lists-thread-safe)
        # we are going to play safe by protecting all access and modifications to it with a lock.
        self.running_workers = []
        self.running_workers_lock = threading.Lock()
        # Worker pools should only be launched from main thread, so no locking is needed here.
        self.worker_pools = []

        self.running = False

        self.immediate_worker = ImmediateWorker(worker_error_handler)
        self._network_worker = self._new_worker_pool(
            "network",
            min_workers=0,
            max_workers=max_network_workers,
            max_seconds_idle=DEFAULT_WORKER_POOL_MAX_SECONDS_IDLE
        )
        self._io_worker = self._new_worker_pool(
            "io", min_workers=0, max_workers=1, max_seconds_idle=WORKER_POOL_KEEP_WORKERS_FOREVER
        )
        self._background_worker = self._new_worker_pool(
            "background", min_workers=0, max_workers=1, max_seconds_idle=DEFAULT_WORKER_POOL_MAX_SECONDS_IDLE
        )

    def set_callbacks(self, worker_start_callback: callable, worker_end_callback: callable, are_async: bool = False):
        """
        :param are_async: True if the callbacks execute asynchronously, posting any heavy work to another thread.
        """
        # We are setting self.worker_start_callback and self.worker_end_callback
        # to lambdas instead of saving them in private vars and moving the lambda logic
        # to a member function for, among other reasons, making callback updates atomic,
        # ie. once a callback has been posted, it will be executed as it was in that
        # moment, any call to set_callbacks will only affect callbacks posted since they
        # were updated, but not to any pending callback.

        # If callback is async, execute the start callback in the calling thread
        scheduler = self.immediate if are_async else self.background
        self.worker_start_callback = lambda worker: scheduler(Work(
            lambda: worker_start_callback(worker), "worker_start_callback:" + worker.name
        ))

        # As the end callback is called *just* before the thread dies,
        # there is no problem running it on the thread
        self.worker_end_callback = lambda worker: self.immediate(Work(
            lambda: worker_end_callback(worker), "worker_end_callback:" + worker.name
        ))

    def _new_worker(self, name: str):
        return QueueWorker(name, queue.Queue(), self.worker_error_handler)

    def _new_worker_pool(self, name: str, min_workers: int, max_workers: int, max_seconds_idle: Union[int, None]):
        return QueueWorkerPool(name, queue.Queue(), self.worker_error_handler, self._start_worker,
                               min_workers, max_workers, max_seconds_idle)

    def setup(self):
        self._start_worker_pool(self._network_worker)
        self._start_worker_pool(self._io_worker)
        self._start_worker_pool(self._background_worker)
        self.running = True

    def _start_worker(self, worker: Worker):
        """
        Can be safely called multiple times on the same worker (for workers that support it)
        to start a new thread for it.
        """
        # This function is called from main thread and from worker pools threads to start their children threads
        with self.running_workers_lock:
            self.running_workers.append(worker)
        thread = SchedulerThread(worker, self._worker_ended)
        thread.start()
        # This may or may not be posted to a background thread (see set_callbacks)
        self.worker_start_callback(worker)

    def _start_worker_pool(self, worker: QueueWorkerPool):
        self.worker_pools.append(worker)
        worker.start()

    def _worker_ended(self, worker: Worker):
        # This function is called from worker threads
        with self.running_workers_lock:
            self.running_workers.remove(worker)
        # This is executed on the same thread (see set_callbacks)
        self.worker_end_callback(worker)

    def network(self, work: Work):
        self.network_worker.post(work)

    def io(self, work: Work):
        self.io_worker.post(work)

    def background(self, work: Work):
        self.background_worker.post(work)

    def immediate(self, work: Work):
        self.immediate_worker.post(work)

    @property
    def network_worker(self):
        return self._get_worker(self._network_worker)

    @property
    def io_worker(self):
        return self._get_worker(self._io_worker)

    @property
    def background_worker(self):
        return self._get_worker(self._background_worker)

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

    def new_worker_pool(self, name: str, min_workers: int = 0, max_workers: int = 1,
                        max_seconds_idle: int = DEFAULT_WORKER_POOL_MAX_SECONDS_IDLE):
        """
        Creates a new worker pool and starts it.
        Returns the Worker that schedules works to the pool.
        """
        if not self.running:
            return self.immediate_worker
        worker = self._new_worker_pool(name, min_workers, max_workers, max_seconds_idle)
        self._start_worker_pool(worker)
        return worker

    def get_running_workers(self):
        with self.running_workers_lock:
            # return a copy to avoid concurrent modifications problems by other threads modifications to the list
            return self.running_workers[:]

    def get_worker_pools(self):
        return self.worker_pools

    def shutdown(self):
        # first wait for all worker pools to be idle
        for worker in self.get_worker_pools():
            worker.shutdown()
        # now wait for all active workers to be idle
        # first, because there may be workers not running on a worker pool
        # and second, in case any pending work in a worker pool posted a
        # new work on another worker (pool), that way we wait for it to end too
        for worker in self.get_running_workers():
            worker.shutdown()


class SchedulerThread:
    def __init__(self, worker: Worker, end_callback: callable):
        self.worker = worker
        self.end_callback = end_callback

    def start(self):
        thread = threading.Thread(name=self.worker.name, target=self.run)
        thread.daemon = True
        thread.start()

    def run(self):
        try:
            self.worker.run()
        finally:
            self.end_callback(self.worker)
