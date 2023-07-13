class TimeoutError(Exception):
    def __str__(self) -> str:
        return "function running out of time"


class WrongTypeError(Exception):
    def __str__(self) -> str:
        return "unexpected return value type"
