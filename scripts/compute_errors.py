#!/usr/bin/env python3
"""Compute SGP4 forecast errors from historical TLE records."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tle_accuracy.propagation import compute_errors_frame
from tle_accuracy.tle import load_records, records_to_frame


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", nargs="+", type=Path, default=[ROOT / "data" / "raw"], help="Raw TLE files or directories")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "processed" / "errors.csv")
    parser.add_argument("--records-out", type=Path, default=ROOT / "data" / "interim" / "tle_records.csv")
    parser.add_argument("--horizons", nargs="+", type=float, default=[1.0, 3.0, 7.0], help="Forecast horizons in days")
    parser.add_argument("--max-reference-offset-hours", type=float, default=12.0)
    parser.add_argument("--orbit-types", nargs="*", default=["LEO", "MEO", "GEO"], help="Orbit classes to keep")
    parser.add_argument("--min-records-per-object", type=int, default=2)
    args = parser.parse_args()

    records = load_records(args.input)
    records_frame = records_to_frame(records)
    args.records_out.parent.mkdir(parents=True, exist_ok=True)
    records_frame.to_csv(args.records_out, index=False)
    print(f"Loaded {len(records)} TLE records from {len(args.input)} input path(s).")
    print(f"Wrote normalized records: {args.records_out}")

    errors = compute_errors_frame(
        records,
        horizons_days=args.horizons,
        max_reference_offset_hours=args.max_reference_offset_hours,
        orbit_types=set(args.orbit_types) if args.orbit_types else None,
        min_records_per_object=args.min_records_per_object,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    errors.to_csv(args.output, index=False)
    print(f"Computed {len(errors)} forecast-error rows.")
    print(f"Wrote errors: {args.output}")
    if errors.empty:
        print(
            "No error rows were produced. For 1/3/7 day errors you need repeated TLEs per object "
            "from accumulated CelesTrak snapshots or Space-Track gp_history."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
