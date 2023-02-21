"""
Support for date serialization
"""
from datetime import datetime, timezone

from dateutil import parser


def as_utc_date(str_date: str) -> datetime:
    date = parser.parse(str_date)

    utc_date = date.replace(tzinfo=timezone.utc)
    return utc_date


def start_of_day(date: datetime) -> datetime:
    tz = date.tzinfo or timezone.utc
    return datetime(
        date.year,
        date.month,
        date.day,
        0,
        0,
        0,
        0,
        tzinfo=tz,
    )


def end_of_day(date: datetime) -> datetime:
    tz = date.tzinfo or timezone.utc

    return datetime(
        date.year,
        date.month,
        date.day,
        23,
        59,
        59,
        999999,
        tzinfo=tz,
    )


def day_start_and_end(date: datetime):
    day_start = start_of_day(date=date)
    day_end = end_of_day(date=date)

    return day_start, day_end
