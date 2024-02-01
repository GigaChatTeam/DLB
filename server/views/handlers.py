from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from . import exceptions, forms
from .. import helper
from ..helper import validators, connections
from ..helper.validators import parse_form, validate_token


def passer(*_, **__):
    return HttpResponse(status=501)



class Channels:
    class Invitations:
        @staticmethod
        @require_http_methods(["GET"])
        @parse_form(pattern=forms.Channels.Invitations.VerifyURI)
        @connections.SQLConnection.init_connection
        @validate_token
        def verify_uri(form: forms.Channels.Invitations.VerifyURI, connection):
            result = helper.SQLOperator.Channels.Meta.join(
                connection=connection,
                uri=form.uri
            )

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
            @connections.SQLConnection.init_connection
            @validate_token
            @validators.Channels.validate_presence
            @validators.Channels.validate_permissions(permissions=[0, 1])
            def messages(form: forms.Channels.Messages.History, connection):
                data = helper.SQLOperator.Channels.Messages.History.get_messages(
                    connection=connection,
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
