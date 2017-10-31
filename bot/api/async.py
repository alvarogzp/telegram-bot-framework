from bot.api.api import Api
from bot.api.domain import OutApiObject
from bot.multithreading.scheduler import SchedulerApi


class AsyncApi:
    def __init__(self, api: Api, scheduler: SchedulerApi):
        self.api = api
        self.scheduler = scheduler

    def __getattr__(self, item):
        return self.__get_call_hook_for(item)

    def __get_call_hook_for(self, function_name):
        func = getattr(self.api, function_name)
        return lambda *args, **kwargs: self.__call_hook(func, args, kwargs)

    def __call_hook(self, func, args, kwargs):
        self.__add_scheduler(kwargs)
        return func(*args, **kwargs)

    def __add_scheduler(self, args: dict):
        args[OutApiObject.LOCAL_PARAM_SCHEDULER] = self.scheduler.network
