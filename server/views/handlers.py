from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from . import exceptions, forms
from .. import helper
from ..helper import validators
from ..helper.validators import parse_form, validate_token


def passer(*_, **__):
    return HttpResponse(status=501)


    @staticmethod
    @require_http_methods(["GET"])
    def messages(request: HttpRequest, *, channel: int):
        data = helper.SQLOperator.UsersExecutor.Channels.get_messages(**parsers.messages(request, channel))

        return JsonResponse({
            'status': 'Done',
            'count': data.__len__(),
            'data': data
        }, status=200)
class Channels:

    class Invitations:
        @staticmethod
        @require_http_methods(["GET"])
        @parse_form(pattern=forms.Channels.Invitations.VerifyURI)
        @validate_token
        def verify_uri(form: forms.Channels.Invitations.VerifyURI):
            result = helper.SQLOperator.UsersExecutor.Channels.Meta.join(form.uri)

            if result is None:
                raise exceptions.NotFound()

            if result["icon"] is not None:
                result["icon"] = helper.S3Operator.get_presign_url(
                    bucket=result["icon"]["bucket"],
                    path=result["icon"]["path"]
                )

            return JsonResponse(result)

    class Messages:
        class History:
            @staticmethod
            @require_http_methods(["GET"])
            @parse_form(pattern=forms.Channels.Messages.History)
            @validate_token
            @validators.Channels.validate_presence
            @validators.Channels.validate_permissions(permissions=[0, 1])
            def messages(form: forms.Channels.Messages.History):
                data = helper.SQLOperator.UsersExecutor.Channels.get_messages(
                    channel=form.channel,
                    start=form.start,
                    end=form.end,
                    limit=form.limit,
                    offset=form.offset,
                    sort=form.sort
                )

                return JsonResponse({
                    'status': 'Done',
                    'count': data.__len__(),
                    'data': data
                }, status=200)
