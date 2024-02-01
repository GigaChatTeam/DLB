import datetime
from typing import Literal

import psycopg2

from .parser import verify as verify_token
from .. import settings
from ..helper import constants

connection = psycopg2.connect(
    host=settings.DATABASES['default']['HOST'],
    port=settings.DATABASES['default']['PORT'],
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    application_name=settings.DATABASES['default']['APPLICATION']
)
connection.autocommit = True


def committer(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        connection.commit()
        return result

    return wrapper


def token_validator(client: int, token: str):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            key
        FROM
            users.tokens
        WHERE
            client = %s
    """, (client,))

    for _token in cursor.fetchall():
        if verify_token(token, _token[0].encode()):
            return True

    return False


class Channels:
    class Meta:
        @staticmethod
        def join(uri: str):
            cursor = connection.cursor()

            cursor.execute("""
                       SELECT 
                           channels."index".id,
                           channels."index".title,
                           channels."index".description,
                           channels."index".public,
                           files."index".id IS NOT NULL,
                           files."index".bucket,
                           files."index"."path"
                       FROM channels.invitations
                       JOIN
                           channels."index"
                           ON channels.invitations.channel = channels."index".id
                       LEFT JOIN
                           files."index"
                           ON channels."index"."avatar" = files."index"."id"
                       WHERE
                           channels.invitations.uri = %s AND
                           channels.invitations.enabled
                   """, (uri,))

            data = cursor.fetchone()

            if data is None:
                return None

            return {
                "id": data[0],
                "title": data[1],
                "description": data[2],
                "public": data[3],
                "icon": {
                    "bucket": data[5],
                    "path": data[6]
                } if data[4] else None
            }

    class Users:
        class Permissions:
            @staticmethod
            def validate_presence(user_id: int, channel_id: int) -> bool:
                cursor = connection.cursor()

                cursor.execute(f"""
                    SELECT channels.is_client_in_channel(%s, %s)
                """, (user_id, channel_id))

                return cursor.fetchone()[0]

            @staticmethod
            def validate_permissions(user: int, channel: int, permissions: list[int]) -> bool:
                cursor = connection.cursor()

                cursor.execute(f"""
                    SELECT
                        permission,
                        status
                    FROM channels.select_permissions(%s, %s) AS (
                        permission BIGINT,
                        status BOOLEAN
                    )
                    WHERE
                        permission = ANY ( %s )
                """, (user, channel, permissions))

                print(data := cursor.fetchall())

                return all(r[1] for r in data)

    class Messages:
        class History:
            @staticmethod
            def get_messages(
                    channel: int,
                    *,
                    start=constants.UNIX,
                    end=datetime.datetime.now(),
                    limit: int = 50,
                    offset: int = 0,
                    sort: Literal["asc", "desc"] = 'desc'
            ):
                cursor = connection.cursor()

                cursor.execute(f"""
                    SELECT * FROM channels.select_messages_{sort}(%s::BIGINT, %s, %s, %s::INTEGER, %s::INTEGER) AS (
                        posted NUMERIC,
                        author BIGINT,
                        alias UUID,
                        type TEXT,
                        media BIGINT[][],
                        data TEXT,
                        edited BOOLEAN,
                        files BIGINT[]
                    )
                """, (channel, start, end, limit, offset))

                return [{
                    'posted': record[0],
                    'author': record[1],
                    'alias': record[2],
                    'type': record[3].strip(),
                    'media': record[4],
                    'data': record[5],
                    'edited': record[6],
                    'files': record[7]
                } for record in cursor.fetchall()]
