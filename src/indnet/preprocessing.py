"""Source-independent preprocessing for continuous traits."""

from __future__ import annotations

from statistics import NormalDist

import numpy as np
import pandas as pd
from scipy.stats import rankdata


def rank_inverse_normal(values: pd.Series) -> pd.Series:
    """Apply a rank-based inverse normal transform, retaining missing values."""
    output = pd.Series(np.nan, index=values.index, dtype=float, name=values.name)
    mask = values.notna()
    count = int(mask.sum())
    if count == 0:
        return output
    ranks = rankdata(values.loc[mask].to_numpy(dtype=float), method="average")
    probabilities = (ranks - 0.5) / count
    normal = NormalDist()
    output.loc[mask] = [normal.inv_cdf(float(value)) for value in probabilities]
    return output


def residualize(trait: pd.Series, covariates: pd.DataFrame) -> pd.Series:
    """Return ordinary-least-squares residuals using complete rows only."""
    result = pd.Series(np.nan, index=trait.index, dtype=float, name=trait.name)
    complete = trait.notna() & covariates.notna().all(axis=1)
    if int(complete.sum()) <= covariates.shape[1] + 1:
        return result
    y = trait.loc[complete].to_numpy(dtype=float)
    x = covariates.loc[complete].to_numpy(dtype=float)
    design = np.column_stack([np.ones(x.shape[0]), x])
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
    result.loc[complete] = y - design @ coefficients
    return result


def prepare_traits(
    frame: pd.DataFrame,
    traits: tuple[str, ...] | list[str],
    covariates: tuple[str, ...] | list[str] = (),
    *,
    apply_rank_transform: bool = True,
    apply_residualization: bool = True,
) -> pd.DataFrame:
    """Transform and optionally residualize selected traits."""
    prepared = pd.DataFrame(index=frame.index)
    covariate_frame = frame.loc[:, list(covariates)]
    for name in traits:
        values = frame[name].astype(float)
        if apply_rank_transform:
            values = rank_inverse_normal(values)
        if apply_residualization and covariates:
            values = residualize(values, covariate_frame)
        prepared[name] = values
    return prepared
