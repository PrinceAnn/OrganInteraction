"""Load and validate an indNet TOML configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class PipelineConfig:
    input_path: Path
    sample_id: str
    traits: tuple[str, ...]
    covariates: tuple[str, ...]
    rank_inverse_normal: bool
    residualize: bool
    minimum_pair_size: int
    fdr_level: float
    output_directory: Path
    edge_file: str


def _required(mapping: dict, key: str, section: str):
    try:
        return mapping[key]
    except KeyError as exc:
        raise ValueError(f"Missing configuration value [{section}] {key}") from exc


def _resolve(base: Path, value: str) -> Path:
    candidate = Path(value).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (base / candidate).resolve()


def load_config(path: str | Path) -> PipelineConfig:
    """Load a TOML file and return a validated immutable configuration."""
    config_path = Path(path).resolve()
    with config_path.open("rb") as handle:
        raw = tomllib.load(handle)

    data = raw.get("data", {})
    preprocessing = raw.get("preprocessing", {})
    network = raw.get("network", {})
    output = raw.get("output", {})

    traits = tuple(_required(data, "traits", "data"))
    covariates = tuple(data.get("covariates", ()))
    sample_id = str(_required(data, "sample_id", "data"))
    minimum_pair_size = int(network.get("minimum_pair_size", 20))
    fdr_level = float(network.get("fdr_level", 0.05))
    edge_file = str(output.get("edge_file", "association_edges.csv"))

    if len(traits) < 2:
        raise ValueError("At least two trait columns are required")
    if len(set(traits)) != len(traits):
        raise ValueError("Trait column names must be unique")
    if sample_id in traits or sample_id in covariates:
        raise ValueError("The sample identifier cannot also be a numeric variable")
    if set(traits).intersection(covariates):
        raise ValueError("Trait and covariate columns must not overlap")
    if minimum_pair_size < 3:
        raise ValueError("minimum_pair_size must be at least 3")
    if not 0 < fdr_level < 1:
        raise ValueError("fdr_level must be between 0 and 1")
    if Path(edge_file).name != edge_file:
        raise ValueError("edge_file must be a file name, not a path")

    base = config_path.parent
    return PipelineConfig(
        input_path=_resolve(base, str(_required(data, "input", "data"))),
        sample_id=sample_id,
        traits=traits,
        covariates=covariates,
        rank_inverse_normal=bool(preprocessing.get("rank_inverse_normal", True)),
        residualize=bool(preprocessing.get("residualize", bool(covariates))),
        minimum_pair_size=minimum_pair_size,
        fdr_level=fdr_level,
        output_directory=_resolve(base, str(output.get("directory", "../local-results"))),
        edge_file=edge_file,
    )
