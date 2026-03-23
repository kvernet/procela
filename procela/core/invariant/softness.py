"""
Defines whether an invariant is strict or tolerant.

Examples
--------
>>> from procela import InvariantSoftness
>>>
>>> softness = InvariantSoftness.HARD
>>>
>>> print(softness)
InvariantSoftness.HARD
>>> for softness in InvariantSoftness:
    print(softness.name, softness.value)
HARD 1
SOFT 2

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
    """
    Defines whether an invariant is strict or tolerant.

    Examples
    --------
    >>> from procela import InvariantSoftness
    >>>
    >>> softness = InvariantSoftness.HARD
    >>>
    >>> print(softness)
    InvariantSoftness.HARD
    >>> for softness in InvariantSoftness:
        print(softness.name, softness.value)
    HARD 1
    SOFT 2
    """

    HARD = auto()
    """Must always hold; violation raises an exception."""

    SOFT = auto()
    """May be violated; violation is recorded but execution continues."""
