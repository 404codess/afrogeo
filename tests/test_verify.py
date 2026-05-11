try:
    import pytest
except ImportError:
    pytest = None
from afrogeo import verify

def test_verify_valid_nigeria_full():
    user_input = {
        "country": "Nigeria",
        "state": "Lagos",
        "lga": "Agege",
        "city": "Agege"
    }
    result = verify(user_input)
    assert result.valid is True
    assert result.normalized["state_code"] == "LA"

def test_verify_valid_nigeria_minimal():
    user_input = {
        "country": "NG",
        "state": "LA",
        "lga": "Agege"
    }
    result = verify(user_input)
    assert result.valid is True
    assert result.normalized["state"] == "Lagos"

def test_verify_invalid_state():
    user_input = {
        "country": "Nigeria",
        "state": "InvalidState",
        "lga": "Agege"
    }
    result = verify(user_input)
    assert result.valid is False
    assert "Invalid state" in result.errors

def test_verify_invalid_lga():
    user_input = {
        "country": "Nigeria",
        "state": "Lagos",
        "lga": "InvalidLGA"
    }
    result = verify(user_input)
    assert result.valid is False
    assert "Invalid LGA for selected state" in result.errors

def test_verify_unsupported_country():
    user_input = {
        "country": "UnknownCountry",
        "state": "SomeState",
        "lga": "SomeLGA"
    }
    result = verify(user_input)
    assert result.valid is False
    assert "Data for country" in result.errors[0]

if __name__ == "__main__":
    # If run directly without pytest, just run a quick check
    print("Running basic check...")
    res = verify({"country": "Nigeria", "state": "Lagos", "lga": "Agege"})
    print(f"Success: {res.valid}, Data: {res.normalized}")
