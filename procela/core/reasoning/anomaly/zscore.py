"""
Z-Score Anomaly Detector for the Procela Framework.

This module implements a Z-Score based anomaly detector, a fundamental
statistical method for identifying outliers by measuring how many standard
deviations a data point is from the mean. This detector is particularly
effective for data that is approximately normally distributed and is a
cornerstone of univariate statistical process control.

Examples
--------
>>> from procela import (
...     Variable,
...     StatisticalDomain,
...     VariableRecord,
...     ZScoreDetector
... )
>>>
>>> var = Variable("var", StatisticalDomain())
>>> var.set(VariableRecord(value=12, confidence=0.98))
>>> var.set(VariableRecord(value=13, confidence=0.94))
>>> var.set(VariableRecord(value=11, confidence=0.90))
>>> view = var.epistemic()
>>>
>>> detector = ZScoreDetector()
>>>
>>> result = detector.detect(stats=view.stats)
>>>
>>> print(result.is_anomaly)
False
>>> print(result.confidence())
None
>>> print(result.method)
ZScoreDetector
>>> print(result.score)
1.2247448713915976
>>> print(result.threshold)
3.0
>>> for key, value in result.metadata.items():
...     print(f"{key:18}: {value}")
mean              : 12.0
std               : 0.8164965809277203
value             : 11.0
count             : 3
z_score           : 1.2247448713915976
threshold         : 3.0
deviation         : -1.0
absolute_deviation: 1.0

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/anomaly/zscore.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/anomaly/zscore.html
"""

from __future__ import annotations

from typing import ClassVar

from ...assessment.anomaly import AnomalyResult
from ...assessment.statistics import StatisticsResult
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

    Examples
    --------
    >>> from procela import (
    ...     Variable,
    ...     StatisticalDomain,
    ...     VariableRecord,
    ...     ZScoreDetector
    ... )
    >>>
    >>> var = Variable("var", StatisticalDomain())
    >>> var.set(VariableRecord(value=12, confidence=0.98))
    >>> var.set(VariableRecord(value=13, confidence=0.94))
    >>> var.set(VariableRecord(value=11, confidence=0.90))
    >>> view = var.epistemic()
    >>>
    >>> detector = ZScoreDetector()
    >>>
    >>> result = detector.detect(stats=view.stats)
    >>>
    >>> print(result.is_anomaly)
    False
    >>> print(result.confidence())
    None
    >>> print(result.method)
    ZScoreDetector
    >>> print(result.score)
    1.2247448713915976
    >>> print(result.threshold)
    3.0
    >>> for key, value in result.metadata.items():
    ...     print(f"{key:18}: {value}")
    mean              : 12.0
    std               : 0.8164965809277203
    value             : 11.0
    count             : 3
    z_score           : 1.2247448713915976
    threshold         : 3.0
    deviation         : -1.0
    absolute_deviation: 1.0

    Notes
    -----
    The Z-Score method assumes:
    1. Data is approximately normally distributed
    2. Mean and standard deviation are stable over time
    3. Observations are independent and identically distributed

    For non-normal distributions or time-varying statistics, consider
    complementary methods like EWMADetector or other adaptive approaches.
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
        >>> from procela import (
        ...     Variable,
        ...     StatisticalDomain,
        ...     VariableRecord,
        ...     ZScoreDetector
        ... )
        >>>
        >>> var = Variable("var", StatisticalDomain())
        >>> var.set(VariableRecord(value=12, confidence=0.98))
        >>> var.set(VariableRecord(value=13, confidence=0.94))
        >>> var.set(VariableRecord(value=11, confidence=0.90))
        >>> view = var.epistemic()
        >>>
        >>> detector = ZScoreDetector()
        >>>
        >>> result = detector.detect(stats=view.stats)
        >>>
        >>> print(result.is_anomaly)
        False
        >>> print(result.confidence())
        None
        >>> print(result.method)
        ZScoreDetector
        >>> print(result.score)
        1.2247448713915976
        >>> print(result.threshold)
        3.0
        >>> for key, value in result.metadata.items():
        ...     print(f"{key:18}: {value}")
        mean              : 12.0
        std               : 0.8164965809277203
        value             : 11.0
        count             : 3
        z_score           : 1.2247448713915976
        threshold         : 3.0
        deviation         : -1.0
        absolute_deviation: 1.0
        """
        if threshold <= 0:
            raise ValueError(f"Threshold must be > 0, got {threshold}")
        self.threshold = threshold

    def detect(self, stats: StatisticsResult) -> AnomalyResult:
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
        4. Missing value: Returns non-anomalous

        Parameters
        ----------
        stats : StatisticsResult
            Statistical summary containing:
            - count: Number of observations (must be ≥ 2 for detection)
            - mean: Historical mean (callable or property)
            - std: Historical standard deviation (callable or property)
            - value: Most recent observation

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
            If stats is not a StatisticsResult instance.
        """
        # Validate input type
        if not isinstance(stats, StatisticsResult):
            raise TypeError(
                f"stats must be StatisticsResult, got {type(stats).__name__}"
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

        mean, std = stats.mean, stats.std
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
        if stats.value is None:
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
                    "value": stats.value,
                },
            )

        # Calculate Z-Score
        score = abs(stats.value - mean) / std
        is_anomaly = score >= self.threshold

        # Prepare comprehensive metadata
        metadata = {
            "mean": mean,
            "std": std,
            "value": stats.value,
            "count": stats.count,
            "z_score": score,
            "threshold": self.threshold,
            "deviation": stats.value - mean,
            "absolute_deviation": abs(stats.value - mean),
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
        return f"ZScoreDetector(threshold={self.threshold})"

    def __str__(self) -> str:
        """
        Return human-readable description.

        Returns
        -------
        str
            Human-readable description.
        """
        return f"Z-Score Anomaly Detector ({self.threshold} threshold)"
