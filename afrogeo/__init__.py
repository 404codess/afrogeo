"""
Afrogeo: Offline-first African location verification for Python.

Validate and normalize location data across African countries using local
JSON datasets. Each country file defines its own administrative level names
(e.g. State/LGA, Province/Municipality). Works without an internet connection.

Main function:
    verify: Validates location data and returns a Result object.

Usage:
    >>> from afrogeo import verify
    >>> result = verify({"country": "Nigeria", "state": "Lagos", "lga": "Agege"})
    >>> if result:
    ...     print("Location is valid!")
"""

from .result import Result
from .verify import verify, normalize

__all__ = ["verify", "normalize", "Result"]
