"""Construct an undirected pairwise association network."""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

from .statistics import benjamini_hochberg


EDGE_COLUMNS = ["source", "target", "n", "correlation", "p_value", "q_value", "significant"]


def build_association_network(
    traits: pd.DataFrame,
    *,
    minimum_pair_size: int = 20,
    fdr_level: float = 0.05,
) -> pd.DataFrame:
    """Test all trait pairs and return a tidy undirected edge table."""
    if traits.shape[1] < 2:
        raise ValueError("At least two trait columns are required")
    if minimum_pair_size < 3:
        raise ValueError("minimum_pair_size must be at least 3")
    if not 0 < fdr_level < 1:
        raise ValueError("fdr_level must be between 0 and 1")

    records: list[dict] = []
    for source, target in combinations(traits.columns, 2):
        pair = traits.loc[:, [source, target]].dropna()
        n = len(pair)
        correlation = np.nan
        p_value = np.nan
        if n >= minimum_pair_size and pair[source].nunique() > 1 and pair[target].nunique() > 1:
            result = pearsonr(pair[source], pair[target])
            correlation = float(result.statistic)
            p_value = float(result.pvalue)
        records.append(
            {
                "source": source,
                "target": target,
                "n": n,
                "correlation": correlation,
                "p_value": p_value,
            }
        )

    edges = pd.DataFrame.from_records(records)
    edges["q_value"] = benjamini_hochberg(edges["p_value"].to_numpy())
    edges["significant"] = edges["q_value"].le(fdr_level).fillna(False)
    return edges.loc[:, EDGE_COLUMNS]
