from datetime import datetime, timezone
from pytz import timezone as pytz_timezone
from django.utils import timezone as django_timezone


def timestamp_as_datetime(timestamp):
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def datetime_as_timezone(dt: datetime, tz: str) -> datetime:
    """
    Converts a naive or timezone-aware datetime to a specific timezone.

    Args:
        dt (datetime): The datetime object to convert.
        tz (str): The timezone as a string (e.g., 'America/New_York', 'UTC').

    Returns:
        datetime: A timezone-aware datetime object.
    """
    # Ensure that the datetime object is timezone-aware (make it UTC by default if naive)
    if django_timezone.is_naive(dt):
        dt = django_timezone.make_aware(dt, django_timezone.utc)
    
    # Get the desired timezone using pytz
    target_timezone = pytz_timezone(tz)

    # Convert the datetime to the target timezone
    converted_dt = dt.astimezone(target_timezone)

    return converted_dt


def convert_timezone_to_datetime(dt: datetime, target_timezone: str = "UTC") -> datetime:
    """
    Converts a timezone-aware datetime object to a datetime in a specified timezone.

    Args:
        dt (datetime): A timezone-aware datetime object.
        target_timezone (str): The target timezone (e.g., 'America/New_York', 'UTC').

    Returns:
        datetime: A timezone-aware datetime object converted to the target timezone.
    """
    if not dt.tzinfo:
        raise ValueError("The datetime object must be timezone-aware.")

    # Convert the datetime to the target timezone
    target_tz = pytz_timezone(target_timezone)
    converted_dt = dt.astimezone(target_tz)

    return converted_dt
