"""
Action management subsystem for Procela's active reasoning engine.

The action module provides the complete infrastructure for creating,
validating, selecting, and executing intervention proposals generated
by the reasoning engine. It implements the "propose-validate-select"
pattern that is central to Procela's active reasoning methodology.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/action/

Examples Reference
-------------------
https://procela.org/docs/examples/core/action/
"""

from .effect import ActionEffect
from .policy import HighestConfidencePolicy, ResolutionPolicy
from .proposal import ActionProposal, ProposalStatus
from .proposer import ActionProposer
from .resolver import ConflictResolver
from .validator import ConfidenceThresholdValidator, ProposalValidator

__all__ = [
    # Effect modeling
    "ActionEffect",
    # Selection policies
    "ResolutionPolicy",
    "HighestConfidencePolicy",
    # Proposal system
    "ProposalStatus",
    "ActionProposal",
    # Proposer
    "ActionProposer",
    # Resolver
    "ConflictResolver",
    # Validation
    "ProposalValidator",
    "ConfidenceThresholdValidator",
]
