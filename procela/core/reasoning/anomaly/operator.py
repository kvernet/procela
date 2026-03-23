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

    Examples
    --------
    >>> from procela import (
    ...     Variable,
    ...     StatisticalDomain,
    ...     VariableRecord,
    ...     AnomalyOperator,
    ...     get_detector
    ... )
    >>>
    >>> class MyAnomalyOperator(AnomalyOperator):
    ...     def __init__(self, name, **kwargs):
    ...         super().__init__()
    ...         self.detector = get_detector(name, **kwargs)
    ...     def detect(self, stats):
    ...         return self.detector.detect(stats)
    >>>
    >>> var = Variable("var", StatisticalDomain())
    >>> var.set(VariableRecord(value=12, confidence=0.98))
    >>> var.set(VariableRecord(value=13, confidence=0.94))
    >>> var.set(VariableRecord(value=11, confidence=0.90))
    >>> view = var.epistemic()
    >>>
    >>> operator = MyAnomalyOperator(name="ewma")
    >>>
    >>> result = operator.detect(stats=view.stats)
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
    ...    print(f"{key:10}: {value}")
    value     : 11.0
    ewma      : 11.91
    std       : 0.8164965809277203
    difference: -0.9100000000000001
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

    Examples
    --------
    >>> from procela import (
    ...     Variable,
    ...     StatisticalDomain,
    ...     VariableRecord,
    ...     AnomalyOperatorThreshold
    ... )
    >>>
    >>> var = Variable("var", StatisticalDomain())
    >>> var.set(VariableRecord(value=12, confidence=0.98))
    >>> var.set(VariableRecord(value=13, confidence=0.94))
    >>> var.set(VariableRecord(value=11, confidence=0.90))
    >>> view = var.epistemic()
    >>>
    >>> operator = AnomalyOperatorThreshold(name="z-score")
    >>>
    >>> result = operator.detect(stats=view.stats)
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
    ...     print(f"{key:10}: {value}")
    mean      : 12.0
    std       : 0.8164965809277203
    value     : 11.0
    count     : 3
    z_score   : 1.2247448713915976
    threshold : 3.0
    deviation : -1.0
    absolute_deviation: 1.0
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

        Examples
        --------
        >>> from procela import (
        ...     Variable,
        ...     StatisticalDomain,
        ...     VariableRecord,
        ...     AnomalyOperatorThreshold
        ... )
        >>>
        >>> var = Variable("var", StatisticalDomain())
        >>> var.set(VariableRecord(value=12, confidence=0.98))
        >>> var.set(VariableRecord(value=13, confidence=0.94))
        >>> var.set(VariableRecord(value=11, confidence=0.90))
        >>> view = var.epistemic()
        >>>
        >>> operator = AnomalyOperatorThreshold(name="z-score")
        >>>
        >>> result = operator.detect(stats=view.stats)
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
        ...     print(f"{key:10}: {value}")
        mean      : 12.0
        std       : 0.8164965809277203
        value     : 11.0
        count     : 3
        z_score   : 1.2247448713915976
        threshold : 3.0
        deviation : -1.0
        absolute_deviation: 1.0

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
