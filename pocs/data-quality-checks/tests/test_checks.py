"""Tests for the data-quality checks.

Strategy:
- Clean synthetic data must pass every check.
- Each injected defect must fire exactly the check it targets, and no other.
- Failure paths (missing columns, empty input, stale data, bad values) must return
  a fail or skipped result, never raise.
"""

from __future__ import annotations

import json
from datetime import timedelta

import pandas as pd
import pytest

from dq.checks import (
    ALLOWED_STATUSES,
    FAIL,
    PASS,
    SKIPPED,
    check_allowed_values,
    check_freshness,
    check_non_negative,
    check_not_null,
    check_row_count_band,
    check_unique,
    check_valid_dates,
    run_checks,
    summarise,
)
from dq.run import main
from dq.synthetic import (
    EXPECTED_FAILURES_WITH_DEFECTS,
    REFERENCE_DATE,
    make_customers,
    make_orders,
)

HISTORY = [480, 510, 495, 502, 488]


@pytest.fixture(scope="module")
def customers() -> pd.DataFrame:
    return make_customers(seed=42)


@pytest.fixture(scope="module")
def clean_orders(customers) -> pd.DataFrame:
    return make_orders(customers, n=500, seed=42, inject_defects=False)


@pytest.fixture(scope="module")
def defective_orders(customers) -> pd.DataFrame:
    return make_orders(customers, n=500, seed=42, inject_defects=True)


def _by_name(results):
    return {r.name: r for r in results}


# --- Clean data --------------------------------------------------------------


def test_clean_data_passes_every_check(clean_orders, customers):
    results = run_checks(clean_orders, customers, REFERENCE_DATE, history_counts=HISTORY)
    failing = [r for r in results if r.status != PASS]
    assert failing == [], f"unexpected non-pass results: {failing}"
    assert summarise(results) == {PASS: len(results), FAIL: 0, SKIPPED: 0}


# --- Injected defects ---------------------------------------------------------


def test_injected_defects_fire_exactly_the_expected_checks(defective_orders, customers):
    results = run_checks(defective_orders, customers, REFERENCE_DATE, history_counts=HISTORY)
    failing = {r.name for r in results if r.status == FAIL}
    assert failing == set(EXPECTED_FAILURES_WITH_DEFECTS)


@pytest.mark.parametrize(
    "check_name, expected_rows",
    [
        ("not_null:order_id", 1),
        ("unique:order_id", 2),  # both members of the duplicate pair are counted
        ("non_negative:amount", 1),
        ("allowed_values:status", 1),
        ("valid_dates:order_date", 1),
        ("referential:customer_id->customer_id", 1),
    ],
)
def test_injected_defect_row_counts(defective_orders, customers, check_name, expected_rows):
    results = _by_name(run_checks(defective_orders, customers, REFERENCE_DATE, HISTORY))
    assert results[check_name].status == FAIL
    assert results[check_name].failing_rows == expected_rows


def test_defect_free_checks_still_pass_when_defects_injected(defective_orders, customers):
    results = _by_name(run_checks(defective_orders, customers, REFERENCE_DATE, HISTORY))
    # Freshness and the volume band are unaffected by the injected row-level defects.
    assert results["freshness:order_date"].status == PASS
    assert results["row_count_band"].status == PASS
    assert results["not_null:customer_id"].status == PASS


# --- Failure paths -------------------------------------------------------------


def test_missing_column_is_skipped_not_raised(clean_orders, customers):
    broken = clean_orders.drop(columns=["amount"])
    results = _by_name(run_checks(broken, customers, REFERENCE_DATE, HISTORY))
    assert results["orders.schema"].status == FAIL
    assert "amount" in results["orders.schema"].detail
    assert results["non_negative:amount"].status == SKIPPED


def test_empty_orders_do_not_crash(customers):
    empty = pd.DataFrame(columns=["order_id", "customer_id", "order_date", "amount", "status"])
    results = _by_name(run_checks(empty, customers, REFERENCE_DATE, HISTORY))
    # Vacuously true on zero rows.
    assert results["not_null:order_id"].status == PASS
    # But there is no date to assess, so freshness must fail, not pass.
    assert results["freshness:order_date"].status == FAIL
    assert "no valid dates" in results["freshness:order_date"].detail


def test_stale_data_fails_freshness(clean_orders):
    late_reference = REFERENCE_DATE + timedelta(days=10)
    result = check_freshness(clean_orders, "order_date", late_reference, max_age_days=2)
    assert result.status == FAIL
    assert "days before reference" in result.detail


def test_all_invalid_dates_fail_freshness_not_pass():
    df = pd.DataFrame({"order_date": ["not-a-date", "31/31/2026"]})
    assert check_freshness(df, "order_date", REFERENCE_DATE, 2).status == FAIL


def test_blank_strings_count_as_null():
    df = pd.DataFrame({"order_id": ["O1", "   ", None]})
    result = check_not_null(df, "order_id")
    assert result.status == FAIL
    assert result.failing_rows == 2


def test_non_numeric_amount_is_counted_as_bad():
    df = pd.DataFrame({"amount": [10.0, "abc", -1.0]})
    result = check_non_negative(df, "amount")
    assert result.status == FAIL
    assert result.failing_rows == 2  # one non-numeric, one negative


def test_unique_ignores_nulls():
    df = pd.DataFrame({"order_id": [None, None, "O1"]})
    assert check_unique(df, "order_id").status == PASS


def test_allowed_values_flags_unknown_status():
    df = pd.DataFrame({"status": [ALLOWED_STATUSES[0], "lost"]})
    result = check_allowed_values(df, "status", ALLOWED_STATUSES)
    assert result.status == FAIL
    assert result.failing_rows == 1


def test_valid_dates_accepts_iso_and_flags_impossible_day():
    df = pd.DataFrame({"order_date": ["2026-11-01", "2026-02-31"]})
    result = check_valid_dates(df, "order_date")
    assert result.status == FAIL
    assert result.failing_rows == 1


# --- Row-count band ----------------------------------------------------------


def test_row_count_band_within_history_passes():
    assert check_row_count_band(500, HISTORY).status == PASS


def test_row_count_band_outside_history_fails():
    assert check_row_count_band(5000, HISTORY).status == FAIL


def test_row_count_band_needs_at_least_three_points():
    assert check_row_count_band(500, [500, 500]).status == SKIPPED
    assert check_row_count_band(500, None).status == SKIPPED


def test_row_count_band_zero_variance_is_exact():
    assert check_row_count_band(500, [500, 500, 500]).status == PASS
    assert check_row_count_band(501, [500, 500, 500]).status == FAIL


# --- Generator and CLI ----------------------------------------------------------


def test_generator_is_deterministic(customers):
    a = make_orders(customers, n=200, seed=7, inject_defects=True)
    b = make_orders(customers, n=200, seed=7, inject_defects=True)
    pd.testing.assert_frame_equal(a, b)


def test_generator_rejects_too_few_rows(customers):
    with pytest.raises(ValueError):
        make_orders(customers, n=10)


def test_cli_clean_run_exits_zero_and_writes_report(tmp_path):
    out = tmp_path / "report.json"
    assert main(["--out", str(out)]) == 0
    report = json.loads(out.read_text())
    assert report["summary"]["fail"] == 0
    assert report["summary"]["skipped"] == 0
    assert report["summary"]["pass"] == len(report["results"]) > 0
    assert report["data"] == "synthetic"
    assert report["inject_defects"] is False


def test_cli_defect_run_exits_one(tmp_path):
    out = tmp_path / "report.json"
    assert main(["--inject-defects", "--out", str(out)]) == 1
    report = json.loads(out.read_text())
    failing = {r["name"] for r in report["results"] if r["status"] == FAIL}
    assert failing == set(EXPECTED_FAILURES_WITH_DEFECTS)
