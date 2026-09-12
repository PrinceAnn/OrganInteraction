#!/usr/bin/env python3
"""Validate selected numeric columns and mask extreme values."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from indnet.io import read_table, validate_table


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-id", required=True)
    parser.add_argument("--columns", nargs="+", required=True)
    parser.add_argument("--z-threshold", type=float, default=4.0)
    args = parser.parse_args()
    if args.z_threshold <= 0:
        parser.error("--z-threshold must be positive")

    frame = validate_table(read_table(args.input), args.sample_id, args.columns)
    for column in args.columns:
        values = frame[column]
        standard_deviation = values.std()
        if np.isfinite(standard_deviation) and standard_deviation > 0:
            z_score = (values - values.mean()) / standard_deviation
            frame.loc[z_score.abs() > args.z_threshold, column] = np.nan
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)
    print(f"Wrote validated table to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
