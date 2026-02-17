# afrogeo/verify.py

import json
from pathlib import Path
from afrogeo.result import Result

# Path to ng.json (works offline and editable mode)
BASE = Path(__file__).parent
DATA_PATH = BASE / "data" / "ng2.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)


def verify(user_input: dict):
    """
    Verify Nigerian location based on:
    - state + city + LGA (full mode)
    - state + LGA only (minimal mode)

    Returns a Result object with normalized proper-case output.
    """
    errors = []
    normalized = {}

    # Extract user input & normalize
    country = user_input.get("country", "").strip()
    state = user_input.get("state", "").strip()
    city = user_input.get("city", "").strip() or None
    lga = user_input.get("lga", "").strip()
    
    

    if not country or not state or not lga:
        errors.append("country, state, and lga are required")
        return Result(False, errors)

    # Lowercase for matching
    country_lower = country.lower()
    state_lower = state.lower()
    city_lower = city.lower() if city else None
    lga_lower = lga.lower()

    # ----- COUNTRY CHECK -----
    found_country = None
    for c in DATA:
        if c.lower() == country_lower:
            found_country = c
            break
    if not found_country:
        errors.append("Invalid country")
        return Result(False, errors)

    # ----- STATE CHECK -----
    found_state = None
    for s in DATA[found_country]:
        if s.lower() == state_lower:
            found_state = s
            break
    if not found_state:
        errors.append("Invalid state")
        return Result(False, errors)

    state_cities = DATA[found_country][found_state]

    # ----- FULL MODE: city + lga -----
    if city_lower:
        found_city = None
        for ct in state_cities:
            if ct.lower() == city_lower:
                found_city = ct
                break
        if not found_city:
            errors.append("Invalid city")
            return Result(False, errors)

        # LGA check
        lgas = state_cities[found_city]
        found_lga = None
        for l in lgas:
            if l.lower() == lga_lower:
                found_lga = l
                break
        if not found_lga:
            errors.append("Invalid LGA for selected city")
            return Result(False, errors)

        normalized = {
            "country": found_country,
            "state": found_state,
            "city": found_city,
            "lga": found_lga
        }
        return Result(True, [], normalized)

    # ----- MINIMAL MODE: state + lga -----
    else:
        found_lga = None
        found_city = None
        for ct, lgas in state_cities.items():
            for l in lgas:
                if l.lower() == lga_lower:
                    found_lga = l
                    found_city = ct
                    break
            if found_lga:
                break

        if not found_lga:
            errors.append("LGA not found in state")
            return Result(False, errors)

        normalized = {
            "country": found_country,
            "state": found_state,
            "city": found_city,
            "lga": found_lga
        }
        return Result(True, [], normalized)
