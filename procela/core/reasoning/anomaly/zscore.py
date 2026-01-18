"""
Z-Score Anomaly Detector for the Procela Framework.

This module implements a Z-Score based anomaly detector, a fundamental
statistical method for identifying outliers by measuring how many standard
deviations a data point is from the mean. This detector is particularly
effective for data that is approximately normally distributed and is a
cornerstone of univariate statistical process control.

The Z-Score (standard score) is calculated as:
    z = |x - mu| / sigma
where:
    x is the most recent observation
    mu is the sample mean
    sigma is the sample standard deviation
"""

from __future__ import annotations

from typing import ClassVar

from ...memory.variable.statistics import HistoryStatistics
from ..result import AnomalyResult
from .base import AnomalyDetector


class ZScoreDetector(AnomalyDetector):
    """
    Z-Score based anomaly detector for univariate statistical control.

    This detector implements the classic Z-Score method for anomaly detection,
    flagging observations that fall outside a specified number of standard
    deviations from the mean. It's one of the simplest yet most widely used
    statistical anomaly detection methods, particularly effective for
    monitoring processes with stable, normally distributed measurements.

    The detector requires at least 2 samples to estimate standard deviation
    meaningfully and handles edge cases such as zero standard deviation
    or insufficient data gracefully.

    Parameters
    ----------
    threshold : float, optional
        The anomaly detection threshold in standard deviation units.
        Observations with |Z-Score| ≥ threshold are flagged as anomalies.
        Typical values are 2.0 (≈95% confidence) to 3.0 (≈99.7% confidence).
        Must be > 0. Default is 3.0.

    Attributes
    ----------
    name : ClassVar[str]
        Class attribute identifying this detector as "ZScoreDetector".

    threshold : float
        The anomaly detection threshold in standard deviation units.

    Methods
    -------
    detect(stats: HistoryStatistics) -> AnomalyResult
        Detect anomalies using Z-Score method.

    See Also
    --------
    AnomalyDetector : Abstract base class for all anomaly detectors.
    HistoryStatistics : Statistical summary containing mean and std.
    AnomalyResult : Structured container for anomaly detection results.

    Notes
    -----
    The Z-Score method assumes:
    1. Data is approximately normally distributed
    2. Mean and standard deviation are stable over time
    3. Observations are independent and identically distributed

    For non-normal distributions or time-varying statistics, consider
    complementary methods like EWMADetector or other adaptive approaches.

    The "≥" operator (score >= threshold) is used for anomaly determination,
    meaning values exactly at the threshold are considered anomalous. This
    provides a clear, deterministic boundary for anomaly classification.

    Examples
    --------
    >>> from procela.core.reasoning import ZScoreDetector
    >>> from procela.core.memory import HistoryStatistics
    >>>
    >>> # Create detector with 3-sigma threshold
    >>> detector = ZScoreDetector(threshold=3.0)
    >>> # Create statistics with sufficient data
    >>> stats = HistoryStatistics(
    ...     count=10,
    ...     sum=1000.0,
    ...     sumsq=100250.0,
    ...     min=None,
    ...     max=None,
    ...     last_value=115.0,
    ...     confidence_sum=None,
    ...     ewma=108.0,
    ...     sources=frozenset()
    ... )
    >>> result = detector.detect(stats)
    >>> result.score  # abs(115-100)/5 = 3.0
    3.0
    >>> result.is_anomaly  # 3.0 >= 3.0
    True
    >>> result.method
    'ZScoreDetector'
    """

    name: ClassVar[str] = "ZScoreDetector"

    def __init__(self, threshold: float = 3.0) -> None:
        """
        Initialize a Z-Score anomaly detector with specified threshold.

        Parameters
        ----------
        threshold : float, optional
            Anomaly threshold in standard deviation units.
            Must satisfy threshold > 0. Default is 3.0.

        Raises
        ------
        ValueError
            If threshold is not positive (<= 0).

        Examples
        --------
        >>> from procela.core.reasoning import ZScoreDetector
        >>>
        >>> detector = ZScoreDetector(threshold=2.5)
        >>> detector.threshold
        2.5
        >>> detector.name
        'ZScoreDetector'
        """
        if threshold <= 0:
            raise ValueError(f"Threshold must be > 0, got {threshold}")
        self.threshold = threshold

    def detect(self, stats: HistoryStatistics) -> AnomalyResult:
        """
        Detect anomalies using Z-Score statistical method.

        This method calculates the Z-Score of the most recent observation
        relative to the historical mean and standard deviation. The Z-Score
        represents how many standard deviations the observation is from
        the mean, with higher absolute values indicating greater deviation.

        The method handles several edge cases gracefully:
        1. Insufficient data (count < 2): Returns non-anomalous result
        2. Missing statistics (std or mean is None): Returns non-anomalous
        3. Zero standard deviation: Returns non-anomalous (degenerate case)
        4. Missing last value: Returns non-anomalous

        Parameters
        ----------
        stats : HistoryStatistics
            Statistical summary containing:
            - count: Number of observations (must be ≥ 2 for detection)
            - mean: Historical mean (callable or property)
            - std: Historical standard deviation (callable or property)
            - last_value: Most recent observation

        Returns
        -------
        AnomalyResult
            Structured result containing:
            - is_anomaly: True if |Z-Score| ≥ threshold
            - score: Z-Score value (None if cannot be calculated)
            - threshold: The detector's threshold value
            - method: "ZScoreDetector"
            - metadata: Additional diagnostic information

        Raises
        ------
        TypeError
            If stats is not a HistoryStatistics instance.

        Examples
        --------
        >>> from procela.core.reasoning import ZScoreDetector
        >>> from procela.core.memory import HistoryStatistics
        >>>
        >>> # Normal case: value within 2 standard deviations
        >>> detector = ZScoreDetector(threshold=2.0)
        >>> # count=10, mean=50.0, std=5.0, last_value=58.0
        >>> stats1 = HistoryStatistics(
        ...     count=10,
        ...     sum=500.0,
        ...     sumsq=25250.0,
        ...     min=None,
        ...     max=None,
        ...     last_value=58.0,
        ...     confidence_sum=None,
        ...     ewma=60.0,
        ...     sources=frozenset()
        ... )
        >>> result1 = detector.detect(stats1)
        >>> result1.score  # abs(58-50)/5 = 1.6
        1.6
        >>> result1.is_anomaly  # 1.6 < 2.0
        False
        >>> # Anomaly case: value beyond threshold
        >>> stats2 = HistoryStatistics(
        ...     count=10,
        ...     sum=500.0,
        ...     sumsq=25250.0,
        ...     min=None,
        ...     max=None,
        ...     last_value=62.0,
        ...     confidence_sum=None,
        ...     ewma=60.0,
        ...     sources=frozenset()
        ... )
        >>> result2 = detector.detect(stats2)
        >>> result2.score  # abs(62-50)/5 = 2.4
        2.4
        >>> result2.is_anomaly  # 2.4 >= 2.0
        True
        """
        # Validate input type
        if not isinstance(stats, HistoryStatistics):
            raise TypeError(
                f"stats must be HistoryStatistics, got {type(stats).__name__}"
            )

        # Check for sufficient data
        if stats.count < 2:
            return AnomalyResult(
                is_anomaly=False,
                score=None,
                threshold=self.threshold,
                method=self.name,
                metadata={
                    "reason": "insufficient data",
                    "count": stats.count,
                    "required_count": 2,
                },
            )

        mean, std = stats.mean(), stats.std()
        if mean is None:
            return AnomalyResult(
                is_anomaly=False,
                score=None,
                threshold=self.threshold,
                method=self.name,
                metadata={"reason": "missing mean"},
            )

        if std is None:
            return AnomalyResult(
                is_anomaly=False,
                score=None,
                threshold=self.threshold,
                method=self.name,
                metadata={"reason": "missing standard deviation"},
            )

        # Check for last value
        if stats.last_value is None:
            return AnomalyResult(
                is_anomaly=False,
                score=None,
                threshold=self.threshold,
                method=self.name,
                metadata={"reason": "missing last value"},
            )

        # Handle degenerate distribution (zero variance)
        if std == 0:
            return AnomalyResult(
                is_anomaly=False,
                score=None,
                threshold=self.threshold,
                method=self.name,
                metadata={
                    "reason": "degenerate distribution",
                    "mean": mean,
                    "last_value": stats.last_value,
                },
            )

        # Calculate Z-Score
        score = abs(stats.last_value - mean) / std
        is_anomaly = score >= self.threshold

        # Prepare comprehensive metadata
        metadata = {
            "mean": mean,
            "std": std,
            "last_value": stats.last_value,
            "count": stats.count,
            "z_score": score,
            "threshold": self.threshold,
            "deviation": stats.last_value - mean,
            "absolute_deviation": abs(stats.last_value - mean),
        }

        return AnomalyResult(
            is_anomaly=is_anomaly,
            score=score,
            threshold=self.threshold,
            method=self.name,
            metadata=metadata,
        )

    def __repr__(self) -> str:
        """Return unambiguous string representation."""
        return f"ZScoreDetector(threshold={self.threshold})"

    def __str__(self) -> str:
        """Return human-readable description."""
        return f"Z-Score Anomaly Detector ({self.threshold} threshold)"
