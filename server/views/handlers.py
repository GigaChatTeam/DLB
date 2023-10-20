import datetime

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from .. import helper
from . import exceptions

def load_messages(request: HttpRequest, channel=None):
    form = {
        'channel': channel or int(request.GET.get('channel', 0)),
        'start': helper.parser.parse_datetime(request.GET.get('start', None)) or helper.constants.UNIX,
        'client': request.GET.get('client', None),
        'limit': int(request.GET.get('limit', 50))
    }

    form['limit'] = abs(form['limit']) if abs(form['limit']) < 50 else 50

    return JsonResponse(
        helper.DBOperator.load_last_messages(form['channel']),
        safe=False, status=200
    )

class UsersLoader:
    class Parser:
        @staticmethod
        def messages(request: HttpRequest, channel):
            form = {}
            invalid = {}
            missing = []

            try:
                form['client'] = request.POST['client']
            except KeyError:
                missing.append('client')

            try:
                form['token'] = request.POST['token']
            except KeyError:
                missing.append('token')

            try:
                form['channel'] = int(channel)
            except ValueError:
                invalid['channel'] = channel
            except TypeError:
                missing.append('channel')

            try:
                form['start'] = helper.parser.parse_datetime(request.GET.get('start', None))
            except ValueError:
                invalid['start'] = request.GET['start']
            except TypeError:
                form['start'] = helper.constants.UNIX

            try:
                form['end'] = helper.parser.parse_datetime(request.GET.get('end', None))
            except ValueError:
                invalid['end'] = request.GET['end']
            except TypeError:
                form['end'] = datetime.datetime.now()

            try:
                form['limit'] = int(request.GET.get('limit', 50))
            except ValueError:
                invalid['limit'] = request.GET['limit']
            else:
                form['limit'] = form['limit'] if form['limit'] < 50 else 50

            if len(missing) != 0 or len(invalid) != 0:
                raise exceptions.MissingValues(invalid, missing)
            else:
                return form

        @staticmethod
        def channels(request: HttpRequest):
            form = {}
            missing = []

            try:
                form['client'] = request.POST['client']
            except KeyError:
                missing.append('client')

            try:
                form['token'] = request.POST['token']
            except KeyError:
                missing.append('token')

            if len(missing) != 0:
                raise exceptions.MissingValues({}, missing)
            else:
                return form

    @classmethod
    @require_http_methods(["GET"])
    def channels(cls, request: HttpRequest):
        try:
            form = cls.Parser.channels(request)
        except exceptions.MissingValues as error:
            return JsonResponse({
                'status': 'Refused',
                'reason': 'IncorrectArguments',
                'arguments': {
                    'invalid': error.invalid,
                    'missing': error.missing
                }
            }, status=406)

    @classmethod
    @require_http_methods(["GET"])
    def messages(cls, request: HttpRequest, *, channel):
        try:
            form = cls.Parser.messages(request, channel)
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
            helper.DBOperator.load_last_messages(channel=form['channel'], limit=form['limit']),
            safe=False, status=200
        )

class AdminLoader:
    pass
