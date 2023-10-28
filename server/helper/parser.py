from datetime import datetime


def parse_datetime(source):
    return datetime.strptime(source, "%Y-%m-%d %H:%M:%S")


def serialize_datetime(source):
    return datetime.strftime(source, "%Y-%m-%d %H:%M:%S")