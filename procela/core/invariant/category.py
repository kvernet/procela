"""
Semantic category of a system invariant.

Examples
--------
>>> from procela import InvariantCategory
>>>
>>> print(InvariantCategory.CONSISTENCY)
InvariantCategory.CONSISTENCY
>>> for category in InvariantCategory:
...     print(category.name, category.value)
SAFETY 1
CONSISTENCY 2
EPISTEMIC 3
DYNAMICAL 4
RESOURCE 5

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

    Examples
    --------
    >>> from procela import InvariantCategory
    >>>
    >>> print(InvariantCategory.CONSISTENCY)
    InvariantCategory.CONSISTENCY
    >>> for category in InvariantCategory:
    ...     print(category.name, category.value)
    SAFETY 1
    CONSISTENCY 2
    EPISTEMIC 3
    DYNAMICAL 4
    RESOURCE 5
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
