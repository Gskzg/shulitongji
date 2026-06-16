#!/usr/bin/env python3
"""Run compute, analysis, and plotting steps in order."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", nargs="+", type=Path, default=[ROOT / "data" / "raw"])
    parser.add_argument("--horizons", nargs="+", type=float, default=[1.0, 3.0, 7.0])
    parser.add_argument("--max-reference-offset-hours", type=float, default=12.0)
    parser.add_argument("--n-bootstrap", type=int, default=5000)
    args = parser.parse_args()

    commands = [
        [
            sys.executable,
            str(ROOT / "scripts" / "compute_errors.py"),
            "--input",
            *[str(path) for path in args.raw],
            "--horizons",
            *[str(value) for value in args.horizons],
            "--max-reference-offset-hours",
            str(args.max_reference_offset_hours),
        ],
        [
            sys.executable,
            str(ROOT / "scripts" / "analyze_errors.py"),
            "--n-bootstrap",
            str(args.n_bootstrap),
        ],
        [sys.executable, str(ROOT / "scripts" / "generate_plots.py")],
    ]
    for command in commands:
        print("+ " + " ".join(command))
        subprocess.run(command, cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
