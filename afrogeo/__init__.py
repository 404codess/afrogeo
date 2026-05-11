"""
Afrogeo: Offline-first African location verification for Python.

This package provides tools to validate and normalize location data
(Country, State, LGA, City) across Africa using local JSON datasets.
It is designed to work without an internet connection.

Main function:
    verify: Validates location data and returns a Result object.

Usage:
    >>> from afrogeo import verify
    >>> result = verify({"country": "Nigeria", "state": "Lagos", "lga": "Agege"})
    >>> if result:
    ...     print("Location is valid!")
"""

from .verify import verify

__all__ = ["verify"]
