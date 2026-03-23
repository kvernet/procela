"""
Anomaly result container.

Examples
--------
>>> from procela import AnomalyResult
>>>
>>> result = AnomalyResult(
...     is_anomaly=True,
...     score=0.9,
...     threshold=3.0
... )
>>>
>>> print(result.confidence())
0.3

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/assessment/anomaly.html

Examples Reference
------------------
https://procela.org/docs/examples/core/assessment/anomaly.html
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AnomalyResult:
    """
    Result of an anomaly assessment.

    Instances of this class represent the outcome of an anomaly assessment,
    capturing whether an anomaly was detected along with associated
    quantitative indicators.

    Parameters
    ----------
    is_anomaly : bool
        Indicates if the assessed input was classified as anomalous.
    score : float | None, optional
        Numeric score produced by the anomaly assessment mechanism,
        if available.
    threshold : float | None, optional
        Threshold value used to decide anomaly status; must be positive
        when provided.
    method : str | None, optional
        Identifier of the anomaly assessment method used.
    metadata : dict[str, Any] | None, optional
        Additional assessment metadata.

    Notes
    -----
    Instances are immutable and frozen.

    Raises
    ------
    ValueError
        If `threshold` is non-positive when provided.

    Examples
    --------
    >>> from procela import AnomalyResult
    >>>
    >>> result = AnomalyResult(
    ...     is_anomaly=True,
    ...     score=0.9,
    ...     threshold=3.0
    ... )
    >>>
    >>> print(result.confidence())
    0.3
    """

    is_anomaly: bool
    score: float | None = None
    threshold: float | None = None
    method: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """
        Validate anomaly assessment invariants after initialization.

        This method enforces structural and semantic constraints on the
        anomaly assessment result to ensure internal consistency and
        downstream reliability. It is automatically invoked after
        dataclass initialization and may raise if invariants are violated.

        Validation performed here guarantees that:
        - Declared anomaly status is compatible with provided quantitative
          indicators.
        - Threshold values, when present, are strictly positive.
        - Partial specifications (e.g., score without threshold) remain
          semantically admissible but limit derived interpretations.

        Raises
        ------
        ValueError
            If `threshold` is provided and is not strictly positive.
        """
        if self.threshold is not None and self.threshold <= 0:
            raise ValueError(f"Threshold must be positive, got {self.threshold}")

    def confidence(self) -> float | None:
        """
        Return normalized confidence in anomaly status.

        Computes the ratio of `score` to `threshold` capped at 1, if
        `is_anomaly`, `score`, and `threshold` are all provided.

        Returns
        -------
        float | None
            Confidence value between 0 and 1, or None if insufficient
            inputs are present.
        """
        if not self.is_anomaly or self.score is None or self.threshold is None:
            return None

        return min(1.0, self.score / max(self.threshold, 1e-9))
