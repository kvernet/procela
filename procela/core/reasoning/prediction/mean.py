"""
Mean Value Predictor for the Procela Framework.

This module implements a predictor that forecasts future values based on the
historical arithmetic mean of the observed data. It is a simple baseline model
that assumes the central tendency of past behavior will continue into the future.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/prediction/mean.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/reasoning/prediction/mean.html
"""

from __future__ import annotations

from ...assessment.prediction import PredictionResult
from ...epistemic.variable import VariableView
from .base import Predictor


class MeanPredictor(Predictor):
    """
    Mean Value Predictor for forecasting using the historical average.

    This predictor uses the pre-computed arithmetic mean from the epistemic
    statistics to forecast future values. It represents a simple model where
    the expected future value is assumed to be the average of all past
    observations.

    Parameters
    ----------
    None
        This predictor does not require initialization parameters.

    Attributes
    ----------
    None
        This predictor does not have instance attributes.
    """

    def predict(
        self,
        view: VariableView,
        horizon: int | None = None,
    ) -> PredictionResult:
        """
        Generate predictions using the historical mean.

        This method accesses the pre-computed mean statistic from the epistemic
        data layer and returns it as the prediction. The `horizon` parameter is
        accepted for interface compatibility but does not affect the result.

        Parameters
        ----------
        view : VariableView
            A view containing epistemic data with pre-computed statistics.
            Must provide access to `stats.mean()` method.
        horizon : int | None, optional
            The number of future steps to predict. This parameter is ignored
            by the MeanPredictor but is included for interface consistency.
            Default is None.

        Returns
        -------
        PredictionResult
            The prediction result containing value, confidence, and metadata.
            The value type matches the output of `stats.mean()`.

        Raises
        ------
        TypeError
            If `view` is not an instance of `VariableView`.
        AttributeError
            If the `view` does not provide the required `stats.mean()`
            interface.

        Notes
        -----
        - The MeanPredictor implements a constant model, returning the same
          value regardless of the prediction horizon.
        - This predictor serves as a useful baseline for comparing more
          sophisticated forecasting methods within the Procela framework.
        """
        if not isinstance(view, VariableView):
            raise TypeError(f"view must be VariableView, got {type(view).__name__}")

        if view.stats is None:
            return PredictionResult(
                value=None,
                horizon=horizon,
                metadata={"reason": "No statistics available"},
            )

        return PredictionResult(
            value=view.stats.mean,
            horizon=horizon,
            confidence=view.stats.confidence,
            metadata={
                "count": view.stats.count,
                "sum": view.stats.sum,
                "horizon": horizon,
            },
        )

    def __repr__(self) -> str:
        """
        Return official string representation of the predictor.

        Returns
        -------
        str
            String that can be used to recreate the predictor instance.
        """
        return "MeanPredictor()"

    def __str__(self) -> str:
        """
        Return human-readable string representation.

        Returns
        -------
        str
            Descriptive string of the predictor.
        """
        return "MeanPredictor()"
