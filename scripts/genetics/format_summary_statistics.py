#!/usr/bin/env python3
"""Map a local association table to a source-neutral summary-statistics schema."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from indnet.io import read_table


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variant-column", required=True)
    parser.add_argument("--effect-allele-column", required=True)
    parser.add_argument("--other-allele-column", required=True)
    parser.add_argument("--estimate-column", required=True)
    parser.add_argument("--standard-error-column", required=True)
    parser.add_argument("--p-value-column", required=True)
    parser.add_argument("--sample-size-column", required=True)
    args = parser.parse_args()

    frame = read_table(args.input)
    mapping = {
        args.variant_column: "variant",
        args.effect_allele_column: "effect_allele",
        args.other_allele_column: "other_allele",
        args.estimate_column: "estimate",
        args.standard_error_column: "standard_error",
        args.p_value_column: "p_value",
        args.sample_size_column: "sample_size",
    }
    missing = [column for column in mapping if column not in frame.columns]
    if missing:
        raise ValueError(f"Input is missing {len(missing)} requested column(s)")
    formatted = frame.loc[:, list(mapping)].rename(columns=mapping)
    for column in ("estimate", "standard_error", "p_value", "sample_size"):
        formatted[column] = pd.to_numeric(formatted[column], errors="raise")
    valid = (
        formatted["p_value"].between(0, 1)
        & formatted["standard_error"].gt(0)
        & formatted["sample_size"].gt(0)
    )
    formatted = formatted.loc[valid].drop_duplicates("variant")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    formatted.to_csv(args.output, sep="\t", index=False)
    print(f"Wrote formatted summary statistics to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
