"""Utility helpers for working with subscription timings."""
from __future__ import annotations

import time
from datetime import timedelta


def days_to_seconds(*, days: int) -> int:
    return days * 24 * 60 * 60


def humanize_subscription_time(timestamp: int | None) -> str | None | bool:
    if timestamp is None:
        return None

    time_now = int(time.time())
    middle_time = int(timestamp) - time_now

    if middle_time <= 0:
        return False

    remaining_time = str(timedelta(seconds=middle_time))
    remaining_time = remaining_time.replace("days", "дней")
    remaining_time = remaining_time.replace("day", "день")
    return remaining_time
