from django.http import HttpRequest
from psycopg2 import Error as DBSQLError

from server.helper import SQLOperator
from server.helper.connections import SQLConnection
from server.views import forms, exceptions


def init_form(*, pattern: type, connections: list[str] | tuple[str] = ()):
    def wrapper(handler):
        def executor(request: HttpRequest, **kwargs):
            form = pattern(request, **kwargs)

            _connections = {}

            if "SQL" in connections:
                _connections["SQL"], _connections["SQL-KEY"] = SQLConnection.get_connection()
                form.init_sql_connection(_connections["SQL"])

            try:
                return handler(form)
            except DBSQLError as db_error:
                _connections["SQL"].rollback()
                raise db_error
            finally:
                try:
                    _connections["SQL"].commit()
                finally:
                    SQLConnection.return_connection(_connections["SQL"], key=_connections["SQL-KEY"])

        return executor

    return wrapper


def validate_token(handler):
    def wrapper(form: forms.RequestForm):
        if not SQLOperator.token_validator(
                connection=form.sql_connection,
                client=form.client,
                token=form.token):
            raise exceptions.AccessDenied()
        return handler(form)

    return wrapper


class Channels:
    @staticmethod
    def validate_permissions(*, permissions: list[int]):
        def wrapper(handler):
            def executor(form: forms.Channels.SuperPatternChannel):
                if not SQLOperator.Channels.Users.Permissions.validate_permissions(
                        form.sql_connection,
                        form.client,
                        form.client,
                        permissions):
                    raise exceptions.AccessDenied()
                return handler(form)

            return executor

        return wrapper

    @staticmethod
    def validate_presence(handler):
        def wrapper(form: forms.Channels.SuperPatternChannel):
            if not SQLOperator.Channels.Users.Permissions.validate_presence(
                    connection=form.sql_connection,
                    user_id=form.client,
                    channel_id=form.channel):
                raise exceptions.AccessDenied()
            return handler(form)

        return wrapper
