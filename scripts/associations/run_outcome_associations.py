#!/usr/bin/env python3
"""Run exposure-by-exposure linear or binary outcome models."""

from __future__ import annotations

import argparse
from pathlib import Path

from indnet.association import binary_associations, linear_associations
from indnet.io import read_table, validate_table


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-id", required=True)
    parser.add_argument("--outcome", required=True)
    parser.add_argument("--exposures", nargs="+", required=True)
    parser.add_argument("--covariates", nargs="*", default=[])
    parser.add_argument("--model", choices=("linear", "binary"), default="linear")
    parser.add_argument("--minimum-complete", type=int, default=20)
    args = parser.parse_args()

    numeric = [args.outcome, *args.exposures, *args.covariates]
    frame = validate_table(read_table(args.input), args.sample_id, numeric)
    model = linear_associations if args.model == "linear" else binary_associations
    results = model(
        frame,
        args.outcome,
        args.exposures,
        args.covariates,
        minimum_complete=args.minimum_complete,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output, index=False)
    print(f"Wrote association results to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
