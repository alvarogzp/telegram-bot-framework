import threading
import time

import psutil

from bot.action.core.action import Action
from bot.action.util.format import TimeFormatter, SizeFormatter
from bot.action.util.textformat import FormattedText
from bot.api.domain import Message


CPU_USAGE_SAMPLE_INTERVAL_SECONDS = 1


class BenchmarkAction(Action):
    def process(self, event):
        (message, response), benchmark_execution_time = self.__benchmark(lambda: self._do_benchmark(event))

        benchmark_execution_value = TimeFormatter.format(benchmark_execution_time)
        benchmark_time = FormattedText()\
            .normal("Benchmark duration: {benchmark_time}").start_format()\
            .bold(benchmark_time=benchmark_execution_value).end_format()
        response.newline().newline().concat(benchmark_time)

        self.api.send_message(response.build_message().to_chat_replying(message))

    def _do_benchmark(self, event):
        message, benchmark_result = self._get_benchmark_result(event)

        return message, FormattedText().newline().newline().join((
            benchmark_result,
            self._get_bot_status(),
            self._get_system_status()
        ))

    def _get_benchmark_result(self, event):
        message = FormattedText().bold("Performing benchmark...").build_message().to_chat_replying(event.message)

        message, send_message_time = self.__benchmark_send_message(message)
        api_time_value = TimeFormatter.format(send_message_time)
        api_time = FormattedText()\
            .normal("API call RTT: {api_time}").start_format().bold(api_time=api_time_value).end_format()

        _, code_execution_time = self.__benchmark_code_execution()
        code_execution_value = TimeFormatter.format(code_execution_time)
        code_time = FormattedText()\
            .normal("Code execution: {code_time}").start_format().bold(code_time=code_execution_value).end_format()

        _, storage_access_time = self.__benchmark_storage_access()
        storage_access_value = TimeFormatter.format(storage_access_time)
        storage_time = FormattedText()\
            .normal("Storage access: {storage_time}").start_format()\
            .bold(storage_time=storage_access_value).end_format()

        return message, FormattedText().newline().join((
            FormattedText().bold("Benchmark result"),
            api_time,
            code_time,
            storage_time
        ))

    def __benchmark_send_message(self, message: Message):
        return self.__benchmark(lambda: self.api.send_message(message))

    def __benchmark_code_execution(self):
        return self.__benchmark(lambda: [i*j*i*j for i in range(100) for j in range(100)])

    def __benchmark_storage_access(self):
        return self.__benchmark(lambda: self.state.get_for_chat_id("0").get_for("any_feature").any_value)

    def _get_bot_status(self):
        process_uptime_value = TimeFormatter.format(self.__get_process_uptime())
        process_uptime = FormattedText()\
            .normal("Uptime: {bot_uptime}").start_format().bold(bot_uptime=process_uptime_value).end_format()

        process_memory_usage_value, process_memory_usage_attribute_name = self.__get_process_memory_usage()
        process_memory_usage_formatted_value = SizeFormatter.format(process_memory_usage_value)
        process_memory_usage = FormattedText()\
            .normal("Memory usage: {memory_usage} ({memory_usage_attribute_name})").start_format()\
            .bold(memory_usage=process_memory_usage_formatted_value)\
            .normal(memory_usage_attribute_name=process_memory_usage_attribute_name).end_format()

        thread_number_value = threading.active_count()
        thread_number = FormattedText()\
            .normal("Active threads: {thread_number}").start_format()\
            .bold(thread_number=thread_number_value).end_format()

        return FormattedText().newline().join((
            FormattedText().bold("Bot status"),
            process_uptime,
            process_memory_usage,
            thread_number
        ))

    def __get_process_uptime(self):
        create_time = psutil.Process().create_time()
        return self.__get_elapsed_seconds_since(create_time)

    @staticmethod
    def __get_process_memory_usage():
        current_process = psutil.Process()
        try:
            return current_process.memory_full_info().uss, "USS"
        except:
            return current_process.memory_info().rss, "RSS"

    def _get_system_status(self):
        system_uptime_value = TimeFormatter.format(self.__get_elapsed_seconds_since(psutil.boot_time()))
        system_uptime = FormattedText()\
            .normal("Uptime: {system_uptime}").start_format().bold(system_uptime=system_uptime_value).end_format()

        cpu_usage_value = str(psutil.cpu_percent(interval=CPU_USAGE_SAMPLE_INTERVAL_SECONDS)) + " %"
        cpu_usage = FormattedText()\
            .normal("CPU usage: {cpu_usage} ({sample_interval} sec. sample)").start_format()\
            .bold(cpu_usage=cpu_usage_value).normal(sample_interval=CPU_USAGE_SAMPLE_INTERVAL_SECONDS).end_format()

        return FormattedText().newline().join((
            FormattedText().bold("System status"),
            system_uptime,
            cpu_usage
        ))

    @staticmethod
    def __get_elapsed_seconds_since(timestamp):
        return time.time() - timestamp

    @staticmethod
    def __benchmark(func: callable):
        start_time = time.time()
        return_value = func()
        return return_value, time.time() - start_time
