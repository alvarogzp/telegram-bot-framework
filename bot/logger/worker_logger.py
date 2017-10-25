from bot.action.util.textformat import FormattedText
from bot.logger.logger import Logger
from bot.multithreading.worker import Worker


WORKER_TAG = FormattedText().normal("WORKER")


class WorkerStartStopLogger:
    def __init__(self, logger: Logger):
        self.logger = logger

    def worker_start(self, worker: Worker):
        self.__worker(worker, "started ✅")

    def worker_stop(self, worker: Worker):
        self.__worker(worker, "stopped ◾️")

    def __worker(self, worker: Worker, action: str):
        self.logger.log(
            WORKER_TAG,
            FormattedText().bold(worker.name),
            FormattedText().normal("Worker {action}").start_format().bold(action=action).end_format()
        )
