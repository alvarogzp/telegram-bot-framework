import queue
import threading

from bot.multithreading.worker import Worker
from bot.multithreading.worker.queue import QueueWorker
from bot.multithreading.worker.pool.name_generator import WorkerPoolNameGenerator
from bot.multithreading.worker.pool.workers.limited_lifespan import LimitedLifespanQueueWorker


class WorkerSpawner:
    def __init__(self, name_generator: WorkerPoolNameGenerator, work_queue: queue.Queue, error_handler: callable,
                 worker_starter: callable, min_workers: int, max_workers: int, max_seconds_idle: int):
        self.name_generator = name_generator
        self.queue = work_queue
        self.error_handler = error_handler
        self.worker_starter = worker_starter
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.max_seconds_idle = max_seconds_idle
        # children workers will update this value when they end,
        # so all modifications to this value must be protected by the lock
        self.number_of_running_workers = 0
        # re-entrant lock to allow nesting with statements
        self.lock = threading.RLock()

    # PUBLIC API
    # Ensures thread safety when necessary

    def spawn_initial_workers(self):
        # Lock is not needed here as it must be called only once at startup from a single thread
        # before anything is posted to the worker, and it only spawns not ending workers that don't
        # have access to the spawner.
        for _ in range(self.min_workers):
            worker = self._new_not_ending_worker()
            self._start_worker(worker)

    def spawn_worker_if_needed(self):
        # Called from main thread when a work is posted to the pool, and from temporal workers when they end
        with self.lock:
            if self._should_spawn_new_worker():
                self._spawn_worker()

    def worker_ended(self):
        # Called from temporal workers when they end
        with self.lock:
            # lock the decrease operation as it is not atomic
            self.number_of_running_workers -= 1
            # Keep the lock as we do not want anyone to interfere between updating the running workers count
            # and checking if a new worker should be spawned.
            # Check if this worker ended in an inappropriate moment and more workers are needed
            self.spawn_worker_if_needed()

    # PRIVATE FUNCTIONS
    # They assume only one thread will be calling them concurrently

    def _should_spawn_new_worker(self):
        unfinished_tasks_number = self.queue.unfinished_tasks
        running_workers_number = self.number_of_running_workers
        # Spawn a new thread if there are more unfinished tasks than running workers.
        #
        # Only the unfinished tasks number is checked in an unsafe way.
        # The number of unfinished tasks should only decrease, as tasks should all be posted on the same thread.
        # The number of running workers is protected by the lock and will not change.
        #
        # The possible edge cases and race conditions are:
        #  - The unfinished tasks number decrease (or increase) right after reading the value.
        #  - A thread is about to die but have still not updated the number_of_running_workers
        #    (as we have the lock).
        #
        # The possible consequences for the previous cases are:
        #  - We counted more unfinished tasks than the real ones. So we might spawn a worker when it should
        #    had not been necessary. This is acceptable and supposes no problem, as the worker will die in
        #    max_seconds_idle.
        #  - We counted less unfinished tasks than the real ones. This will only happen if multiple threads
        #    are posting to the pool. The consequence will be that we might not spawn a worker when it would
        #    be desirable. But the thread that posted the second work will call this function again when we
        #    release the lock, and it will be spawned if needed, so there is no problem.
        #  - We counted more workers than the active ones. So, a new one might not be spawned when it should.
        #    But there is no problem, as the thread that is about to die will call again this function when
        #    we release the lock, and a new thread will then be spawned.
        return unfinished_tasks_number > running_workers_number

    def _spawn_worker(self):
        if self.number_of_running_workers >= self.max_workers:
            # We are not allowed to spawn more workers.
            #
            # The possible edge case is:
            #  - A thread is about to die.
            #
            # The consequence will be:
            #  - We will not spawn a new worker when we really could. There is no problem, as when the thread
            #    that is about to die dies it will also call this and spawn the new worker if still needed.
            return
        worker = self._new_temporal_worker()
        self._start_worker(worker)

    def _new_not_ending_worker(self):
        return QueueWorker(
            self._get_worker_name(),
            self.queue,
            self.error_handler
        )

    def _new_temporal_worker(self):
        return LimitedLifespanQueueWorker(
            self._get_worker_name(is_temporal=True),
            self.queue,
            self.error_handler,
            self.max_seconds_idle,
            self.worker_ended
        )

    def _start_worker(self, worker: Worker):
        self.number_of_running_workers += 1
        self.worker_starter(worker)

    def _get_worker_name(self, is_temporal: bool = False):
        return self.name_generator.get_name(self.number_of_running_workers+1, is_temporal)
