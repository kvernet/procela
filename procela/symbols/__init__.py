"""
Symbolic representation system for Procela's mechanistic core framework.

The symbols module provides the fundamental building blocks for Procela's
active reasoning engine - symbolic representations of identity and time that
enable mechanistic modeling of real-world systems.

Semantics Reference
-------------------
https://procela.org/docs/semantics/symbols/

Examples Reference
------------------
https://procela.org/docs/examples/symbols/
"""

from .key import Key, generate_key
from .time import TimePoint, create_timepoint

__all__ = [
    "Key",
    "generate_key",
    "TimePoint",
    "create_timepoint",
]
