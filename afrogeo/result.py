class Result:
    def __init__(self, valid: bool, errors=None, normalized=None):
        self.valid = valid
        self.errors = errors or []
        self.normalized = normalized or {}

    def __bool__(self):
        return self.valid

    def __repr__(self):
        return f"<AfrogeoResult valid={self.valid} errors={self.errors}>"
