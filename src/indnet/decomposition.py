"""Principal-component decomposition for complete numeric trait matrices."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PCAResult:
    scores: pd.DataFrame
    loadings: pd.DataFrame
    explained_variance_ratio: pd.Series


def principal_components(
    frame: pd.DataFrame,
    columns: Sequence[str],
    *,
    components: int = 2,
) -> PCAResult:
    """Standardize complete rows and compute principal components with SVD."""
    if not columns:
        raise ValueError("At least one numeric column is required")
    numeric = frame.loc[:, list(columns)].apply(pd.to_numeric, errors="coerce").dropna()
    if len(numeric) < 2:
        raise ValueError("At least two complete rows are required")
    maximum_components = min(numeric.shape)
    if not 1 <= components <= maximum_components:
        raise ValueError(f"components must be between 1 and {maximum_components}")

    values = numeric.to_numpy(dtype=float)
    means = values.mean(axis=0)
    scales = values.std(axis=0, ddof=1)
    if np.any(scales == 0):
        raise ValueError("PCA columns must have non-zero variance")
    standardized = (values - means) / scales
    left, singular, right = np.linalg.svd(standardized, full_matrices=False)
    names = [f"PC{index}" for index in range(1, components + 1)]
    scores = pd.DataFrame(
        left[:, :components] * singular[:components], index=numeric.index, columns=names
    )
    loadings = pd.DataFrame(right[:components].T, index=list(columns), columns=names)
    variance = singular**2 / (len(numeric) - 1)
    explained = pd.Series(variance[:components] / variance.sum(), index=names, name="ratio")
    return PCAResult(scores=scores, loadings=loadings, explained_variance_ratio=explained)
