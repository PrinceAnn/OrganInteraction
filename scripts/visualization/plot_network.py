#!/usr/bin/env python3
"""Render an association edge table as a network figure."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--edges", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--significant-only", action="store_true")
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    edges = pd.read_csv(args.edges)
    required = {"source", "target", "correlation", "significant"}
    if not required.issubset(edges.columns):
        raise ValueError("Edge table does not follow the documented schema")
    if args.significant_only:
        edges = edges.loc[edges["significant"].astype(bool)]
    graph = nx.from_pandas_edgelist(edges, "source", "target", edge_attr="correlation")
    positions = nx.spring_layout(graph, seed=args.seed, weight=None)
    correlations = [graph[u][v]["correlation"] for u, v in graph.edges]
    widths = [0.5 + 2.5 * abs(value) for value in correlations]
    colors = ["#B64242" if value < 0 else "#3267A8" for value in correlations]

    figure, axis = plt.subplots(figsize=(8, 6))
    nx.draw_networkx_nodes(graph, positions, node_color="#E6EEF7", edgecolors="#23364D", ax=axis)
    nx.draw_networkx_labels(graph, positions, font_size=9, ax=axis)
    nx.draw_networkx_edges(graph, positions, width=widths, edge_color=colors, alpha=0.8, ax=axis)
    axis.set_axis_off()
    figure.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=200, bbox_inches="tight")
    print(f"Wrote network figure to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
