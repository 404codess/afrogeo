import json
import functools
from pathlib import Path
from afrogeo.result import Result

# Constants
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

@functools.lru_cache(maxsize=10)
def load_country_data(country_code: str):
    """
    Load country data from a JSON file in the data directory.

    Args:
        country_code: The ISO country code (e.g., 'ng').

    Returns:
        A dictionary containing the country data, or None if not found.
    """
    file_path = DATA_DIR / f"{country_code.lower()}.json"
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def verify(user_input: dict):
    """
    Verify African location data against local datasets.

    This function validates if a given state, LGA, and optional city exist
    within the specified country. It handles case-insensitivity and 
    normalizes the output.

    Args:
        user_input (dict): A dictionary containing:
            - 'country' (str): Full name or ISO code (e.g., 'Nigeria' or 'NG').
            - 'state' (str): Full name or code (e.g., 'Lagos' or 'LA').
            - 'lga' (str): Local Government Area name.
            - 'city' (str, optional): City name for validation.

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
    country_input = str(user_input.get("country", "")).strip().lower()
    state_input = str(user_input.get("state", "")).strip().lower()
    lga_input = str(user_input.get("lga", "")).strip().lower()
    city_input = str(user_input.get("city", "")).strip().lower() or None

    if not country_input:
        return Result(False, ["country is required"])
    if not state_input or not lga_input:
        return Result(False, ["state and lga are required"])

    # -------------------------
    # DATA LOADING (Dynamic)
    # -------------------------
    # Map country names to codes if necessary (Basic mapping for now)
    country_map = {"nigeria": "ng", "ghana": "gh", "kenya": "ke"}
    country_code = country_map.get(country_input, country_input)
    
    data = load_country_data(country_code)
    if not data:
        return Result(False, [f"Data for country '{country_input}' not found or unsupported"])

    # -------------------------
    # COUNTRY MATCH
    # -------------------------
    found_country_key = None
    for key in data.keys():
        if key.lower() == country_code:
            found_country_key = key
            break
    
    if not found_country_key:
        return Result(False, [f"Invalid country code in data for '{country_input}'"])

    country_data = data[found_country_key]
    states = country_data.get("states", {})

    # -------------------------
    # STATE MATCH (code OR name)
    # -------------------------
    found_state_code = None
    found_state_data = None

    for code, state in states.items():
        if (
            code.lower() == state_input
            or state["name"].lower() == state_input
        ):
            found_state_code = code
            found_state_data = state
            break

    if not found_state_code:
        return Result(False, ["Invalid state"])

    # -------------------------
    # LGA MATCH
    # -------------------------
    lgas = found_state_data.get("lgas", {})

    found_lga_name = None
    found_lga_info = None

    for lga_name, lga_info in lgas.items():
        if lga_name.lower() == lga_input:
            found_lga_name = lga_name
            found_lga_info = lga_info
            break

    if not found_lga_name:
        return Result(False, ["Invalid LGA for selected state"])

    # -------------------------
    # OPTIONAL CITY CHECK
    # -------------------------
    found_city_name = found_lga_info.get("city")
    if city_input:
        if not found_city_name:
            return Result(False, ["LGA does not belong to a city"])

        if found_city_name.lower() != city_input:
            return Result(False, ["City does not match LGA"])

    # -------------------------
    # SUCCESS
    # -------------------------
    normalized = {
        "country_code": found_country_key,
        "country": country_data["name"],
        "state_code": found_state_code,
        "state": found_state_data["name"],
        "capital": found_state_data.get("capital"),
        "lga": found_lga_name,
        "city": found_city_name,
    }

    return Result(True, [], normalized)
