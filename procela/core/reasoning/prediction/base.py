"""
Base Abstract Predictor Class for the Procela Framework.

This module defines the foundational abstract base class for all predictors
within the Procela framework. Predictors are specialized components responsible
for forecasting future states and values of system variables based on
epistemic data and active reasoning.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/prediction/base.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/prediction/base.html
"""

from abc import ABC, abstractmethod

from ..result import PredictionResult
from ..view import PredictionView


class Predictor(ABC):
    """
    Abstract Base Class for all predictive reasoners in Procela.

    A `Predictor` is an active reasoning entity that forecasts future values or
    states of system variables. It operates on epistemic data (what is known)
    to generate predictions, supporting the framework's goal of moving beyond
    correlations to model stateful, resource-aware, and constraint-respecting
    processes.

    This class defines the mandatory interface that all concrete predictor
    implementations must fulfill. Implementations should provide intelligent,
    context-aware forecasting with capabilities for explaining their state and
    reasoning in human-readable terms.

    Parameters
    ----------
    This is an abstract base class and is not instantiated directly.
    Concrete subclasses define their own `__init__` parameters.

    Attributes
    ----------
    Subclasses define their own attributes based on their predictive logic.

    Methods
    -------
    predict(view: PredictionView, horizon: int | None = None) -> Any
        Core abstract method to generate predictions. Must be implemented
        by all subclasses.

    Raises
    ------
    TypeError
        If `view` is not an instance of `PredictionView`.
    NotImplementedError
        If a concrete subclass does not implement the `predict` method.

    Notes
    -----
    - The `horizon` parameter typically defines how many steps into the future
      to predict. A value of `None` may indicate a default horizon or a
      single-step prediction, depending on the subclass implementation.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/prediction/base.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/reasoning/prediction/base.html
    """

    @abstractmethod
    def predict(
        self,
        view: PredictionView,
        horizon: int | None = None,
    ) -> PredictionResult:
        """
        Generate a prediction based on the provided epistemic view.

        This is the core method of the predictor. It takes a snapshot of the
        system's current and historical state and produces a forecast for one
        or more future time steps.

        Parameters
        ----------
        view : PredictionView
            A structured view containing the historical data, current state,
            variable metadata, and any other epistemic information required
            to form a prediction. The predictor may analyze trends, patterns,
            or constraints within this view.
        horizon : int | None, optional
            The number of future steps to predict. The interpretation (e.g.,
            time units, cycles) is domain-specific.
            If `None`, the predictor should use a default horizon or make a
            single-step prediction. The default is `None`.

        Returns
        -------
        PredictionResult
            The prediction result containing value, confidence, and metadata.

        Raises
        ------
        TypeError
            If the provided `view` is not a valid `PredictionView` instance.
        ValueError
            If the `view` does not contain sufficient or valid data for
            prediction, or if the `horizon` is invalid (e.g., negative).
        RuntimeError
            If an internal error occurs during the prediction logic.

        Notes
        -----
        Implementations of this method in subclasses should:
        1. Validate the input `view` and `horizon` parameters.
        2. Perform the core predictive reasoning.
        3. Return the result in a consistent, documented format.
        4. Ideally, provide explanations for the prediction suitable for the
           framework's goal of human-readable state explanation.
        """
        pass
