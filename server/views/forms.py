import datetime
import ipaddress

from django.http import HttpRequest

from ..helper import constants
from ..middleware.exceptions import forms as exceptions


class AuthorizeToken:
    def __init__(self, token: str | None):
        try:
            client_id, token, *sup = token.split("-")
            self.client = int(client_id or 0)
            self.token = token
        except (ValueError, AttributeError):
            self.client = 0
            self.token = ""


class Headers:
    def __init__(self, request: HttpRequest):
        self.agent = request.headers.get("User-Agent")
        self.addr = ipaddress.ip_address(request.META["REMOTE_ADDR"])
        self.authorize = AuthorizeToken(request.headers.get("Authorization"))


class RequestForm:
    def __init__(self, request: HttpRequest, *, missing: list, invalid: dict):
        self.sql_connection = None

        self.tr_fix = False
        self.tr_time = None

        self.headers = Headers(request)

    def init_sql_connection(self, connection):
        self.sql_connection = connection


class Channels:
    class SuperPatternChannel(RequestForm):
        def __init__(self, request: HttpRequest, channel: int, *, missing: list, invalid: dict):
            super().__init__(
                request,
                missing=missing,
                invalid=invalid,
            )

            try:
                self.channel = int(channel)
            except ValueError:
                invalid["channel"] = channel

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

                self.meta = request.GET.get("meta", "true").lower()
                if self.meta == "true":
                    self.meta = True
                elif self.meta == "false":
                    self.meta = False
                else:
                    invalid["meta"] = request.GET["meta"]

                self.sort = request.GET.get("sort", "desc").lower()
                if self.sort not in ("desc", "asc"):
                    invalid["sort"] = request.GET["sort"]

                self.order = request.GET.get("order", "id").lower()
                if self.order not in ("id", "activity"):
                    invalid["order"] = request.GET["order"]

                try:
                    self.limit = int(request.GET["limit"])
                    if self.limit not in range(1, 151):
                        raise ValueError()
                except ValueError:
                    invalid["limit"] = request.GET["limit"]
                except KeyError:
                    self.limit = 150

                try:
                    self.offset = int(request.GET["offset"])
                    if self.offset < 0:
                        raise ValueError()
                except (ValueError, TypeError):
                    invalid["offset"] = request.GET["offset"]
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
                    self.uri = request.GET["uri"]
                except KeyError:
                    missing.append("uri")

                if len(missing) != 0 or len(invalid) != 0:
                    raise exceptions.MissingValues(invalid, missing)

    class Messages:
        class Message(RequestForm):
            def __init__(self, request: HttpRequest, channel: int, message_id: int):
                missing = []
                invalid = {}

                super().__init__(
                    request,
                    missing=missing,
                    invalid=invalid,
                )

                try:
                    self.channel = int(channel)
                except ValueError:
                    invalid["channel"] = channel

                try:
                    self.id = int(message_id)
                except ValueError:
                    invalid["id"] = request.GET["id"]

                if len(missing) != 0 or len(invalid) != 0:
                    raise exceptions.MissingValues(invalid, missing)

        class History(RequestForm):
            def __init__(self, request: HttpRequest, channel: int):
                missing = []
                invalid = {}

                super().__init__(
                    request,
                    missing=missing,
                    invalid=invalid,
                )

                self.meta = request.GET.get("meta", "true").lower()
                if self.meta == "true":
                    self.meta = True
                elif self.meta == "false":
                    self.meta = False
                else:
                    invalid["meta"] = request.GET["meta"]

                try:
                    self.channel = int(channel)
                except ValueError:
                    invalid["channel"] = channel

                try:
                    self.start = constants.UNIX + datetime.timedelta(microsecond=int(request.GET["start"]))
                except ValueError:
                    invalid["start"] = request.GET["start"]
                except KeyError:
                    self.start = constants.UNIX

                try:
                    self.end = constants.UNIX + datetime.timedelta(microsecond=int(request.GET["end"]))
                except ValueError:
                    invalid["end"] = request.GET["end"]
                except KeyError:
                    self.end = None

                try:
                    self.limit = int(request.GET["limit"])
                    if self.limit not in range(1, 101):
                        raise ValueError()
                except (ValueError, TypeError):
                    invalid["limit"] = request.GET["limit"]
                except KeyError:
                    self.limit = 50

                try:
                    self.offset = int(request.GET["offset"])
                    if self.offset < 0:
                        raise ValueError()
                except (ValueError, TypeError):
                    invalid["offset"] = request.GET["offset"]
                except KeyError:
                    self.offset = 0

                try:
                    match request.GET["sort"].lower():
                        case "asc":
                            self.sort = "asc"
                        case "desc":
                            self.sort = "desc"
                        case _:
                            raise ValueError()
                except ValueError:
                    invalid["sort"] = request.GET["sort"]
                except KeyError:
                    self.sort = "desc"

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
