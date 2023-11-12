import datetime

from django.http import HttpRequest

from . import exceptions
from .. import helper


def messages(request: HttpRequest, channel):
    form = {}
    invalid = {}
    missing = []

    try:
        form['client'] = int(request.GET['client'])
    except KeyError:
        missing.append('client')
    except ValueError:
        invalid['client'] = request.GET['client']

    try:
        form['token'] = request.GET['token']
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

    try:
        form['offset'] = int(request.GET.get('offset', 0))
    except (ValueError, TypeError):
        invalid['offset'] = request.GET['offset']

    if len(missing) != 0 or len(invalid) != 0:
        raise exceptions.MissingValues(invalid, missing)
    else:
        return form


def channels(request: HttpRequest):
    form = {}
    invalid = {}
    missing = []

    try:
        form['client'] = int(request.GET['client'])
    except KeyError:
        missing.append('client')
    except ValueError:
        invalid['client'] = request.GET['client']

    try:
        form['token'] = request.GET['token']
    except KeyError:
        missing.append('token')

    if len(missing) != 0 or len(invalid) != 0:
        raise exceptions.MissingValues(invalid, missing)
    else:
        return form
