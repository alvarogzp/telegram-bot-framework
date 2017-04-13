class Throttler:
    def should_execute(self, event):
        raise NotImplementedError()


class NoThrottler(Throttler):
    def should_execute(self, event):
        return True
