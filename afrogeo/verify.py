import copy
import functools
import json
from pathlib import Path
from typing import Any, Dict, Optional

from afrogeo.normalize import build_normalized
from afrogeo.result import Result

# Constants
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"


@functools.lru_cache(maxsize=32)
def _load_country_json_cached(country_code: str) -> Optional[Dict[str, Any]]:
    if not country_code.isalpha():
        return None

    file_path = DATA_DIR / f"{country_code}.json"
    if not file_path.exists():
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def load_country_data(country_code: str) -> Optional[Dict[str, Any]]:
    """
    Load country data from a JSON file in the data directory.

    Args:
        country_code: The ISO country code (e.g., 'ng').

    Returns:
        A defensive copy of the country data dictionary, or None if not found.
    """
    if not country_code or not isinstance(country_code, str):
        return None
    data = _load_country_json_cached(country_code.strip().lower())
    return copy.deepcopy(data) if data is not None else None


@functools.lru_cache(maxsize=1)
def _cached_country_registry() -> Dict[str, str]:
    """Map country code or name (lowercase) to file stem code."""
    registry: Dict[str, str] = {}
    for path in DATA_DIR.glob("*.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        if "country_code" not in data:
            continue
        code = str(data["country_code"]).strip().lower()
        registry[code] = code
        if "country_name" in data:
            registry[str(data["country_name"]).strip().lower()] = code
    return registry


def _country_registry() -> Dict[str, str]:
    """Return a copy of the country registry."""
    return dict(_cached_country_registry())


def _get_input(user_input: Dict[str, Any], primary: str, alias: str) -> str:
    """Return primary key string value, else alias; empty string if neither set."""
    primary_val = user_input.get(primary)
    if isinstance(primary_val, str) and primary_val.strip():
        return primary_val.strip()
    alias_val = user_input.get(alias)
    if isinstance(alias_val, str) and alias_val.strip():
        return alias_val.strip()
    return ""


def _resolve_country_code(country_input: str) -> Optional[str]:
    if len(country_input) == 2 and country_input.isalpha():
        return country_input
    registry = _cached_country_registry()
    return registry.get(country_input.lower())


def verify(user_input: Any) -> Result:
    """
    Verify African location data against local datasets.

    Validates administrative divisions within a country using bundled JSON.
    Handles case-insensitivity and normalizes the output.

    Args:
        user_input (dict): A dictionary containing:
            - 'country' (str): Full name or ISO code (e.g., 'Nigeria' or 'NG').
            - 'state' (str): Level-1 division name or code (alias: 'division_1').
            - 'lga' (str): Level-2 division name (alias: 'division_2').
            - 'city' (str, optional): Settlement name (alias: 'settlement').

    Returns:
        afrogeo.result.Result: An object containing validation status,
            errors (if any), and normalized data.

    Example:
        >>> from afrogeo import verify
        >>> res = verify({"country": "NG", "state": "LA", "lga": "Agege"})
        >>> if res:
        ...     print(res.normalized['state'])
        Lagos
    """
    if not isinstance(user_input, dict):
        return Result(False, ["user_input must be a dictionary"])

    country_raw = _get_input(user_input, "country", "country")
    state_raw = _get_input(user_input, "state", "division_1")
    lga_raw = _get_input(user_input, "lga", "division_2")
    city_raw = _get_input(user_input, "city", "settlement")

    country_input = country_raw.lower()
    state_input = state_raw.lower()
    lga_input = lga_raw.lower()
    city_input = city_raw.lower() or None

    if not country_input:
        return Result(False, ["country is required"])
    if not state_input or not lga_input:
        return Result(False, ["state and lga are required"])

    country_code = _resolve_country_code(country_input)
    data = _load_country_json_cached(country_code) if country_code else None
    if not data:
        return Result(False, [f"Data for country '{country_raw}' not found or unsupported"])

    levels = data.get("levels", {})
    level_1_label = levels.get("level_1", "State")
    level_2_label = levels.get("level_2", "LGA")

    divisions = data.get("divisions", {})

    # -------------------------
    # LEVEL-1 MATCH (code OR name)
    # -------------------------
    found_division_code = None
    found_division_data = None

    for code, division in divisions.items():
        if (
            code.lower() == state_input
            or division.get("name", "").lower() == state_input
        ):
            found_division_code = code
            found_division_data = division
            break

    if not found_division_code or not found_division_data:
        return Result(False, [f"Invalid {level_1_label}"])

    # -------------------------
    # LEVEL-2 MATCH
    # -------------------------
    children = found_division_data.get("children", {})

    found_child_name = None
    found_child_info = None

    for child_name, child_info in children.items():
        if child_name.lower() == lga_input:
            found_child_name = child_name
            found_child_info = child_info
            break

    if not found_child_name or not found_child_info:
        return Result(
            False,
            [f"Invalid {level_2_label} for selected {level_1_label.lower()}"],
        )

    # -------------------------
    # OPTIONAL SETTLEMENT CHECK
    # -------------------------
    settlements = found_child_info.get("settlements", [])
    found_settlement = None

    if city_input:
        if not settlements:
            return Result(
                False,
                [f"{level_2_label} has no settlements defined"],
            )

        for settlement in settlements:
            if settlement and settlement.lower() == city_input:
                found_settlement = settlement
                break

        if not found_settlement:
            return Result(
                False,
                [f"Settlement does not match {level_2_label}"],
            )

    # -------------------------
    # SUCCESS
    # -------------------------
    normalized = build_normalized(
        country_code=data["country_code"],
        country_name=data["country_name"],
        levels=levels,
        division_code=found_division_code,
        division_name=found_division_data["name"],
        capital=found_division_data.get("capital"),
        child_name=found_child_name,
        settlements=settlements,
        settlement=found_settlement,
    )

    return Result(True, [], normalized)


def normalize(user_input: Any) -> Dict[str, Any]:
    """
    Validate and return normalized location data.

    Same validation as verify(). Returns the full normalized dictionary
    on success, or an empty dict on failure.

    Example:
        >>> from afrogeo import normalize
        >>> data = normalize({"country": "NG", "state": "LA", "lga": "Agege"})
        >>> data["division_1_name"]
        'Lagos'
    """
    result = verify(user_input)
    return result.normalized if result.valid else {}
