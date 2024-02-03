import datetime

from django.http import HttpRequest

from . import exceptions
from .. import helper
from ..helper import constants


class RequestForm:
    def __init__(self, request: HttpRequest, *, missing: list, invalid: dict):
        self.sql_connection = None

        try:
            self.client = int(request.GET['client'])
        except KeyError:
            missing.append('client')
        except ValueError:
            invalid['client'] = request.GET['client']

        try:
            self.token = request.GET['token']
        except KeyError:
            missing.append('token')

    def init_sql_connection(self, connection):
        self.sql_connection = connection


class Channels:
    class SuperPatternChannel(RequestForm):
        def __init__(self, request: HttpRequest, channel: int, *, missing: list, invalid: dict):
            super().__init__(
                request,
                missing=missing,
                invalid=invalid
            )

            try:
                self.channel = int(channel)
            except ValueError:
                invalid['channel'] = channel

    class Meta(SuperPatternChannel):
        def __init__(self, request: HttpRequest, channel: int):
            missing = []
            invalid = {}

            super().__init__(
                request,
                channel,
                missing=missing,
                invalid=invalid
            )

            if len(missing) != 0 or len(invalid) != 0:
                raise exceptions.MissingValues(invalid, missing)

    class Users:
        class ChannelsPresenceList(RequestForm):
            def __init__(self, request: HttpRequest):
                missing = []
                invalid = {}

                super().__init__(
                    request,
                    missing=missing,
                    invalid=invalid
                )

                self.sort = request.GET.get("sort", "id")
                if self.sort not in ("id", "activity"):
                    invalid["sort"] = request.GET["sort"]

                self.order = request.GET.get("order", "desc")
                if self.order not in ("asc", "desc"):
                    invalid["order"] = request.GET["order"]

                try:
                    self.meta = request.GET["meta"]
                except KeyError:
                    self.meta = False
                else:
                    if self.meta == "true":
                        self.meta = True
                    elif self.meta == "false":
                        self.meta = False
                    else:
                        invalid["meta"] = request.GET["meta"]

                try:
                    self.limit = int(request.GET['limit'])
                    if self.limit not in range(1, 151):
                        raise ValueError()
                except ValueError:
                    invalid['limit'] = request.GET['limit']
                except KeyError:
                    self.limit = 150

                try:
                    self.offset = int(request.GET['offset'])
                    if self.offset < 0:
                        raise ValueError()
                except (ValueError, TypeError):
                    invalid['offset'] = request.GET['offset']
                except KeyError:
                    self.offset = 0

                if len(missing) != 0 or len(invalid) != 0:
                    raise exceptions.MissingValues(invalid, missing)

    class Invitations:
        class VerifyURI(RequestForm):
            def __init__(self, request: HttpRequest):
                missing = []
                invalid = {}

                super().__init__(
                    request,
                    missing=missing,
                    invalid=invalid
                )

                try:
                    self.uri = request.GET['uri']
                except KeyError:
                    missing.append('uri')

                if len(missing) != 0 or len(invalid) != 0:
                    raise exceptions.MissingValues(invalid, missing)

    class Messages:
        class History(RequestForm):
            def __init__(self, request: HttpRequest, channel: int):
                missing = []
                invalid = {}

                super().__init__(
                    request,
                    missing=missing,
                    invalid=invalid
                )

                try:
                    self.channel = int(channel)
                except ValueError:
                    invalid['channel'] = channel

                try:
                    self.start = helper.parser.parse_datetime(request.GET['start'])
                except ValueError:
                    invalid['start'] = request.GET['start']
                except KeyError:
                    self.start = constants.UNIX

                try:
                    self.end = helper.parser.parse_datetime(request.GET['end'])
                except ValueError:
                    invalid['end'] = request.GET['end']
                except KeyError:
                    self.end = datetime.datetime.now()

                try:
                    self.limit = int(request.GET['limit'])
                    if self.limit not in range(1, 101):
                        raise ValueError()
                except (ValueError, TypeError):
                    invalid['limit'] = request.GET['limit']
                except KeyError:
                    self.limit = 50

                try:
                    self.offset = int(request.GET['offset'])
                    if self.offset < 0:
                        raise ValueError()
                except (ValueError, TypeError):
                    invalid['offset'] = request.GET['offset']
                except KeyError:
                    self.offset = 0

                try:
                    match request.GET['sort'].lower():
                        case 'asc':
                            self.sort = 'asc'
                        case 'desc':
                            self.sort = 'desc'
                        case _:
                            raise ValueError()
                except ValueError:
                    invalid['sort'] = request.GET['sort']
                except KeyError:
                    self.sort = 'desc'

                if len(missing) != 0 or len(invalid) != 0:
                    raise exceptions.MissingValues(invalid, missing)


class Users:
    class Channels:
        class ListUserChannels(RequestForm):
            def __init__(self, request: HttpRequest):
                missing = []
                invalid = {}

                super().__init__(
                    request,
                    missing=missing,
                    invalid=invalid
                )

                if len(missing) != 0 or len(invalid) != 0:
                    raise exceptions.MissingValues(invalid, missing)
