from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from . import parsers
from .. import helper


class UsersLoader:
    @staticmethod
    @require_http_methods(["GET"])
    def channels(request: HttpRequest):
        data = helper.DBOperator.UsersExecutor.Channels.get(**parsers.channels(request))

        return JsonResponse({
            'status': 'Done',
            'count': data.__len__(),
            'data': data
        }, status=200)

    @staticmethod
    @require_http_methods(["GET"])
    def messages(request: HttpRequest, *, channel: int):
        data = helper.DBOperator.UsersExecutor.Channels.get_messages(**parsers.messages(request, channel))

        return JsonResponse({
            'status': 'Done',
            'count': data.__len__(),
            'data': data
        }, status=200)
