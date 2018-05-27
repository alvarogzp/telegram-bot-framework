from sqlite_framework.log.logger import SqliteLogger
from sqlite_framework.session.session import SqliteSession

from bot.storage.data_source.data_source import StorageDataSource


class SqliteStorageDataSource(StorageDataSource):
    def __init__(self, session: SqliteSession, logger: SqliteLogger):
        super().__init__()
        self.session = session
        self.logger = logger

    def init(self):
        self.session.init()

    def context_manager(self):
        return self.session.context_manager()
