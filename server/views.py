import datetime

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from . import helper


class Channels:
    @classmethod
    def point(cls, request: HttpRequest, channel: int = None):
        if channel is None:
            return cls.get_channels(request)
        else:
            return cls.load_messages(request, channel)

    @staticmethod
    def get_channels(request: HttpRequest):
        return JsonResponse(
            helper.DBOperator.select_allowed_channels(request.GET.get('client', 0)),
            safe=False, status=200
        )

    @staticmethod
    def load_messages(request: HttpRequest, channel = None):
        form = {
            'channel': channel or int(request.GET.get('channel', 0)),
            'start': helper.parser.parse_datetime(request.GET.get('start', None)) or helper.constants.UNIX,
            'client': request.GET.get('client', None),
            'limit': int(request.GET.get('limit', 50))
        }

        form['limit'] = form['limit'] if form['limit'] < 50 else 50

        return JsonResponse(
            helper.DBOperator.load_last_messages(form['channel']),
            safe=False, status=200
        )
