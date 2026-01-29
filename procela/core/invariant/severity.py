"""
Severity level of an invariant violation.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/invariant/severity.html

Examples Reference
------------------
https://procela.org/docs/examples/core/invariant/severity.html
"""

from __future__ import annotations

from enum import Enum, auto


class InvariantSeverity(Enum):
    """Severity level of an invariant violation."""

    INFO = auto()
    """Violation is informative; no corrective action required."""

    WARNING = auto()
    """Violation indicates degradation or risk but system may continue."""

    CRITICAL = auto()
    """Violation indicates a system failure requiring immediate attention."""

    FATAL = auto()
    """Violation invalidates the simulation or model entirely."""
