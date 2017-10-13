class Work:
    def __init__(self, func: callable, name: str):
        self.func = func
        self.name = name

    def do_work(self):
        self.func()
