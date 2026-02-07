"""
Anomaly operator base definitions.

This module defines the base classes for anomaly operators used by the
reasoning subsystem. Operators encapsulate computational behavior for
detecting anomalies from variable memory statistics. They do not define
the semantics of what constitutes an anomaly.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/anomaly/operator.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/anomaly/operator.html
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ...assessment.anomaly import AnomalyResult
from ...assessment.statistics import StatisticsResult
from .registry import get_detector


class AnomalyOperator(ABC):
    """
    Abstract base class for anomaly operators.

    Subclasses implement a specific strategy for detecting anomalies given
    a set of memory statistics. This class defines the interface that all
    anomaly operators must follow.
    """

    @abstractmethod
    def detect(self, stats: StatisticsResult) -> AnomalyResult:
        """
        Perform anomaly detection on memory statistics.

        Parameters
        ----------
        stats : StatisticsResult
            Aggregated statistics for a variable memory to be evaluated.

        Returns
        -------
        AnomalyResult
            The outcome of the anomaly detection computation.

        Notes
        -----
        This method runs only computational detection logic; interpretation or
        labeling of the result is defined in the semantic documentation.
        """
        ...


class AnomalyOperatorThreshold(AnomalyOperator):
    """
    Threshold-based anomaly operator.

    This operator delegates detection to a named detector obtained from
    the anomaly detector registry. The detector is configured using the
    provided parameters.
    """

    def __init__(self, name: str, **kwargs: Any) -> None:
        """
        Initialize a threshold-based anomaly operator.

        Parameters
        ----------
        name : str
            Identifier of the anomaly detector implementation to use.
        **kwargs
            Keyword arguments passed to the detector factory.

        Notes
        -----
        The name and parameters control which underlying detector is used and
        how it is configured. See the anomaly detector registry for options.
        """
        self.detector = get_detector(name, **kwargs)

    def detect(self, stats: StatisticsResult) -> AnomalyResult:
        """
        Detect anomalies using the configured detector.

        Parameters
        ----------
        stats : StatisticsResult
            Aggregated memory statistics to evaluate.

        Returns
        -------
        AnomalyResult
            Result of the underlying detector's computation.

        Notes
        -----
        This method delegates to the detector returned by the registry. No
        semantic labeling is performed here.
        """
        return self.detector.detect(stats)
