#!/usr/bin/env python3
"""
flight_parser.py

University final assignment: Flight Schedule Parser and Query Tool

This script parses CSV flight schedules, validates records, writes a
database `db.json`, reports errors to `errors.txt`, and supports running
queries against the loaded database.

Usage flags (short forms only):
  -i PATH   parse a single CSV file
  -d PATH   parse all *.csv files in a folder (combine results)
  -o PATH   custom output path for db.json (default: db.json)
  -j PATH   load existing db.json instead of parsing CSVs
  -q PATH   execute queries from a JSON file on the loaded database
  -h        show help

No external dependencies; standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import glob
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional


STUDENT_ID = "241ADB"
STUDENT_NAME = "Dev"
STUDENT_LASTNAME = "Talati"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments using argparse.

    Flags (short forms required): -i, -d, -o, -j, -q, -h
    """
    parser = argparse.ArgumentParser(description="Flight Schedule Parser and Query Tool")
    parser.add_argument("-i", dest="input_file", help="parse a single CSV file", metavar="PATH")
    parser.add_argument("-d", dest="input_dir", help="parse all *.csv files in a folder (combine results)", metavar="PATH")
    parser.add_argument("-o", dest="output_db", help="custom output path for db.json (default: db.json)", metavar="PATH")
    parser.add_argument("-j", dest="json_db", help="load existing db.json instead of parsing CSVs", metavar="PATH")
    parser.add_argument("-q", dest="query_file", help="execute queries from a JSON file on the loaded database", metavar="PATH")
    return parser.parse_args()


def validate_record(fields: List[str]) -> List[str]:
    """Validate a list of 6 fields according to assignment rules.

    Returns a list of human-readable error messages (empty if valid).
    Validation order is important and followed exactly here.
    - flight_id: ^[A-Za-z0-9]{2,8}$
    - origin, destination: ^[A-Z]{3}$
    - departure_datetime, arrival_datetime: '%Y-%m-%d %H:%M' and valid
    - arrival strictly later than departure
    - price: positive float (> 0.0)
    """
    errors: List[str] = []
    # fields expected: flight_id, origin, destination, departure_datetime, arrival_datetime, price
    flight_id, origin, destination, dep_dt, arr_dt, price = fields

    # flight_id
    import re

    if not re.match(r"^[A-Za-z0-9]{2,8}$", flight_id):
        errors.append("Invalid flight_id")

    # origin and destination
    if not re.match(r"^[A-Z]{3}$", origin):
        errors.append("Invalid origin")
    if not re.match(r"^[A-Z]{3}$", destination):
        errors.append("Invalid destination")

    # departure and arrival datetimes
    dt_format = "%Y-%m-%d %H:%M"
    dep_dt_obj = None
    arr_dt_obj = None
    try:
        dep_dt_obj = datetime.strptime(dep_dt, dt_format)
    except Exception:
        errors.append("Invalid departure_datetime")

    try:
        arr_dt_obj = datetime.strptime(arr_dt, dt_format)
    except Exception:
        errors.append("Invalid arrival_datetime")

    # if both parsed, check arrival > departure
    if dep_dt_obj is not None and arr_dt_obj is not None:
        if not (arr_dt_obj > dep_dt_obj):
            errors.append("Arrival not after departure")

    # price positive float
    try:
        price_val = float(price)
        if not (price_val > 0.0):
            errors.append("Invalid price")
    except Exception:
        errors.append("Invalid price")

    return errors


def parse_csv_file(path: str, start_line_no: int = 1) -> Tuple[List[Dict[str, str]], List[Tuple[int, str, str]], int]:
    """Parse a single CSV file and return valid flights and errors.

    Returns (valid_flights, errors, next_line_no).
    - valid_flights: list of dicts for valid lines (datetimes kept as strings)
    - errors: list of tuples (line_number, original_line, explanation)
    - next_line_no: integer for the next line number after processing (useful for combined files)

    Comment lines (starting with '#') are included in `errors` with explanation 'Comment'.
    Blank lines are skipped and not reported.
    """
    valid: List[Dict[str, str]] = []
    errors: List[Tuple[int, str, str]] = []
    ln = start_line_no

    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.rstrip("\n")
                stripped = line.strip()
                # skip blank lines
                if stripped == "":
                    ln += 1
                    continue

                # comment lines: include in output with original content
                if stripped.startswith("#"):
                    errors.append((ln, line, "Comment"))
                    ln += 1
                    continue

                # split CSV by comma (assume no quoted commas)
                parts = [p.strip() for p in line.split(",")]
                if len(parts) != 6:
                    errors.append((ln, line, "Invalid number of fields"))
                    ln += 1
                    continue

                # validate
                issues = validate_record(parts)
                if issues:
                    errors.append((ln, line, ", ".join(issues)))
                else:
                    flight = {
                        "flight_id": parts[0],
                        "origin": parts[1],
                        "destination": parts[2],
                        "departure_datetime": parts[3],
                        "arrival_datetime": parts[4],
                        "price": parts[5],
                    }
                    valid.append(flight)
                ln += 1
    except FileNotFoundError:
        raise
    return valid, errors, ln


def write_errors_txt(errors: List[Tuple[int, str, str]], path: str = "errors.txt") -> None:
    """Write errors to `errors.txt` with the required format.

    Format per line: Line X: ORIGINAL_LINE → human-readable explanation
    Multiple issues in explanation are separated by ", ".
    """
    try:
        with open(path, "w", encoding="utf-8") as fh:
            for ln, original, explanation in errors:
                fh.write(f"Line {ln}: {original} → {explanation}\n")
    except Exception as e:
        print(f"Error writing errors file '{path}': {e}", file=sys.stderr)
        raise


def write_db_json(flights: List[Dict[str, str]], path: str = "db.json") -> None:
    """Write flights list to JSON file (pretty, indent=2, sorted keys)."""
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(flights, fh, indent=2, sort_keys=True)
    except Exception as e:
        print(f"Error writing DB file '{path}': {e}", file=sys.stderr)
        raise


def load_db_json(path: str) -> List[Dict[str, Any]]:
    """Load existing db.json and return the flight list."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            if not isinstance(data, list):
                raise ValueError("DB JSON must be a list of flight objects")
            return data
    except Exception:
        raise


def load_queries(path: str) -> List[Dict[str, Any]]:
    """Load queries from a JSON file. Accepts a single object or an array."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            if isinstance(data, dict):
                return [data]
            if isinstance(data, list):
                return data
            raise ValueError("Query JSON must be an object or an array of objects")
    except Exception:
        raise


def flight_matches_query(f: Dict[str, Any], q: Dict[str, Any]) -> bool:
    """Return True if flight `f` matches the query `q`.

    Supported filters (AND-ed together):
      - flight_id, origin, destination: exact string match
      - price: <= given value
      - departure_datetime: departure >= given datetime (string compare okay)
      - arrival_datetime: arrival <= given datetime
    """
    # exact matches
    for key in ("flight_id", "origin", "destination"):
        if key in q:
            if f.get(key) != q[key]:
                return False

    # price <=
    if "price" in q:
        try:
            qprice = float(q["price"])
            if float(f.get("price", "0")) > qprice:
                return False
        except Exception:
            # invalid query price value -> treat as no match
            return False

    # departure_datetime >=
    if "departure_datetime" in q:
        if f.get("departure_datetime") < q["departure_datetime"]:
            return False

    # arrival_datetime <=
    if "arrival_datetime" in q:
        if f.get("arrival_datetime") > q["arrival_datetime"]:
            return False

    return True


def run_queries_and_write_response(flights: List[Dict[str, Any]], queries: List[Dict[str, Any]]) -> str:
    """Run queries against `flights` and write response file.

    Returns the path to the created response file.
    """
    results: List[Dict[str, Any]] = []
    for q in queries:
        matches = [f for f in flights if flight_matches_query(f, q)]
        results.append({"query": q, "matches": matches})

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"response_{STUDENT_ID}_{STUDENT_NAME}_{STUDENT_LASTNAME}_{timestamp}.json"
    try:
        with open(filename, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2, sort_keys=True)
    except Exception as e:
        print(f"Error writing response file '{filename}': {e}", file=sys.stderr)
        raise
    return filename


def main() -> None:
    """Main entry point handling CLI and orchestrating behavior.

    Priority: if `-j` is provided, load DB from JSON and skip parsing.
    If `-q` used without parsed/loaded DB -> error.
    """
    args = parse_args()

    # determine db output path
    db_path = args.output_db if args.output_db else "db.json"

    flights: List[Dict[str, Any]] = []
    all_errors: List[Tuple[int, str, str]] = []

    # If -j provided, load DB and skip parsing
    if args.json_db:
        try:
            flights = load_db_json(args.json_db)
        except FileNotFoundError:
            print(f"JSON DB file not found: {args.json_db}", file=sys.stderr)
            sys.exit(2)
        except Exception as e:
            print(f"Failed to load JSON DB '{args.json_db}': {e}", file=sys.stderr)
            sys.exit(2)
    else:
        # parse CSVs if any parsing args provided
        had_parsing = False
        next_ln = 1
        if args.input_file:
            had_parsing = True
            if not os.path.isfile(args.input_file):
                print(f"Input file not found: {args.input_file}", file=sys.stderr)
                sys.exit(2)
            try:
                v, e, next_ln = parse_csv_file(args.input_file, start_line_no=next_ln)
                flights.extend(v)
                all_errors.extend(e)
            except Exception as e:
                print(f"Error parsing file '{args.input_file}': {e}", file=sys.stderr)
                sys.exit(2)

        if args.input_dir:
            had_parsing = True
            if not os.path.isdir(args.input_dir):
                print(f"Input directory not found: {args.input_dir}", file=sys.stderr)
                sys.exit(2)
            # find all *.csv files (non-recursive)
            pattern = os.path.join(args.input_dir, "*.csv")
            files = sorted(glob.glob(pattern))
            for fpath in files:
                try:
                    v, e, next_ln = parse_csv_file(fpath, start_line_no=next_ln)
                    flights.extend(v)
                    all_errors.extend(e)
                except Exception as e:
                    print(f"Error parsing file '{fpath}': {e}", file=sys.stderr)
                    sys.exit(2)

        # if no parsing and no -j and -q used, error per assignment
        if args.query_file and not had_parsing and not args.json_db:
            print("Error: -q used without loading a DB (-j) or parsing CSVs (-i/-d)", file=sys.stderr)
            sys.exit(2)

        # write DB JSON (only if we parsed files)
        try:
            write_db_json(flights, db_path)
        except Exception:
            sys.exit(2)

    # write errors.txt (if we parsed; if -j used there are no parsing errors)
    try:
        # Only write errors from parsing stage; if -j used, no errors to write.
        if all_errors:
            write_errors_txt(all_errors, path="errors.txt")
    except Exception:
        sys.exit(2)

    # handle queries if requested
    if args.query_file:
        # ensure we have flights loaded (either via -j or parsing)
        if not flights:
            print("No flights loaded to run queries against", file=sys.stderr)
            sys.exit(2)
        try:
            queries = load_queries(args.query_file)
        except FileNotFoundError:
            print(f"Query file not found: {args.query_file}", file=sys.stderr)
            sys.exit(2)
        except Exception as e:
            print(f"Failed to load queries '{args.query_file}': {e}", file=sys.stderr)
            sys.exit(2)

        try:
            resp = run_queries_and_write_response(flights, queries)
            print(f"Wrote response file: {resp}")
        except Exception:
            sys.exit(2)


if __name__ == "__main__":
    main()
