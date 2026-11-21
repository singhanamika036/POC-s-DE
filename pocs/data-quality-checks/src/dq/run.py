"""Command-line runner: generate synthetic data, run the checks, write a JSON report.

Exit code: 0 if every check passed; 1 if any check failed or was skipped.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dq.checks import run_checks, summarise
from dq.synthetic import REFERENCE_DATE, make_customers, make_orders

DEFAULT_HISTORY = (480, 510, 495, 502, 488)


def _parse_history(text: str) -> list[int]:
    return [int(x) for x in text.split(",") if x.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run data-quality checks on synthetic data.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--rows", type=int, default=500)
    parser.add_argument("--inject-defects", action="store_true", help="add known defects")
    parser.add_argument(
        "--history",
        type=_parse_history,
        default=list(DEFAULT_HISTORY),
        help="comma-separated historical row counts for the volume check",
    )
    parser.add_argument("--out", type=Path, default=Path("output/dq_report.json"))
    args = parser.parse_args(argv)

    customers = make_customers(seed=args.seed)
    orders = make_orders(
        customers,
        n=args.rows,
        reference=REFERENCE_DATE,
        seed=args.seed,
        inject_defects=args.inject_defects,
    )
    results = run_checks(orders, customers, REFERENCE_DATE, history_counts=args.history)
    counts = summarise(results)

    report = {
        "data": "synthetic",
        "seed": args.seed,
        "inject_defects": args.inject_defects,
        "reference_date": REFERENCE_DATE.isoformat(),
        "orders_rows": len(orders),
        "customers_rows": len(customers),
        "summary": counts,
        "results": [r.to_dict() for r in results],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2))

    width = max(len(r.name) for r in results)
    for r in results:
        line = f"{r.status.upper():8} {r.name:<{width}}  {r.detail}"
        print(line.rstrip())
    print(
        f"\n{counts['pass']} passed, {counts['fail']} failed, {counts['skipped']} skipped "
        f"-> report: {args.out}"
    )
    return 0 if counts["fail"] == 0 and counts["skipped"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
