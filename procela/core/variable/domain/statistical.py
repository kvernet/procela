"""
Statistical value domains for Procela.

This module provides domain classes for numeric values with statistical
validation based on historical data (mean and standard deviation).

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/domain/statistical.html
"""

from __future__ import annotations

from typing import Any

from ...memory.variable.statistics import HistoryStatistics
from .value import ValueDomain


class StatisticalDomain(ValueDomain):
    """
    Numeric domain with statistical validation based on historical data.

    This domain validates numeric values based on statistical bounds computed
    from historical data. Values must fall within `k` standard deviations
    from the mean of historical data provided via HistoryStatistics.

    Attributes
    ----------
    k : float
        Number of standard deviations from the mean for validation bounds.
        Default is 3.0 (approximately 99.7% of data in normal distribution).
    name : str
        Optional name for the domain, inherited from ValueDomain.

    Notes
    -----
    - Validation requires HistoryStatistics (mean and std) to be provided
    - Without HistoryStatistics, validation always passes
    - The bounds are inclusive: [mean - k*std, mean + k*std]
    - This is useful for outlier detection and data quality monitoring
    - For normal distributions, common k values are:
        - 1.0: ~68% of data
        - 2.0: ~95% of data
        - 3.0: ~99.7% of data

    Examples
    --------
    >>> from procela.core.variable import StatisticalDomain, HistoryStatistics
    >>>
    >>> # Create domain for values within 2 standard deviations
    >>> domain = StatisticalDomain(k=2.0, name="two_sigma")
    >>> domain.k
    2.0

    >>> # Validation with stats
    >>> stats = HistoryStatistics(2, 20, 640, None, None, None, 1.0, None, frozenset())
    >>> domain.validate(9, stats)
    True
    >>> domain.validate(45, stats)
    False

    >>> # Validation without stats passes
    >>> domain.validate(999)
    True

    >>> # Validation with incomplete stats passes
    >>> stats = HistoryStatistics(1, 20, 640, None, None, None, 1.0, None, frozenset())
    >>> domain.validate(50, stats)  # Missing std
    True
    """

    def __init__(
        self,
        *,
        k: float = 3.0,
        name: str = "",
    ) -> None:
        """
        Initialize a StatisticalDomain.

        Parameters
        ----------
        k : float, optional
            Number of standard deviations from the mean for validation bounds.
            Must be non-negative. Default is 3.0.
        name : str, optional
            Name for the domain. Default is empty string.

        Raises
        ------
        ValueError
            If k is negative.
        TypeError
            If k is not numeric.

        Examples
        --------
        >>> from procela.core.variable import StatisticalDomain
        >>>
        >>> # Default domain (3 sigma)
        >>> domain1 = StatisticalDomain()
        >>> domain1.k
        3.0

        >>> # Domain with 2 sigma bounds
        >>> domain2 = StatisticalDomain(k=2.0, name="quality_check")
        >>> domain2.k
        2.0
        >>> domain2.name
        'quality_check'

        >>> # Zero sigma domain (only allows exact mean)
        >>> domain3 = StatisticalDomain(k=0.0)
        >>> domain3.k
        0.0

        >>> # Negative k raises ValueError
        >>> StatisticalDomain(k=-1.0)
        Traceback (most recent call last):
            ...
        ValueError: k must be non-negative, got -1.0
        """
        super().__init__(name=name)
        if not isinstance(k, int | float):
            raise TypeError(f"k must be numeric, got {k}")
        if k < 0:
            raise ValueError(f"k must be non-negative, got {k}")

        self.k = k

    def validate(self, value: Any, stats: HistoryStatistics | None = None) -> bool:
        """
        Validate that a value is within k standard deviations of mean.

        Checks if the value falls within the inclusive range:
        [mean - k*std, mean + k*std]

        If stats is None, missing, or incomplete (missing mean or std),
        validation passes by default (returns True).

        Parameters
        ----------
        value : Any
            Value to validate. Should be numeric (int or float).
            Non-numeric values will fail comparison operations.
        stats : HistoryStatistics | None, optional
            HistoryStatistics containing statistical parameters:
            - "mean": float - mean of historical data
            - "std": float - standard deviation of historical data
            Default is None.

        Returns
        -------
        bool
            True if:
            - HistoryStatistics is None or missing mean/std
            - Value is within [mean - k*std, mean + k*std]
            False otherwise.

        Raises
        ------
        TypeError
            If value is not comparable with numeric bounds (e.g., string).

        Notes
        -----
        - The validation is lenient by default when stats is insufficient
        - This prevents false failures when statistical data is unavailable
        - Non-numeric values will raise TypeError when compared

        Examples
        --------
        >>> from procela.core.variable import StatisticalDomain, HistoryStatistics
        >>>
        >>> domain = StatisticalDomain(k=2.0)
        >>> stats = HistoryStatistics(
        ...     2, 20, 640, None, None, None, 1.0, None, frozenset()
        ... )

        >>> domain.validate(45, stats)
        False
        >>> domain.validate(55, stats)
        False
        >>> domain.validate(40, stats)
        False
        >>> domain.validate(24, stats)
        True

        >>> # Values outside bounds
        >>> domain.validate(49, stats)
        False
        >>> domain.validate(61, stats)
        False

        >>> # Insufficient stats passes validation
        >>> domain.validate(999)  # No stats
        True
        >>> stats = HistoryStatistics(
        ...     1, 20, 640, None, None, None, 1.0, None, frozenset()
        ... )
        >>> domain.validate(999, stats)  # Missing std
        True
        >>> stats = HistoryStatistics(
        ...     2, 20, 640, None, None, None, 1.0, None, frozenset()
        ... )
        >>> domain.validate(999, stats)
        False

        >>> # Edge case: k = 0 (only exact mean allowed)
        >>> exact_domain = StatisticalDomain(k=0.0)
        >>> exact_domain.validate(10, stats)
        True
        >>> exact_domain.validate(11, stats)
        False
        """
        if not isinstance(value, (int, float)):
            return False

        if not stats:
            return True

        mean, std = stats.mean(), stats.std()

        if mean is None or std is None:
            return True

        return bool(mean - self.k * std <= value <= mean + self.k * std)

    def explain(self, value: Any, stats: HistoryStatistics | None = None) -> str:
        """
        Explain statistical validation bounds and result.

        Provides a human-readable explanation of the statistical bounds
        and whether the value falls within them.

        Parameters
        ----------
        value : Any
            Value to explain validation for.
        stats : HistoryStatistics | None, optional
            HistoryStatistics containing statistical parameters:
            - "mean": float - mean of historical data
            - "std": float - standard deviation of historical data
            Default is None.

        Returns
        -------
        str
            Explanation string. Either:
            - "Insufficient history for statistical validation." if stats
              is missing mean or std
            - "Value X must be within [lower, upper]." showing the
              calculated bounds

        Examples
        --------
        >>> from procela.core.variable import StatisticalDomain, HistoryStatistics
        >>>
        >>> domain = StatisticalDomain(k=2.0)

        >>> stats = HistoryStatistics(
        ...     4, 400, 40400, None, None, None, 1.0, None, frozenset()
        ... )
        >>> domain.explain(95, stats)
        'Value 95 is within [80.0, 120.0].'
        >>> domain.explain(400, stats)
        'Value 400 is not within [80.0, 120.0].'

        >>> # Insufficient stats
        >>> domain.explain(50)  # No stats
        'Insufficient history for statistical validation.'
        >>> stats = HistoryStatistics(
        ...     1, 20, 640, None, None, None, 1.0, None, frozenset()
        ... )
        >>> domain.explain(50, stats)  # Missing std
        'Insufficient history for statistical validation.'

        >>> domain3 = StatisticalDomain(k=3.0)
        >>> stats = HistoryStatistics(
        ...     4, 400, 40400, None, None, None, 1.0, None, frozenset()
        ... )
        >>> domain3.explain(195, stats)
        'Value 195 is not within [70.0, 130.0].'

        >>> stats = HistoryStatistics(
        ...     2, 20, 400, None, None, None, 1.0, None, frozenset()
        ... )
        >>> domain.explain(10, stats)
        'Value 10 is within [-10.0, 30.0].'
        """
        if not isinstance(value, (int, float)):
            return "Value must be numeric."

        mean = stats.mean() if stats else None
        std = stats.std() if stats else None

        if mean is None or std is None:
            return "Insufficient history for statistical validation."

        lower = mean - self.k * std
        upper = mean + self.k * std
        if lower <= value <= upper:
            return f"Value {value} is within [{lower}, {upper}]."
        return f"Value {value} is not within [{lower}, {upper}]."

    def trend_threshold(
        self,
        stats: HistoryStatistics,
        *,
        absolute: float | None = None,
        std_factor: float | None = 1.0,
    ) -> float | None:
        """
        Compute trend threshold for some history statistics.

        Parameters
        ----------
        absolute : float | None
            The minimum deviation from baseline that warrants attention.
        std_factor : float | None
            The std factor used if trend_threshold is None

        Returns
        -------
        float | None
            The computed trend threshold or None

        Examples
        --------
        >>> from procela.core.variable import StatisticalDomain, HistoryStatistics
        >>>
        >>> domain = StatisticalDomain(k=2.0)
        >>> stats = HistoryStatistics(
        ...     4, 400, 40400, None, None, None, 1.0, None, frozenset()
        ... )
        >>> domain.trend_threshold(stats, absolute=0.75)
        0.75

        >>> domain = StatisticalDomain(k=3.0)
        >>> domain.trend_threshold(stats, std_factor=0.03)
        0.3
        """
        if absolute is None and std_factor is None:
            raise ValueError("Provide either absolute or std_factor.")

        if absolute is not None:
            return absolute

        std = stats.std()
        if std is not None and std_factor is not None:
            return std_factor * std

        return None
