"""
System-level invariant abstraction within Procela's.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/invariant/

Examples Reference
------------------
https://procela.org/docs/examples/core/invariant/
"""

from .category import InvariantCategory
from .exceptions import (
    InvariantViolation,
    InvariantViolationCritical,
    InvariantViolationFatal,
    InvariantViolationInfo,
    InvariantViolationWarning,
)
from .phase import InvariantPhase
from .severity import InvariantSeverity
from .snapshot import VariableSnapshot
from .softness import InvariantSoftness
from .system import SystemInvariant

__all__ = [
    "InvariantCategory",
    "InvariantViolation",
    "InvariantViolationInfo",
    "InvariantViolationWarning",
    "InvariantViolationCritical",
    "InvariantViolationFatal",
    "InvariantPhase",
    "InvariantSeverity",
    "VariableSnapshot",
    "InvariantSoftness",
    "SystemInvariant",
]
