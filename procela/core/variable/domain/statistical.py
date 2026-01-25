"""
Statistical value domains for Procela.

This module provides domain classes for numeric values with statistical
validation based on historical data (mean and standard deviation).

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/domain/statistical.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/variable/domain/statistical.html
"""

from __future__ import annotations

from typing import Any

from ...assessment.statistics import StatisticsResult
from .value import ValueDomain


class StatisticalDomain(ValueDomain):
    """
    Numeric domain with statistical validation based on historical data.

    This domain validates numeric values based on statistical bounds computed
    from historical data. Values must fall within `k` standard deviations
    from the mean of historical data provided via StatisticsResult.

    Attributes
    ----------
    k : float
        Number of standard deviations from the mean for validation bounds.
        Default is 3.0 (approximately 99.7% of data in normal distribution).
    name : str
        Optional name for the domain, inherited from ValueDomain.

    Notes
    -----
    - Validation requires StatisticsResult (mean and std) to be provided
    - Without StatisticsResult, validation always passes
    - The bounds are inclusive: [mean - k*std, mean + k*std]
    - This is useful for outlier detection and data quality monitoring
    - For normal distributions, common k values are:
        - 1.0: ~68% of data
        - 2.0: ~95% of data
        - 3.0: ~99.7% of data
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
        """
        super().__init__(name=name)
        if not isinstance(k, int | float):
            raise TypeError(f"k must be numeric, got {k}")
        if k < 0:
            raise ValueError(f"k must be non-negative, got {k}")

        self.k = k

    def validate(self, value: Any, stats: StatisticsResult | None = None) -> bool:
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
        stats : StatisticsResult | None, optional
            StatisticsResult containing statistical parameters:
            - "mean": float - mean of historical data
            - "std": float - standard deviation of historical data
            Default is None.

        Returns
        -------
        bool
            True if:
            - StatisticsResult is None or missing mean/std
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
        """
        if not isinstance(value, (int, float)):
            return False

        if not stats:
            return True

        mean, std = stats.mean, stats.std

        if mean is None or std is None:
            return True

        return bool(mean - self.k * std <= value <= mean + self.k * std)

    def explain(self, value: Any, stats: StatisticsResult | None = None) -> str:
        """
        Explain statistical validation bounds and result.

        Provides a human-readable explanation of the statistical bounds
        and whether the value falls within them.

        Parameters
        ----------
        value : Any
            Value to explain validation for.
        stats : StatisticsResult | None, optional
            StatisticsResult containing statistical parameters:
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
        """
        if not isinstance(value, (int, float)):
            return "Value must be numeric."

        mean = stats.mean if stats else None
        std = stats.std if stats else None

        if mean is None or std is None:
            return "Insufficient history for statistical validation."

        lower = mean - self.k * std
        upper = mean + self.k * std
        if lower <= value <= upper:
            return f"Value {value} is within [{lower}, {upper}]."
        return f"Value {value} is not within [{lower}, {upper}]."

    def trend_threshold(
        self,
        stats: StatisticsResult,
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
        """
        if absolute is None and std_factor is None:
            raise ValueError("Provide either absolute or std_factor.")

        if absolute is not None:
            return absolute

        std = stats.std
        if std is not None and std_factor is not None:
            return std_factor * std

        return None
