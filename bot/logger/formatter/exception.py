class ExceptionFormatter:
    @staticmethod
    def format(exception: BaseException):
        return "{type}: {description}".format(type=type(exception).__name__, description=str(exception))
