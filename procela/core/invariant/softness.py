"""
Defines whether an invariant is strict or tolerant.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/invariant/softness.html

Examples Reference
------------------
https://procela.org/docs/examples/core/invariant/softness.html
"""

from __future__ import annotations

from enum import Enum, auto


class InvariantSoftness(Enum):
    """Defines whether an invariant is strict or tolerant."""

    HARD = auto()
    """Must always hold; violation raises an exception."""

    SOFT = auto()
    """May be violated; violation is recorded but execution continues."""
