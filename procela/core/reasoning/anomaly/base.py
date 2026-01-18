"""
Anomaly Detection Base Module for the Procela Framework.

This module defines the abstract base class for all anomaly detection
algorithms within Procela's active reasoning engine. Anomaly detectors
are specialized reasoning components that analyze historical statistics
to identify deviations from expected behavior, forming the foundation
for proactive system monitoring and diagnostic reasoning.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from ...memory.variable.statistics import HistoryStatistics
from ..result import AnomalyResult


class AnomalyDetector(ABC):
    """
    Abstract base class for all anomaly detection algorithms in Procela.

    This class defines the uniform interface that all concrete anomaly
    detectors must implement. By providing a consistent abstraction,
    Procela enables polymorphic use of different detection algorithms
    while ensuring type safety and contractual guarantees about anomaly
    detection results.

    Anomaly detectors in Procela analyze `HistoryStatistics` to identify
    statistically significant deviations from expected patterns. They
    translate quantitative statistical evidence into `AnomalyResult`
    objects that include binary classification, confidence scores, and
    explanatory metadata.

    Subclasses must implement the `detect` method with specific detection
    logic (e.g., z-score thresholds, moving average comparisons, machine
    learning models) and set the `name` class attribute.

    Attributes
    ----------
    name : str
        A unique identifier for this anomaly detection algorithm.
        This should be a descriptive, human-readable name that
        distinguishes the detection method (e.g., "ZScoreDetector",
        "MovingAverageDetector", "IsolationForestDetector").
        This is a class attribute that should be set by subclasses.

    Methods
    -------
    detect(stats: HistoryStatistics) -> AnomalyResult
        Analyze historical statistics to detect anomalies.

    See Also
    --------
    HistoryStatistics : Statistical summary of variable history used as input.
    AnomalyResult : Structured output containing detection results.

    Notes
    -----
    As an abstract base class, `AnomalyDetector` cannot be instantiated
    directly. Concrete implementations must inherit from this class and
    provide implementations for all abstract methods.

    The design follows the Template Method pattern, where the base class
    defines the algorithm structure (interface) and subclasses provide
    specific detection implementations.

    Examples
    --------
    >>> from procela.core.reasoning import AnomalyDetector, AnomalyResult
    >>> from procela.core.memory import HistoryStatistics
    >>>
    >>> # Define a concrete detector
    >>> class SimpleThresholdDetector(AnomalyDetector):
    ...     name = "SimpleThresholdDetector"
    ...     def detect(self, stats: HistoryStatistics) -> AnomalyResult:
    ...         # Simple implementation checking if mean exceeds threshold
    ...         threshold = 100.0
    ...         mean = stats.mean()
    ...         is_anomaly = mean > threshold if mean else False
    ...         score = mean / threshold if mean else 0.0
    ...         return AnomalyResult(
    ...             is_anomaly=is_anomaly,
    ...             score=score,
    ...             threshold=threshold,
    ...             method=self.name,
    ...         )

    >>> # Create and use the detector
    >>> detector = SimpleThresholdDetector()
    >>> stats = HistoryStatistics(
    ...     count=1, sum=123.8, sumsq=98064.82,
    ...     min=0.3, max=9.1, last_value=None,
    ...     confidence_sum=1.4, ewma=34.2,
    ...     sources=frozenset()
    ... )
    >>> result = detector.detect(stats)
    >>> result.is_anomaly
    True
    >>> result.method
    'SimpleThresholdDetector'
    """

    name: ClassVar[str]
    """A unique identifier for this anomaly detection algorithm."""

    @abstractmethod
    def detect(self, stats: HistoryStatistics) -> AnomalyResult:
        """
        Detect anomalies based on historical statistics.

        This is the core method that all concrete anomaly detectors must
        implement. It analyzes the provided `HistoryStatistics` object
        to determine if the current or recent behavior of a variable
        constitutes an anomaly according to the detector's specific
        algorithm and criteria.

        Parameters
        ----------
        stats : HistoryStatistics
            Statistical summary of a variable's historical data.
            This typically includes measures like mean, variance,
            recent values, distribution characteristics, and temporal
            patterns that the detector uses to assess normal vs.
            anomalous behavior.

        Returns
        -------
        AnomalyResult
            A structured result containing:
            - Binary classification (`is_anomaly`)
            - Anomaly score (continuous measure of anomaly strength)
            - Detection threshold used
            - Method identifier
            - Optional metadata with algorithm-specific details

        Raises
        ------
        ValueError
            If the `HistoryStatistics` object is incomplete, invalid,
            or contains data that the detector cannot process.
        NotImplementedError
            If called directly on the abstract base class (must be
            implemented by concrete subclasses).

        Notes
        -----
        Implementations should:
        1. Handle edge cases gracefully (e.g., insufficient data,
           extreme values, missing statistics)
        2. Provide meaningful anomaly scores that reflect confidence
           or severity, typically normalized or threshold-relative
        3. Include algorithm-specific details in the `metadata` field
           of the returned `AnomalyResult` for traceability and debugging
        4. Be deterministic when possible (same input → same output)
        5. Document any assumptions about the input statistics

        The method should not modify the input `HistoryStatistics` object.

        Examples
        --------
        >>> class MyDetector(AnomalyDetector):
        ...     name = "MyDetector"
        ...     def detect(self, stats: HistoryStatistics) -> AnomalyResult:
        ...         # Example: Check if recent value exceeds 3 standard deviations
        ...         mean, std = stats.mean(), stats.std()
        ...         if mean is None or std is None:
        ...             return AnomalyResult(
        ...                 is_anomaly=False,
        ...                 score=0.0,
        ...                 threshold=3.0,
        ...                 method=self.name,
        ...                 metadata={"error": "Insufficient statistics"}
        ...             )
        ...         if std == 0:
        ...             z_score = 0
        ...         else:
        ...             z_score = abs((stats.last_value - mean) / std)
        ...         is_anomaly = z_score > 3.0
        ...         return AnomalyResult(
        ...             is_anomaly=is_anomaly,
        ...             score=z_score,
        ...             threshold=3.0,
        ...             method=self.name,
        ...             metadata={"z_score": z_score, "mean": mean, "std": std}
        ...         )
        """
        raise NotImplementedError("Subclasses must implement the detect method")
