"""
Symbolic representation system for Procela's mechanistic core framework.

The symbols module provides the fundamental building blocks for Procela's
active reasoning engine - symbolic representations of identity and time that
enable mechanistic modeling of real-world systems.

Core Philosophy
---------------
In Procela, symbols are immutable identity tokens that serve as the atomic
units of the reasoning system. They provide the foundation for the contractual
mechanistic approach, where each symbol maintains pure identity without
semantic baggage, enabling external relationship management.

Key Symbol Types
----------------
1. **Identity Symbols (Key)**: Unique, immutable identity tokens
2. **Temporal Symbols (TimePoint)**: Pure temporal identity tokens representing
   declared positions in the system's temporal space

Symbolic Properties
-------------------
All symbols in Procela adhere to these core principles:
- **Identity Purity**: Symbols wrap Keys with no additional state
- **Immutability**: Cannot be modified after creation
- **Opaqueness**: No semantic information beyond identity
- **External Relationship Management**: All relationships (temporal precedence,
  spatial relationships, etc.) are managed externally to maintain separation
  of concerns

Semantic Reference
------------------
For detailed semantics of the symbolic system, see:
https://procela.org/docs/semantics/symbols/

Usage Examples
--------------
>>> from procela.symbols import Key, generate_key, TimePoint, create_timepoint
>>>
>>> # Create identity keys
>>> k1 = generate_key()
>>> k2 = Key()
>>> print(f"Key 1: {k1}")
>>> print(f"Key 2: {k2}")
>>>
>>> # Create temporal symbols
>>> tp1 = create_timepoint()
>>> tp2 = TimePoint()
>>> print(f"TimePoint 1: {tp1}")
>>> print(f"TimePoint 2: {tp2}")
>>>
>>> # Access the underlying key of a TimePoint
>>> tp_key = tp1.key()
>>> print(f"TimePoint's key: {tp_key}")

Module Structure
----------------
- `key.py`: Key class and generation functions for identity management
- `time.py`: TimePoint class for temporal identity representation

Exported Symbols
----------------
- **Key**: Immutable identity token class
- **generate_key**: Factory function for creating new Keys
- **TimePoint**: Temporal identity token class
- **create_timepoint**: Factory function for creating new TimePoints

Notes
-----
- All symbols are hashable and can be used as dictionary keys
- Symbol comparison is based on identity equality, not value
- The system prohibits mathematical operations on symbols to maintain
  semantic purity (e.g., TimePoint + TimePoint raises SemanticViolation)
- Symbols serialize to bytes containing only their identity Key

See Also
--------
procela.core.key_authority : Centralized key generation and management
procela.core.exceptions : Exception hierarchy including SemanticViolation
"""

from .key import Key, generate_key
from .time import TimePoint, create_timepoint

__all__ = [
    "Key",
    "generate_key",
    "TimePoint",
    "create_timepoint",
]
