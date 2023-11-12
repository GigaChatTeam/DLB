import datetime

import psycopg2

from . import parser
from ..helper import constants
from ..views import exceptions


connection = psycopg2.connect(host='localhost', port=5432, user='postgres', password='password')


def committer(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        connection.commit()
        return result

    return wrapper


class PermissionExecutor:
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
        @committer
        def get(client: int, token: str):
            cursor = connection.cursor()

            cursor.execute("""
                SELECT * FROM channels.select_channels(%s, %s) AS (
                    id BIGINT,
                    title TEXT,
                    description TEXT,
                    avatar BIGINT,
                    links TEXT[],
                    created TIMESTAMP,
                    enabled BOOLEAN
                )
            """, (client, token))

            data = cursor.fetchall()

            if not data:
                raise exceptions.AccessDenied()
            elif data[0][0] == 0:
                return {
                    'count': 0,
                    'channels': []
                }
            else:
                returns = {
                    'count': len(data),
                    'channels': []
                }

                for record in data:
                    returns['channels'].append({
                        'id': record[0],
                        'title': record[1],
                        'description': record[2],
                        'avatar': record[3],
                        'links': record[4],
                        'created': parser.serialize_datetime(record[5]),
                        'enabled': record[6]
                    })

                return returns

        @staticmethod
        @committer
        def get_messages(client: int, channel: int, token: str, *,
                         start=constants.UNIX, end=datetime.datetime.now(), limit: int = 20, offset: int = 0):
            cursor = connection.cursor()

            cursor.execute("""
                SELECT * FROM channels.select_messages(%s, %s, %s, %s, %s, %s, %s) AS (
                    posted TIMESTAMP,
                    author BIGINT,
                    alias CHAR(32),
                    type CHAR(12),
                    data TEXT,
                    attachments JSONB,
                    edited BOOLEAN
                )
            """, (client, channel, start, end, limit, offset, token))

            data = cursor.fetchall()

            if not data:
                raise exceptions.AccessDenied()
            elif data[0][1] == 0:
                return {
                    'count': 0,
                    'channel': channel,
                    'data': []
                }
            else:
                returns = {
                    'count': len(data),
                    'channel': channel,
                    'data': []
                }

                for record in data:
                    returns['data'].append({
                        'posted': parser.serialize_datetime(record[0]),
                        'author': record[1],
                        'alias': record[2].strip() if record[2] is not None else None,
                        'type': record[3].strip(),
                        'data': record[4],
                        'attachments': record[5],
                        'edited': record[6]
                    })

                return returns
