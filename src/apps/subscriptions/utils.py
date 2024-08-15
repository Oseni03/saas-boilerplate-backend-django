from datetime import datetime


def timestamp_as_datetime(timestamp):
    return datetime.fromtimestamp(timestamp, tz=datetime.UTC)