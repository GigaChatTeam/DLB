from .general import Reason, AccessError


# 401
class AuthorizationRequired(AccessError):
    pass


# 403
class AccessDenied(AccessError):
    insufficient_permissions = Reason(43, "InsufficientPermissions")
    permissions_not_enough = Reason(44, "PermissionsNotEnough")
    permissions_not_confirmed = Reason(45, "PermissionsNotConfirmed")
    change_superior = Reason(46, "AttemptToChangeSuperior")

    def __init__(self, reason: Reason):
        self.reason = reason



# 403 -> 404
class HiddenDenied(AccessError):
    ...
