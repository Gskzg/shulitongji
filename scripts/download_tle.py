#!/usr/bin/env python3
"""Download TLE/GP data from CelesTrak or Space-Track."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tle_accuracy.download import download_celestrak, download_spacetrack_history


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["celestrak", "spacetrack"], required=True)
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "raw")

    parser.add_argument("--groups", nargs="*", default=None, help="CelesTrak groups, e.g. active geo gps-ops")
    parser.add_argument("--catnr", nargs="*", default=None, help="CelesTrak NORAD catalog numbers")
    parser.add_argument("--format", default="TLE", help="CelesTrak format: TLE, CSV, JSON, ...")

    parser.add_argument("--ids", nargs="*", default=None, help="Space-Track NORAD catalog numbers")
    parser.add_argument("--ids-file", type=Path, help="File with one Space-Track catalog number per line or comma-separated")
    parser.add_argument("--start", help="Space-Track history start date, e.g. 2025-01-01")
    parser.add_argument("--end", help="Space-Track history end date, e.g. 2025-03-31")
    parser.add_argument("--chunk-size", type=int, default=50)
    args = parser.parse_args()

    if args.source == "celestrak":
        groups = args.groups if args.groups is not None else ["active", "geo", "gps-ops"]
        out_dir = args.out / "celestrak" if args.out.name == "raw" else args.out
        paths = download_celestrak(out_dir=out_dir, groups=groups, catalog_numbers=args.catnr, fmt=args.format)
    else:
        ids = _collect_ids(args.ids or [], args.ids_file)
        if not args.start or not args.end:
            parser.error("--start and --end are required for Space-Track history downloads")
        out_dir = args.out / "spacetrack" if args.out.name == "raw" else args.out
        paths = download_spacetrack_history(
            out_dir=out_dir,
            catalog_numbers=ids,
            start_date=args.start,
            end_date=args.end,
            chunk_size=args.chunk_size,
        )

    for path in paths:
        print(path)
    return 0


def _collect_ids(ids: list[str], ids_file: Path | None) -> list[str]:
    collected = list(ids)
    if ids_file:
        text = ids_file.read_text(encoding="utf-8")
        text = text.replace(",", "\n")
        collected.extend(line.strip() for line in text.splitlines() if line.strip())
    return sorted(set(collected), key=lambda item: int(item) if item.isdigit() else item)


if __name__ == "__main__":
    raise SystemExit(main())
