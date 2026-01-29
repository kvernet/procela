"""
Semantic category of a system invariant.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/invariant/category.html

Examples Reference
------------------
https://procela.org/docs/examples/core/invariant/category.html
"""

from __future__ import annotations

from enum import Enum, auto


class InvariantCategory(Enum):
    """
    Semantic category of a system invariant.

    Categories describe *what kind of system property* the invariant expresses,
    not how it is enforced.
    """

    SAFETY = auto()
    """Prevents the system from entering invalid or dangerous states."""

    CONSISTENCY = auto()
    """Ensures coherence between variables, mechanisms, or beliefs."""

    EPISTEMIC = auto()
    """Ensures epistemic soundness (confidence bounds, uncertainty rules)."""

    DYNAMICAL = auto()
    """Constrains temporal or dynamical behavior (monotonicity, stability)."""

    RESOURCE = auto()
    """Ensures bounded use or conservation of abstract resources."""
