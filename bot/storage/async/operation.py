import queue

from bot.multithreading.work import Work
from bot.multithreading.worker import Worker


class StorageOperation:
    def __init__(self, worker: Worker, context_manager, func: callable, name: str, ignore_result: bool):
        self.worker = worker
        self.context_manager = context_manager
        self.func = func
        self.name = name
        self.ignore_result = ignore_result
        self.result_queue = queue.Queue() if not ignore_result else None

    def execute(self):
        work = self._get_work()
        self.worker.post(work)
        if not self.ignore_result:
            return self._wait_for_result()

    def _wait_for_result(self):
        # block until result is obtained
        result = self.result_queue.get()
        if isinstance(result, StorageOperationException):
            # raise the exception in calling thread
            raise result.exception
        # return result if no exception was raised
        return result

    def _get_work(self):
        func = self._wrapper_func_no_result if self.ignore_result else self._wrapper_func_with_result
        name = self._get_work_name()
        return Work(func, name)

    def _wrapper_func_no_result(self):
        self._run_func_in_context_manager()

    def _wrapper_func_with_result(self):
        result = None
        try:
            result = self._run_func_in_context_manager()
        except Exception as e:
            result = StorageOperationException(e)
        finally:
            # always put a result, even if the operation crashes,
            # to avoid caller from getting deadlocked waiting for the result
            self.result_queue.put(result)

    def _run_func_in_context_manager(self):
        with self.context_manager:
            return self.func()

    def _get_work_name(self):
        is_blocking = "NO" if self.ignore_result else ""
        return ":".join([
            "storage_operation",
            is_blocking + "blocking",
            self.name
        ])


class StorageOperationException(Exception):
    def __init__(self, real_exception: Exception):
        self.exception = real_exception
