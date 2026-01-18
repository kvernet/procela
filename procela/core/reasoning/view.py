"""
View Protocol Definitions for the Procela Framework.

This module defines runtime-checkable protocol interfaces (structural subtyping)
that specify the minimal epistemic "views" required by different reasoning tasks.
These protocols enable the Procela framework to perform type-safe dependency
injection and ensure that reasoning components receive the appropriate contextual
data they need without requiring specific concrete implementations.

Each protocol defines a minimal set of properties that a reasoning task requires
to perform its function. This architectural pattern supports separation of
concerns and allows different variable implementations to be used interchangeably
as long as they provide the required view interfaces.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ..memory.variable.statistics import HistoryStatistics
from .result import (
    AnomalyResult,
    DiagnosisResult,
    PredictionResult,
    TrendResult,
)


@runtime_checkable
class EpistemicView(Protocol):
    """
    Minimal epistemic view of a variable for basic reasoning tasks.

    This protocol defines the most fundamental view of a variable that
    provides access to historical statistics and basic state assessments.
    It serves as the foundation for most reasoning operations in Procela,
    offering a consistent interface to a variable's historical context and
    current assessments without exposing implementation details.

    Properties
    ----------
    stats : HistoryStatistics
        Statistical summary of the variable's historical data, including
        measures like mean, variance, distribution characteristics, and
        temporal patterns. This provides the empirical foundation for
        data-driven reasoning.

    anomaly : AnomalyResult | None
        The most recent anomaly detection result for this variable, or
        None if no anomaly analysis has been performed or is available.
        This represents the system's current assessment of whether the
        variable's behavior is within expected bounds.

    trend : TrendResult | None
        The most recent trend analysis result for this variable, or None
        if no trend analysis has been performed or is available. This
        captures directional patterns and rates of change in the variable's
        behavior over time.

    Notes
    -----
    As a runtime-checkable protocol, this interface supports structural
    subtyping: any object that provides these three properties (with
    compatible types) is considered to implement EpistemicView, regardless
    of its explicit inheritance declarations. This enables flexible
    composition and dependency injection throughout the Procela framework.

    Examples
    --------
    >>> from procela.core.memory import HistoryStatistics
    >>> from procela.core.reasoning import EpistemicView
    >>>
    >>> # Any object with stats, anomaly, and trend properties implements this
    >>> class MyVariable:
    ...     def __init__(self):
    ...         self._stats = HistoryStatistics(
    ...             count=1,
    ...             sum=23.1,
    ...             sumsq=781.3,
    ...             min=None,
    ...             max=None,
    ...             last_value=None,
    ...             confidence_sum=0.53,
    ...             ewma=None,
    ...             sources=[],
    ...         )
    ...         self._anomaly = None
    ...         self._trend = None
    ...
    ...     @property
    ...     def stats(self):
    ...         return self._stats
    ...
    ...     @property
    ...     def anomaly(self):
    ...         return self._anomaly
    ...
    ...     @property
    ...     def trend(self):
    ...         return self._trend
    ...
    >>> var = MyVariable()
    >>> isinstance(var, EpistemicView)  # Runtime type checking
    True
    """

    @property
    def stats(self) -> HistoryStatistics:
        """Access the variable's historical statistics."""
        ...

    @property
    def anomaly(self) -> AnomalyResult | None:
        """Access the most recent anomaly detection result."""
        ...

    @property
    def trend(self) -> TrendResult | None:
        """Access the most recent trend analysis result."""
        ...


@runtime_checkable
class DiagnosisView(Protocol):
    """
    View interface required to perform causal diagnostic reasoning.

    This protocol extends the epistemic foundation with additional context
    needed specifically for root cause analysis and diagnostic reasoning.
    It provides the historical context, anomaly status, and trend information
    that diagnostic algorithms need to identify potential causes of observed
    behaviors or deviations.

    Properties
    ----------
    stats : HistoryStatistics
        Statistical summary of historical data, providing the baseline
        against which current behavior is compared during diagnosis.

    anomaly : AnomalyResult | None
        Anomaly detection results that may indicate issues requiring
        diagnostic investigation. The presence, type, and characteristics
        of anomalies often provide key clues for causal diagnosis.

    trend : TrendResult | None
        Trend analysis results that reveal directional patterns which
        may be symptomatic of underlying issues or gradual degradation.

    Notes
    -----
    DiagnosisView is currently identical to EpistemicView in structure but
    represents a distinct semantic role in the reasoning architecture. This
    separation allows for future differentiation and ensures that diagnostic
    components explicitly declare their dependency requirements.
    """

    @property
    def stats(self) -> HistoryStatistics:
        """Access the variable's historical statistics."""
        ...

    @property
    def anomaly(self) -> AnomalyResult | None:
        """Access the most recent anomaly detection result."""
        ...

    @property
    def trend(self) -> TrendResult | None:
        """Access the most recent trend analysis result."""
        ...


@runtime_checkable
class ProposalView(Protocol):
    """
    View interface required to perform action proposals reasoning.

    This protocol extends the epistemic foundation with additional context
    needed specifically for action proposals reasoning.
    It provides the historical context, anomaly status, and trend information
    that action proposal algorithms need to identify proposals of observed
    behaviors or deviations.

    Properties
    ----------
    stats : HistoryStatistics
        Statistical summary of historical data, providing the baseline
        against which current behavior is compared during action proposals.

    anomaly : AnomalyResult | None
        Anomaly detection results that may indicate issues requiring
        action investigation. The presence, type, and characteristics
        of anomalies often provide key clues for proposals.

    trend : TrendResult | None
        Trend analysis results that reveal directional patterns which
        may be symptomatic of underlying issues or gradual degradation.
    """

    @property
    def stats(self) -> HistoryStatistics:
        """Access the variable's historical statistics."""
        ...

    @property
    def anomaly(self) -> AnomalyResult | None:
        """Access the most recent anomaly detection result."""
        ...

    @property
    def trend(self) -> TrendResult | None:
        """Access the most recent trend analysis result."""
        ...


@runtime_checkable
class PredictionView(Protocol):
    """
    View interface required to perform predictive reasoning.

    This protocol specifies the minimal data required for forecasting
    and predictive modeling tasks. It focuses on historical patterns
    and trend information while excluding anomaly data, reflecting the
    typical needs of time series forecasting and predictive algorithms.

    Properties
    ----------
    stats : HistoryStatistics
        Comprehensive historical statistics needed for predictive modeling,
        including distribution parameters, seasonal patterns, autocorrelation
        structures, and other temporal characteristics that inform forecasts.

    trend : TrendResult | None
        Current trend analysis that can inform near-term predictions,
        particularly for extrapolation-based forecasting methods.

    Notes
    -----
    The absence of `anomaly` in this protocol reflects that predictive
    models often need to separate signal from noise, and may handle
    anomalies differently than diagnostic or planning components. Some
    prediction algorithms may explicitly filter or model anomalies, while
    others may ignore them as outliers.

    Examples
    --------
    >>> from procela.core.reasoning import PredictionView, TrendResult
    >>> from procela.core.memory import HistoryStatistics
    >>>
    >>> # A variable suitable for prediction
    >>> class PredictableVariable:
    ...     @property
    ...     def stats(self):
    ...         return HistoryStatistics(
    ...             count=1,
    ...             sum=23.1,
    ...             sumsq=781.3,
    ...             min=None,
    ...             max=None,
    ...             last_value=None,
    ...             confidence_sum=0.53,
    ...             ewma=None,
    ...             sources=[],
    ...         )
    ...
    ...     @property
    ...     def trend(self):
    ...         return TrendResult(value=0.5, direction="up", threshold=0.1)
    ...
    >>> var = PredictableVariable()
    >>> isinstance(var, PredictionView)
    True
    """

    @property
    def stats(self) -> HistoryStatistics:
        """Access the variable's historical statistics."""
        ...

    @property
    def trend(self) -> TrendResult | None:
        """Access the most recent trend analysis result."""
        ...


@runtime_checkable
class PlanningView(Protocol):
    """
    View interface required to perform intervention planning.

    This protocol specifies the contextual data needed for planning
    and decision-making tasks. Unlike the data-focused views, PlanningView
    emphasizes diagnostic conclusions and predictive scenarios that inform
    action selection and strategy formulation.

    Properties
    ----------
    diagnosis : DiagnosisResult | None
        Diagnostic conclusions about the current state or identified issues.
        This provides the "why" that informs planning decisions—understanding
        what needs to be addressed or what opportunities exist.

    predictions : list[PredictionResult]
        Forecasted future scenarios or outcomes under different conditions.
        Planning algorithms use these predictions to evaluate potential
        consequences of different intervention strategies.

    current_value : Any
        The variable's current value or state. This provides the starting
        point for planning and is essential for constructing action proposals
        that transition from the current state to desired future states.

    Notes
    -----
    PlanningView differs significantly from the other views by focusing on
    synthesized reasoning results (diagnosis, predictions) rather than raw
    statistical data. This reflects planning's role as a higher-order
    reasoning task that operates on the outputs of other reasoning processes.

    The `current_value` property uses type `Any` to accommodate the diverse
    value types that different variables in the Procela framework may have
    (scalars, vectors, categorical values, complex structures, etc.).

    See Also
    --------
    DiagnosisResult : The diagnostic conclusions used by planning.
    PredictionResult : The forecasted scenarios used by planning.
    """

    @property
    def diagnosis(self) -> DiagnosisResult | None:
        """Access diagnostic conclusions about the current state."""
        ...

    @property
    def predictions(self) -> list[PredictionResult]:
        """Access forecasted future scenarios."""
        ...

    @property
    def current_value(self) -> Any:
        """Access the variable's current value or state."""
        ...
