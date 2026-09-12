#!/usr/bin/env python3
"""Build a pairwise association network from selected continuous traits."""

from __future__ import annotations

import argparse
from pathlib import Path

from indnet.io import read_table, validate_table
from indnet.network import build_association_network


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-id", required=True)
    parser.add_argument("--traits", nargs="+", required=True)
    parser.add_argument("--minimum-pair-size", type=int, default=20)
    parser.add_argument("--fdr-level", type=float, default=0.05)
    args = parser.parse_args()

    frame = validate_table(read_table(args.input), args.sample_id, args.traits)
    edges = build_association_network(
        frame.loc[:, args.traits],
        minimum_pair_size=args.minimum_pair_size,
        fdr_level=args.fdr_level,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    edges.to_csv(args.output, index=False)
    print(f"Wrote network edge table to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
