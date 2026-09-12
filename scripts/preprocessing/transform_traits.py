#!/usr/bin/env python3
"""Transform continuous traits and optionally residualize covariates."""

from __future__ import annotations

import argparse
from pathlib import Path

from indnet.io import read_table, validate_table
from indnet.preprocessing import prepare_traits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-id", required=True)
    parser.add_argument("--traits", nargs="+", required=True)
    parser.add_argument("--covariates", nargs="*", default=[])
    parser.add_argument("--no-rank-transform", action="store_true")
    parser.add_argument("--no-residualization", action="store_true")
    args = parser.parse_args()

    numeric = [*args.traits, *args.covariates]
    frame = validate_table(read_table(args.input), args.sample_id, numeric)
    transformed = prepare_traits(
        frame,
        args.traits,
        args.covariates,
        apply_rank_transform=not args.no_rank_transform,
        apply_residualization=not args.no_residualization,
    )
    transformed.insert(0, args.sample_id, frame[args.sample_id])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    transformed.to_csv(args.output, index=False)
    print(f"Wrote transformed traits to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
