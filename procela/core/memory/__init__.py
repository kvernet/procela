"""
Core memory management for persistent, immutable state tracking.

Provides immutable data structures for tracking variable changes and
reasoning outcomes with full historical context, statistical analysis,
and epistemic view.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/memory/

Examples Reference
------------------
https://procela.org/docs/examples/core/memory/
"""

from .variable import (
    CandidatesHistory,
    HistoryStatistics,
    ReasoningHistory,
    VariableHistory,
    VariableRecord,
)

__all__ = [
    "VariableRecord",
    "HistoryStatistics",
    "CandidatesHistory",
    "VariableHistory",
    "ReasoningHistory",
]
