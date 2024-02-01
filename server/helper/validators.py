from django.http import HttpRequest

from server.helper import SQLOperator
from server.views import forms, exceptions


def parse_form(*, pattern: type):
    def wrapper(handler):
        def executor(request: HttpRequest, **kwargs):
            return handler(pattern(request, **kwargs))

        return executor

    return wrapper


def validate_token(handler):
    def wrapper(form: forms.RequestForm):
        if not SQLOperator.token_validator(form.client, form.token):
            raise exceptions.AccessDenied()
        return handler(form)

    return wrapper


class Channels:
    @staticmethod
    def validate_permissions(*, permissions: list[int]):
        def wrapper(handler):
            def executor(form: forms.Channels.SuperPatternChannel, **kwargs):
                if not SQLOperator.Channels.Users.Permissions.validate_permissions(
                        form.client,
                        form.client,
                        permissions):
                    raise exceptions.AccessDenied()
                return handler(form, **kwargs)
            return executor
        return wrapper

    @staticmethod
    def validate_presence(handler):
        def wrapper(form: forms.Channels.SuperPatternChannel):
            if not SQLOperator.Channels.Users.Permissions.validate_presence(form.client, form.channel):
                raise exceptions.AccessDenied()
            return handler(form)

        return wrapper
