"""
Last Value Predictor for the Procela Framework.

This module implements a simple predictor that forecasts future values based
on the last observed value from epistemic statistics. It's a persistence
model that assumes the most recent observation will continue into the future.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/prediction/last.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/reasoning/prediction/last.html
"""

from __future__ import annotations

from ..result import PredictionResult
from ..view import PredictionView
from .base import Predictor


class LastPredictor(Predictor):
    """
    Last Value Predictor for persistence-based forecasting.

    This predictor uses the most recent observed value from epistemic
    statistics to forecast future values. It implements a simple persistence
    model where the last observed value is assumed to continue unchanged
    into the future.

    This is particularly useful as a baseline predictor or for systems
    where values change slowly or infrequently.

    Parameters
    ----------
    allow_none : bool, optional
        Whether to allow prediction when last_value is None.
        If True and last_value is None, returns [0.0] * horizon.
        If False and last_value is None, raises ValueError.
        Default is False.

    Attributes
    ----------
    allow_none : bool
        Flag indicating whether to allow None last_value.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/prediction/last.html

    Examples Reference
    -------------------
    https://procela.org/docs/examples/core/reasoning/prediction/last.html
    """

    def __init__(self, allow_none: bool = False) -> None:
        """
        Initialize the Last Value Predictor.

        Parameters
        ----------
        allow_none : bool, optional
            Whether to allow prediction when last_value is None.
            Default is False.
        """
        self.allow_none = allow_none

    def predict(
        self,
        view: PredictionView,
        horizon: int | None = None,
    ) -> PredictionResult:
        """
        Generate predictions using the last observed value.

        This method retrieves the last_value from epistemic statistics
        and returns it repeated for the specified horizon. If last_value
        is None and allow_none is True, returns zeros instead.

        Parameters
        ----------
        view : PredictionView
            View containing epistemic data including pre-computed statistics.
            Must provide access to `epistemic.stats.last_value`.
        horizon : int | None, optional
            Number of future steps to predict. If None, defaults to 1.
            Must be ≥ 1 if specified.

        Returns
        -------
        PredictionResult
            The prediction result containing value, confidence, and metadata.
            All values are identical, representing persistence of
            the last observed value.

        Raises
        ------
        TypeError
            If view is not a PredictionView instance.
        ValueError
            If horizon is specified but < 1, or if last_value is None
            and allow_none is False.
        RuntimeError
            If the view's epistemic data doesn't contain the expected
            statistics structure.
        """
        if not isinstance(view, PredictionView):
            raise TypeError(f"view must be PredictionView, got {type(view).__name__}")

        if not view.stats:
            raise TypeError("view.stats must be provided")

        if horizon is None:
            horizon = 1
        elif horizon < 1:
            raise ValueError(f"horizon must be >= 1, got {horizon}")

        last_value = view.stats.last_value

        if last_value is None:
            if self.allow_none:
                # Use zeros when last_value is None and allow_none is True
                predictions = [0.0] * horizon
            else:
                raise ValueError(
                    "last_value is None. Set allow_none=True to use zeros."
                )
        else:
            # Use the last_value for all predictions
            predictions = [float(last_value)] * horizon

        return PredictionResult(
            value=predictions,
            horizon=horizon,
            confidence=None,
            metadata={"n_predictions": len(predictions), "horizon": horizon},
        )

    def __repr__(self) -> str:
        """
        Return official string representation of the predictor.

        Returns
        -------
        str
            String that can be used to recreate the predictor instance.
        """
        return f"LastPredictor(allow_none={self.allow_none})"

    def __str__(self) -> str:
        """
        Return human-readable string representation.

        Returns
        -------
        str
            Descriptive string of the predictor configuration.
        """
        return f"LastPredictor(allow_none={self.allow_none})"
