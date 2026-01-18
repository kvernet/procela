"""
EWMA (Exponentially Weighted Moving Average) Anomaly Detector for Procela.

This detector uses precomputed EWMA statistics from HistoryStatistics to
identify anomalies based on the deviation of recent values from the EWMA
estimate. It's a lightweight detector that leverages the framework's
built-in statistical computations rather than maintaining its own state.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/anomaly/ewma.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/anomaly/ewma.html
"""

from __future__ import annotations

from typing import ClassVar

from ...memory.variable.statistics import HistoryStatistics
from ..result import AnomalyResult
from .base import AnomalyDetector


class EWMADetector(AnomalyDetector):
    """
    EWMA-based anomaly detector using precomputed statistics.

    This detector identifies anomalies by comparing the most recent value
    against the EWMA (Exponentially Weighted Moving Average) computed by
    the HistoryStatistics object. Anomalies are detected when the
    standardized deviation (z-score) exceeds a configurable threshold.

    The detection logic is:
        score = abs(last_value - stats.ewma) / std
        is_anomaly = score > threshold

    Where:
        - last_value: The most recent value from statistics
        - stats.ewma: Precomputed EWMA from HistoryStatistics
        - std: Standard deviation from HistoryStatistics
        - threshold: Configurable anomaly threshold

    Parameters
    ----------
    threshold : float, optional
        The anomaly detection threshold in standard deviation units.
        Values exceeding this threshold are flagged as anomalies.
        Must be > 0. Default is 3.0.

    Attributes
    ----------
    name : ClassVar[str]
        Class attribute identifying this detector as "EWMADetector".

    threshold : float
        The anomaly detection threshold.

    Notes
    -----
    This detector assumes that HistoryStatistics provides:
    - last_value: The most recent observed value
    - ewma: The exponentially weighted moving average
    - std: The standard deviation for normalization

    The detector is stateless and relies entirely on the input statistics,
    making it suitable for distributed or parallel processing scenarios.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/anomaly/ewma.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/reasoning/anomaly/ewma.html
    """

    name: ClassVar[str] = "EWMADetector"

    def __init__(self, threshold: float = 3.0) -> None:
        """
        Initialize an EWMA anomaly detector.

        Parameters
        ----------
        threshold : float, optional
            Anomaly threshold in standard deviation units.
            Must be > 0. Default is 3.0.

        Raises
        ------
        ValueError
            If threshold is not positive.
        """
        if threshold <= 0:
            raise ValueError(f"threshold must be > 0, got {threshold}")
        self.threshold = threshold

    def detect(self, stats: HistoryStatistics) -> AnomalyResult:
        """
        Detect anomalies using precomputed EWMA statistics.

        The anomaly score is calculated as the absolute difference between
        the most recent value and the EWMA, normalized by the standard
        deviation. If the score exceeds the threshold, an anomaly is
        detected.

        Parameters
        ----------
        stats : HistoryStatistics
            Statistical summary containing last_value, ewma, and std.
            All three attributes must be available for detection.

        Returns
        -------
        AnomalyResult
            Structured result containing:
            - is_anomaly: True if score > threshold
            - score: The calculated anomaly score
            - threshold: The detector's threshold value
            - method: "EWMADetector"
            - metadata: Additional detection details

        Raises
        ------
        ValueError
            If required statistics (last_value, ewma, or std) are missing
            or if std is zero (cannot normalize).
        TypeError
            If stats is not a HistoryStatistics instance.
        """
        # Validate input type
        if not isinstance(stats, HistoryStatistics):
            raise TypeError(
                f"stats must be HistoryStatistics, got {type(stats).__name__}"
            )

        # Check for required statistics
        std = stats.std()
        if stats.last_value is None:
            raise ValueError("stats.last_value is None")
        if stats.ewma is None:
            raise ValueError("stats.ewma is None")
        if std is None:
            raise ValueError("stats.std is None")

        # Ensure we can calculate the score (avoid division by zero)
        if std == 0:
            raise ValueError("stats.std is zero, cannot normalize")

        # Calculate anomaly score
        score = abs(stats.last_value - stats.ewma) / std

        # Determine if anomaly exists
        is_anomaly = score > self.threshold

        # Prepare metadata
        metadata = {
            "last_value": stats.last_value,
            "ewma": stats.ewma,
            "std": std,
            "difference": stats.last_value - stats.ewma,
        }

        return AnomalyResult(
            is_anomaly=is_anomaly,
            score=score,
            threshold=self.threshold,
            method=self.name,
            metadata=metadata,
        )

    def __repr__(self) -> str:
        """
        Return unambiguous string representation.

        Returns
        -------
        str
            Unambiguous string representation.
        """
        return f"EWMADetector(threshold={self.threshold})"

    def __str__(self) -> str:
        """
        Return human-readable description.

        Returns
        -------
        str
            Human-readable description.
        """
        return f"EWMA Anomaly Detector (threshold={self.threshold})"
