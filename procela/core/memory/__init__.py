"""
Core components for managing variable memory in Procela.

This module provides the foundational data structures for tracking variable
changes over time, maintaining immutable memory, and computing
epistemic statistics for reasoning about variable behavior.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/memory/

Examples Reference
------------------
https://procela.org/docs/examples/core/memory/
"""

from .base import VariableMemory
from .hypothesis import HypothesisRecord, HypothesisState
from .record import VariableRecord
from .statistics import MemoryStatistics

__all__ = [
    "HypothesisState",
    "HypothesisRecord",
    "VariableMemory",
    "VariableRecord",
    "MemoryStatistics",
]
