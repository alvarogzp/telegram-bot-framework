class WorkerPoolNameGenerator:
    def __init__(self, base_name: str, max_workers: int, max_seconds_idle: int):
        self.base_name = base_name
        self.max_workers = max_workers
        self.max_seconds_idle = max_seconds_idle

    def get_name(self, number: int, is_temporal: bool = False):
        name = self.base_name + "#{current}/{max}".format(current=number, max=self.max_workers)
        if is_temporal:
            name += "(max_idle:{max_seconds_idle}s)".format(max_seconds_idle=self.max_seconds_idle)
        return name
