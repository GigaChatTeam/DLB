from psycopg2.pool import ThreadedConnectionPool

from server import settings


class SQLConnection:
    connections_pool: ThreadedConnectionPool = ThreadedConnectionPool(
        settings.DATABASES["SQL"]["POOL"]["MIN CONNECTIONS"],
        settings.DATABASES["SQL"]["POOL"]["MAX CONNECTIONS"],
        host=settings.DATABASES["SQL"]["HOST"],
        port=settings.DATABASES["SQL"]["PORT"],
        user=settings.DATABASES["SQL"]["USER"],
        password=settings.DATABASES["SQL"]["PASSWORD"],
        application_name=settings.DATABASES["SQL"]["APPLICATION"],
    )

    @classmethod
    def _get_connection(cls, *, key=None, isolation: int = 4):
        connection = cls.connections_pool.getconn(key=key)
        connection.autocommit = False
        connection.set_isolation_level(isolation)
        return connection, key

    @classmethod
    def _return_connection(cls, connection, *, key=None, close=False):
        return cls.connections_pool.putconn(connection, key=key, close=close)

    @classmethod
    def get_connection(cls):
        return cls._get_connection()

    @classmethod
    def return_connection(cls, connection, key=None):
        return cls._return_connection(connection, key=key)
