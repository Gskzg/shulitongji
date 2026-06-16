#!/usr/bin/env python3
"""Run summary statistics, bootstrap intervals, covariance estimates, and tests."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd
from pandas.errors import EmptyDataError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tle_accuracy.covariance import empirical_covariance_table, identity_process_noise_table
from tle_accuracy.propagation import ERROR_COLUMNS
from tle_accuracy.stats import bootstrap_table, fit_growth_laws, group_tests, summarize_errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--errors", type=Path, default=ROOT / "data" / "processed" / "errors.csv")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "outputs" / "tables")
    parser.add_argument("--value-col", default="position_error_km")
    parser.add_argument("--n-bootstrap", type=int, default=5000)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--min-test-n", type=int, default=5)
    args = parser.parse_args()

    if not args.errors.exists():
        raise FileNotFoundError(args.errors)
    try:
        errors = pd.read_csv(args.errors)
    except EmptyDataError:
        errors = pd.DataFrame(columns=ERROR_COLUMNS)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if errors.empty:
        print("errors.csv is empty; no analysis tables were generated.")
        return 0

    summary = summarize_errors(errors, args.value_col)
    ci = bootstrap_table(errors, args.value_col, n_bootstrap=args.n_bootstrap, confidence=args.confidence)
    growth = fit_growth_laws(summary, "median_km")
    omnibus, pairwise = group_tests(errors, args.value_col, min_n=args.min_test_n)
    cov_ric = empirical_covariance_table(errors, frame="ric")
    cov_teme = empirical_covariance_table(errors, frame="teme")
    q_ric = identity_process_noise_table(cov_ric)
    q_teme = identity_process_noise_table(cov_teme)

    outputs = {
        "summary.csv": summary,
        "bootstrap_ci.csv": ci,
        "growth_fit.csv": growth,
        "group_tests.csv": omnibus,
        "pairwise_mannwhitney_holm.csv": pairwise,
        "covariance_ric.csv": cov_ric,
        "covariance_teme.csv": cov_teme,
        "process_noise_identity_ric.csv": q_ric,
        "process_noise_identity_teme.csv": q_teme,
    }
    for filename, table in outputs.items():
        path = args.out_dir / filename
        table.to_csv(path, index=False)
        print(f"{filename}: {len(table)} row(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
