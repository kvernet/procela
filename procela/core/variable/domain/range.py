"""
Numeric value domains for Procela.

This module provides domain classes for numeric values with various constraints.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/domain/range.html
"""

from __future__ import annotations

import math
from typing import Any

from ...memory.variable.statistics import HistoryStatistics
from .value import ValueDomain


class RangeDomain(ValueDomain):
    """
    Domain for numeric values with optional inclusive bounds.

    This domain validates that a value is numeric (int or float) and
    falls within optional minimum and maximum bounds. Both bounds are
    inclusive when specified.

    Attributes
    ----------
    min_value : float | None
        Minimum allowed value (inclusive). None means no lower bound.
    max_value : float | None
        Maximum allowed value (inclusive). None means no upper bound.
    name : str
        Optional name for the domain, inherited from ValueDomain.

    Examples
    --------
    >>> from procela.core.variable import RangeDomain
    >>>
    >>> # Domain for positive numbers
    >>> positive_domain = RangeDomain(min_value=0, name="positive")
    >>> positive_domain.validate(5)
    True
    >>> positive_domain.validate(-1)
    False

    >>> # Domain for percentages (0-100)
    >>> percent_domain = RangeDomain(min_value=0, max_value=100, name="percent")
    >>> percent_domain.validate(50)
    True
    >>> percent_domain.validate(150)
    False

    >>> # Unbounded domain (any numeric value)
    >>> any_numeric = RangeDomain(name="any_numeric")
    >>> any_numeric.validate(3.14)
    True
    >>> any_numeric.validate("string")
    False
    """

    def __init__(
        self,
        min_value: float | None = None,
        max_value: float | None = None,
        name: str = "",
    ) -> None:
        """
        Initialize a RangeDomain with optional bounds.

        Parameters
        ----------
        min_value : float | None, optional
            Minimum allowed value (inclusive). If None, no minimum bound.
            Default is None.
        max_value : float | None, optional
            Maximum allowed value (inclusive). If None, no maximum bound.
            Default is None.
        name : str, optional
            Name for the domain. Default is empty string.

        Raises
        ------
        ValueError
            If min_value > max_value when both are specified.

        Examples
        --------
        >>> from procela.core.variable import RangeDomain
        >>>
        >>> domain = RangeDomain(min_value=0, max_value=10, name="zero_to_ten")
        >>> domain.min_value
        0
        >>> domain.max_value
        10
        >>> domain.name
        'zero_to_ten'

        >>> # Invalid bounds raise ValueError
        >>> RangeDomain(min_value=10, max_value=0)
        Traceback (most recent call last):
            ...
        ValueError: min_value (10) cannot be greater than max_value (0)
        """
        super().__init__(name)
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise ValueError(
                    f"min_value ({min_value}) cannot be greater "
                    f"than max_value ({max_value})"
                )
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any, stats: HistoryStatistics | None = None) -> bool:
        """
        Validate that a value is numeric and within bounds.

        Checks if the value is numeric (int or float) and, if bounds are
        specified, whether it falls within those bounds (inclusive).

        Parameters
        ----------
        value : Any
            Value to validate. Can be any type, but only int and float
            can be valid.
        stats : HistoryStatistics | None, optional
            Additional stats for validation (not used in this implementation
            but included for interface compatibility). Default is None.

        Returns
        -------
        bool
            True if value is numeric and within bounds (or bounds are None),
            False otherwise.

        Examples
        --------
        >>> from procela.core.variable import RangeDomain
        >>>
        >>> domain = RangeDomain(min_value=0, max_value=100)
        >>> domain.validate(50)
        True
        >>> domain.validate(150)
        False
        >>> domain.validate(-10)
        False
        >>> domain.validate("50")  # String, not numeric
        False
        >>> domain.validate(0)  # Inclusive bounds
        True
        >>> domain.validate(100)  # Inclusive bounds
        True
        """
        if not isinstance(value, (int, float)):
            return False
        if math.isnan(value):
            return False
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True

    def explain(self, value: Any, stats: HistoryStatistics | None = None) -> str:
        """
        Explain why a value is valid or invalid for this domain.

        Provides a human-readable explanation of validation results,
        including specific reasons for failure when applicable.

        Parameters
        ----------
        value : Any
            Value to explain validation for.
        stats : HistoryStatistics | None, optional
            Additional stats for explanation (not used in this implementation
            but included for interface compatibility). Default is None.

        Returns
        -------
        str
            Explanation of validation result. Includes:
            - Non-numeric type rejection
            - Below minimum bound rejection
            - Above maximum bound rejection
            - Success confirmation

        Examples
        --------
        >>> from procela.core.variable import RangeDomain
        >>>
        >>> domain = RangeDomain(min_value=0, max_value=100)
        >>> domain.explain(50)
        'Value 50 is valid in RangeDomain.'
        >>> domain.explain(-10)
        'Value -10 is less than minimum 0.'
        >>> domain.explain(150)
        'Value 150 is greater than maximum 100.'
        >>> domain.explain("fifty")
        'Value fifty is not numeric.'

        >>> # Domain with only lower bound
        >>> positive_domain = RangeDomain(min_value=0)
        >>> positive_domain.explain(-5)
        'Value -5 is less than minimum 0.'
        >>> positive_domain.explain(42)
        'Value 42 is valid in RangeDomain.'

        >>> # Domain with only upper bound
        >>> negative_domain = RangeDomain(max_value=0)
        >>> negative_domain.explain(5)
        'Value 5 is greater than maximum 0.'
        """
        if not isinstance(value, (int, float)):
            return f"Value {value} is not numeric."
        if self.min_value is not None and value < self.min_value:
            return f"Value {value} is less than minimum {self.min_value}."
        if self.max_value is not None and value > self.max_value:
            return f"Value {value} is greater than maximum {self.max_value}."
        return f"Value {value} is valid in RangeDomain."
