# Contributing to Afrogeo

Thank you for your interest in improving Afrogeo! This project relies on local JSON data to provide offline location verification across Africa.

## How to Add a New Country

Create a JSON file in the `afrogeo/data/` directory.

### 1. File Naming

Use the lowercase ISO 3166-1 alpha-2 country code (e.g., `ng.json`, `za.json`).

### 2. Data Structure

Each file is one country document at the root:

```json
{
  "country_code": "NG",
  "country_name": "Nigeria",
  "levels": {
    "level_1": "State",
    "level_2": "LGA"
  },
  "divisions": {
    "LA": {
      "name": "Lagos",
      "capital": "Ikeja",
      "children": {
        "Agege": {
          "settlements": ["Agege"]
        }
      }
    }
  }
}
```

South Africa example (different level labels):

```json
{
  "country_code": "ZA",
  "country_name": "South Africa",
  "levels": {
    "level_1": "Province",
    "level_2": "Municipality"
  },
  "divisions": {
    "GT": {
      "name": "Gauteng",
      "children": {
        "City of Johannesburg": {
          "settlements": ["Johannesburg", "Sandton", "Soweto"]
        }
      }
    }
  }
}
```

**Fields:**

- `country_code` / `country_name`: ISO code and display name (used for lookup).
- `levels`: Human-readable labels for level 1 and level 2 only.
- `divisions`: Level-1 units keyed by short code.
- `divisions.*.children`: Level-2 units keyed by name.
- `divisions.*.children.*.settlements`: List of settlement names (use `[]` if none).

No code changes are required to register a country: `verify()` discovers countries by scanning `afrogeo/data/*.json`.

### 3. Migrating Old Format

If you have legacy nested JSON (`"NG": { "states": ... }`), run:

```bash
python scripts/migrate_country_json.py path/to/file.json
```

## Rebuilding South Africa (`za.json`)

South Africa data is generated from Wikidata + ISO province codes:

```bash
# Municipalities + Wikidata settlements (default)
python scripts/build_za_data.py

# Skip settlement fetch (faster, municipalities only)
python scripts/build_za_data.py --no-fetch-settlements
```

See [DATA_SOURCES.md](DATA_SOURCES.md) for attribution and source details.

## Normalizing Country Data

After editing JSON files, run the data normalizer to sort keys, trim strings, and dedupe settlements:

```bash
python scripts/normalize_country_data.py
```

## Running Tests

```bash
pip install -e ".[dev]"
pytest
```

## Documentation Guidelines

If you add new features, please ensure:

- Docstrings are updated.
- Examples are added to the `examples/` directory when helpful.
