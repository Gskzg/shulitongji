#!/usr/bin/env python3
"""Generate publication-ready figures from forecast-error outputs."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd
from pandas.errors import EmptyDataError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tle_accuracy.plots import make_all_plots
from tle_accuracy.propagation import ERROR_COLUMNS


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--errors", type=Path, default=ROOT / "data" / "processed" / "errors.csv")
    parser.add_argument("--ci", type=Path, default=ROOT / "outputs" / "tables" / "bootstrap_ci.csv")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "outputs" / "figures")
    args = parser.parse_args()

    if not args.errors.exists():
        raise FileNotFoundError(args.errors)
    try:
        errors = pd.read_csv(args.errors)
    except EmptyDataError:
        errors = pd.DataFrame(columns=ERROR_COLUMNS)
    ci = pd.read_csv(args.ci) if args.ci.exists() else None
    paths = make_all_plots(errors, args.out_dir, ci)
    for path in paths:
        print(path)
    if not paths:
        print("No plots generated because the input errors table is empty.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
