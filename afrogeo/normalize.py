"""Build canonical normalized location dictionaries."""

from __future__ import annotations
from typing import Any, Dict, Iterable, Optional


def build_normalized(
    country_code: str,
    country_name: str,
    levels: Dict[str, str],
    division_code: str,
    division_name: str,
    capital: Optional[str],
    child_name: str,
    settlements: Optional[Iterable[str]],
    settlement: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a normalized location dict with legacy and generic keys.

    Legacy keys (state/lga/city) map to level-1, level-2, and settlement
    for backward compatibility across all countries.
    """
    level_1_label = levels.get("level_1", "State")
    level_2_label = levels.get("level_2", "LGA")
    settlement_list = list(settlements) if settlements is not None else []

    return {
        # Country
        "country_code": country_code,
        "country": country_name,
        "country_name": country_name,
        "levels": {
            "level_1": level_1_label,
            "level_2": level_2_label,
        },
        "level_1_label": level_1_label,
        "level_2_label": level_2_label,
        # Legacy (generic slots)
        "state_code": division_code,
        "state": division_name,
        "capital": capital,
        "lga": child_name,
        "city": settlement,
        # Generic division keys
        "division_1_code": division_code,
        "division_1_name": division_name,
        "division_2_name": child_name,
        "settlement": settlement,
        "settlements": settlement_list,
    }
