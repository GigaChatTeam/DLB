import datetime

import psycopg2

from . import parser
from ..helper import constants


connection = psycopg2.connect(host='localhost', port=5432, user='postgres', password='password')


def committer(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        connection.commit()
        return result

    return wrapper


class PermissionExecutor(object):
    @staticmethod
    @committer
    def validate_ttoken(client: int, token: str, intention: list[str, ...]):
        cursor = connection.cursor()

        cursor.execute("""
            SELECT public.validate_ttoken(%s, %s, %s)
        """, (client, token, intention))

        try:
            return cursor.fetchone()[0]
        except IndexError:
            return False

    class Channels:
        @staticmethod
        def have_permission(client: int, channel: int, permission: list[int, int, int, int]):
            cursor = connection.cursor()

            cursor.execute("""
                SELECT COALESCE (
                    (
                        SELECT status
                        FROM channels.permissions
                        WHERE
                            client = %s AND
                            channel = %s AND
                            permission = %s
                    ),
                    (
                        SELECT status
                        FROM channels.permissions
                        WHERE
                            client = 1 AND
                            channel = %s AND
                            permission = %s
                    )
                )
            """, (client, channel, permission, channel, permission))

            try:
                return cursor.fetchone()[0]
            except IndexError:
                return None

        @staticmethod
        def is_consist(client: int, channel: int):
            cursor = connection.cursor()

            cursor.execute("""
                SELECT EXISTS (
                    SELECT *
                    FROM channels.users
                    WHERE
                        client = %s AND
                        channel = %s AND
                        leaved IS NULL
                )
            """, (client, channel))

            try:
                return cursor.fetchone()[0]
            except IndexError:
                return False


class UsersExecutor:
    class Channels:
        @staticmethod
        def get(client: int):
            cursor = connection.cursor()

            cursor.execute("""
                SELECT "index".id
                FROM channels.index "index"
                JOIN
                    channels.users users
                    ON
                        "index".id = users.channel
                WHERE
                    "index".enabled = TRUE AND
                    users.leaved IS NULL AND
                    users.client = %s
            """, (client,))

            return tuple(x[0] for x in cursor.fetchall())

        @staticmethod
        def load_messages(channel: int, *, start=constants.UNIX, end=datetime.datetime.now(), limit: int = 20):
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    "index".posted,
                    "index".author,
                    "index".alias,
                    "index".type,
                    data.data,
                    data.attachments,
                    MAX(data.version) <> 1
                FROM
                    channels.messages "index"
                JOIN
                    channels.messages_data data
                    ON
                        "index".channel = data.channel AND
                        "index".posted = data.original
                WHERE
                    data.version = (
                        SELECT MAX(version)
                        FROM channels.messages_data
                        WHERE
                            channels.messages_data.channel = "index".channel AND
                            channels.messages_data.original = "index".posted
                    ) AND
                    "index".channel = %s AND
                    "index".posted > %s AND
                    "index".posted < %s
                GROUP BY
                    "index".posted,
                    "index".author,
                    "index".alias,
                    "index".type,
                    data.data,
                    data.attachments
                ORDER BY
                    "index".posted ASC
                LIMIT %s
            """, (channel, start, end, limit))

            return [{
                'posted': parser.serialize_datetime(element[0]),
                'author': element[1],
                'alias': element[2],
                'type': element[3],
                'data': element[4],
                'attachments': element[5]
            } for element in cursor.fetchall()]

        @staticmethod
        def load_last_messages(channel: int, limit: int = 50):
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    "index".posted,
                    "index".author,
                    "index".alias,
                    "index".type,
                    data.data,
                    data.attachments,
                    MAX(data.version) <> 1
                FROM
                    channels.messages "index"
                JOIN
                    channels.messages_data data
                    ON
                        "index".channel = data.channel AND
                        "index".posted = data.original
                WHERE
                    data.version = (
                        SELECT MAX(version)
                        FROM channels.messages_data
                        WHERE
                            channels.messages_data.channel = "index".channel AND
                            channels.messages_data.original = "index".posted
                    ) AND
                    "index".channel = %s
                GROUP BY
                    "index".posted,
                    "index".author,
                    "index".alias,
                    "index".type,
                    data.data,
                    data.attachments
                ORDER BY
                    "index".posted ASC
                LIMIT %s
           """, (channel, limit))

            return [{
                'posted': parser.serialize_datetime(element[0]),
                'author': element[1],
                'alias': element[2],
                'type': element[3],
                'data': element[4],
                'attachments': element[5],
                'edited': element[6]
            } for element in cursor.fetchall()]
