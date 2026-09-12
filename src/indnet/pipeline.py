"""End-to-end pipeline orchestration."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import PipelineConfig
from .io import read_table, validate_table
from .network import build_association_network
from .preprocessing import prepare_traits


def run_pipeline(config: PipelineConfig) -> Path:
    """Run preprocessing and association testing, then write an edge table."""
    frame = read_table(config.input_path)
    numeric_columns = [*config.traits, *config.covariates]
    validated = validate_table(frame, config.sample_id, numeric_columns)
    prepared = prepare_traits(
        validated,
        config.traits,
        config.covariates,
        apply_rank_transform=config.rank_inverse_normal,
        apply_residualization=config.residualize,
    )
    edges = build_association_network(
        prepared,
        minimum_pair_size=config.minimum_pair_size,
        fdr_level=config.fdr_level,
    )
    config.output_directory.mkdir(parents=True, exist_ok=True)
    destination = config.output_directory / config.edge_file
    edges.to_csv(destination, index=False)
    return destination
