class MissingValues(Exception):
    def __init__(self, invalid: dict[str: str], missing: list[str]):
        self.invalid = invalid
        self.missing = missing
        super().__init__()


class AccessDenied(Exception):
    ...


class NotFound(Exception):
    ...
