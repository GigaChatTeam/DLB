from datetime import datetime

import bcrypt


def parse_datetime(source: int):
    return datetime.strptime(source, "%Y-%m-%d %H:%M:%S")


def serialize_datetime(source):
    return datetime.strftime(source, "%Y-%m-%d %H:%M:%S")


def verify(data, hashpw):
    return bcrypt.checkpw(data.encode(), hashpw)
