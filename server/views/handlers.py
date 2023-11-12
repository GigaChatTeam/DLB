from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from . import exceptions
from . import parsers
from .. import helper


class UsersLoader:
    @staticmethod
    @require_http_methods(["GET"])
    def channels(request: HttpRequest):
        data = helper.DBOperator.UsersExecutor.Channels.get(**parsers.channels(request))

        data['status'] = 'Done'

        return JsonResponse(data, status=200)

    @staticmethod
    @require_http_methods(["GET"])
    def messages(request: HttpRequest, *, channel):
        data = helper.DBOperator.UsersExecutor.Channels.get_messages(**parsers.messages(request, channel))

        data['status'] = 'Done'

        return JsonResponse(data, status=200)

class AdminLoader:
    pass
