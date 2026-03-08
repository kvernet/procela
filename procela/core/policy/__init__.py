"""
Policy module abstraction in Procela.

This module defines policies for resolution and action proposals within
Procela's active reasoning engine.

Policies implement strategic decision-making logic to:
- choose the most appropriate action from a set of competing proposals,
  enabling resource-aware, constraint-respecting system optimization
- resolve competing hypotheses into a single authoritative conclusion.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/policy/

Examples Reference
-------------------
https://procela.org/docs/examples/core/policy/
"""

from .resolution import (
    HighestConfidencePolicy,
    ResolutionPolicy,
    ResolverPolicy,
    WeightedConfidencePolicy,
    WeightedVotingPolicy,
)

__all__ = [
    "ResolutionPolicy",
    "HighestConfidencePolicy",
    "WeightedConfidencePolicy",
    "ResolverPolicy",
    "WeightedVotingPolicy",
]
