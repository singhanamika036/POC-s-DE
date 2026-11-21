"""Data-quality checks. Plain Python rules: no LLM is involved.

Every check returns a CheckResult with one of three statuses:
- ``pass``: the rule was evaluated and held.
- ``fail``: the rule was evaluated and found a problem.
- ``skipped``: the rule could not be evaluated (for example, a column is missing).
  A skipped check is not a pass, and it must not be reported as one.
"""

from __future__ import annotations

import statistics
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from datetime import date

import pandas as pd

PASS = "pass"
FAIL = "fail"
SKIPPED = "skipped"

REQUIRED_ORDER_COLUMNS: tuple[str, ...] = (
    "order_id",
    "customer_id",
    "order_date",
    "amount",
    "status",
)
REQUIRED_CUSTOMER_COLUMNS: tuple[str, ...] = ("customer_id", "name", "country")
ALLOWED_STATUSES: tuple[str, ...] = ("placed", "shipped", "delivered", "cancelled", "returned")


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    failing_rows: int = 0
    detail: str = ""

    @property
    def passed(self) -> bool:
        return self.status == PASS

    def to_dict(self) -> dict:
        return asdict(self)


def _pass(name: str, detail: str = "") -> CheckResult:
    return CheckResult(name, PASS, 0, detail)


def _fail(name: str, failing_rows: int, detail: str) -> CheckResult:
    return CheckResult(name, FAIL, int(failing_rows), detail)


def _skip(name: str, detail: str) -> CheckResult:
    return CheckResult(name, SKIPPED, 0, detail)


def check_schema(df: pd.DataFrame, required: Sequence[str], name: str = "schema") -> CheckResult:
    missing = [c for c in required if c not in df.columns]
    if missing:
        return _fail(name, 0, f"missing columns: {', '.join(missing)}")
    return _pass(name)


def check_not_null(df: pd.DataFrame, column: str) -> CheckResult:
    name = f"not_null:{column}"
    if column not in df.columns:
        return _skip(name, "column missing")
    values = df[column]
    blank = values.isna() | values.astype(str).str.strip().eq("")
    n = int(blank.sum())
    return _pass(name) if n == 0 else _fail(name, n, f"{n} null or blank value(s)")


def check_unique(df: pd.DataFrame, column: str) -> CheckResult:
    name = f"unique:{column}"
    if column not in df.columns:
        return _skip(name, "column missing")
    # keep=False marks every member of a duplicate group, so both rows are counted.
    dup = int(df[column].dropna().duplicated(keep=False).sum())
    return _pass(name) if dup == 0 else _fail(name, dup, f"{dup} rows share a duplicated value")


def check_non_negative(df: pd.DataFrame, column: str) -> CheckResult:
    name = f"non_negative:{column}"
    if column not in df.columns:
        return _skip(name, "column missing")
    numeric = pd.to_numeric(df[column], errors="coerce")
    negative = int((numeric < 0).sum())
    non_numeric = int((numeric.isna() & df[column].notna()).sum())
    bad = negative + non_numeric
    if bad == 0:
        return _pass(name)
    return _fail(name, bad, f"{negative} negative and {non_numeric} non-numeric value(s)")


def check_allowed_values(df: pd.DataFrame, column: str, allowed: Iterable[str]) -> CheckResult:
    name = f"allowed_values:{column}"
    if column not in df.columns:
        return _skip(name, "column missing")
    allowed_set = set(allowed)
    values = df[column].dropna()
    bad = int((~values.isin(allowed_set)).sum())
    return _pass(name) if bad == 0 else _fail(name, bad, f"{bad} value(s) outside the allowed set")


def check_valid_dates(df: pd.DataFrame, column: str) -> CheckResult:
    name = f"valid_dates:{column}"
    if column not in df.columns:
        return _skip(name, "column missing")
    parsed = pd.to_datetime(df[column], errors="coerce", format="ISO8601")
    bad = int((parsed.isna() & df[column].notna()).sum())
    return _pass(name) if bad == 0 else _fail(name, bad, f"{bad} unparseable date value(s)")


def check_referential(child: pd.DataFrame, fk: str, parent: pd.DataFrame, pk: str) -> CheckResult:
    name = f"referential:{fk}->{pk}"
    if fk not in child.columns or pk not in parent.columns:
        return _skip(name, "key column missing")
    orphans = int((~child[fk].dropna().isin(parent[pk].dropna())).sum())
    if orphans == 0:
        return _pass(name)
    return _fail(name, orphans, f"{orphans} row(s) reference a missing {pk}")


def check_freshness(
    df: pd.DataFrame, column: str, reference: date, max_age_days: int
) -> CheckResult:
    name = f"freshness:{column}"
    if column not in df.columns:
        return _skip(name, "column missing")
    parsed = pd.to_datetime(df[column], errors="coerce", format="ISO8601").dropna()
    if parsed.empty:
        return _fail(name, 0, "no valid dates, so freshness cannot be assessed")
    latest = parsed.max().date()
    age_days = (reference - latest).days
    if age_days <= max_age_days:
        return _pass(name, f"latest={latest}, age={age_days}d")
    return _fail(name, 0, f"latest={latest} is {age_days} days before reference {reference}")


def check_row_count_band(
    count: int, history: Sequence[int] | None, z_max: float = 3.0
) -> CheckResult:
    name = "row_count_band"
    n = 0 if history is None else len(history)
    if n < 3:
        return _skip(name, f"need at least 3 historical counts, got {n}")
    mean = statistics.fmean(history)
    sd = statistics.stdev(history)
    lower, upper = mean - z_max * sd, mean + z_max * sd
    if lower <= count <= upper:
        return _pass(name, f"count={count} within [{lower:.0f}, {upper:.0f}]")
    return _fail(name, 0, f"count={count} outside [{lower:.0f}, {upper:.0f}]")


def run_checks(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    reference: date,
    history_counts: Sequence[int] | None = None,
    max_age_days: int = 2,
) -> list[CheckResult]:
    """Run every check and return the results in a stable order.

    Checks never raise on bad input. A missing column produces a ``skipped`` result.
    """
    results: list[CheckResult] = []

    results.append(check_schema(orders, REQUIRED_ORDER_COLUMNS, "orders.schema"))
    results.append(check_not_null(orders, "order_id"))
    results.append(check_not_null(orders, "customer_id"))
    results.append(check_not_null(orders, "order_date"))
    results.append(check_unique(orders, "order_id"))
    results.append(check_non_negative(orders, "amount"))
    results.append(check_allowed_values(orders, "status", ALLOWED_STATUSES))
    results.append(check_valid_dates(orders, "order_date"))
    results.append(check_freshness(orders, "order_date", reference, max_age_days))
    results.append(check_referential(orders, "customer_id", customers, "customer_id"))
    results.append(check_row_count_band(len(orders), history_counts))

    results.append(check_schema(customers, REQUIRED_CUSTOMER_COLUMNS, "customers.schema"))
    results.append(check_not_null(customers, "customer_id"))
    results.append(check_unique(customers, "customer_id"))

    return results


def summarise(results: Sequence[CheckResult]) -> dict[str, int]:
    counts = {PASS: 0, FAIL: 0, SKIPPED: 0}
    for r in results:
        counts[r.status] += 1
    return counts
