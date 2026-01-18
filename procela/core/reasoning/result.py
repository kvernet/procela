"""
Result module for the Procela framework.

This module defines structured result containers for all reasoning tasks performed
by active variables within Procela's mechanistic modeling and active reasoning
engine. Each result class provides standardized, type-safe representations of
reasoning outcomes with built-in confidence quantification, explainability,
and audit trail capabilities.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/result.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/result.html
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

from .task import ReasoningTask


@dataclass(frozen=True, slots=True)
class ReasoningResult:
    """
    Generic container for the output of any reasoning task.

    This is the most general result type in Procela, serving as a unified
    interface for all reasoning operations. It encapsulates the essential
    metadata about a reasoning task's execution and outcome, enabling
    consistent handling, logging, and analysis across different task types.

    Parameters
    ----------
    task : ReasoningTask
        The specific reasoning task that produced this result (e.g.,
        `ReasoningTask.ANOMALY_DETECTION`). This provides semantic context.

    success : bool
        Whether the reasoning task completed successfully (True) or
        encountered an error or produced an invalid result (False).
        This is distinct from the semantic meaning of the result (e.g.,
        an anomaly detection task can be successful but find no anomaly).

    result : Any | None
        The primary output of the reasoning task. The type is task-dependent
        and can be any Python object (e.g., a boolean for anomaly detection,
        a float for predictions, a list for diagnoses).

    confidence : float | None, optional
        A quantitative measure of certainty in the result, typically in
        the range [0.0, 1.0]. Should be provided when meaningful.
        Default is None.

    explanation : str | None, optional
        A human-readable explanation of how the result was derived or what
        it means. This is crucial for explainability and debugging.
        Default is None.

    metadata : dict[str, Any], optional
        A flexible dictionary for additional task-specific data, intermediate
        computation results, provenance information, or custom annotations.
        Default is an empty dict.

    timestamp : datetime, optional
        The UTC datetime when this result was created. Managed automatically
        via `default_factory`. Defaults to `datetime.now(timezone.utc)`.

    execution_time : float | None, optional
        The time (in seconds) taken to execute the reasoning task.
        Useful for performance monitoring and optimization.
        Default is None.

    Attributes
    ----------
    task : ReasoningTask
        See Parameters section.

    success : bool
        See Parameters section.

    result : Any | None
        See Parameters section.

    confidence : float | None
        See Parameters section.

    explanation : str | None
        See Parameters section.

    metadata : dict[str, Any]
        See Parameters section.

    timestamp : datetime
        See Parameters section.

    execution_time : float | None
        See Parameters section.

    Raises
    ------
    TypeError
        If `task` is not a `ReasoningTask` instance, or `timestamp` is not a
        `datetime` object.
    ValueError
        If `confidence` is provided but is outside the logical range [0.0, 1.0].

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/result.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/reasoning/result.html
    """

    task: ReasoningTask
    success: bool
    result: Any | None
    confidence: float | None = None
    explanation: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time: float | None = None

    def __post_init__(self) -> None:
        """
        Validate the dataclass fields after initialization.

        Ensures contractual guarantees for result validity and consistency.

        Raises
        ------
        TypeError
            If `task` is not a `ReasoningTask` or `timestamp` is not a `datetime`.
        ValueError
            If `confidence` is outside [0.0, 1.0] or `execution_time` is negative.
        """
        # Validate task type
        if not isinstance(self.task, ReasoningTask):
            raise TypeError(
                "Task must be a ReasoningTask instance, "
                f"got {type(self.task).__name__}"
            )

        # Validate confidence range
        if self.confidence is not None:
            if not isinstance(self.confidence, int | float):
                raise TypeError(
                    "Confidence must be int or float, "
                    f"got {type(self.confidence).__name__}"
                )
            if not 0.0 <= self.confidence <= 1.0:
                raise ValueError(
                    "Confidence must be between 0.0 and 1.0, " f"got {self.confidence}"
                )

        # Validate timestamp type
        if not isinstance(self.timestamp, datetime):
            raise TypeError(
                f"Timestamp must be a datetime object, "
                f"got {type(self.timestamp).__name__}"
            )

        # Ensure timestamp is timezone-aware (preferably UTC)
        if self.timestamp.tzinfo is None:
            # Convert naive datetime to UTC-aware
            object.__setattr__(
                self, "timestamp", self.timestamp.replace(tzinfo=timezone.utc)
            )

        # Validate execution_time (if provided)
        if self.execution_time is not None:
            if not isinstance(self.execution_time, int | float):
                raise TypeError(
                    "Execution time must be numeric, "
                    f"got {type(self.execution_time).__name__}"
                )
            if self.execution_time < 0:
                raise ValueError(
                    "Execution time must be non-negative, " f"got {self.execution_time}"
                )


@dataclass(frozen=True, slots=True)
class AnomalyResult:
    """
    Specialized result container for anomaly detection tasks.

    Encapsulates the outcome of anomaly detection methods, including binary
    classification (anomaly vs. normal) and continuous anomaly scores with
    confidence quantification.

    Parameters
    ----------
    is_anomaly : bool
        The primary classification result: True if an anomaly was detected,
        False otherwise.

    score : float | None, optional
        A continuous anomaly score produced by the detection method.
        Higher values typically indicate stronger anomaly signals.
        Default is None.

    threshold : float | None, optional
        The decision threshold used to convert the continuous score into
        the binary `is_anomaly` classification. Must be > 0 if provided.
        Default is None.

    method : str | None, optional
        The name or identifier of the anomaly detection method used
        (e.g., "zscore", "isolation_forest", "moving_average").
        Default is None.

    metadata : dict[str, Any] | None, optional
        Additional method-specific details or diagnostics.
        Default is None.

    Attributes
    ----------
    is_anomaly : bool
        See Parameters section.

    score : float | None
        See Parameters section.

    threshold : float | None
        See Parameters section.

    method : str | None
        See Parameters section.

    metadata : dict[str, Any] | None
        See Parameters section.

    Raises
    ------
    ValueError
        If `threshold` is provided and is non-positive (<= 0).

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/result.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/reasoning/result.html
    """

    is_anomaly: bool
    score: float | None = None
    threshold: float | None = None
    method: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Validate threshold if provided."""
        if self.threshold is not None and self.threshold <= 0:
            raise ValueError(f"Threshold must be positive, got {self.threshold}")

    def confidence(self) -> float | None:
        """
        Compute anomaly confidence as a normalized score.

        Confidence is only meaningful when:
        1. An anomaly was detected (`is_anomaly` is True)
        2. Both `score` and `threshold` are available and valid
        3. `threshold` is positive

        The confidence is computed as `min(1.0, score / max(threshold, 1e-9))`,
        which normalizes the anomaly score relative to the detection threshold.
        Values above 1.0 are capped at 1.0 (maximum confidence).

        Returns
        -------
        float | None
            A confidence value between 0.0 and 1.0, or None if confidence
            cannot be meaningfully computed.
        """
        if not self.is_anomaly or self.score is None or self.threshold is None:
            return None
        # Avoid division by zero with a small epsilon
        return min(1.0, self.score / max(self.threshold, 1e-9))


@dataclass(frozen=True, slots=True)
class TrendResult:
    """
    Specialized result container for trend analysis tasks.

    Represents the outcome of analyzing directional changes in a time series
    or sequential data, including magnitude, direction, and statistical
    significance measures.

    Parameters
    ----------
    value : float
        The magnitude of the trend (e.g., slope, change rate, difference).
        Positive values typically indicate increasing trends.

    direction : Literal["up", "down", "stable"]
        The categorical direction of the trend:
        - "up": increasing trend (value > 0)
        - "down": decreasing trend (value < 0)
        - "stable": no significant trend (value ≈ 0)

    threshold : float
        The stability threshold used to determine if a trend is significant.
        Trends with |value| < threshold are typically classified as "stable".
        Must be > 0.

    Attributes
    ----------
    value : float
        See Parameters section.

    direction : Literal["up", "down", "stable"]
        See Parameters section.

    threshold : float
        See Parameters section.

    Raises
    ------
    ValueError
        If `threshold` is non-positive (<= 0).
        If `direction` is not one of "up", "down", or "stable".

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/result.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/reasoning/result.html
    """

    value: float
    direction: Literal["up", "down", "stable"]
    threshold: float

    def __post_init__(self) -> None:
        """Validate direction and threshold."""
        if self.direction not in ("up", "down", "stable"):
            raise ValueError(
                f"Direction must be 'up', 'down', or 'stable', got '{self.direction}'"
            )
        if self.threshold <= 0:
            raise ValueError(f"Threshold must be positive, got {self.threshold}")

    def confidence(self) -> float:
        """
        Compute confidence based on distance from stability threshold.

        Confidence quantifies how strongly the trend deviates from stability:
        - Returns 0.0 for "stable" trends (by definition)
        - Otherwise, computes `min(1.0, abs(value) / max(threshold, 1e-9))`
        - Values are capped at 1.0 (maximum confidence)

        This metric is useful for ranking trends by significance or for
        downstream decision-making processes.

        Returns
        -------
        float
            A confidence value between 0.0 and 1.0.
        """
        if self.direction == "stable":
            return 0.0
        # Avoid division by zero with a small epsilon
        return min(1.0, abs(self.value) / max(self.threshold, 1e-9))

    def zscore(self, std: float | None) -> float | None:
        """
        Express trend value as a z-score, if standard deviation is available.

        The z-score standardizes the trend magnitude by expressing it in
        units of standard deviations from zero. This is useful for comparing
        trends across different scales or for statistical significance testing.

        Parameters
        ----------
        std : float | None
            The standard deviation of the trend metric or the underlying data.
            Must be > 0 if provided.

        Returns
        -------
        float | None
            The z-score or None if std is None or zero.

        Raises
        ------
        ValueError
            If `std` is provided but is non-positive (<= 0).
        """
        if std is None:
            return None
        if std == 0:
            return None
        if std < 0:
            raise ValueError(f"Standard deviation must be positive, got {std}")
        return self.value / std


@dataclass(frozen=True, slots=True)
class DiagnosisResult:
    """
    Specialized result container for causal diagnostic reasoning.

    Encapsulates the outcome of root cause analysis or diagnostic reasoning,
    identifying potential causes for observed system behaviors or anomalies.

    Parameters
    ----------
    causes : list[str]
        A list of identified potential root causes. Each cause should be
        described as a human-readable string. The list may be empty if
        no causes were identified.

    confidence : float | None, optional
        An overall confidence in the diagnostic conclusion, typically
        between 0.0 and 1.0. This may reflect the certainty that the
        identified causes are correct and complete.
        Default is None.

    metadata : dict[str, Any], optional
        Additional diagnostic details, such as evidence supporting each
        cause, causal graphs, or method-specific parameters.
        Default is an empty dict.

    Attributes
    ----------
    causes : list[str]
        See Parameters section.

    confidence : float | None
        See Parameters section.

    metadata : dict[str, Any]
        See Parameters section.

    Raises
    ------
    TypeError
        If `causes` is not a list or contains non-string items.
    ValueError
        If `confidence` is outside [0.0, 1.0].

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/result.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/reasoning/result.html
    """

    causes: list[str]
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate causes and confidence."""
        # Validate causes type and content
        if not isinstance(self.causes, list):
            raise TypeError(
                "Causes must be a list, " f"got {type(self.causes).__name__}"
            )
        for i, cause in enumerate(self.causes):
            if not isinstance(cause, str):
                raise TypeError(
                    "All causes must be strings, "
                    f"got {type(cause).__name__} at index {i}"
                )

        # Validate confidence range
        if self.confidence is not None:
            if not isinstance(self.confidence, int | float):
                raise TypeError(
                    "Confidence must be int or float, "
                    f"got {type(self.confidence).__name__}"
                )
            if not 0.0 <= self.confidence <= 1.0:
                raise ValueError(
                    "Confidence must be between 0.0 and 1.0, " f"got {self.confidence}"
                )


@dataclass(frozen=True, slots=True)
class PlanningResult:
    """
    Specialized result container for intervention planning tasks.

    Encapsulates the outcome of planning reasoning, which generates and
    optionally ranks potential action sequences to achieve system objectives.
    Planning proposes actions but does not select or execute them—that's
    handled by the selection policies and execution engine.

    Parameters
    ----------
    proposals : list[Any]
        The complete set of candidate action proposals generated by the
        planner. This is the primary output of planning reasoning.

    recommended : list[Any] | None, optional
        A subset of `proposals` that the planner specifically recommends
        for consideration. If None, all proposals are equally recommended.
        Default is None.

    confidence : float | None, optional
        The planner's overall confidence in the quality or suitability of
        the generated proposals, typically between 0.0 and 1.0.
        Default is None.

    strategy : str | None, optional
        The name or type of planning strategy used (e.g., "reactive",
        "preventive", "optimistic", "pessimistic").
        Default is None.

    metadata : dict[str, Any], optional
        Additional planning details, such as search depth, evaluated
        alternatives, cost estimates, or constraint violations.
        Default is an empty dict.

    timestamp : datetime, optional
        The UTC datetime when this planning result was created.
        Defaults to `datetime.now(timezone.utc)`.

    Attributes
    ----------
    proposals : list[Any]
        See Parameters section.

    recommended : list[Any] | None
        See Parameters section.

    confidence : float | None
        See Parameters section.

    strategy : str | None
        See Parameters section.

    metadata : dict[str, Any]
        See Parameters section.

    timestamp : datetime
        See Parameters section.

    Raises
    ------
    TypeError
        If `proposals` is not a list.
    ValueError
        If `confidence` is outside [0.0, 1.0], or `recommended` contains
        proposals not in `proposals`.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/result.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/reasoning/result.html
    """

    proposals: list[Any]
    recommended: list[Any] | None = None
    confidence: float | None = None
    strategy: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate proposals, recommended, and confidence."""
        # Validate proposals type and content
        if not isinstance(self.proposals, list):
            raise TypeError(
                "Proposals must be a list, " f"got {type(self.proposals).__name__}"
            )

        # Validate that all recommended proposals are in proposals
        if self.recommended is not None:
            if not isinstance(self.recommended, list):
                raise TypeError(
                    "Recommended must be a list or None, "
                    f"got {type(self.recommended).__name__}"
                )
            for rec in self.recommended:
                if rec not in self.proposals:
                    raise ValueError(
                        f"Recommended proposal {rec} is not in the proposals list"
                    )

        # Validate confidence range
        if self.confidence is not None:
            if not isinstance(self.confidence, int | float):
                raise TypeError(
                    "Confidence must be int or float, "
                    f"got {type(self.confidence).__name__}"
                )
            if not 0.0 <= self.confidence <= 1.0:
                raise ValueError(
                    "Confidence must be between 0.0 and 1.0, " f"got {self.confidence}"
                )

        # Ensure timestamp is timezone-aware
        if self.timestamp.tzinfo is None:
            object.__setattr__(
                self, "timestamp", self.timestamp.replace(tzinfo=timezone.utc)
            )


@dataclass(frozen=True, slots=True)
class PredictionResult:
    """
    Specialized result container for value prediction tasks.

    Encapsulates the outcome of predictive reasoning, which forecasts future
    values or states based on historical data, current conditions, and
    predictive models.

    Parameters
    ----------
    value : Any
        The predicted value. This can be of any type appropriate to the
        prediction task (e.g., float for numeric forecasts, string for
        categorical predictions, dict for multi-output predictions).

    horizon : int | None, optional
        The prediction horizon, indicating how many steps ahead the
        prediction was made (e.g., 1 for next time step, 5 for five
        steps ahead). Must be positive if provided.
        Default is None.

    confidence : float | None, optional
        Confidence in the prediction accuracy, typically between 0.0 and 1.0.
        This may represent statistical confidence intervals, model
        certainty, or other reliability metrics.
        Default is None.

    metadata : dict[str, Any], optional
        Additional prediction details, such as model parameters,
        prediction intervals, feature importance, or alternative scenarios.
        Default is an empty dict.

    Attributes
    ----------
    value : Any
        See Parameters section.

    horizon : int | None
        See Parameters section.

    confidence : float | None
        See Parameters section.

    metadata : dict[str, Any]
        See Parameters section.

    Raises
    ------
    ValueError
        If `horizon` is provided but is non-positive (<= 0).
        If `confidence` is outside [0.0, 1.0].

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/result.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/reasoning/result.html
    """

    value: Any
    horizon: int | None = None
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate horizon and confidence."""
        # Validate horizon
        if self.horizon is not None:
            if not isinstance(self.horizon, int):
                raise TypeError(
                    "Horizon must be an integer, " f"got {type(self.horizon).__name__}"
                )
            if self.horizon <= 0:
                raise ValueError(f"Horizon must be positive, got {self.horizon}")

        # Validate confidence range
        if self.confidence is not None:
            if not isinstance(self.confidence, int | float):
                raise TypeError(
                    "Confidence must be int or float, "
                    f"got {type(self.confidence).__name__}"
                )
            if not 0.0 <= self.confidence <= 1.0:
                raise ValueError(
                    "Confidence must be between 0.0 and 1.0, " f"got {self.confidence}"
                )
