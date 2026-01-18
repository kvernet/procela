"""
Core components for managing variable memory within the Procela reasoning framework.

This module provides the foundational data structures for tracking variable
changes over time, maintaining immutable history logs, and computing
epistemic statistics for reasoning about variable behavior.

Classes
-------
VariableRecord
    Immutable record of a single variable state change, containing value,
    time, source, and metadata.

VariableHistory
    Immutable, append-only history log for variable changes, implemented as
    a persistent linked list. Each new record creates a new history instance,
    preserving the complete history chain.

ReasoningHistory
    Immutable, append-only history log for reasoning results, tracking
    task execution outcomes in a persistent linked list structure.

VariableEpistemic
    Epistemic state manager that combines variable history with reasoning
    context to maintain knowledge about variable behavior and uncertainty.

HistoryStatistics
    Statistical analyzer for variable histories, computing metrics like
    frequency, volatility, anomaly scores, and value distributions.

Key Concepts
------------
- **Immutability**: All history classes are frozen dataclasses; operations
  return new instances rather than modifying existing ones.
- **Key-based Identity**: All entities use keys for secure
  reference and resolution via KeyAuthority.
- **Persistent Data Structures**: History chains use structural sharing
  for memory efficiency.
- **Epistemic Tracking**: Integration of factual records with reasoning
  context to support uncertainty modeling.

Usage Example
-------------
>>> from procela.core.memory.variable import (
...     VariableRecord, VariableHistory, VariableEpistemic
... )
>>> from procela.symbols.time import TimePoint
>>> from procela.symbols.key import Key
>>>
>>> # Create initial history
>>> history = VariableHistory()
>>>
>>> # Record variable changes
>>> record = VariableRecord(
...     value=42,
...     time=TimePoint(),
...     source=Key()
... )
>>> updated_history = history.new(record)
>>>
>>> # Query history
>>> records = updated_history.get_records()
>>> latest = updated_history.latest()

Semantics Reference
-------------------
For detailed semantics and behavioral specifications, see:
https://procela.org/docs/semantics/core/memory/variable/

See Also
--------
procela.core.memory.key_authority : Key management and resolution
procela.symbols.key : Key infrastructure
procela.symbols.time : Temporal reasoning
procela.core.reasoning : Reasoning task and result definitions
"""

from .epistemic import VariableEpistemic
from .history import ReasoningHistory, VariableHistory
from .record import VariableRecord
from .statistics import HistoryStatistics

__all__ = [
    "VariableEpistemic",
    "VariableHistory",
    "ReasoningHistory",
    "VariableRecord",
    "HistoryStatistics",
]
