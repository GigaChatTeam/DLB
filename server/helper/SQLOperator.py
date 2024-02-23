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
        @staticmethod
        def get_presence_list(
                connection,
                client: int, *,
                sort: Literal["ASC", "DESC"] = "DESC",
                limit: int = 150,
                offset: int = 0):
            cursor = connection.cursor()

            cursor.execute(f"""
                SELECT
                    "channels"."users"."channel"
                FROM
                    "channels"."users"
                WHERE
                    "channels"."users"."client" = %s
                ORDER BY
                    "channels"."users"."channel" {sort}
                LIMIT %s
                OFFSET %s
            """, (client, limit, offset))

            return [{
                "id": record[0]
            } for record in cursor.fetchall()]

        class Permissions:
            @staticmethod
            def validate_permissions(connection, user: int, channel: int, permissions: list[int]) -> bool:
                cursor = connection.cursor()

                cursor.execute(f"""
                    SELECT
                        "status"
                    FROM "channels"."select_permissions"(%s, %s) AS (
                        "permission" BIGINT,
                        "status" BOOLEAN
                    )
                    WHERE
                        "permission" = ANY ( %s )
                """, (user, channel, permissions))

                return all(r[0] for r in cursor.fetchall())

            @staticmethod
            def validate_presence(connection, user, channel):
                cursor = connection.cursor()

                cursor.execute(f"""
                    SELECT EXISTS (
                        SELECT
                            *
                        FROM
                            "channels"."users"
                        WHERE
                            "channels"."users"."client" = %s AND
                            "channels"."users"."channel" = %s AND
                            "channels"."users"."status" = 1
                    )
                """, (user, channel))

                return cursor.fetchone()[0]
