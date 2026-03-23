"""
Prediction operators for the reasoning subsystem.

This module defines the PredictionOperator class used to perform
computational predictions over variable histories. Operators in this
module compute prediction results only; the semantics of predictions
are defined externally.

Examples
--------
>>> from procela import (
...     Variable,
...     StatisticalDomain,
...     VariableRecord,
...     PredictionOperator,
...     get_predictor
... )
>>>
>>> var = Variable("var", StatisticalDomain())
>>> var.set(VariableRecord(value=12, confidence=0.98))
>>> var.set(VariableRecord(value=13, confidence=0.94))
>>> var.set(VariableRecord(value=11, confidence=0.90))
>>> view = var.epistemic()
>>>
>>> operator = PredictionOperator()
>>> predictor = get_predictor(name="ewma")
>>>
>>> result = operator.predict(
...     predictor=predictor,
...     view=view, horizon=3
... )
>>> print(result.value)
PredictionResult(value=[11.91, 11.91, 11.91], horizon=3, confidence=0.94, ...
>>> print(result.horizon)
3

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/prediction/operator.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/prediction/operator.html
"""

from __future__ import annotations

from ...assessment.prediction import PredictionResult
from ...epistemic.variable import VariableView
from .base import Predictor


class PredictionOperator:
    """
    Operator for performing predictions.

    This class executes computational prediction using a Predictor instance
    over a VariableView. It does not define the semantic interpretation
    of predictions; this is handled externally.

    Examples
    --------
    >>> from procela import (
    ...     Variable,
    ...     StatisticalDomain,
    ...     VariableRecord,
    ...     PredictionOperator,
    ...     get_predictor
    ... )
    >>>
    >>> var = Variable("var", StatisticalDomain())
    >>> var.set(VariableRecord(value=12, confidence=0.98))
    >>> var.set(VariableRecord(value=13, confidence=0.94))
    >>> var.set(VariableRecord(value=11, confidence=0.90))
    >>> view = var.epistemic()
    >>>
    >>> operator = PredictionOperator()
    >>> predictor = get_predictor(name="ewma")
    >>>
    >>> result = operator.predict(
    ...     predictor=predictor,
    ...     view=view, horizon=3
    ... )
    >>> print(result.value)
    PredictionResult(value=[11.91, 11.91, 11.91], horizon=3, confidence=0.94, ...
    >>> print(result.horizon)
    3
    """

    def predict(
        self,
        predictor: Predictor,
        view: VariableView,
        horizon: int | None = None,
    ) -> PredictionResult:
        """
        Predict future values for a given horizon.

        Parameters
        ----------
        predictor : Predictor
            Predictor instance used to perform the computation.
        view : VariableView
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
            VariableView.

        Notes
        -----
        This method performs computation only. Semantic interpretation of the
        predicted value is defined in the external semantics documentation.
        """
        if not isinstance(predictor, Predictor):
            raise TypeError(
                f"predictor should be a Predictor instance, got {predictor}"
            )

        if not isinstance(view, VariableView):
            raise TypeError(f"view should be a VariableView, got {view}")

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
