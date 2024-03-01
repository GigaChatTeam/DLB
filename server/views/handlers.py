from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from . import exceptions
from . import forms as request_forms
from .. import helper
from ..helper.logging import log_request
from ..helper.validators import access_handlers
from ..helper.validators.validators import init_form, ValidateAccess
from ..middleware.exceptions.forms import MissingValues


def passer(*_, **__):
    return HttpResponse(status=501)


class Channels:
    class Invitations:
        @staticmethod
        @require_http_methods(["GET"])
        @init_form(pattern=request_forms.Channels.Invitations.VerifyURI, connections=["SQL"])
        @log_request
        def verify_uri(form: request_forms.Channels.Invitations.VerifyURI):
            result = helper.SQLOperator.Channels.Invitations.validate(
                connection=form.sql_connection,
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

    class Users:
        @staticmethod
        @require_http_methods(["GET"])
        @init_form(pattern=request_forms.Channels.Users.ChannelsPresenceList, connections=["SQL"])
        @log_request
        @ValidateAccess.validate_access(
            required=
            (all, [
                access_handlers.ValidateToken,
            ]))
        def get_self_presence_list(form: request_forms.Channels.Users.ChannelsPresenceList):
            if (not form.meta) and (form.order == "id"):
                result = helper.SQLOperator.Channels.Users.get_presence_list(
                    connection=form.sql_connection,
                    client=form.headers.authorize.client,
                    sort=form.sort,
                    limit=form.limit,
                    offset=form.offset
                )
            else:
                result = helper.CHOperator.Channels.Users.get_presence_list(
                    meta=form.meta,
                    order=form.order,
                    sort=form.sort,
                    client=form.headers.authorize.client,
                    limit=form.limit,
                    offset=form.offset
                )

            if form.meta:
                for index, record in enumerate(result):
                    if record["icon"] is not None:
                        result[index]["icon"] = {
                            "id": record["icon"]["id"],
                            "url": helper.S3Operator.get_presign_url(
                                bucket=record["icon"]["bucket"],
                                path=record["icon"]["path"]
                            )
                        }

            return JsonResponse({
                'status': 'Done',
                'count': result.__len__(),
                'data': result
            }, status=200)

    class Messages:
        class History:
            @staticmethod
            @require_http_methods(["GET"])
            @init_form(pattern=request_forms.Channels.Messages.History, connections=["SQL"], fix_transaction=True)
            @log_request
            @ValidateAccess.validate_access(
                required=
                (any, [
                    access_handlers.Channels.Meta.IsChannelPublic,
                    (all, [
                        access_handlers.ValidateToken,
                        access_handlers.Channels.ValidateUserSelfPresence
                    ])
                ]))
            def messages(form: request_forms.Channels.Messages.History):
                form.end = form.end or form.tr_time

                if not form.start < form.end <= form.tr_time:
                    # TODO("Check this logic to correctness")
                    raise MissingValues({
                        "start": form.start.timestamp() * 1000,
                        "end": form.end.timestamp() * 1000
                    }, [])

                data = helper.CHOperator.Channels.Messages.get_messages_history_on_channel(
                    channel=form.channel,
                    meta=form.meta,
                    min_ts=form.start,
                    max_ts=form.end,
                    sort=form.sort,
                    limit=form.limit,
                    offset=form.offset,
                )

                return JsonResponse({
                    'status': 'Done',
                    'count': data.__len__(),
                    'data': data
                }, status=200)
