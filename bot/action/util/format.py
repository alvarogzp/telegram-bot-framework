import time

import datetime

from bot.action.userinfo import UserStorageHandler


class DateFormatter:
    @classmethod
    def format(cls, timestamp):
        return cls._format("%d %b %H:%M", timestamp)

    @classmethod
    def format_full(cls, timestamp):
        return cls._format("%d %b %Y %H:%M:%S", timestamp)

    @classmethod
    def format_only_date(cls, timestamp):
        return cls._format("%d %b %Y", timestamp)

    @staticmethod
    def _format(string_format, timestamp):
        local_time_struct = time.localtime(int(timestamp))
        return time.strftime(string_format, local_time_struct)


class UserFormatter:
    @staticmethod
    def format(user):
        if user.first_name is not None:
            formatted_user = user.first_name
            if user.last_name is not None:
                formatted_user += " " + user.last_name
        elif user.username is not None:
            formatted_user = user.username
        else:
            formatted_user = str(user.id)
        return formatted_user

    @classmethod
    def retrieve_and_format(cls, user_id, user_storage_handler: UserStorageHandler):
        return cls.format(user_storage_handler.get(user_id))


class TimeFormatter:
    @staticmethod
    def format(seconds):
        return str(datetime.timedelta(seconds=seconds))


class SizeFormatter:
    MULTIPLIER_FACTOR = 1024

    @classmethod
    def format(cls, number, suffix='B'):
        if abs(number) < cls.MULTIPLIER_FACTOR:
            return "{} {}".format(number, suffix)
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi']:
            if abs(number) < cls.MULTIPLIER_FACTOR:
                break
            number /= cls.MULTIPLIER_FACTOR
        return "{:.2f} {}{}".format(number, unit, suffix)
