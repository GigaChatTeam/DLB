from django.http import HttpRequest

from . import exceptions
from .. import helper


def messages(request: HttpRequest, channel: int):
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
        form['start'] = helper.parser.parse_datetime(request.GET['start'])
    except ValueError:
        invalid['start'] = request.GET['start']
    except KeyError:
        pass

    try:
        form['end'] = helper.parser.parse_datetime(request.GET['end'])
    except ValueError:
        invalid['end'] = request.GET['end']
    except KeyError:
        pass

    try:
        form['limit'] = int(request.GET['limit'])
        if form['limit'] not in range(1, 101):
            raise ValueError()
    except (ValueError, TypeError):
        invalid['limit'] = request.GET['limit']
    except KeyError:
        pass

    try:
        form['offset'] = int(request.GET['offset'])
        if form['offset'] < 0:
            raise ValueError()
    except (ValueError, TypeError):
        invalid['offset'] = request.GET['offset']
    except KeyError:
        pass

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
