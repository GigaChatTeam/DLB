import bcrypt


def verify(data, hashpw):
    return bcrypt.checkpw(data.encode(), hashpw)
