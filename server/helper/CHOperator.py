import datetime
from typing import Literal

import clickhouse_connect

from server import settings

connection = clickhouse_connect.get_client(
    host=settings.DATABASES["CH"]["HOST"],
    port=settings.DATABASES["CH"]["PORT"],
    user=settings.DATABASES["CH"]["USER"],
    password=settings.DATABASES["CH"]["PASSWORD"],
    secure=settings.DATABASES["CH"]["SECURE"],
)


def log_query(
        *,
        user: int,
        agent: str,
        success: bool,
        error: bool,
        addr: str):
    connection.command("""
        INSERT INTO users.logins
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)
    """, (user, datetime.datetime.now(datetime.UTC), "query", success, error, agent, addr))


class Queries:
    class Channels:
        class Users:
            get_presence_list = {
                (True, "activity"): """
                    SELECT
                        `channels`.`users2channels`.`channel`,
                        argMax (`channels`.`users2channels`.`client-status`, `timestamp`),
                        argMax (`channels`.`users2channels`.`channel-title`, `timestamp`),
                        argMax (`channels`.`users2channels`.`channel-description`, `timestamp`),
                        argMax (`channels`.`users2channels`.`channel-public`, `timestamp`),
                        argMax (`channels`.`users2channels`.`channel-enabled`, `timestamp`),
                        (argMax (`channels`.`users2channels`.`channel-icon-status`, `timestamp`))::BOOL,
                        argMax (`channels`.`users2channels`.`channel-icon-id`, `timestamp`),
                        argMax (`channels`.`users2channels`.`channel-icon-bucket`, `timestamp`),
                        argMax (`channels`.`users2channels`.`channel-icon-path`, `timestamp`),
                        argMax (`channels`.`messages`.`id`, `timestamp`),
                        argMax (`channels`.`messages`.`author`, `timestamp`),
                        (argMax (`channels`.`messages`.`version`, `timestamp`) != 1)::BOOL,
                        MAX (`channels`.`messages`.`timestamp`) AS `m-timestamp`,
                        toUnixTimestamp64Micro(`m-timestamp`),
                        argMax (`channels`.`messages`.`type`, `timestamp`),
                        argMax (`channels`.`messages`.`data`, `timestamp`),
                        argMax (`channels`.`messages`.`files`, `timestamp`),
                        argMax (`channels`.`messages`.`media`, `timestamp`),
                        argMax (`channels`.`messages`.`is forward`, `timestamp`),
                        argMax (`channels`.`messages`.`forward type`, `timestamp`),
                        argMax (`channels`.`messages`.`forward by`, `timestamp`)
                    FROM `channels`.`users2channels`
                    LEFT JOIN
                        `channels`.`messages`
                        ON
                            `channels`.`users2channels`.`channel` = `channels`.`messages`.`channel`
                    WHERE
                        `channels`.`users2channels`.`client` = %s AND
                        NOT `channels`.`messages`.`is deleted`
                    GROUP BY
                        `channels`.`users2channels`.`channel`
                    ORDER BY
                        `m-timestamp` {sort}
                    LIMIT %s
                    OFFSET %s
                """,
                (True, "id"): """
                    SELECT
                        `channels`.`users2channels`.`channel`,
                        argMax (`channels`.`users2channels`.`client-status`, `timestamp`),
                        argMax (`channels`.`users2channels`.`channel-title`, `timestamp`),
                        argMax (`channels`.`users2channels`.`channel-description`, `timestamp`),
                        argMax (`channels`.`users2channels`.`channel-public`, `timestamp`),
                        argMax (`channels`.`users2channels`.`channel-enabled`, `timestamp`),
                        (argMax (`channels`.`users2channels`.`channel-icon-status`, `timestamp`))::BOOL,
                        argMax (`channels`.`users2channels`.`channel-icon-id`, `timestamp`),
                        argMax (`channels`.`users2channels`.`channel-icon-bucket`, `timestamp`),
                        argMax (`channels`.`users2channels`.`channel-icon-path`, `timestamp`),
                        argMax (`channels`.`messages`.`id`, `timestamp`),
                        argMax (`channels`.`messages`.`author`, `timestamp`),
                        (argMax (`channels`.`messages`.`version`, `timestamp`) != 1)::BOOL,
                        MAX (`channels`.`messages`.`timestamp`) AS `m-timestamp`,
                        toUnixTimestamp64Micro(`m-timestamp`),
                        argMax (`channels`.`messages`.`type`, `timestamp`),
                        argMax (`channels`.`messages`.`data`, `timestamp`),
                        argMax (`channels`.`messages`.`files`, `timestamp`),
                        argMax (`channels`.`messages`.`media`, `timestamp`),
                        argMax (`channels`.`messages`.`is forward`, `timestamp`),
                        argMax (`channels`.`messages`.`forward type`, `timestamp`),
                        argMax (`channels`.`messages`.`forward by`, `timestamp`)
                    FROM `channels`.`users2channels`
                    LEFT JOIN
                        `channels`.`messages`
                        ON
                            `channels`.`users2channels`.`channel` = `channels`.`messages`.`channel`
                    WHERE
                        `channels`.`users2channels`.`client` = %s AND
                        NOT `channels`.`messages`.`is deleted`
                    GROUP BY
                        `channels`.`users2channels`.`channel`
                    ORDER BY
                        `channels`.`users2channels`.`channel` {sort}
                    LIMIT %s
                    OFFSET %s
                """,
                (False, "activity"): """
                    SELECT
                        `channels`.`users2channels`.`channel`
                    FROM `channels`.`users2channels`
                    LEFT JOIN
                        `channels`.`messages`
                        ON
                            `channels`.`users2channels`.`channel` = `channels`.`messages`.`channel`
                    WHERE
                        `channels`.`users2channels`.`client` = %s AND
                        NOT `channels`.`messages`.`is deleted`
                    GROUP BY
                        `channels`.`users2channels`.`channel`
                    ORDER BY
                        MAX (`channels`.`messages`.`timestamp`) DESC
                    LIMIT %s
                    OFFSET %s
                """
            }

        class Messages:
            get_messages_history_on_channel = {
                True: """
                    SELECT
                        `channels`.`messages`.`id`,
                        argMax (`channels`.`messages`.`author`, `channels`.`messages`.`version`),
                        (MAX (`channels`.`messages`.`version`) != 1)::BOOL,
                        toUnixTimestamp64Micro(MIN (`channels`.`messages`.`timestamp`)),
                        argMax (`channels`.`messages`.`type`, `channels`.`messages`.`version`),
                        argMax (`channels`.`messages`.`data`, `channels`.`messages`.`version`),
                        argMax (`channels`.`messages`.`files`, `channels`.`messages`.`version`),
                        argMax (`channels`.`messages`.`media`, `channels`.`messages`.`version`),
                        argMax (`channels`.`messages`.`is forward`, `channels`.`messages`.`version`),
                        argMax (`channels`.`messages`.`forward type`, `channels`.`messages`.`version`),
                        argMax (`channels`.`messages`.`forward by`, `channels`.`messages`.`version`)
                    FROM `channels`.`messages`
                    WHERE
                        `channels`.`messages`.`channel` = %s AND
                        `timestamp` BETWEEN %s AND %s AND
                        NOT `channels`.`messages`.`is deleted`
                    GROUP BY
                        `channels`.`messages`.`id`
                    ORDER BY
                        MIN (`channels`.`messages`.`timestamp`) {sort}
                    LIMIT %s
                    OFFSET %s
                """,
                False: """
                    SELECT
                        `channels`.`messages`.`id`,
                    FROM
                        `channels`.`messages`
                    WHERE
                        `channels`.`messages`.`channel` = %s AND
                        `channels`.`messages`.`version` = 1 AND
                        `channels`.`messages`.`timestamp` BETWEEN %s AND %s AND
                        NOT `channels`.`messages`.`is deleted`
                    GROUP BY
                        `channels`.`messages`.`id`
                    ORDER BY
                        MIN (`channels`.`messages`.`timestamp`) {sort}
                    LIMIT %s
                    OFFSET %s
                """
            }


class Channels:
    class Users:
        @staticmethod
        def get_presence_list(
                *,
                client: int,
                meta: bool = True,
                order: Literal["id", "activity"],
                sort: Literal["ASC", "DESC"],
                limit: int = 150,
                offset: int = 0):
            response = connection.query(
                Queries.Channels.Users.get_presence_list[(meta, order)].format(sort=sort),
                (client, limit, offset)
            )

            if meta:
                return [{
                    "id": record[0],
                    "user-status": record[1],
                    "title": record[2],
                    "description": record[3],
                    "public": record[4],
                    "enabled": record[5],
                    "icon": {
                        "id": record[7],
                        "bucket": record[8],
                        "path": record[9]
                    } if record[6] != 0 else None,
                    "last-message": {
                        "id": record[10],
                        "author": record[11],
                        "edited": record[12],
                        "timestamp": record[14],
                        "type": record[15],
                        "data": record[16],
                        "files": record[17],
                        "media": record[18],
                        "forward": {
                            "type": record[20],
                            "path": record[21],
                        } if record[19] else None,
                    }
                } for record in response.result_rows]
            else:
                return [{
                    "id": record[0]
                } for record in response.result_rows]

    class Messages:
        @staticmethod
        def get_messages_history_on_channel(
                *,
                channel: int,
                meta: bool,
                min_ts: datetime,
                max_ts: datetime,
                sort: Literal["ASC", "DESC"],
                limit: int,
                offset: int):
            response = connection.query(
                Queries.Channels.Messages.get_messages_history_on_channel[meta].format(sort=sort),
                (channel, min_ts, max_ts, limit, offset)
            )

            if meta:
                return [{
                    "id": record[0],
                    "author": record[1],
                    "edited": record[2],
                    "timestamp": record[3],
                    "type": record[4],
                    "data": record[5],
                    "files": record[6],
                    "media": record[7],
                    "forward": {
                        "type": record[9],
                        "path": record[10],
                    } if record[8] else None,
                } for record in response.result_rows]
            else:
                return [{
                    "id": record[0]
                } for record in response.result_rows]
