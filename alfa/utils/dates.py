#!/bin/python3
'''
shared date/time parsing helpers
'''
from datetime import date, datetime, timezone
from dateutil import parser as dateparser


def normalize_datetime(value):
    """
    Normalizes a user-supplied date/time value into an RFC3339 string,
    assuming UTC when no timezone is given. Accepts a string, or a
    date/datetime object (e.g. from an unquoted date in a --query YAML
    file, which PyYAML auto-parses into one of those types rather than
    a string).
    """
    if value is None:
        return None
    if isinstance(value, str):
        try:
            dt = dateparser.isoparse(value)
        except ValueError:
            raise ValueError(
                f"'{value}' is not a valid ISO 8601 date/time"
            ) from None
    elif isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        dt = datetime.combine(value, datetime.min.time())
    else:
        raise ValueError(f"Unsupported date/time value: {value!r}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()
