"""Source-independent outcome association models."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.stats import norm, t

from .statistics import benjamini_hochberg


RESULT_COLUMNS = [
    "exposure", "n", "estimate", "standard_error", "statistic", "p_value", "q_value"
]


def _complete_design(
    frame: pd.DataFrame,
    outcome: str,
    exposure: str,
    covariates: Sequence[str],
) -> tuple[np.ndarray, np.ndarray]:
    columns = [outcome, exposure, *covariates]
    complete = frame.loc[:, columns].apply(pd.to_numeric, errors="coerce").dropna()
    y = complete[outcome].to_numpy(dtype=float)
    x = complete.loc[:, [exposure, *covariates]].to_numpy(dtype=float)
    return y, np.column_stack([np.ones(len(complete)), x])


def _finalize(records: list[dict]) -> pd.DataFrame:
    result = pd.DataFrame.from_records(records)
    result["q_value"] = benjamini_hochberg(result["p_value"].to_numpy())
    return result.loc[:, RESULT_COLUMNS]


def linear_associations(
    frame: pd.DataFrame,
    outcome: str,
    exposures: Sequence[str],
    covariates: Sequence[str] = (),
    *,
    minimum_complete: int = 20,
) -> pd.DataFrame:
    """Fit one ordinary-least-squares model per exposure."""
    records: list[dict] = []
    for exposure in exposures:
        y, design = _complete_design(frame, outcome, exposure, covariates)
        estimate = standard_error = statistic = p_value = np.nan
        rank = np.linalg.matrix_rank(design) if len(y) else 0
        degrees_freedom = len(y) - rank
        if len(y) >= minimum_complete and degrees_freedom > 0 and rank == design.shape[1]:
            coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)
            residuals = y - design @ coefficients
            variance = float(residuals @ residuals / degrees_freedom)
            covariance = variance * np.linalg.inv(design.T @ design)
            estimate = float(coefficients[1])
            standard_error = float(np.sqrt(covariance[1, 1]))
            statistic = estimate / standard_error if standard_error > 0 else np.nan
            p_value = float(2 * t.sf(abs(statistic), degrees_freedom))
        records.append(
            {
                "exposure": exposure,
                "n": len(y),
                "estimate": estimate,
                "standard_error": standard_error,
                "statistic": statistic,
                "p_value": p_value,
            }
        )
    return _finalize(records)


def binary_associations(
    frame: pd.DataFrame,
    outcome: str,
    exposures: Sequence[str],
    covariates: Sequence[str] = (),
    *,
    minimum_complete: int = 20,
    maximum_iterations: int = 100,
    tolerance: float = 1e-8,
) -> pd.DataFrame:
    """Fit one logistic-regression model per exposure using stable IRLS."""
    records: list[dict] = []
    for exposure in exposures:
        y, design = _complete_design(frame, outcome, exposure, covariates)
        estimate = standard_error = statistic = p_value = np.nan
        valid_outcome = len(y) and set(np.unique(y)).issubset({0.0, 1.0}) and len(np.unique(y)) == 2
        rank = np.linalg.matrix_rank(design) if len(y) else 0
        if len(y) >= minimum_complete and valid_outcome and rank == design.shape[1]:
            coefficients = np.zeros(design.shape[1], dtype=float)
            information = None
            for _ in range(maximum_iterations):
                probability = expit(np.clip(design @ coefficients, -30.0, 30.0))
                weights = np.clip(probability * (1.0 - probability), 1e-9, None)
                information = design.T @ (weights[:, None] * design)
                score = design.T @ (y - probability)
                step = np.linalg.pinv(information) @ score
                coefficients += step
                if np.max(np.abs(step)) < tolerance:
                    break
            if information is not None and np.isfinite(coefficients).all():
                covariance = np.linalg.pinv(information)
                estimate = float(coefficients[1])
                standard_error = float(np.sqrt(covariance[1, 1]))
                statistic = estimate / standard_error if standard_error > 0 else np.nan
                p_value = float(2 * norm.sf(abs(statistic)))
        records.append(
            {
                "exposure": exposure,
                "n": len(y),
                "estimate": estimate,
                "standard_error": standard_error,
                "statistic": statistic,
                "p_value": p_value,
            }
        )
    return _finalize(records)
