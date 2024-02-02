import datetime
from typing import Literal

from .parser import verify as verify_token
from ..helper import constants


def token_validator(connection, client: int, token: str):
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
        def join(connection, uri: str):
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
            def validate_presence(connection, user_id: int, channel_id: int) -> bool:
                cursor = connection.cursor()

                cursor.execute(f"""
                    SELECT channels.is_client_in_channel(%s, %s)
                """, (user_id, channel_id))

                return cursor.fetchone()[0]

            @staticmethod
            def validate_permissions(connection, user: int, channel: int, permissions: list[int]) -> bool:
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

                return all(r[1] for r in cursor.fetchall())

    class Messages:
        class History:
            @staticmethod
            def get_messages(
                    connection,
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
