from django.http import HttpRequest, JsonResponse, HttpResponse
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

        try:
            data = helper.DBOperator.UsersExecutor.Channels.get(form['client'], form['token'])
        except exceptions.AccessDenied:
            return HttpResponse(status=403)
        else:
            data['status'] = 'Done'

            return JsonResponse(data, status=200)

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
