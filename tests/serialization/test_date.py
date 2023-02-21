from datetime import datetime, timedelta, timezone

from gdcbeutils.parsing.date import (
    as_utc_date,
    day_start_and_end,
    end_of_day,
    start_of_day,
)


def test_as_utc_date_ignores_offset():
    date = "2020-11-20T14:30:00+0900"

    utc_date = as_utc_date(str_date=date)

    assert utc_date.utcoffset() == timedelta(0)
    assert str(utc_date) == "2020-11-20 14:30:00+00:00"


def test_as_utc_converts_naive_date():
    date = "2020-11-20T14:30:00"

    utc_date = as_utc_date(str_date=date)

    assert utc_date.utcoffset() == timedelta(0)
    assert str(utc_date) == "2020-11-20 14:30:00+00:00"


def test_get_start_of_day_from_naive():
    date = datetime(2020, 11, 20, 14, 30, 00)
    day_start = start_of_day(date)

    assert day_start.utcoffset() == timedelta(0)
    assert str(day_start) == "2020-11-20 00:00:00+00:00"
    assert day_start.microsecond == 0


def test_get_start_of_day_from_aware():
    tz = timezone(timedelta(hours=9))
    date = datetime(2020, 11, 20, 14, 30, 00, tzinfo=tz)
    day_start = start_of_day(date)

    assert str(day_start) == "2020-11-20 00:00:00+09:00"
    assert day_start.microsecond == 0


def test_get_end_of_day_from_naive():
    date = datetime(2020, 11, 20, 14, 30, 00)
    day_end = end_of_day(date)

    assert day_end.utcoffset() == timedelta(0)
    assert str(day_end) == "2020-11-20 23:59:59.999999+00:00"


def test_get_end_of_day_from_aware():
    tz = timezone(timedelta(hours=9))
    date = datetime(2020, 11, 20, 14, 30, 00, tzinfo=tz)
    day_end = end_of_day(date)

    assert str(day_end) == "2020-11-20 23:59:59.999999+09:00"


def test_get_start_and_end_of_day_utc():
    date = datetime(2020, 11, 20, 14, 30, 00)

    day_start, day_end = day_start_and_end(date=date)

    assert str(day_start) == "2020-11-20 00:00:00+00:00"
    assert str(day_end) == "2020-11-20 23:59:59.999999+00:00"
