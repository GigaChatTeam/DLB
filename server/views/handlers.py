from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from . import parsers, exceptions
from .. import helper


class UsersLoader:
    @staticmethod
    @require_http_methods(["GET"])
    def channels(request: HttpRequest):
        data = helper.SQLOperator.UsersExecutor.Channels.get(**parsers.channels(request))

        return JsonResponse({
            'status': 'Done',
            'count': data.__len__(),
            'data': data
        }, status=200)

    @staticmethod
    @require_http_methods(["GET"])
    def messages(request: HttpRequest, *, channel: int):
        data = helper.SQLOperator.UsersExecutor.Channels.get_messages(**parsers.messages(request, channel))

        return JsonResponse({
            'status': 'Done',
            'count': data.__len__(),
            'data': data
        }, status=200)


class ChannelsLoader:
    class Meta:
        @staticmethod
        @require_http_methods(["GET"])
        def join(request: HttpRequest):
            form = parsers.channel_join(request)

            if not helper.SQLOperator.token_validator(form["client"], form["token"]):
                raise exceptions.AccessDenied()

            result = helper.SQLOperator.UsersExecutor.Channels.Meta.join(form["uri"])

            if result is None:
                raise exceptions.NotFound()

            if result["icon"] is not None:
                result["icon"] = helper.S3Operator.get_presign_url(
                    bucket=result["icon"]["bucket"],
                    path=result["icon"]["path"]
                )

            return JsonResponse(result)
