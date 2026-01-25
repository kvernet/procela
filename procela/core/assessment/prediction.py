"""
Prediction result container.

This module defines the canonical result type produced by predictive
assessment mechanisms in Procela. A prediction result represents a
forecasted value along with its associated epistemic attributes such
as planning horizon and confidence.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/assessment/prediction.html

Examples Reference
------------------
https://procela.org/docs/examples/core/assessment/prediction.html
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class PredictionResult:
    """
    Outcome of a predictive assessment.

    Instances of this class encapsulate the forecasted `value` produced
    by a mechanism, an optional prediction horizon (e.g., steps ahead),
    an optional confidence score, and an optional metadata mapping.

    Prediction results are immutable epistemic artifacts that can
    propagate through reasoning pipelines, be evaluated by policies,
    and be recorded in variable histories.

    Parameters
    ----------
    value : Any
        The predicted value or state produced by the assessment mechanism.
    horizon : int | None, default None
        The positive integer horizon indicating how far ahead the
        prediction applies (e.g., number of time steps), or None if
        unspecified.
    confidence : float | None, default None
        A confidence score in the prediction in the interval [0.0, 1.0],
        or None if not available.
    metadata : dict[str, Any], default_factory=dict
        Arbitrary additional information associated with this prediction.

    Raises
    ------
    TypeError
        If `horizon` is provided and not an integer.
    ValueError
        If `horizon` is provided and not positive, or if `confidence`
        is provided but not in [0.0, 1.0].
    """

    value: Any
    horizon: int | None = None
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Enforce structural consistency of prediction results after instantiation.

        This method is invoked automatically after the dataclass
        initializer. It validates the following invariants:

        - If `horizon` is not None, it must be an integer and greater than zero.
        - If `confidence` is not None, it must be a numeric type (int or float)
          and lie in the closed interval [0.0, 1.0].

        These invariants ensure that downstream reasoning mechanisms
        relying on forecast horizon and confidence can assume well-formed
        inputs.

        Raises
        ------
        TypeError
            If `horizon` is not an integer when provided, or if `confidence` is
            not int or float when provided.
        ValueError
            If `horizon` is not positive, or if `confidence` is outside
            [0.0, 1.0].
        """
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
