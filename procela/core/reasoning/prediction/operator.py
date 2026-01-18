"""
Prediction operators for the reasoning subsystem.

This module defines the PredictionOperator class used to perform
computational predictions over variable histories. Operators in this
module compute prediction results only; the semantics of predictions
are defined externally.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/prediction/operator.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/prediction/operator.html
"""

from __future__ import annotations

from ..result import PredictionResult
from ..view import PredictionView
from .base import Predictor


class PredictionOperator:
    """
    Operator for performing predictions.

    This class executes computational prediction using a Predictor instance
    over a PredictionView. It does not define the semantic interpretation
    of predictions; this is handled externally.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/prediction/operator.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/reasoning/prediction/operator.html
    """

    def predict(
        self,
        predictor: Predictor,
        view: PredictionView,
        horizon: int | None = None,
    ) -> PredictionResult:
        """
        Predict future values for a given horizon.

        Parameters
        ----------
        predictor : Predictor
            Predictor instance used to perform the computation.
        view : PredictionView
            Structured view of the data to predict.
        horizon : int or None, optional
            Number of steps into the future to predict. Default is None.

        Returns
        -------
        PredictionResult
            Object containing the predicted value, optional horizon, confidence,
            and metadata about the predictor and horizon.

        Raises
        ------
        TypeError
            If `predictor` is not a Predictor instance or `view` is not a
            PredictionView.

        Notes
        -----
        This method performs computation only. Semantic interpretation of the
        predicted value is defined in the external semantics documentation.
        """
        if not isinstance(predictor, Predictor):
            raise TypeError(
                f"predictor should be a Predictor instance, got {predictor}"
            )

        if not isinstance(view, PredictionView):
            raise TypeError(f"view should be a PredictionView, got {view}")

        result = predictor.predict(view, horizon)

        return PredictionResult(
            value=result,
            horizon=horizon,
            confidence=None,  # explicitly undefined for now
            metadata={
                "predictor": predictor.__class__.__name__,
                "horizon": horizon,
            },
        )
