import time
from datetime import timedelta


def days_to_seconds(*, days: int) -> int:
    return days * 24 * 60 * 60


def time_sub_day(get_time):
    if get_time is None:
        return None

    time_now = int(time.time())
    middle_time = int(get_time) - time_now

    if middle_time <= 0:
        return False
    else:
        remaining_time = str(timedelta(seconds=middle_time))
        remaining_time = remaining_time.replace("days", "дней")
        remaining_time = remaining_time.replace("day", "день")
        return remaining_time