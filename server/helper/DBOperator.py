import datetime

import psycopg2

from . import constants


connection = psycopg2.connect(host='localhost', port=5432, user='postgres', password='password')

def select_allowed_channels(client: int):
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

def load_messages_from(channel: int, *, start = constants.UNIX, end = datetime.datetime.now(), limit: int = 20):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            "index".posted,
            "index".author,
            "index".alias,
            "index".type,
            data.data,
            data.attachments,
            CASE WHEN
                MAX(data.version) <> 1
                THEN
                    true
                ELSE
                    false
            END AS edited
        FROM
            channels.messages "index"
        JOIN
            channels.messages_data data
            ON
                "index".channel = data.channel AND
                "index".posted = data.posted
        WHERE
            data.version = (
                SELECT MAX(version)
                FROM channels.messages_data
                WHERE
                    channel = "index".channel AND
                    posted = "index".posted
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
        'posted': element[0],
        'author': element[1] if element[2] == 'SYSTEM' else None,
        'alias': element[2],
        'type': element[3],
        'data': element[4],
        'attachments': element[5]
    } for element in cursor.fetchall()]

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
            CASE WHEN
                MAX(data.version) <> 1
                THEN
                    true
                ELSE
                    false
            END AS edited
        FROM
            channels.messages "index"
        JOIN
            channels.messages_data data
            ON
                "index".channel = data.channel AND
                "index".posted = data.posted
        WHERE
            data.version = (
                SELECT MAX(version)
                FROM channels.messages_data
                WHERE
                    channel = "index".channel AND
                    posted = "index".posted
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
            "index".posted DESC
        LIMIT %s
   """, (channel, limit))

    return [{
        'posted': element[0],
        'author': element[1] if element[2] == 'SYSTEM' else None,
        'alias': element[2],
        'type': element[3],
        'data': element[4],
        'attachments': element[5]
    } for element in cursor.fetchall()]
