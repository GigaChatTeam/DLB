# 4XX
class RequestError(Exception):
    ...


class Reason:
    def __init__(self, status_code: int, description: str):
        self.code = status_code
        self.description = description

# 401, 403
class AuthorizationError(RequestError):
    ...


# 400
class FormError(RequestError):
    ...


class AccessError(RequestError):
    ...
