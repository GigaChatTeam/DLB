from typing import Union, Iterable

from django.http import HttpRequest
from psycopg2 import Error as DBSQLError

from server.helper import SQLOperator
from server.helper.connections import SQLConnection
from server.helper.validators.access_handlers import Special
from server.views import forms, exceptions
from server.views.forms import RequestForm


def init_form(*, pattern: type[RequestForm], connections: Iterable[str] = (), fix_transaction: bool = False):
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
                        cursor.execute("SELECT TIMEZONE(\'UTC\', now())")
                        form.tr_time = cursor.fetchone()[0]
                return handler(form)
            except DBSQLError as db_error:
                if "SQL" in connections:
                    _connections["SQL"].rollback()
                raise db_error
            finally:
                if "SQL" in connections:
                    try:
                        _connections["SQL"].commit()
                    finally:
                        SQLConnection.return_connection(_connections["SQL"], key=_connections["SQL-KEY"])

        return executor

    return wrapper


class ValidateAccess:
    type CompareType = Union[all, any]
    type RequirementsTree = tuple[
        ValidateAccess.CompareType, list[Union[Special, type[ValidateAccess.RequirementsTree]]]]

    @classmethod
    def validate_access(cls, *, required: RequirementsTree):
        def wrapper(handler):
            def executor(form: forms.RequestForm):
                if not cls._validate_tree(required, form):
                    raise exceptions.AccessDenied()

                return handler(form)

            return executor

        return wrapper

    @classmethod
    def _validate_tree(cls, tree: RequirementsTree | tuple, form):
        return tree[0](cls._validate_collect(tree[1], form))

    @classmethod
    def _validate_collect(cls, tree: list[Union[Special, type[RequirementsTree]]], form):
        for step in tree:
            if isinstance(step, tuple):
                yield cls._validate_tree(step, form)
            elif issubclass(step, Special):
                yield step.validate_from_form(form)
            else:
                raise TypeError("Invalid type on requirements tree: %s" % step.__class__.__name__)


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
