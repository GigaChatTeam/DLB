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


class Queries:
    class Channels:
        class Users:
            get_presence_list = {
                ("id", "asc", True): """
                    WITH "index" AS (
                        SELECT
                            "channels"."index"."id" AS "id",
                            "channels"."index"."title" AS "title",
                            "channels"."index"."description" AS "description",
                            EXTRACT ( EPOCH FROM "channels"."index"."created" ) AS "created",
                            "channels"."index"."enabled" AS "enabled",
                            MAX ("channels"."messages"."posted") AS "last",
                            "channels"."index"."avatar"
                        FROM "channels"."index"
                        JOIN
                            "channels"."users"
                            ON
                                "channels"."index"."id" = "channels"."users"."channel"
                        LEFT JOIN
                            "channels"."messages"
                            ON
                                "channels"."index"."id" = "channels"."messages"."channel"
                        WHERE
                            "channels"."users"."client" = %s
                        GROUP BY
                            "channels"."index"."id"
                    )
                    SELECT
                        "index"."id",
                        "index"."title",
                        "index"."description",
                        "index"."created",
                        "index"."enabled",
                        "channels"."messages_data"."data",
                        "files"."bucket",
                        "files"."path"
                    FROM "index"
                    LEFT JOIN
                        "channels"."messages_data"
                        ON
                            "index"."id" = "channels"."messages_data"."channel" AND
                            "index"."last" = "channels"."messages_data"."original"
                    LEFT JOIN
                        "files"."index" AS "files"
                        ON
                            "index"."avatar" = "files"."id"
                    ORDER BY
                        "index"."id" ASC
                    LIMIT %s
                    OFFSET %s
                """,
                ("id", "asc", False): """
                    SELECT
                        "channels"."index"."id",
                        "channels"."index"."enabled"
                    FROM "channels"."index"
                    JOIN
                        "channels"."users"
                        ON "channels"."index"."id" = "channels"."users"."channel"
                    WHERE
                        "channels"."users"."client" = %s
                    ORDER BY
                        "channels"."index"."id" ASC
                    LIMIT %s
                    OFFSET %s
                """,
                ("id", "desc", True): """
                    WITH "index" AS (
                        SELECT
                            "channels"."index"."id" AS "id",
                            "channels"."index"."title" AS "title",
                            "channels"."index"."description" AS "description",
                            EXTRACT ( EPOCH FROM "channels"."index"."created" ) AS "created",
                            "channels"."index"."enabled" AS "enabled",
                            MAX ("channels"."messages"."posted") AS "last",
                            "channels"."index"."avatar"
                        FROM "channels"."index"
                        JOIN
                            "channels"."users"
                            ON
                                "channels"."index"."id" = "channels"."users"."channel"
                        LEFT JOIN
                            "channels"."messages"
                            ON
                                "channels"."index"."id" = "channels"."messages"."channel"
                        WHERE
                            "channels"."users"."client" = %s
                        GROUP BY
                            "channels"."index"."id"
                    )
                    SELECT
                        "index"."id",
                        "index"."title",
                        "index"."description",
                        "index"."created",
                        "index"."enabled",
                        "channels"."messages_data"."data",
                        "files"."bucket",
                        "files"."path"
                    FROM "index"
                    LEFT JOIN
                        "channels"."messages_data"
                        ON
                            "index"."id" = "channels"."messages_data"."channel" AND
                            "index"."last" = "channels"."messages_data"."original"
                    LEFT JOIN
                        "files"."index" AS "files"
                        ON
                            "index"."avatar" = "files"."id"
                    ORDER BY
                        "index"."id" DESC
                    LIMIT %s
                    OFFSET %s
                """,
                ("id", "desc", False): """
                    SELECT
                        "channels"."index"."id",
                        "channels"."index"."enabled"
                    FROM "channels"."index"
                    JOIN
                        "channels"."users"
                        ON "channels"."index"."id" = "channels"."users"."channel"
                    WHERE
                        "channels"."users"."client" = %s
                    ORDER BY
                        "channels"."index"."id" DESC
                    LIMIT %s
                    OFFSET %s
                """,
                ("activity", "asc", True): """
                    WITH "index" AS (
                        SELECT
                            "channels"."index"."id" AS "id",
                            "channels"."index"."title" AS "title",
                            "channels"."index"."description" AS "description",
                            EXTRACT ( EPOCH FROM "channels"."index"."created" ) AS "created",
                            "channels"."index"."enabled" AS "enabled",
                            MAX ("channels"."messages"."posted") AS "last",
                            "channels"."index"."avatar"
                        FROM "channels"."index"
                        JOIN
                            "channels"."users"
                            ON
                                "channels"."index"."id" = "channels"."users"."channel"
                        LEFT JOIN
                            "channels"."messages"
                            ON
                                "channels"."index"."id" = "channels"."messages"."channel"
                        WHERE
                            "channels"."users"."client" = %s
                        GROUP BY
                            "channels"."index"."id"
                    )
                    SELECT
                        "index"."id",
                        "index"."title",
                        "index"."description",
                        "index"."created",
                        "index"."enabled",
                        "channels"."messages_data"."data",
                        "files"."bucket",
                        "files"."path"
                    FROM "index"
                    LEFT JOIN
                        "channels"."messages_data"
                        ON
                            "index"."id" = "channels"."messages_data"."channel" AND
                            "index"."last" = "channels"."messages_data"."original"
                    LEFT JOIN
                        "files"."index" AS "files"
                        ON
                            "index"."avatar" = "files"."id"
                    ORDER BY
                        "index"."last" ASC
                    LIMIT %s
                    OFFSET %s
                """,
                ("activity", "asc", False): """
                    WITH "index" AS (
                        SELECT
                            "channels"."index"."id" AS "id",
                            "channels"."index"."enabled" AS "enabled",
                            MAX ("channels"."messages"."posted") AS "last"
                        FROM "channels"."index"
                        JOIN
                            "channels"."users"
                            ON "channels"."index"."id" = "channels"."users"."channel"
                        LEFT JOIN
                            "channels".messages
                            ON
                                "channels"."index"."id" = "channels"."messages"."channel"
                        WHERE
                            "channels"."users"."client" = %s
                        GROUP BY
                            "channels"."index"."id"
                    )
                    SELECT
                        "index"."id",
                        "index"."enabled"
                    FROM "index"
                    LEFT JOIN
                        "channels"."messages_data"
                        ON
                            "index"."id" = "channels"."messages_data"."channel" AND
                            "index"."last" = "channels"."messages_data"."original"
                    ORDER BY
                        "index"."last" ASC
                    LIMIT %s
                    OFFSET %s
                """,
                ("activity", "desc", True): """
                    WITH "index" AS (
                        SELECT
                            "channels"."index"."id" AS "id",
                            "channels"."index"."title" AS "title",
                            "channels"."index"."description" AS "description",
                            EXTRACT ( EPOCH FROM "channels"."index"."created" ) AS "created",
                            "channels"."index"."enabled" AS "enabled",
                            MAX ("channels"."messages"."posted") AS "last",
                            "channels"."index"."avatar"
                        FROM "channels"."index"
                        JOIN
                            "channels"."users"
                            ON
                                "channels"."index"."id" = "channels"."users"."channel"
                        LEFT JOIN
                            "channels"."messages"
                            ON
                                "channels"."index"."id" = "channels"."messages"."channel"
                        WHERE
                            "channels"."users"."client" = %s
                        GROUP BY
                            "channels"."index"."id"
                    )
                    SELECT
                        "index"."id",
                        "index"."title",
                        "index"."description",
                        "index"."created",
                        "index"."enabled",
                        "channels"."messages_data"."data",
                        "files"."bucket",
                        "files"."path"
                    FROM "index"
                    LEFT JOIN
                        "channels"."messages_data"
                        ON
                            "index"."id" = "channels"."messages_data"."channel" AND
                            "index"."last" = "channels"."messages_data"."original"
                    LEFT JOIN
                        "files"."index" AS "files"
                        ON
                            "index"."avatar" = "files"."id"
                    ORDER BY
                        "index"."last" DESC
                    LIMIT %s
                    OFFSET %s
                """,
                ("activity", "desc", False): """
                    WITH "index" AS (
                        SELECT
                            "channels"."index"."id" AS "id",
                            "channels"."index"."enabled" AS "enabled",
                            MAX ("channels"."messages"."posted") AS "last"
                        FROM "channels"."index"
                        JOIN
                            "channels"."users"
                            ON "channels"."index"."id" = "channels"."users"."channel"
                        LEFT JOIN
                            "channels".messages
                            ON
                                "channels"."index"."id" = "channels"."messages"."channel"
                        WHERE
                            "channels"."users"."client" = %s
                        GROUP BY
                            "channels"."index"."id"
                    )
                    SELECT
                        "index"."id",
                        "index"."enabled"
                    FROM "index"
                    LEFT JOIN
                        "channels"."messages_data"
                        ON
                            "index"."id" = "channels"."messages_data"."channel" AND
                            "index"."last" = "channels"."messages_data"."original"
                    ORDER BY
                        "index"."last" DESC
                    LIMIT %s
                    OFFSET %s
                """
            }


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
                connection, user: int, *,
                order: Literal["id", "created", "activity"] = "created",
                sort: Literal["ASC", "DESC"],
                meta: bool = False,
                limit: int = 150,
                offset: int = 0):
            cursor = connection.cursor()

            cursor.execute(Queries.Channels.Users.get_presence_list[(sort, order, meta)], (user, limit, offset))

            if meta:
                return [{
                    "id": record[0],
                    "title": record[1],
                    "description": record[2],
                    "created": record[3],
                    "enabled": record[4],
                    "last-message": record[5],
                    "icon": {
                        "bucket": record[6],
                        "path": record[7]
                    } if record[6] is not None else None
                } for record in cursor.fetchall()]
            else:
                return [{
                    "id": record[0],
                    "enabled": record[1]
                } for record in cursor.fetchall()]

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
