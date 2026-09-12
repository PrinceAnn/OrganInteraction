#!/usr/bin/env python3
"""Create principal-component scores, loadings, and explained variance."""

from __future__ import annotations

import argparse
from pathlib import Path

from indnet.decomposition import principal_components
from indnet.io import read_table, validate_table


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--sample-id", required=True)
    parser.add_argument("--columns", nargs="+", required=True)
    parser.add_argument("--components", type=int, default=2)
    args = parser.parse_args()

    frame = validate_table(read_table(args.input), args.sample_id, args.columns)
    result = principal_components(frame, args.columns, components=args.components)
    scores = result.scores.copy()
    scores.insert(0, args.sample_id, frame.loc[scores.index, args.sample_id])
    args.output_directory.mkdir(parents=True, exist_ok=True)
    scores.to_csv(args.output_directory / "scores.csv", index=False)
    result.loadings.rename_axis("variable").reset_index().to_csv(
        args.output_directory / "loadings.csv", index=False
    )
    result.explained_variance_ratio.rename_axis("component").reset_index().to_csv(
        args.output_directory / "explained_variance.csv", index=False
    )
    print(f"Wrote PCA outputs to {args.output_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
