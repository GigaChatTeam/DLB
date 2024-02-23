from django.http import HttpRequest
from psycopg2 import Error as DBSQLError

from server.helper import SQLOperator
from server.helper.connections import SQLConnection
from server.views import forms, exceptions
from server.views.forms import RequestForm


def init_form(*, pattern: type, connections: list[str] | tuple[str] = (), fix_transaction: bool = False):
    def wrapper(handler):
        def executor(request: HttpRequest, **kwargs):
            form: RequestForm = pattern(request, **kwargs)
            form.tr_fix = fix_transaction

            _connections = {}

            try:
                if "SQL" in connections:
                    _connections["SQL"], _connections["SQL-KEY"] = SQLConnection.get_connection()
                    form.init_sql_connection(_connections["SQL"])

                    if form.tr_fix:
                        cursor = _connections["SQL"].cursor()
                        cursor.execute("SELECT TIMEZONE('UTC', now())")
                        form.tr_time = cursor.fetchone()[0]
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
        if form.headers.authorize is None:
            raise exceptions.AccessDenied()

        if not SQLOperator.token_validator(
                connection=form.sql_connection,
                client=form.headers.authorize.client,
                token=form.headers.authorize.token):
            raise exceptions.AccessDenied()
        return handler(form)

    return wrapper


class Channels:
    @staticmethod
    def validate_permissions(*, permissions: list[int]):
        def wrapper(handler):
            def executor(form: forms.Channels.SuperPatternChannel):
                if not SQLOperator.Channels.Users.Permissions.validate_permissions(
                        connection=form.sql_connection,
                        user=form.headers.authorize.client,
                        channel=form.channel,
                        permissions=permissions):
                    raise exceptions.AccessDenied()
                return handler(form)
            return executor
        return wrapper

    @staticmethod
    def validate_presence(handler):
        def wrapper(form: forms.Channels.SuperPatternChannel):
            if not SQLOperator.Channels.Users.Permissions.validate_presence(
                    connection=form.sql_connection,
                    user=form.headers.authorize.client,
                    channel=form.channel):
                raise exceptions.AccessDenied()
            return handler(form)
        return wrapper
