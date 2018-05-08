from bot.storage.async.scheduler import StorageScheduler
from bot.storage.data_source.data_source import StorageDataSource


class StorageApi:
    def __init__(self, data_source: StorageDataSource, scheduler: StorageScheduler):
        self.data_source = data_source
        self.scheduler = scheduler
        self.init()

    def init(self):
        self._no_result(self.__init, "init")

    def __init(self):
        self.data_source.init()

    def _no_result(self, func: callable, name: str):
        self.scheduler.schedule_no_result(func, name)

    def _with_result(self, func: callable, name: str):
        return self.scheduler.schedule_with_result(func, name)
