"""Synthetic retail data with optional, known defects.

All data is generated, not real. Output is deterministic for a given seed.
Injected defects sit at fixed row positions, so tests can assert which checks fire.
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from dq.checks import ALLOWED_STATUSES

# Fixed reference date. Using a constant (not today's date) keeps runs reproducible.
REFERENCE_DATE = date(2026, 11, 20)

# Which check each injected defect should trigger. Used by the tests.
EXPECTED_FAILURES_WITH_DEFECTS: frozenset[str] = frozenset(
    {
        "not_null:order_id",
        "unique:order_id",
        "non_negative:amount",
        "allowed_values:status",
        "valid_dates:order_date",
        "referential:customer_id->customer_id",
    }
)


def make_customers(n: int = 50, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "customer_id": [f"C{i:04d}" for i in range(1, n + 1)],
            "name": [f"Synthetic Customer {i}" for i in range(1, n + 1)],
            "country": rng.choice(["IN", "US", "GB", "DE", "AE"], size=n),
        }
    )


def make_orders(
    customers: pd.DataFrame,
    n: int = 500,
    reference: date = REFERENCE_DATE,
    seed: int = 42,
    inject_defects: bool = False,
) -> pd.DataFrame:
    if n < 60:
        raise ValueError("n must be at least 60 so every injected defect has its own row")
    rng = np.random.default_rng(seed)

    days_back = rng.integers(0, 30, size=n)
    days_back[0] = 0  # guarantees a row dated at the reference date, so the clean run is fresh

    orders = pd.DataFrame(
        {
            "order_id": [f"O{i:06d}" for i in range(1, n + 1)],
            "customer_id": rng.choice(customers["customer_id"].to_numpy(), size=n),
            "order_date": [(reference - timedelta(days=int(d))).isoformat() for d in days_back],
            "amount": rng.uniform(5, 500, size=n).round(2),
            "status": rng.choice(ALLOWED_STATUSES, size=n),
        }
    )

    if inject_defects:
        orders.loc[3, "order_id"] = None  # not_null:order_id
        orders.loc[10, "order_id"] = orders.loc[9, "order_id"]  # unique:order_id
        orders.loc[20, "amount"] = -15.0  # non_negative:amount
        orders.loc[30, "status"] = "lost"  # allowed_values:status
        orders.loc[40, "customer_id"] = "C9999"  # referential:customer_id->customer_id
        orders.loc[50, "order_date"] = "2026-02-31"  # valid_dates:order_date (no such date)

    return orders
