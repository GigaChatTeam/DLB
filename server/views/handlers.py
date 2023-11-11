from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from . import exceptions
from . import parsers
from .. import helper


class UsersLoader:
    @staticmethod
    @require_http_methods(["GET"])
    def channels(request: HttpRequest):
        try:
            form = parsers.channels(request)
        except exceptions.MissingValues as error:
            return JsonResponse({
                'status': 'Refused',
                'reason': 'IncorrectArguments',
                'arguments': {
                    'invalid': error.invalid,
                    'missing': error.missing
                }
            }, status=406)

        return JsonResponse(
            {
                "client": form['client'],
                "channels": helper.DBOperator.UsersExecutor.Channels.get(form['channel']),
            }, status=200
        )

    @staticmethod
    @require_http_methods(["GET"])
    def messages(request: HttpRequest, *, channel):
        try:
            form = parsers.messages(request, channel)
        except exceptions.MissingValues as error:
            return JsonResponse({
                'status': 'Refused',
                'reason': 'IncorrectArguments',
                'arguments': {
                    'invalid': error.invalid,
                    'missing': error.missing
                }
            }, status=406)

        return JsonResponse(
            helper.DBOperator.UsersExecutor.Channels.load_last_messages(form['channel'], form['limit']),
            safe=False, status=200
        )

class AdminLoader:
    pass
