from .general import AuthorizationError


class AuthorizationHeaderValueMiss(AuthorizationError):
    ...


class AuthorizationHeaderValueInvalid(AuthorizationError):
    def __init__(self, value):
        self.value = value
