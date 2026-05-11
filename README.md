# Afrogeo

Offline-first African location verification for Python.

Validate country, state, city, and district (LGA) without an internet connection.

## Installation

```bash
pip install afrogeo
```

## Usage

Afrogeo provides a simple `verify` function that takes a dictionary and returns a `Result` object.

### Basic Example

```python
from afrogeo import verify

data = {
    "country": "Nigeria",
    "state": "Lagos",
    "lga": "Agege"
}

result = verify(data)

if result.valid:
    print(f"Validated: {result.normalized['state']} - {result.normalized['lga']}")
else:
    print(f"Errors: {result.errors}")
```

### Full Validation (including City)

```python
data = {
    "country": "NG",        # Supports codes or full names
    "state": "LA",          # Supports state codes
    "lga": "Agege",
    "city": "Agege"         # Optional
}

result = verify(data)
```

## Features

- **Offline-First**: Uses local JSON data for instant verification.
- **Data Normalization**: Automatically converts codes to full names and vice-versa.
- **Case Insensitive**: Accepts "LAGOS", "lagos", or "Lagos".
- **Dynamic Loading**: Loads only the data for the country you are verifying.

## API Reference

### `verify(user_input: dict) -> Result`

The `user_input` dictionary accepts:
- `country` (Required): Full name or ISO code.
- `state` (Required): Full name or code.
- `lga` (Required): Local Government Area name.
- `city` (Optional): City name.

Returns a `Result` object with:
- `valid`: Boolean.
- `errors`: List of strings (empty if valid).
- `normalized`: Dictionary of standard location names and codes.

## Contributing

Data is stored in `afrogeo/data/`. To add a new country, create a `<country_code>.json` file following the existing structure.
