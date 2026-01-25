"""
Defines the data structure for representing a quantified trend.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/assessment/trend.html

Examples Reference
------------------
https://procela.org/docs/examples/core/assessment/trend.html
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class TrendResult:
    """
    Contains the numerical result of a trend assessment.

    Parameters
    ----------
    value : float
        The quantified magnitude of the trend.
    direction : Literal["up", "down", "stable"]
        The categorical classification of the trend.
    threshold : float
        The positive reference value against which the trend is measured.

    Returns
    -------
    None
        Instantiates an immutable data container.

    Raises
    ------
    ValueError
        If `direction` is not "up", "down", or "stable".
        If `threshold` is not positive.
    """

    value: float
    direction: Literal["up", "down", "stable"]
    threshold: float

    def __post_init__(self) -> None:
        """
        Validate the parameters after instantiation.

        Raises
        ------
        ValueError
            If `direction` is not "up", "down", or "stable".
            If `threshold` is not positive.
        """
        if self.direction not in ("up", "down", "stable"):
            raise ValueError(
                f"Direction must be 'up', 'down', or 'stable', got '{self.direction}'"
            )
        if self.threshold <= 0:
            raise ValueError(f"Threshold must be positive, got {self.threshold}")

    def confidence(self) -> float:
        """
        Compute a normalized confidence score based on the trend value and threshold.

        Returns
        -------
        float
            A value between 0.0 and 1.0.
        """
        if self.direction == "stable":
            return 0.0
        # Avoid division by zero with a small epsilon
        return min(1.0, abs(self.value) / max(self.threshold, 1e-9))

    def zscore(self, std: float | None) -> float | None:
        """
        Compute the Z-score of the trend value given a standard deviation.

        Parameters
        ----------
        std : float | None
            The standard deviation for normalization.

        Returns
        -------
        float | None
            The normalized Z-score, or `None` if the input is `None` or zero.

        Raises
        ------
        ValueError
            If `std` is negative.
        """
        if std is None:
            return None
        if std == 0:
            return None
        if std < 0:
            raise ValueError(f"Standard deviation must be positive, got {std}")
        return self.value / std
