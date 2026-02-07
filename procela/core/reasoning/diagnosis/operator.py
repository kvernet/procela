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
    """

    def __init__(self, threshold: float | None = 3.0):
        """
        Initialize threshold-based trend operator.

        Parameters
        ----------
        threshold : float or None
            Threshold value used to determine trend stability. If None, trend
            analysis is disabled.

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
