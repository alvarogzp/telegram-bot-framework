class StorageDataSource:
    def init(self):
        raise NotImplementedError()

    def context_manager(self):
        raise NotImplementedError()
