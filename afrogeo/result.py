from __future__ import annotations
from typing import Any, Dict, List, Optional


class Result:
    """
    Represents the outcome of a location verification.

    This object is returned by the `verify()` function and contains
    information about whether the validation succeeded, any errors
    encountered, and the normalized location data.

    Attributes:
        valid (bool): True if the location was successfully verified.
        errors (list[str]): A list of error messages if validation failed.
        normalized (dict): Canonical location data with legacy keys (state, lga,
            city), generic keys (division_1_code, division_1_name, division_2_name,
            settlement, settlements), and level labels when successful.
    """
    def __init__(
        self,
        valid: bool,
        errors: Optional[List[str]] = None,
        normalized: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize a Result object.

        Args:
            valid: Boolean indicating success.
            errors: Optional list of error strings.
            normalized: Optional dictionary of normalized data.
        """
        self.valid: bool = valid
        self.errors: List[str] = list(errors) if errors else []
        self.normalized: Dict[str, Any] = dict(normalized) if normalized else {}

    def __bool__(self) -> bool:
        """Allows using the result directly in an 'if' statement."""
        return self.valid

    def __contains__(self, key: str) -> bool:
        """Check if a key is present in the normalized data."""
        return key in self.normalized

    def __getitem__(self, key: str) -> Any:
        """Access normalized data via dictionary-style indexing."""
        return self.normalized[key]

    def get(self, key: str, default: Any = None) -> Any:
        """Safely retrieve a value from normalized data with a default."""
        return self.normalized.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Return a copy of the normalized location dictionary."""
        return dict(self.normalized)

    def __repr__(self) -> str:
        if self.valid:
            country = self.normalized.get("country_code", "")
            state = self.normalized.get("state", "")
            return f"<AfrogeoResult valid=True country='{country}' state='{state}'>"
        return f"<AfrogeoResult valid=False errors={self.errors}>"
