"""
Reasoning result container.

This module defines the canonical result type returned by reasoning
tasks within the Procela subsystem. A `ReasoningResult`
encapsulates the outcome of a reasoning process, including its originating
task, success status, result payload, optional confidence, and
contextual metadata.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/assessment/reasoning.html

Examples Reference
------------------
https://procela.org/docs/examples/core/assessment/reasoning.html
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .task import ReasoningTask


@dataclass(frozen=True, slots=True)
class ReasoningResult:
    """
    Outcome of a reasoning task.

    A `ReasoningResult` instance represents the result of executing a
    reasoning task (`ReasoningTask`). It captures whether the task
    completed successfully, the concrete result produced, an optional
    epistemic confidence, an optional explanation string, and auxiliary
    metadata. Timestamp and execution time provide temporal context.

    Parameters
    ----------
    task : ReasoningTask
        The reasoning task that produced this result.
    success : bool
        Indicates whether the reasoning process succeeded.
    result : Any | None
        The raw reasoning output or None if unavailable.
    confidence : float | None, optional
        Epistemic confidence in the reasoning outcome, between 0.0 and 1.0,
        or None if unspecified.
    explanation : str | None, optional
        Human-readable explanatory text, if available.
    metadata : dict[str, Any], optional
        Arbitrary additional context or flags associated with the result.
    timestamp : datetime, default now (UTC)
        UTC-aware point in time when the result was created.
    execution_time : float | None, optional
        Measured execution duration in seconds, non-negative, or None.

    Raises
    ------
    TypeError
        If `task` is not a `ReasoningTask`, `confidence` is not numeric when
        provided, or `timestamp` is not a `datetime` object, or `execution_time`
        is not numeric when provided.
    ValueError
        If `confidence` is outside [0.0, 1.0] or `execution_time` is negative.
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
        Enforce structural guarantees of a reasoning result after initialization.

        This method is invoked automatically after the dataclass initializer.
        It validates the following invariants:

        - `task` must be a `ReasoningTask` instance.
        - When provided, `confidence` must be an int or float in [0.0, 1.0].
        - `timestamp` must be a `datetime` object; naive timestamps are
          converted to UTC-aware.
        - When provided, `execution_time` must be non-negative and numeric.

        Proper enforcement of these invariants ensures that reasoning results
        can be safely consumed by downstream logic without additional
        runtime checks.

        Raises
        ------
        TypeError
            If any field has an incompatible type.
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
