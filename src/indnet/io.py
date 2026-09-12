"""Table input and schema validation."""

from __future__ import annotations

from pathlib import Path
from collections.abc import Iterable

import numpy as np
import pandas as pd


def read_table(path: str | Path) -> pd.DataFrame:
    """Read a local CSV or TSV file."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Input table does not exist: {path}")
    suffixes = [suffix.lower() for suffix in path.suffixes]
    if suffixes[-1:] == [".csv"]:
        return pd.read_csv(path)
    if suffixes[-1:] in ([".tsv"], [".txt"]):
        return pd.read_csv(path, sep="\t")
    raise ValueError("Input must be a CSV or TSV text table")


def validate_table(
    frame: pd.DataFrame,
    sample_id: str,
    numeric_columns: Iterable[str],
) -> pd.DataFrame:
    """Validate required columns and return a numeric analysis frame."""
    numeric_columns = list(numeric_columns)
    required = [sample_id, *numeric_columns]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Input is missing {len(missing)} required column(s)")
    if frame[sample_id].isna().any():
        raise ValueError("Sample identifiers must not be missing")
    if frame[sample_id].duplicated().any():
        raise ValueError("Sample identifiers must be unique")

    validated = frame.loc[:, required].copy()
    for column in numeric_columns:
        converted = pd.to_numeric(validated[column], errors="coerce")
        newly_missing = converted.isna() & validated[column].notna()
        if newly_missing.any():
            raise ValueError(f"Column {column!r} contains non-numeric values")
        validated[column] = converted.replace([np.inf, -np.inf], np.nan)
    return validated
