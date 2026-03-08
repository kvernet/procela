"""
Resolution policy module in Procela.

This module defines policies for resolving competing hypotheses
into a single authoritative conclusion.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/policy/resolution/

Examples Reference
-------------------
https://procela.org/docs/examples/core/policy/resolution/
"""

from .base import ResolutionPolicy
from .confidence import HighestConfidencePolicy, WeightedConfidencePolicy
from .resolver import ResolverPolicy
from .voting import WeightedVotingPolicy

__all__ = [
    "ResolutionPolicy",
    "HighestConfidencePolicy",
    "WeightedConfidencePolicy",
    "ResolverPolicy",
    "WeightedVotingPolicy",
]
