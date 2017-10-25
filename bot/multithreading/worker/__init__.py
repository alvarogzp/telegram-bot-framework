from bot.multithreading.work import Work


class Worker:
    def __init__(self, name: str):
        self.name = name

    def run(self):
        raise NotImplementedError()

    def post(self, work: Work):
        raise NotImplementedError()

    def shutdown(self):
        raise NotImplementedError()
