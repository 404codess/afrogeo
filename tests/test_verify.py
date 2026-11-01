from pathlib import Path
import json
import pytest

from afrogeo import verify, normalize, Result
from afrogeo.verify import load_country_data, _country_registry


def test_verify_valid_nigeria_full():
    user_input = {
        "country": "Nigeria",
        "state": "Lagos",
        "lga": "Agege",
        "city": "Agege"
    }
    result = verify(user_input)
    assert result.valid is True
    assert bool(result) is True
    assert result.normalized["state_code"] == "LA"
    assert result.normalized["division_1_code"] == "LA"
    assert result.normalized["division_1_name"] == "Lagos"
    assert result.normalized["division_2_name"] == "Agege"
    assert result.normalized["settlement"] == "Agege"
    assert "Agege" in result.normalized["settlements"]
    assert result.normalized["levels"] == {"level_1": "State", "level_2": "LGA"}


def test_verify_valid_nigeria_minimal():
    user_input = {
        "country": "NG",
        "state": "LA",
        "lga": "Agege"
    }
    result = verify(user_input)
    assert result.valid is True
    assert result.normalized["state"] == "Lagos"
    assert result.normalized["city"] is None


def test_verify_nigeria_aliases():
    user_input = {
        "country": "NG",
        "division_1": "Lagos",
        "division_2": "Agege",
        "settlement": "Agege"
    }
    result = verify(user_input)
    assert result.valid is True
    assert result.normalized["lga"] == "Agege"
    assert result.normalized["city"] == "Agege"


ZA_DATA_PATH = Path(__file__).resolve().parent.parent / "afrogeo" / "data" / "za.json"
requires_za_data = pytest.mark.skipif(
    not ZA_DATA_PATH.exists(),
    reason="za.json is not bundled yet",
)


@requires_za_data
def test_verify_south_africa_sample():
    user_input = {
        "country": "South Africa",
        "state": "gauteng",
        "lga": "City of Johannesburg Metropolitan Municipality",
        "city": "sandton",
    }
    result = verify(user_input)
    assert result.valid is True
    assert result.normalized["country_code"] == "ZA"
    assert result.normalized["state_code"] == "GP"
    assert result.normalized["state"] == "Gauteng"
    assert result.normalized["level_1_label"] == "Province"
    assert result.normalized["level_2_label"] == "Municipality"
    assert result.normalized["city"] == "Sandton"


@requires_za_data
def test_za_johannesburg_settlements():
    data = json.loads(ZA_DATA_PATH.read_text(encoding="utf-8"))
    jhb = data["divisions"]["GP"]["children"][
        "City of Johannesburg Metropolitan Municipality"
    ]["settlements"]
    assert "Sandton" in jhb
    assert "Soweto" in jhb
    assert "Alexandra" in jhb
    assert len(jhb) >= 40


@requires_za_data
def test_za_data_coverage():
    data = json.loads(ZA_DATA_PATH.read_text(encoding="utf-8"))
    assert len(data["divisions"]) == 9
    total = sum(len(d["children"]) for d in data["divisions"].values())
    assert total >= 250


def test_verify_invalid_state():
    user_input = {
        "country": "Nigeria",
        "state": "InvalidState",
        "lga": "Agege"
    }
    result = verify(user_input)
    assert result.valid is False
    assert not bool(result)
    assert "Invalid State" in result.errors


def test_verify_invalid_lga():
    user_input = {
        "country": "Nigeria",
        "state": "Lagos",
        "lga": "InvalidLGA"
    }
    result = verify(user_input)
    assert result.valid is False
    assert "Invalid LGA for selected state" in result.errors


def test_normalize_returns_dict_on_success():
    data = normalize({"country": "NG", "state": "LA", "lga": "Agege"})
    assert data["country_code"] == "NG"
    assert data["division_1_name"] == "Lagos"
    assert data["division_2_name"] == "Agege"


def test_verify_case_insensitive_nigeria():
    variants = [
        {"country": "nigeria", "state": "lagos", "lga": "agege"},
        {"country": "NIGERIA", "state": "LAGOS", "lga": "AGEGE"},
        {"country": "ng", "state": "la", "lga": "agege", "city": "agege"},
        {"country": "Ng", "state": "La", "lga": "Agege", "city": "AGEGE"},
    ]
    for user_input in variants:
        result = verify(user_input)
        assert result.valid is True, f"failed for {user_input}: {result.errors}"
        assert result.normalized["state"] == "Lagos"
        assert result.normalized["lga"] == "Agege"


@requires_za_data
def test_verify_case_insensitive_south_africa():
    result = verify({
        "country": "south africa",
        "state": "gp",
        "lga": "city of johannesburg metropolitan municipality",
        "city": "sandton",
    })
    assert result.valid is True
    assert result.normalized["state"] == "Gauteng"
    assert result.normalized["city"] == "Sandton"


def test_normalize_returns_empty_on_failure():
    data = normalize({"country": "NG", "state": "XX", "lga": "Agege"})
    assert data == {}


def test_verify_unsupported_country():
    user_input = {
        "country": "UnknownCountry",
        "state": "SomeState",
        "lga": "SomeLGA"
    }
    result = verify(user_input)
    assert result.valid is False
    assert "Data for country" in result.errors[0]


@pytest.mark.parametrize("invalid_input", [None, "string", 123, [1, 2, 3], True])
def test_verify_non_dict_input(invalid_input):
    result = verify(invalid_input)
    assert result.valid is False
    assert "user_input must be a dictionary" in result.errors[0]
    assert normalize(invalid_input) == {}


def test_verify_missing_fields():
    # Missing country
    r1 = verify({"state": "Lagos", "lga": "Agege"})
    assert r1.valid is False
    assert "country is required" in r1.errors

    # Missing state
    r2 = verify({"country": "NG", "lga": "Agege"})
    assert r2.valid is False
    assert "state and lga are required" in r2.errors

    # Missing lga
    r3 = verify({"country": "NG", "state": "Lagos"})
    assert r3.valid is False
    assert "state and lga are required" in r3.errors


def test_verify_settlement_errors():
    from unittest.mock import patch

    # LGA without matching settlement
    r1 = verify({
        "country": "NG",
        "state": "Lagos",
        "lga": "Agege",
        "city": "NonExistentCity"
    })
    assert r1.valid is False
    assert "Settlement does not match LGA" in r1.errors

    # Division with no settlements defined (does not depend on za.json)
    mock_country = {
        "country_code": "NG",
        "country_name": "Nigeria",
        "levels": {"level_1": "State", "level_2": "LGA"},
        "divisions": {
            "LA": {
                "name": "Lagos",
                "capital": "Ikeja",
                "children": {
                    "EmptyLGA": {"settlements": []},
                },
            }
        },
    }
    with patch("afrogeo.verify._load_country_json_cached", return_value=mock_country):
        r2 = verify({
            "country": "NG",
            "state": "LA",
            "lga": "EmptyLGA",
            "city": "SomeCity"
        })
        assert r2.valid is False
        assert "LGA has no settlements defined" in r2.errors[0]


def test_verify_two_letter_unknown_country():
    result = verify({
        "country": "zz",
        "state": "SomeState",
        "lga": "SomeLGA"
    })
    assert result.valid is False
    assert "Data for country 'zz' not found" in result.errors[0]


def test_corrupted_json_loading():
    from unittest.mock import patch
    from afrogeo.verify import _load_country_json_cached, load_country_data, _cached_country_registry

    # Test error handling when file read fails
    with patch("builtins.open", side_effect=OSError("Disk error")):
        _load_country_json_cached.cache_clear()
        assert load_country_data("ng") is None
    _load_country_json_cached.cache_clear()

    # Test error handling when registry reads fail
    with patch("builtins.open", side_effect=OSError("Disk error")):
        _cached_country_registry.cache_clear()
        assert _cached_country_registry() == {}
    _cached_country_registry.cache_clear()


def test_registry_missing_country_code():
    from unittest.mock import patch, mock_open
    from afrogeo.verify import _cached_country_registry

    with patch("pathlib.Path.glob", return_value=[Path("dummy.json")]), \
         patch("builtins.open", mock_open(read_data='{"country_name": "NoCode"}')):
        _cached_country_registry.cache_clear()
        reg = _cached_country_registry()
        assert "nocode" not in reg
    _cached_country_registry.cache_clear()


def test_result_object_methods():
    result = verify({"country": "NG", "state": "Lagos", "lga": "Agege"})
    assert result.valid is True
    assert "state" in result
    assert "non_existent_key" not in result
    assert result["state"] == "Lagos"
    assert result.get("state") == "Lagos"
    assert result.get("non_existent", "fallback") == "fallback"

    d = result.to_dict()
    assert isinstance(d, dict)
    assert d["state"] == "Lagos"

    # String representation
    valid_repr = repr(result)
    assert "valid=True" in valid_repr
    assert "country='NG'" in valid_repr

    invalid_result = verify({"country": "NG", "state": "Invalid", "lga": "Agege"})
    invalid_repr = repr(invalid_result)
    assert "valid=False" in invalid_repr
    assert "Invalid State" in invalid_repr


def test_cache_immutability():
    data1 = load_country_data("ng")
    assert data1 is not None
    original_name = data1["country_name"]

    # Mutate data1
    data1["country_name"] = "MUTATED"
    data1["divisions"]["LA"]["name"] = "MUTATED_STATE"

    # Fetch again - must not be contaminated
    data2 = load_country_data("ng")
    assert data2["country_name"] == original_name
    assert data2["divisions"]["LA"]["name"] == "Lagos"


def test_country_registry_immutability():
    reg1 = _country_registry()
    reg1["custom"] = "fake"
    reg2 = _country_registry()
    assert "custom" not in reg2


def test_load_country_data_edge_cases():
    assert load_country_data(None) is None
    assert load_country_data("") is None
    assert load_country_data(123) is None
    assert load_country_data("non_existent_country_xyz") is None
    assert load_country_data("../ng") is None
    assert load_country_data("ng/../../etc") is None


def test_verify_non_string_field_values():
    r1 = verify({"country": True, "state": "Lagos", "lga": "Agege"})
    assert r1.valid is False
    assert "country is required" in r1.errors

    r2 = verify({"country": "NG", "state": 123, "lga": "Agege"})
    assert r2.valid is False
    assert "state and lga are required" in r2.errors


def test_verify_result_settlements_mutation_safety():
    r1 = verify({"country": "NG", "state": "Lagos", "lga": "Agege"})
    assert r1.valid is True
    r1.normalized["settlements"].append("INJECTED_SETTLEMENT")

    r2 = verify({"country": "NG", "state": "Lagos", "lga": "Agege"})
    assert "INJECTED_SETTLEMENT" not in r2.normalized["settlements"]

