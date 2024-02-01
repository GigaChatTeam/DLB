import time

from django.http import HttpRequest

from server.helper import SQLOperator
from server.views import forms, exceptions


def parse_form(*, pattern: type):
    def wrapper(handler):
        def executor(request: HttpRequest, *args, **kwargs):
            return handler(pattern(request, *args, **kwargs))

        return executor

    return wrapper


def validate_token(handler):
    def wrapper(form: forms.RequestForm, connection, *args, **kwargs):
        if not SQLOperator.token_validator(
                connection=connection,
                client=form.client,
                token=form.token):
            raise exceptions.AccessDenied()
        return handler(form, connection, *args, **kwargs)

    return wrapper


class Channels:
    @staticmethod
    def validate_permissions(*, permissions: list[int]):
        def wrapper(handler):
            def executor(form: forms.Channels.SuperPatternChannel, connection, *args, **kwargs):
                if not SQLOperator.Channels.Users.Permissions.validate_permissions(
                        connection,
                        form.client,
                        form.client,
                        permissions):
                    raise exceptions.AccessDenied()
                return handler(form, connection, *args, **kwargs)

            return executor

        return wrapper

    @staticmethod
    def validate_presence(handler):
        def wrapper(form: forms.Channels.SuperPatternChannel, connection, *args, **kwargs):
            if not SQLOperator.Channels.Users.Permissions.validate_presence(
                    connection=connection,
                    user_id=form.client,
                    channel_id=form.channel):
                raise exceptions.AccessDenied()
            return handler(form, connection, *args, **kwargs)

        return wrapper
