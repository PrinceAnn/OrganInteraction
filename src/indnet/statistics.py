"""Small statistical helpers used by the network pipeline."""

from __future__ import annotations

import numpy as np


def benjamini_hochberg(p_values) -> np.ndarray:
    """Return Benjamini-Hochberg adjusted p-values while preserving missingness."""
    values = np.asarray(p_values, dtype=float)
    adjusted = np.full(values.shape, np.nan, dtype=float)
    finite = np.isfinite(values)
    if not finite.any():
        return adjusted
    observed = values[finite]
    if ((observed < 0) | (observed > 1)).any():
        raise ValueError("p-values must lie between 0 and 1")

    order = np.argsort(observed)
    ranked = observed[order]
    scale = observed.size / np.arange(1, observed.size + 1)
    monotone = np.minimum.accumulate((ranked * scale)[::-1])[::-1]
    restored = np.empty_like(monotone)
    restored[order] = np.clip(monotone, 0.0, 1.0)
    adjusted[finite] = restored
    return adjusted
