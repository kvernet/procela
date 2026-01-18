"""
Core memory management for persistent, immutable state tracking.

Provides immutable data structures for tracking variable changes and
reasoning outcomes with full historical context, statistical analysis,
and epistemic view.

Classes:
    VariableRecord: Immutable record of a single variable state change.
    VariableHistory: Append-only, immutable log of variable changes.
    ReasoningHistory: Append-only, immutable log of reasoning outcomes.
    HistoryStatistics: Statistical analysis of variable history.
    VariableEpistemic: Epistemic state combining history and reasoning.

All components are immutable and temporally consistent.

See: https://procela.org/docs/semantics/core/memory/
"""

from .variable import (
    HistoryStatistics,
    ReasoningHistory,
    VariableEpistemic,
    VariableHistory,
    VariableRecord,
)

__all__ = [
    "VariableRecord",
    "HistoryStatistics",
    "VariableHistory",
    "ReasoningHistory",
    "VariableEpistemic",
]
