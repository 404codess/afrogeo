import json
from pathlib import Path
from afrogeo.result import Result

# Load JSON
BASE = Path(__file__).parent
DATA_PATH = BASE / "data" / "ng.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)


def verify(user_input: dict):
    """
    Verify Nigerian location using:

    - state (code OR full name)
    - lga (required)
    - city (optional)

    Accepts lowercase inputs.
    """

    errors = []

    country_input = user_input.get("country", "").strip().lower()
    state_input = user_input.get("state", "").strip().lower()
    lga_input = user_input.get("lga", "").strip().lower()
    city_input = user_input.get("city", "").strip().lower() or None

    if not state_input or not lga_input:
        return Result(False, ["state and lga are required"])

    # -------------------------
    # COUNTRY MATCH (NG / Nigeria)
    # -------------------------
    found_country_code = None

    for code, country in DATA.items():
        if (
            code.lower() == country_input
            or country["name"].lower() == country_input
            or country_input == ""
        ):
            found_country_code = code
            break

    if not found_country_code:
        return Result(False, ["Invalid country"])

    country_data = DATA[found_country_code]
    states = country_data["states"]

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
    lgas = found_state_data["lgas"]

    found_lga_name = None
    found_city_name = None

    for lga_name, lga_info in lgas.items():
        if lga_name.lower() == lga_input:
            found_lga_name = lga_name
            found_city_name = lga_info["city"]
            break

    if not found_lga_name:
        return Result(False, ["Invalid LGA for selected state"])

    # -------------------------
    # OPTIONAL CITY CHECK
    # -------------------------
    if city_input:
        if not found_city_name:
            return Result(False, ["LGA does not belong to a city"])

        if found_city_name.lower() != city_input:
            return Result(False, ["City does not match LGA"])

    # -------------------------
    # SUCCESS
    # -------------------------
    normalized = {
        "country_code": found_country_code,
        "country": country_data["name"],
        "state_code": found_state_code,
        "state": found_state_data["name"],
        "capital": found_state_data["capital"],
        "lga": found_lga_name,
        "city": found_city_name,
    }

    return Result(True, [], normalized)
