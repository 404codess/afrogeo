# Afrogeo

Offline-first African location verification for Python.

Validate country and administrative divisions without an internet connection. Each country defines its own level names (e.g. State/LGA for Nigeria, Province/Municipality for South Africa).

## Installation

```bash
pip install afrogeo
```

## Usage

Afrogeo provides a simple `verify` function that takes a dictionary and returns a `Result` object.

### Basic Example (Nigeria)

```python
from afrogeo import verify

# Lowercase input is fine — output is always canonical casing from the data
data = {
    "country": "nigeria",
    "state": "lagos",
    "lga": "agege"
}

result = verify(data)

if result.valid:
    print(f"Validated: {result.normalized['state']} - {result.normalized['lga']}")
else:
    print(f"Errors: {result.errors}")
```

### Full Validation (including settlement)

```python
data = {
    "country": "NG",        # Supports codes or full names
    "state": "LA",          # Supports division codes
    "lga": "Agege",
    "city": "Agege"         # Optional settlement
}

result = verify(data)
```

### South Africa (starter data)

For South Africa, `state` and `lga` map to province and municipality. Use `city` for a settlement within that municipality.

```python
result = verify({
    "country": "South Africa",
    "state": "Gauteng",  # or province code "GP"
    "lga": "City of Johannesburg Metropolitan Municipality",
    "city": "Sandton",
})
```

Municipality names match official Wikidata labels (see [DATA_SOURCES.md](DATA_SOURCES.md)).

### Normalize helper

`normalize()` runs the same validation as `verify()` and returns the canonical dict (or `{}` on failure):

```python
from afrogeo import normalize

data = normalize({"country": "NG", "state": "LA", "lga": "Agege"})
# data["division_1_name"] -> "Lagos"
# data["division_2_name"] -> "Agege"
# data["state"] / data["lga"]  -> same values (legacy keys)
```

### Generic aliases

You can use country-agnostic keys instead of `state` / `lga` / `city`:

```python
result = verify({
    "country": "NG",
    "division_1": "Lagos",
    "division_2": "Agege",
    "settlement": "Agege"
})
```

Primary keys take precedence when both primary and alias are provided.

## Features

- **Offline-First**: Uses local JSON data for instant verification.
- **Multi-Country Schema**: One file per country with flexible admin level labels.
- **Data Normalization**: Converts codes to full names and standardizes output.
- **Case Insensitive**: All inputs (`country`, `state`, `lga`, `city` and aliases) are matched without regard to case. `"lagos"`, `"LAGOS"`, and `"Lagos"` all validate; normalized output uses canonical casing from the dataset (e.g. `"Lagos"`, not `"lagos"`).
- **Dynamic Loading & Cache Safety**: Loads only the data for the country you are verifying, caching reads safely without risk of dataset mutation.
- **Type Annotated**: Fully typed with PEP 561 (`py.typed`) support for `mypy` and `pyright`.

## API Reference

### `verify(user_input: dict) -> Result`

The `user_input` dictionary accepts:

- `country` (Required): Full name or ISO code.
- `state` (Required): Level-1 division name or code. Alias: `division_1`.
- `lga` (Required): Level-2 division name. Alias: `division_2`.
- `city` (Optional): Settlement name. Alias: `settlement`.

For all countries, `state`, `lga`, and `city` are generic slots (e.g. province, municipality, settlement for South Africa). Check `level_1_label` and `level_2_label` in the normalized output for the country's terminology.

Returns a `Result` object:

- `result.valid` (or `bool(result)`): `True` if valid, `False` otherwise.
- `result.errors`: List of error message strings (empty if valid).
- `result.normalized`: Canonical dict with:
  - **Legacy:** `country_code`, `country`, `state_code`, `state`, `lga`, `city`, `capital`
  - **Generic:** `division_1_code`, `division_1_name`, `division_2_name`, `settlement`, `settlements`
  - **Labels:** `levels`, `level_1_label`, `level_2_label`, `country_name`
- **Dictionary Convenience Methods**:
  - `result["state"]` — Indexing shorthand for `result.normalized["state"]`
  - `result.get("state", default)` — Safe lookup with default
  - `"state" in result` — Membership check
  - `result.to_dict()` — Returns a copy of the normalized dictionary

### `normalize(user_input: dict) -> dict`

Returns `result.normalized` on success, or `{}` if validation fails.

### `Result`

Importable directly from `afrogeo` for type checking and custom handling:

```python
from afrogeo import Result, verify
```

## Contributing

Data is stored in `afrogeo/data/`. See [CONTRIBUTING.md](CONTRIBUTING.md) for the JSON schema and how to add a country.
