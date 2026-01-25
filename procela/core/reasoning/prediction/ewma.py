"""
Exponentially Weighted Moving Average (EWMA) Predictor for the Procela Framework.

This module implements an EWMA-based predictor that forecasts future values
using pre-computed exponentially weighted moving average statistics from
the epistemic data layer. The predictor leverages incrementally maintained
statistics to provide efficient, real-time predictions.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/prediction/ewma.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/prediction/ewma.html
"""

from __future__ import annotations

from ...assessment.prediction import PredictionResult
from ...epistemic.variable import VariableView
from .base import Predictor


class EWMAPredictor(Predictor):
    """
    Exponentially Weighted Moving Average predictor using pre-computed statistics.

    This predictor uses the EWMA value maintained incrementally in the
    epistemic statistics to forecast future values. The EWMA is computed
    as: S_t = alpha * Y_t + (1 - alpha) * S_{t-1}, where the current S_t is
    available in `epistemic.stats.ewma`.

    Parameters
    ----------
    alpha : float, optional
        Smoothing factor (0 < alpha ≤ 1) used in EWMA computation.
        This should match the alpha used to compute the ewma statistic.
        Default is 0.3.

    Attributes
    ----------
    alpha : float
        Smoothing factor used in EWMA computation.

    Raises
    ------
    ValueError
        If alpha is not in range (0, 1].
    """

    def __init__(self, alpha: float = 0.3) -> None:
        """
        Initialize the EWMA predictor with smoothing factor.

        Parameters
        ----------
        alpha : float, optional
            Smoothing factor controlling the weight given to recent observations.
            Must satisfy 0 < alpha ≤ 1. This should match the alpha value
            used to compute the ewma statistic in epistemic.stats.

        Raises
        ------
        ValueError
            If alpha is outside the valid range (0, 1].
        """
        if not 0 < alpha <= 1:
            raise ValueError(f"alpha must be in range (0, 1], got {alpha}")

        self.alpha = alpha

    def predict(
        self,
        view: VariableView,
        horizon: int | None = None,
    ) -> PredictionResult:
        """
        Generate predictions using pre-computed EWMA statistics.

        This method uses the current EWMA value from epistemic statistics
        to forecast future values. The prediction assumes the current EWMA
        represents the best estimate of the current level, and future
        predictions maintain this level (persistence model).

        Parameters
        ----------
        view : VariableView
            View containing epistemic data including pre-computed statistics.
            Must provide access to `epistemic.stats.ewma` and
            `epistemic.stats.last_value`.
        horizon : int | None, optional
            Number of future steps to predict. If None, defaults to 1.
            Must be ≥ 1 if specified.

        Returns
        -------
        PredictionResult
            The prediction result containing value, confidence, and metadata.
            All values are identical, representing persistence
            of the current EWMA level.

        Raises
        ------
        TypeError
            If view is not a VariableView instance.
        ValueError
            If horizon is specified but < 1, or if required statistics
            are not available (ewma is None).
        RuntimeError
            If the view's epistemic data doesn't contain the expected
            statistics structure.
        """
        if not isinstance(view, VariableView):
            raise TypeError(f"view must be VariableView, got {type(view).__name__}")

        if horizon is None:
            horizon = 1
        elif horizon < 1:
            raise ValueError(f"horizon must be >= 1, got {horizon}")

        ewma_value = view.stats.ewma

        if ewma_value is None:
            return PredictionResult(
                value=None,
                horizon=horizon,
                metadata={
                    "reason": "EWMA statistic is not available (None). "
                    "Ensure data has been properly processed."
                },
            )

        # Use the pre-computed EWMA as the current level
        # For a persistence model, all future predictions are this value
        ewma_value = float(ewma_value)
        return PredictionResult(
            value=[ewma_value] * horizon,
            horizon=horizon,
            confidence=view.stats.confidence,
            metadata={"ewma": ewma_value, "horizon": horizon},
        )

    def __repr__(self) -> str:
        """
        Return official string representation of the predictor.

        Returns
        -------
        str
            String that can be used to recreate the predictor instance.
        """
        return f"EWMAPredictor(alpha={self.alpha})"

    def __str__(self) -> str:
        """
        Return human-readable string representation.

        Returns
        -------
        str
            Descriptive string of the predictor configuration.
        """
        return f"EWMAPredictor(alpha={self.alpha})"
