"""
Mean Value Predictor for the Procela Framework.

This module implements a predictor that forecasts future values based on the
historical arithmetic mean of the observed data. It is a simple baseline model
that assumes the central tendency of past behavior will continue into the future.
"""

from __future__ import annotations

from ..result import PredictionResult
from ..view import PredictionView
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

    Methods
    -------
    predict(view: PredictionView, horizon: int | None = None) -> float | None
        Returns the historical mean as the prediction.

    Examples
    --------
    >>> from procela.core.reasoning import MeanPredictor
    >>>
    >>> predictor = MeanPredictor()
    >>> # Assuming `view` is a properly constructed PredictionView
    >>> # with stats.mean() method
    >>> predictor.predict(view)
    """

    def predict(
        self,
        view: PredictionView,
        horizon: int | None = None,
    ) -> PredictionResult:
        """
        Generate predictions using the historical mean.

        This method accesses the pre-computed mean statistic from the epistemic
        data layer and returns it as the prediction. The `horizon` parameter is
        accepted for interface compatibility but does not affect the result.

        Parameters
        ----------
        view : PredictionView
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
            If `view` is not an instance of `PredictionView`.
        AttributeError
            If the `view` does not provide the required `stats.mean()`
            interface.

        Notes
        -----
        - The MeanPredictor implements a constant model, returning the same
          value regardless of the prediction horizon.
        - This predictor serves as a useful baseline for comparing more
          sophisticated forecasting methods within the Procela framework.

        Examples
        --------
        >>> from procela.core.reasoning import MeanPredictor
        >>> from procela.core.memory import HistoryStatistics
        >>>
        >>> predictor = MeanPredictor()
        >>> # Create a view with stats
        >>> class View:
        ...     stats = HistoryStatistics(count=5, sum=210.0)
        ...     trend = None
        >>>
        >>> view = View()
        >>> # Cast to PredictionView for example (in reality, would be instance)
        >>> result = predictor.predict(view, horizon=5)
        >>> result
        42.0
        """
        if not isinstance(view, PredictionView):
            raise TypeError(f"view must be PredictionView, got {type(view).__name__}")

        if view.stats is None:
            return PredictionResult(
                value=None,
                horizon=horizon,
                metadata={"reason": "No statistics available"},
            )

        return PredictionResult(
            value=view.stats.mean(),
            horizon=horizon,
            confidence=view.stats.confidence(),
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

        Examples
        --------
        >>> from procela.core.reasoning import MeanPredictor
        >>>
        >>> predictor = MeanPredictor()
        >>> repr(predictor)
        'MeanPredictor()'
        """
        return "MeanPredictor()"

    def __str__(self) -> str:
        """
        Return human-readable string representation.

        Returns
        -------
        str
            Descriptive string of the predictor.

        Examples
        --------
        >>> from procela.core.reasoning import MeanPredictor
        >>>
        >>> predictor = MeanPredictor()
        >>> str(predictor)
        'MeanPredictor()'
        """
        return "MeanPredictor()"
