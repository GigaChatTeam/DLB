from datetime import datetime


def parse_datetime(source):
    try:
        return datetime.strptime(source, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None
