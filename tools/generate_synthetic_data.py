#!/usr/bin/env python3
"""Generate a deterministic artificial table for the documented example."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate(rows: int, seed: int) -> pd.DataFrame:
    if rows < 30:
        raise ValueError("rows must be at least 30")
    rng = np.random.default_rng(seed)
    covariate_a = rng.normal(size=rows)
    covariate_b = rng.integers(0, 2, size=rows)
    shared = rng.normal(size=rows)
    frame = pd.DataFrame(
        {
            "sample_id": [f"synthetic_{index:04d}" for index in range(rows)],
            "trait_a": 0.8 * shared + 0.4 * covariate_a + rng.normal(scale=0.7, size=rows),
            "trait_b": -0.6 * shared + 0.3 * covariate_a + rng.normal(scale=0.8, size=rows),
            "trait_c": rng.normal(size=rows),
            "trait_d": 0.5 * shared + rng.normal(scale=0.9, size=rows),
            "covariate_a": covariate_a,
            "covariate_b": covariate_b,
        }
    )
    frame.loc[frame.index[::37], "trait_c"] = np.nan
    return frame


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=250)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "local-data" / "synthetic_traits.csv",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    generate(args.rows, args.seed).to_csv(args.output, index=False)
    print(f"Wrote artificial example data to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
