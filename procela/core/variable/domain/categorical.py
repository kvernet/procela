"""
Categorical value domains for Procela.

This module provides domain classes for categorical values with finite sets.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/domain/categorical.html
"""

from __future__ import annotations

from typing import Any, Iterable

from ...memory.variable.statistics import HistoryStatistics
from .value import ValueDomain


class CategoricalDomain(ValueDomain):
    """
    Domain for categorical values with a finite set of allowed values.

    A categorical domain defines a finite set of allowed values. Any value
    not in this set is considered invalid. This is useful for representing
    enumerated types, classifications, or any discrete set of options.

    Attributes
    ----------
    categories : set
        Set of allowed values.
        The original ordering from the input iterable is not preserved.
    name : str
        Optional name for the domain, inherited from ValueDomain.

    Notes
    -----
    The categories are stored as a set, which means:
      - Duplicate values in the input are automatically deduplicated
      - Order is not preserved
      - Only hashable values can be used as categories

    Examples
    --------
    >>> from procela.core.variable import CategoricalDomain
    >>>
    >>> # Domain for traffic light colors
    >>> domain = CategoricalDomain(["red", "yellow", "green"], name="traffic_light")
    >>> domain.validate("red")
    True
    >>> domain.validate("blue")
    False
    >>> domain.categories
    {'red', 'green', 'yellow'}

    >>> # Domain with numeric categories
    >>> status_domain = CategoricalDomain([0, 1, 2, 3], name="status_codes")
    >>> status_domain.validate(1)
    True
    >>> status_domain.validate(99)
    False

    >>> # Domain with mixed types (not recommended but possible)
    >>> mixed_domain = CategoricalDomain(["low", "medium", "high", 1, 2, 3])
    >>> mixed_domain.validate("low")
    True
    >>> mixed_domain.validate(2)
    True
    """

    def __init__(self, categories: Iterable[Any], name: str = "") -> None:
        """
        Initialize a CategoricalDomain with a set of allowed values.

        Parameters
        ----------
        categories : Iterable[Any]
            Iterable of allowed values. Can be any iterable (list, tuple, set, etc.).
            Values must be hashable to be stored in a set.
        name : str, optional
            Name for the domain. Default is empty string.

        Raises
        ------
        TypeError
            If any value in categories is not hashable (e.g., list, dict).

        Warnings
        --------
        Using unhashable values (like lists or dicts) as categories will
        raise a TypeError when converting to set.

        Examples
        --------
        >>> from procela.core.variable import CategoricalDomain
        >>>
        >>> domain = CategoricalDomain(["cat", "dog", "bird"], name="pets")
        >>> len(domain.categories)
        3
        >>> "cat" in domain.categories
        True

        >>> # Duplicates are automatically removed
        >>> domain = CategoricalDomain(["a", "b", "a", "c", "b"])
        >>> len(domain.categories)
        3

        >>> # Empty domain is allowed
        >>> empty_domain = CategoricalDomain([])
        >>> len(empty_domain.categories)
        0
        """
        super().__init__(name)
        self.categories = set(categories)

    def validate(self, value: Any, stats: HistoryStatistics | None = None) -> bool:
        """
        Validate that a value is in the allowed categories.

        Checks if the value exists in the domain's set of allowed categories
        using set membership testing.

        Parameters
        ----------
        value : Any
            Value to validate. Can be any type, but must match exactly
            (including type) one of the categories to be valid.
        stats : HistoryStatistics | None, optional
            Additional stats for validation (not used in this implementation
            but included for interface compatibility). Default is None.

        Returns
        -------
        bool
            True if the value is in the categories set, False otherwise.

        Notes
        -----
        - Validation uses exact matching: `value in self.categories`
        - The comparison respects Python's equality semantics (e.g., 1 == 1.0 is True)
        - Empty domains will reject all values

        Examples
        --------
        >>> from procela.core.variable import CategoricalDomain
        >>>
        >>> domain = CategoricalDomain(["apple", "banana", "orange"])
        >>> domain.validate("apple")
        True
        >>> domain.validate("grape")
        False
        >>> domain.validate("Apple")  # Case-sensitive
        False

        >>> # Numeric matching respects Python equality
        >>> num_domain = CategoricalDomain([1, 2, 3])
        >>> num_domain.validate(1)
        True
        >>> num_domain.validate(1.0)  # 1 == 1.0 in Python
        True
        >>> num_domain.validate("1")  # String "1" != integer 1
        False

        >>> # Empty domain rejects everything
        >>> empty_domain = CategoricalDomain([])
        >>> empty_domain.validate("any_value")
        False
        """
        return value in self.categories

    def explain(self, value: Any, stats: HistoryStatistics | None = None) -> str:
        """
        Explain why a value is valid or invalid for this domain.

        Provides a human-readable explanation indicating whether the value
        is in the allowed categories set or not.

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
            Explanation of validation result. Either:
            - "Value X is allowed in categories {set}." (if valid)
            - "Value X is not in allowed categories {set}." (if invalid)

        Notes
        -----
        The string representation of the categories set may vary between
        Python versions and runs due to set's unordered nature.

        Examples
        --------
        >>> from procela.core.variable import CategoricalDomain
        >>>
        >>> domain = CategoricalDomain(["red", "green", "blue"])
        >>> domain.explain("red")
        "Value red is allowed in categories {'red', 'blue', 'green'}."
        >>> domain.explain("yellow")
        "Value yellow is not in allowed categories {'red', 'blue', 'green'}."

        >>> # With numeric categories
        >>> num_domain = CategoricalDomain([1, 2, 3])
        >>> num_domain.explain(2)
        'Value 2 is allowed in categories {1, 2, 3}.'
        >>> num_domain.explain(4)
        'Value 4 is not in allowed categories {1, 2, 3}.'

        >>> # Empty domain
        >>> empty_domain = CategoricalDomain([])
        >>> empty_domain.explain("test")
        'Value test is not in allowed categories set().'
        """
        if value in self.categories:
            return f"Value {value} is allowed in categories {self.categories}."
        return f"Value {value} is not in allowed categories {self.categories}."
