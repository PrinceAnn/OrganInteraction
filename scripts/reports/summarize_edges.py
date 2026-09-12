#!/usr/bin/env python3
"""Create a compact Markdown summary from a network edge table."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--edges", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    edges = pd.read_csv(args.edges)
    required = {"source", "target", "correlation", "q_value", "significant"}
    if not required.issubset(edges.columns):
        raise ValueError("Edge table does not follow the documented schema")
    significant = edges.loc[edges["significant"].astype(bool)].copy()
    significant["absolute_correlation"] = significant["correlation"].abs()
    strongest = significant.nlargest(10, "absolute_correlation")
    lines = [
        "# Network summary",
        "",
        f"- Tested edges: {len(edges)}",
        f"- FDR-significant edges: {len(significant)}",
        "",
        "## Strongest significant edges",
        "",
        "| Source | Target | Correlation | q-value |",
        "|---|---|---:|---:|",
    ]
    for row in strongest.itertuples(index=False):
        lines.append(
            f"| {row.source} | {row.target} | {row.correlation:.4f} | {row.q_value:.3g} |"
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote network summary to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
