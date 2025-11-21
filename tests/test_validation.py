import pytest
from flight_parser import validate_record


def test_valid_record():
    fields = ["AB12", "JFK", "LAX", "2025-12-01 09:00", "2025-12-01 12:00", "199.99"]
    errs = validate_record(fields)
    assert errs == []


def test_invalid_flight_id_and_origin():
    fields = ["A!", "jkf", "LAX", "2025-12-01 09:00", "2025-12-01 12:00", "199.99"]
    errs = validate_record(fields)
    assert "Invalid flight_id" in errs
    assert "Invalid origin" in errs


def test_invalid_datetimes_and_arrival_before_dep():
    fields = ["CD34", "SFO", "LAX", "2025/12/01 09:00", "2025-12-01 08:00", "100"]
    errs = validate_record(fields)
    assert "Invalid departure_datetime" in errs or "Arrival not after departure" in errs


def test_invalid_price():
    fields = ["EF56", "BOS", "MIA", "2025-11-10 15:00", "2025-11-10 16:00", "-10"]
    errs = validate_record(fields)
    assert "Invalid price" in errs
