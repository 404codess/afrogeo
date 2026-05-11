class Result:
    """
    Represents the outcome of a location verification.

    This object is returned by the `verify()` function and contains
    information about whether the validation succeeded, any errors
    encountered, and the normalized location data.

    Attributes:
        valid (bool): True if the location was successfully verified.
        errors (list[str]): A list of error messages if validation failed.
        normalized (dict): A dictionary containing standardized location names
            (country, state, lga, city) and codes if successful.
    """
    def __init__(self, valid: bool, errors=None, normalized=None):
        """
        Initialize a Result object.

        Args:
            valid: Boolean indicating success.
            errors: Optional list of error strings.
            normalized: Optional dictionary of normalized data.
        """
        self.valid = valid
        self.errors = errors or []
        self.normalized = normalized or {}

    def __bool__(self):
        """Allows using the result directly in an 'if' statement."""
        return self.valid

    def __repr__(self):
        return f"<AfrogeoResult valid={self.valid} errors={self.errors}>"
