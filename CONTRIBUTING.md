# Contributing to Afrogeo

Thank you for your interest in improving Afrogeo! This project relies on local JSON data to provide offline location verification across Africa.

## How to Add a New Country

To add a new country, you need to create a JSON file in the `afrogeo/data/` directory.

### 1. File Naming
The file should be named using the lowercase ISO 3166-1 alpha-2 country code (e.g., `gh.json` for Ghana, `ke.json` for Kenya).

### 2. Data Structure
The JSON should follow this structure:

```json
{
  "GH": {
    "name": "Ghana",
    "states": {
      "GA": {
        "name": "Greater Accra",
        "capital": "Accra",
        "lgas": {
          "Accra Metropolitan": {
            "city": "Accra"
          }
        }
      }
    }
  }
}
```

*   **Top Level Key**: Uppercase ISO country code.
*   **states**: Dictionary of state codes to state objects.
*   **lgas**: Dictionary of LGA names to info objects (currently supports `city`).

### 3. Registering the Country
In `afrogeo/verify.py`, update the `country_map` dictionary in the `verify()` function if you want to support full-name mapping for the new country:

```python
country_map = {
    "nigeria": "ng",
    "ghana": "gh",
    "kenya": "ke",
    # Add your country here
}
```

## Running Tests

Before submitting a pull request, please run the tests:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Documentation Guidelines
If you add new features, please ensure:
- Docstrings are updated (Google/NumPy style).
- Type hints are provided.
- Examples are added to the `examples/` directory if necessary.
