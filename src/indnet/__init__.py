"""Public, source-agnostic association-network utilities."""

from .association import binary_associations, linear_associations
from .decomposition import PCAResult, principal_components
from .network import build_association_network
from .preprocessing import prepare_traits, rank_inverse_normal, residualize
from .statistics import benjamini_hochberg

__all__ = [
    "benjamini_hochberg",
    "binary_associations",
    "build_association_network",
    "linear_associations",
    "PCAResult",
    "principal_components",
    "prepare_traits",
    "rank_inverse_normal",
    "residualize",
]

__version__ = "0.1.0"
