# Flight Schedule Parser and Query Tool

This repository contains `flight_parser.py`, a command-line tool to parse CSV flight schedules, validate records, produce a JSON database, report parsing errors, and run queries against the resulting database.

Usage

- Parse a single CSV and write `db.json`:

```bash
python3 flight_parser.py -i path/to/file.csv
```

- Parse all CSV files in a directory and write to a custom DB path:

```bash
python3 flight_parser.py -d path/to/folder -o output_db.json
```

- Load an existing DB and run queries from JSON:

```bash
python3 flight_parser.py -j db.json -q queries.json
```

Flags (short forms required):
- `-i PATH` parse a single CSV file
- `-d PATH` parse all `*.csv` files in a folder (combine results)
- `-o PATH` custom output path for `db.json` (default: `db.json`)
- `-j PATH` load existing `db.json` instead of parsing CSVs
- `-q PATH` execute queries from a JSON file on the loaded database
- `-h` show help

Notes
- CSV lines starting with `#` are treated as comments and written to `errors.txt` with explanation `Comment`.
- Blank lines are skipped.
- Each non-comment line must contain exactly 6 comma-separated fields: `flight_id,origin,destination,departure_datetime,arrival_datetime,price`.
- Datetime format: `YYYY-MM-DD HH:MM` (validated with Python's `datetime.strptime`).
- `db.json` is pretty-printed with `indent=2` and keys sorted.

Query output

Queries are provided as a JSON object or an array of objects. The response file is written as:

```
response_12345_John_Doe_<YYYYMMDD_HHMM>.json
```

which contains an array of objects `{ "query": ..., "matches": [...] }`.

Running tests

- Install `pytest` (only for running tests):

```bash
python3 -m pip install --user pytest
```

- Run tests:

```bash
pytest -q
```

Contact

If you want changes or extra features (filters, sorting, CSV quoting support), tell me and I'll iterate.
