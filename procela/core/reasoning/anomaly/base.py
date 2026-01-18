"""
Anomaly Detection Base Module for the Procela Framework.

This module defines the abstract base class for all anomaly detection
algorithms within Procela's active reasoning engine. Anomaly detectors
are specialized reasoning components that analyze historical statistics
to identify deviations from expected behavior, forming the foundation
for proactive system monitoring and diagnostic reasoning.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/anomaly/base.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/anomaly/base.html
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

    Notes
    -----
    As an abstract base class, `AnomalyDetector` cannot be instantiated
    directly. Concrete implementations must inherit from this class and
    provide implementations for all abstract methods.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/anomaly/base.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/reasoning/anomaly/base.html
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
        """
        raise NotImplementedError("Subclasses must implement the detect method")
