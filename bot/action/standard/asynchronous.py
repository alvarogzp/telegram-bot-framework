from bot.action.core.action import IntermediateAction
from bot.multithreading.work import Work


class AsynchronousAction(IntermediateAction):
    def __init__(self, name: str, min_workers: int = 0, max_workers: int = 4, max_seconds_idle: int = 60):
        super().__init__()
        self.name = name
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.max_seconds_idle = max_seconds_idle
        self.worker_pool = None  # initialized in post_setup where we have access to scheduler

    def post_setup(self):
        self.worker_pool = self.scheduler.new_worker_pool(
            self.name,
            self.min_workers,
            self.max_workers,
            self.max_seconds_idle
        )

    def process(self, event):
        self.worker_pool.post(Work(lambda: self._continue(event), "asynchronous_action"))
