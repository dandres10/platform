# SPEC-001 T4


class BusinessException(Exception):
    def __init__(self, key: str, code: str | None = None):
        self.key = key
        self.code = code
        super().__init__(key)
