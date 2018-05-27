from bot.multithreading.worker import Worker

from bot.storage.async.scheduler import StorageScheduler
from bot.storage.data_source.data_source import StorageDataSource


class StorageApiFactory:
    @staticmethod
    def _get_scheduler_for(worker: Worker, data_source: StorageDataSource):
        return StorageScheduler(worker, data_source.context_manager())
