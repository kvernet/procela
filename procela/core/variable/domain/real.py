"""
Real value domains for Procela.

This module provides domain classes for real values.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/domain/real.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/variable/domain/real.html
"""

from __future__ import annotations

from .range import RangeDomain


class RealDomain(RangeDomain):
    """
    Domain for real values with infinite bounds.

    This domain validates that a value is real (int or float) and
    falls within -inf and +inf bounds.
    """

    def __init__(self, name: str = "") -> None:
        """
        Initialize a RealDomain with infinite bounds.

        Parameters
        ----------
        name : str, optional
            Name for the domain. Default is empty string.
        """
        super().__init__(min_value=-float("inf"), max_value=float("inf"), name=name)
