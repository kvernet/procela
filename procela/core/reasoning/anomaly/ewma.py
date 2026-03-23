"""
EWMA (Exponentially Weighted Moving Average) Anomaly Detector for Procela.

This detector uses precomputed EWMA statistics from StatisticsResult to
identify anomalies based on the deviation of recent values from the EWMA
estimate. It's a lightweight detector that leverages the framework's
built-in statistical computations rather than maintaining its own state.

Examples
--------
>>> from procela import (
...     Variable,
...     StatisticalDomain,
...     VariableRecord,
...     EWMADetector
... )
>>>
>>> var = Variable("var", StatisticalDomain())
>>> var.set(VariableRecord(value=12, confidence=0.98))
>>> var.set(VariableRecord(value=13, confidence=0.94))
>>> var.set(VariableRecord(value=11, confidence=0.90))
>>> view = var.epistemic()
>>>
>>> detector = EWMADetector()
>>>
>>> result = detector.detect(stats=view.stats)
>>>
>>> print(result.is_anomaly)
False
>>> print(result.confidence())
None
>>> print(result.method)
EWMADetector
>>> print(result.score)
1.114517832966354
>>> print(result.threshold)
3.0
>>> for key, value in result.metadata.items():
...     print(f"{key:10}: {value}")
value     : 11.0
ewma      : 11.91
std       : 0.8164965809277203
difference: -0.9100000000000001

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/anomaly/ewma.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/anomaly/ewma.html
"""

from __future__ import annotations

from typing import ClassVar

from ...assessment.anomaly import AnomalyResult
from ...assessment.statistics import StatisticsResult
from .base import AnomalyDetector


class EWMADetector(AnomalyDetector):
    """
    EWMA-based anomaly detector using precomputed statistics.

    This detector identifies anomalies by comparing the most recent value
    against the EWMA (Exponentially Weighted Moving Average) computed by
    the StatisticsResult object. Anomalies are detected when the
    standardized deviation (z-score) exceeds a configurable threshold.

    The detection logic is:
        score = abs(value - stats.ewma) / std
        is_anomaly = score > threshold

    Where:
        - value: The most recent value from statistics
        - stats.ewma: Precomputed EWMA from StatisticsResult
        - std: Standard deviation from StatisticsResult
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

    Examples
    --------
    >>> from procela import (
    ...     Variable,
    ...     StatisticalDomain,
    ...     VariableRecord,
    ...     EWMADetector
    ... )
    >>>
    >>> var = Variable("var", StatisticalDomain())
    >>> var.set(VariableRecord(value=12, confidence=0.98))
    >>> var.set(VariableRecord(value=13, confidence=0.94))
    >>> var.set(VariableRecord(value=11, confidence=0.90))
    >>> view = var.epistemic()
    >>>
    >>> detector = EWMADetector()
    >>>
    >>> result = detector.detect(stats=view.stats)
    >>>
    >>> print(result.is_anomaly)
    False
    >>> print(result.confidence())
    None
    >>> print(result.method)
    EWMADetector
    >>> print(result.score)
    1.114517832966354
    >>> print(result.threshold)
    3.0
    >>> for key, value in result.metadata.items():
    ...     print(f"{key:10}: {value}")
    value     : 11.0
    ewma      : 11.91
    std       : 0.8164965809277203
    difference: -0.9100000000000001

    Notes
    -----
    This detector assumes that StatisticsResult provides:
    - value: The most recent observed value
    - ewma: The exponentially weighted moving average
    - std: The standard deviation for normalization

    The detector is stateless and relies entirely on the input statistics,
    making it suitable for distributed or parallel processing scenarios.
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

        Examples
        --------
        >>> from procela import (
        ...     Variable,
        ...     StatisticalDomain,
        ...     VariableRecord,
        ...     EWMADetector
        ... )
        >>>
        >>> var = Variable("var", StatisticalDomain())
        >>> var.set(VariableRecord(value=12, confidence=0.98))
        >>> var.set(VariableRecord(value=13, confidence=0.94))
        >>> var.set(VariableRecord(value=11, confidence=0.90))
        >>> view = var.epistemic()
        >>>
        >>> detector = EWMADetector()
        >>>
        >>> result = detector.detect(stats=view.stats)
        >>>
        >>> print(result.is_anomaly)
        False
        >>> print(result.confidence())
        None
        >>> print(result.method)
        EWMADetector
        >>> print(result.score)
        1.114517832966354
        >>> print(result.threshold)
        3.0
        >>> for key, value in result.metadata.items():
        ...     print(f"{key:10}: {value}")
        value     : 11.0
        ewma      : 11.91
        std       : 0.8164965809277203
        difference: -0.9100000000000001
        """
        if threshold <= 0:
            raise ValueError(f"threshold must be > 0, got {threshold}")
        self.threshold = threshold

    def detect(self, stats: StatisticsResult) -> AnomalyResult:
        """
        Detect anomalies using precomputed EWMA statistics.

        The anomaly score is calculated as the absolute difference between
        the most recent value and the EWMA, normalized by the standard
        deviation. If the score exceeds the threshold, an anomaly is
        detected.

        Parameters
        ----------
        stats : StatisticsResult
            Statistical summary containing value, ewma, and std.
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
            If required statistics (value, ewma, or std) are missing
            or if std is zero (cannot normalize).
        TypeError
            If stats is not a StatisticsResult instance.
        """
        # Validate input type
        if not isinstance(stats, StatisticsResult):
            raise TypeError(
                f"stats must be StatisticsResult, got {type(stats).__name__}"
            )

        # Check for required statistics
        std = stats.std
        if stats.value is None:
            raise ValueError("stats.value is None")
        if stats.ewma is None:
            raise ValueError("stats.ewma is None")
        if std is None:
            raise ValueError("stats.std is None")

        # Ensure we can calculate the score (avoid division by zero)
        if std == 0:
            raise ValueError("stats.std is zero, cannot normalize")

        # Calculate anomaly score
        score = abs(stats.value - stats.ewma) / std

        # Determine if anomaly exists
        is_anomaly = score > self.threshold

        # Prepare metadata
        metadata = {
            "value": stats.value,
            "ewma": stats.ewma,
            "std": std,
            "difference": stats.value - stats.ewma,
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
