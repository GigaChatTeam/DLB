from .general import FormError


class MissingValues(FormError):
    def __init__(self, invalid: dict[str: str], missing: list[str]):
        self.invalid = invalid
        self.missing = missing
