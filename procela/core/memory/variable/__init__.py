"""
Core components for managing variable memory within the Procela reasoning framework.

This module provides the foundational data structures for tracking variable
changes over time, maintaining immutable history logs, and computing
epistemic statistics for reasoning about variable behavior.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/memory/variable/

Examples Reference
------------------
https://procela.org/docs/examples/core/memory/variable/
"""

from .history import CandidatesHistory, ReasoningHistory, VariableHistory
from .record import VariableRecord
from .statistics import HistoryStatistics

__all__ = [
    "VariableHistory",
    "ReasoningHistory",
    "CandidatesHistory",
    "VariableRecord",
    "HistoryStatistics",
]
