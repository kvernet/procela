"""
Categorical value domains for Procela.

This module provides domain classes for categorical values with finite sets.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/domain/categorical.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/variable/domain/categorical.html
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

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/variable/domain/categorical.html

    Examples Reference
    -------------------
    https://procela.org/docs/examples/core/variable/domain/categorical.html
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
        """
        if value in self.categories:
            return f"Value {value} is allowed in categories {self.categories}."
        return f"Value {value} is not in allowed categories {self.categories}."
