"""
Real value domains for Procela.

This module provides domain classes for real values.

Examples
--------
>>> from procela import RealDomain
>>>
>>> domain = RealDomain(name="Real numbers")
>>>
>>> print(domain.min_value, domain.max_value)
-inf inf
>>> print(domain.validate(37.432))
True
>>> print(domain.explain(37.432))
Value 37.432 is valid in RealDomain
>>> print(domain.validate(-float("inf")))
True
>>> print(domain.explain(-float("inf")))
Value -inf is valid in RealDomain
>>> print(domain.validate("test"))
False
>>> print(domain.explain("test"))
Value test is not numeric

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

    Examples
    --------
    >>> from procela import RealDomain
    >>>
    >>> domain = RealDomain(name="Real numbers")
    >>>
    >>> print(domain.min_value, domain.max_value)
    -inf inf
    >>> print(domain.validate(37.432))
    True
    >>> print(domain.explain(37.432))
    Value 37.432 is valid in RealDomain
    >>> print(domain.validate(-float("inf")))
    True
    >>> print(domain.explain(-float("inf")))
    Value -inf is valid in RealDomain
    >>> print(domain.validate("test"))
    False
    >>> print(domain.explain("test"))
    Value test is not numeric
    """

    def __init__(self, name: str = "") -> None:
        """
        Initialize a RealDomain with infinite bounds.

        Parameters
        ----------
        name : str, optional
            Name for the domain. Default is empty string.

        Examples
        --------
        >>> from procela import RealDomain
        >>>
        >>> domain = RealDomain(name="Real numbers")
        >>>
        >>> print(domain.min_value, domain.max_value)
        -inf inf
        >>> print(domain.validate(37.432))
        True
        >>> print(domain.explain(37.432))
        Value 37.432 is valid in RealDomain
        >>> print(domain.validate(-float("inf")))
        True
        >>> print(domain.explain(-float("inf")))
        Value -inf is valid in RealDomain
        >>> print(domain.validate("test"))
        False
        >>> print(domain.explain("test"))
        Value test is not numeric
        """
        super().__init__(min_value=-float("inf"), max_value=float("inf"), name=name)
