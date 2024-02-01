from types import FunctionType

from psycopg2 import Error as SQLDBError
from psycopg2.pool import ThreadedConnectionPool

from server import settings


class SQLConnection:
    connections_pool: ThreadedConnectionPool = ThreadedConnectionPool(
        settings.DATABASES['default']['POOL']['MIN CONNECTIONS'],
        settings.DATABASES['default']['POOL']['MAX CONNECTIONS'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        application_name=settings.DATABASES['default']['APPLICATION']
    )

    @classmethod
    def _get_connection(cls, *, key=None, isolation: int = 2):
        connection = cls.connections_pool.getconn(key=key)
        connection.autocommit = False
        connection.set_isolation_level(isolation)
        return connection, key

    @classmethod
    def _return_connection(cls, connection, *, key=None, close=False):
        return cls.connections_pool.putconn(connection, key=key, close=close)

    @classmethod
    def init_connection(cls, handler: FunctionType):
        def wrapper(form, *args, **kwargs):
            connection, key = cls._get_connection()
            try:
                return handler(form, connection, *args, **kwargs)
            except SQLDBError as db_error:
                connection.rollback()
                raise db_error
            finally:
                try:
                    connection.commit()
                finally:
                    cls._return_connection(connection, key=key)

        return wrapper

    @classmethod
    def disable_connection(cls, handler: FunctionType):
        def wrapper(form, _, *args, **kwargs):
            return handler(form, *args, **kwargs)
        return wrapper
