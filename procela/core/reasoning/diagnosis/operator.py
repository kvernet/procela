"""
Trend and diagnosis operators for the reasoning subsystem.

This module defines abstract base classes and concrete operator
implementations used for trend analysis and diagnosis in the
reasoning pipeline. Operators here perform computations only and
do not define the semantics of trends or diagnoses.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/diagnosis/operator.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/diagnosis/operator.html
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ...assessment.diagnosis import DiagnosisResult
from ...assessment.statistics import StatisticsResult
from ...assessment.trend import TrendResult
from ...epistemic.variable import VariableView
from .registry import get_diagnoser


class TrendOperator(ABC):
    """
    Abstract base class for trend operators.

    Trend operators evaluate changes in memory statistics and produce
    trend results for downstream reasoning. This class defines the
    computational interface for trend analysis.

    Examples
    --------
    >>> from procela import (
    ...     Variable,
    ...     StatisticalDomain,
    ...     VariableRecord,
    ...     TrendOperator,
    ...     TrendResult
    ... )
    >>>
    >>> class MyTrendOperator(TrendOperator):
    ...     def analyze(self, stats):
    ...         value = stats.ewma / 2
    ...         return TrendResult(
    ...             value=value,
    ...             direction="stable",
    ...             threshold=3.0,
    ...         )
    >>>
    >>> var = Variable("var", StatisticalDomain())
    >>> var.set(VariableRecord(value=12, confidence=0.98))
    >>> var.set(VariableRecord(value=13, confidence=0.94))
    >>> var.set(VariableRecord(value=11, confidence=0.90))
    >>> view = var.epistemic()
    >>>
    >>> operator = MyTrendOperator()
    >>>
    >>> result = operator.analyze(stats=view.stats)
    >>>
    >>> print(result.value)
    5.955
    >>> print(result.direction)
    stable
    >>> print(result.threshold)
    3.0
    """

    @abstractmethod
    def analyze(self, stats: StatisticsResult) -> TrendResult | None:
        """
        Analyze trend from memory statistics.

        Parameters
        ----------
        stats : StatisticsResult
            Aggregated statistics from variable memory.

        Returns
        -------
        TrendResult or None
            A trend result when sufficient data is available, otherwise None.

        Notes
        -----
        This method executes computation only. Trend interpretation is
        defined in the external semantic documentation.
        """
        ...


class TrendOperatorThreshold(TrendOperator):
    """
    Threshold-based trend operator.

    This operator uses a threshold to determine whether a trend is stable,
    upward, or downward based on EWMA and mean values from memory
    statistics.

    Examples
    --------
    >>> from procela import (
    ...     Variable,
    ...     StatisticalDomain,
    ...     VariableRecord,
    ...     TrendOperatorThreshold
    ... )
    >>>
    >>> var = Variable("var", StatisticalDomain())
    >>> var.set(VariableRecord(value=12, confidence=0.98))
    >>> var.set(VariableRecord(value=13, confidence=0.94))
    >>> var.set(VariableRecord(value=11, confidence=0.90))
    >>> view = var.epistemic()
    >>>
    >>> operator = TrendOperatorThreshold(threshold=2)
    >>>
    >>> result = operator.analyze(stats=view.stats)
    >>>
    >>> print(result.value)
    -0.08999999999999986
    >>> print(result.direction)
    stable
    >>> print(result.threshold)
    2
    """

    def __init__(self, threshold: float | None = 3.0):
        """
        Initialize threshold-based trend operator.

        Parameters
        ----------
        threshold : float or None
            Threshold value used to determine trend stability. If None, trend
            analysis is disabled.

        Examples
        --------
        >>> from procela import (
        ...     Variable,
        ...     StatisticalDomain,
        ...     VariableRecord,
        ...     TrendOperatorThreshold
        ... )
        >>>
        >>> var = Variable("var", StatisticalDomain())
        >>> var.set(VariableRecord(value=12, confidence=0.98))
        >>> var.set(VariableRecord(value=13, confidence=0.94))
        >>> var.set(VariableRecord(value=11, confidence=0.90))
        >>> view = var.epistemic()
        >>>
        >>> operator = TrendOperatorThreshold(threshold=2)
        >>>
        >>> result = operator.analyze(stats=view.stats)
        >>>
        >>> print(result.value)
        -0.08999999999999986
        >>> print(result.direction)
        stable
        >>> print(result.threshold)
        2

        Notes
        -----
        This constructor configures only computational behavior.
        Semantic interpretation of trend results is handled externally.
        """
        super().__init__()
        self.threshold = threshold

    def analyze(self, stats: StatisticsResult) -> TrendResult | None:
        """
        Analyze trend using threshold comparison.

        Parameters
        ----------
        stats : StatisticsResult
            Aggregated statistics from variable memory.

        Returns
        -------
        TrendResult or None
            Result indicating the detected trend, or None if trend analysis
            is disabled or insufficient data is available.

        Notes
        -----
        This method applies threshold-based computation only. The meaning of
        the returned trend is defined in the external semantic documentation.
        """
        if self.threshold is None:
            return None

        if stats is None:
            return None

        if not isinstance(stats, StatisticsResult):
            raise TypeError(f"stats should be a StatisticsResult instance, got {stats}")

        if stats.count is None or stats.count < 2 or stats.ewma is None:
            return None

        mean = stats.mean
        if mean is None:
            return None

        delta = stats.ewma - mean

        is_stable = abs(delta) < self.threshold

        return TrendResult(
            value=delta,
            direction="stable" if is_stable else "up" if delta > 0 else "down",
            threshold=self.threshold,
        )


class DiagnosisOperator(ABC):
    """
    Abstract base class for diagnosis operators.

    Diagnosis operators evaluate DiagnosticViews and produce
    DiagnosisResults. This class defines the computational interface
    for diagnosis operations.

    Examples
    --------
    >>> from procela import (
    ...     Variable,
    ...     StatisticalDomain,
    ...     VariableRecord,
    ...     DiagnosisOperator,
    ...     get_diagnoser
    ... )
    >>>
    >>> class MyDiagnosisOperator(DiagnosisOperator):
    ...     def __init__(self, name, **kwargs):
    ...         super().__init__()
    ...         self.diagnoser = get_diagnoser(name, **kwargs)
    ...     def diagnose(self, view):
    ...         return self.diagnoser.diagnose(view)
    >>>
    >>> var = Variable("var", StatisticalDomain())
    >>> var.set(VariableRecord(value=12, confidence=0.98))
    >>> var.set(VariableRecord(value=13, confidence=0.94))
    >>> var.set(VariableRecord(value=11, confidence=0.90))
    >>> view = var.epistemic()
    >>>
    >>> operator = MyDiagnosisOperator(name="statistical")
    >>>
    >>> result = operator.diagnose(view=view)
    >>>
    >>> print(result.causes)
    []
    >>> print(result.confidence)
    0.0
    >>> for key, value in result.metadata.items():
    ...     print(f"{key:22}: {value}")
    diagnoser             : StatisticalDiagnoser
    variability_threshold : 0.5
    drift_sensitivity     : 0.1
    skewness_threshold    : 1.0
    stats_available       : True
    trend_available       : True
    anomaly_available     : True
    sample_count          : True
    causes_identified     : 0
    patterns_detected     : {'high_variability': False, 'significant_drift': ...}
    confidence            : 0.0
    """

    @abstractmethod
    def diagnose(self, view: VariableView) -> DiagnosisResult:
        """
        Perform diagnosis using a diagnosis operator.

        Parameters
        ----------
        view : VariableView
            Structured view of data for diagnosis evaluation.

        Returns
        -------
        DiagnosisResult
            The result of the diagnosis computation.

        Notes
        -----
        This method performs computation only. The semantic meaning of the
        result is defined in external semantic documentation.
        """
        ...


class DiagnosisOperatorThreshold(DiagnosisOperator):
    """
    Threshold-based diagnosis operator.

    This operator delegates diagnosis to a named diagnoser obtained from
    the diagnosis registry. It does not define meaning of diagnostic
    labels.

    Examples
    --------
    >>> from procela import (
    ...     Variable,
    ...     StatisticalDomain,
    ...     VariableRecord,
    ...     DiagnosisOperatorThreshold
    ... )
    >>>
    >>> var = Variable("var", StatisticalDomain())
    >>> var.set(VariableRecord(value=12, confidence=0.98))
    >>> var.set(VariableRecord(value=13, confidence=0.94))
    >>> var.set(VariableRecord(value=11, confidence=0.90))
    >>> view = var.epistemic()
    >>>
    >>> operator = DiagnosisOperatorThreshold(name="trend")
    >>>
    >>> result = operator.diagnose(view=view)
    >>>
    >>> print(result.causes)
    ['System appears stable', 'Low confidence in trend detection']
    >>> print(result.confidence)
    0.24
    >>> for key, value in result.metadata.items():
    ...     print(f"{key:22}: {value}")
    diagnoser             : TrendDiagnoser
    significance_threshold: 0.2
    strong_threshold      : 0.5
    require_confidence    : True
    trend_available       : True
    trend_value           : -0.08999999999999986
    trend_direction       : stable
    trend_threshold       : 0.3
    stats_available       : True
    anomaly_available     : True
    direction_issues      : 1
    stability_issues      : 1
    anomaly_present       : False
    causes_identified     : 2
    confidence            : 0.24
    trend_confidence      : 0.0
    """

    def __init__(self, name: str, **kwargs: Any):
        """
        Initialize a threshold-based diagnosis operator.

        Parameters
        ----------
        name : str
            Identifier of the diagnoser implementation to use.
        **kwargs : Any
            Additional keyword arguments passed to the diagnoser factory.

        Examples
        --------
        >>> from procela import (
        ...     Variable,
        ...     StatisticalDomain,
        ...     VariableRecord,
        ...     DiagnosisOperatorThreshold
        ... )
        >>>
        >>> var = Variable("var", StatisticalDomain())
        >>> var.set(VariableRecord(value=12, confidence=0.98))
        >>> var.set(VariableRecord(value=13, confidence=0.94))
        >>> var.set(VariableRecord(value=11, confidence=0.90))
        >>> view = var.epistemic()
        >>>
        >>> operator = DiagnosisOperatorThreshold(name="trend")
        >>>
        >>> result = operator.diagnose(view=view)
        >>>
        >>> print(result.causes)
        ['System appears stable', 'Low confidence in trend detection']
        >>> print(result.confidence)
        0.24
        >>> for key, value in result.metadata.items():
        ...     print(f"{key:22}: {value}")
        diagnoser             : TrendDiagnoser
        significance_threshold: 0.2
        strong_threshold      : 0.5
        require_confidence    : True
        trend_available       : True
        trend_value           : -0.08999999999999986
        trend_direction       : stable
        trend_threshold       : 0.3
        stats_available       : True
        anomaly_available     : True
        direction_issues      : 1
        stability_issues      : 1
        anomaly_present       : False
        causes_identified     : 2
        confidence            : 0.24
        trend_confidence      : 0.0

        Notes
        -----
        This constructor configures only computational behavior. Semantic
        interpretation of diagnoses is defined externally.
        """
        super().__init__()
        self.diagnoser = get_diagnoser(name, **kwargs)

    def diagnose(self, view: VariableView) -> DiagnosisResult:
        """
        Run diagnosis via the configured diagnoser.

        Parameters
        ----------
        view : VariableView
            Structured view of data for diagnosis evaluation.

        Returns
        -------
        DiagnosisResult
            Result from the underlying diagnoser.

        Notes
        -----
        This method delegates computation to the diagnoser. Semantic meaning
        of results is defined in external documentation.
        """
        return self.diagnoser.diagnose(view)
