import time


class DateFormatter:
    @staticmethod
    def format(timestamp):
        local_time_struct = time.localtime(int(timestamp))
        return time.strftime("%d %b %H:%M", local_time_struct)


class UserFormatter:
    @staticmethod
    def format(user):
        if user.username is not None:
            formatted_user = "@" + user.username
        elif user.first_name is not None:
            formatted_user = user.first_name
            if user.last_name is not None:
                formatted_user += " " + user.last_name
        else:
            formatted_user = str(user.id)
        return formatted_user
