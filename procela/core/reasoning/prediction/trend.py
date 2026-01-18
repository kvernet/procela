"""
Trend-Based Predictor for the Procela Framework.

This module implements a trend-based predictor that forecasts future values
using pre-computed trend statistics from the epistemic data layer. It uses
the trend direction and magnitude to extrapolate future values.
"""

from __future__ import annotations

from ..result import PredictionResult
from ..view import PredictionView
from .base import Predictor


class TrendPredictor(Predictor):
    """
    Trend-Based Predictor using pre-computed trend statistics.

    This predictor uses the pre-computed trend analysis from the epistemic
    statistics to forecast future values. It extrapolates based on the
    trend direction (up/down/stable) and magnitude.

    Parameters
    ----------
    extrapolation_factor : float, optional
        Multiplier for trend extrapolation. Higher values result in more
        aggressive trend projections. Must be > 0. Default is 1.0.
    use_confidence : bool, optional
        Whether to incorporate trend confidence into predictions.
        Default is True.

    Attributes
    ----------
    extrapolation_factor : float
        Factor controlling trend extrapolation strength.
    use_confidence : bool
        Whether to use trend confidence in predictions.

    Raises
    ------
    ValueError
        If extrapolation_factor <= 0.

    Examples
    --------
    >>> from procela.core.reasoning import TrendPredictor
    >>>
    >>> predictor = TrendPredictor(extrapolation_factor=1.5)
    >>> predictor.extrapolation_factor
    1.5
    >>> predictor.use_confidence
    True
    """

    def __init__(
        self,
        extrapolation_factor: float = 1.0,
        use_confidence: bool = True,
    ) -> None:
        """
        Initialize the Trend Predictor.

        Parameters
        ----------
        extrapolation_factor : float, optional
            Factor controlling how strongly trends are extrapolated.
            Values > 1.0 amplify trends, values < 1.0 dampen them.
        use_confidence : bool, optional
            Whether to weight predictions by trend confidence.

        Raises
        ------
        ValueError
            If extrapolation_factor <= 0.

        Examples
        --------
        >>> from procela.core.reasoning import TrendPredictor
        >>>
        >>> predictor = TrendPredictor(extrapolation_factor=0.8, use_confidence=False)
        >>> predictor.extrapolation_factor
        0.8
        >>> predictor.use_confidence
        False
        """
        if extrapolation_factor <= 0:
            raise ValueError(
                f"extrapolation_factor must be > 0, got {extrapolation_factor}"
            )

        self.extrapolation_factor = extrapolation_factor
        self.use_confidence = use_confidence

    def predict(
        self,
        view: PredictionView,
        horizon: int | None = None,
    ) -> PredictionResult:
        """
        Generate predictions using pre-computed trend statistics.

        This method uses the TrendResult from the view to extrapolate
        future values based on trend direction and magnitude.

        Parameters
        ----------
        view : PredictionView
            View containing trend analysis results. Must provide
            access to `trend` attribute with TrendResult.
        horizon : int | None, optional
            Number of future steps to predict. If None, defaults to 1.
            Must be ≥ 1 if specified.

        Returns
        -------
        PredictionResult
            The prediction result containing value, confidence, and metadata.
            The value contains the predicted values for the specified horizon.

        Raises
        ------
        TypeError
            If view is not a PredictionView instance.
        ValueError
            If horizon is specified but < 1, or if trend data is
            not available or invalid.
        AttributeError
            If view doesn't have the required trend attribute.

        Notes
        -----
        The prediction formula:
        - For upward trend:
            base_value + (trend_value * step * factor * confidence_weight)
        - For downward trend:
            base_value - (trend_value * step * factor * confidence_weight)
        - For stable trend: constant base_value

        The base_value is obtained from `view.stats.last_value`.

        Examples
        --------
        >>> from procela.core.reasoning import TrendPredictor, TrendResult
        >>> from procela.core.memory import HistoryStatistics
        >>>
        >>> predictor = TrendPredictor()
        >>> class View:
        ...     trend = TrendResult(value=0.5, direction="up", threshold=0.3)
        ...     stats = HistoryStatistics(last_value=10.4)
        >>> view = View()
        >>> predictions = predictor.predict(view, horizon=3)
        >>> len(predictions)
        3
        """
        if not isinstance(view, PredictionView):
            raise TypeError(f"view must be PredictionView, got {type(view).__name__}")

        if horizon is None:
            horizon = 1
        elif horizon < 1:
            raise ValueError(f"horizon must be >= 1, got {horizon}")

        trend = view.trend
        if trend is None:
            raise ValueError("Trend data is not available (None)")

        base_value = view.stats.last_value
        if base_value is None:
            raise ValueError("Cannot predict: last_value is None")

        # Calculate confidence weight if enabled
        confidence_weight = 1.0
        if self.use_confidence and hasattr(trend, "confidence"):
            try:
                confidence = trend.confidence()
                # Clamp confidence to [0, 1] range
                confidence_weight = max(0.0, min(1.0, confidence))
            except (TypeError, AttributeError):
                # If confidence() fails or returns invalid value, use default
                confidence_weight = 0.5  # Moderate uncertainty

        # Generate predictions based on trend direction
        predictions = []

        for step in range(1, horizon + 1):
            if trend.direction == "up":
                # Upward trend: add trend value
                prediction = base_value + (
                    trend.value * step * self.extrapolation_factor * confidence_weight
                )
            elif trend.direction == "down":
                # Downward trend: subtract trend value
                prediction = base_value - (
                    trend.value * step * self.extrapolation_factor * confidence_weight
                )
            elif trend.direction == "stable":
                # Stable trend: constant value
                prediction = float(base_value)
            else:
                raise ValueError(
                    f"Invalid trend direction: {trend.direction}. "
                    "Expected 'up', 'down', or 'stable'."
                )

            predictions.append(float(prediction))

        return PredictionResult(
            value=predictions,
            horizon=horizon,
            confidence=None,
            metadata={"n_predictions": len(predictions), "horizon": horizon},
        )

    def __repr__(self) -> str:
        """
        Return official string representation.

        Returns
        -------
        str
            String that can be used to recreate the predictor.

        Examples
        --------
        >>> from procela.core.reasoning import TrendPredictor
        >>>
        >>> predictor = TrendPredictor(extrapolation_factor=1.2, use_confidence=False)
        >>> repr(predictor)
        'TrendPredictor(extrapolation_factor=1.2, use_confidence=False)'
        """
        return (
            f"TrendPredictor(extrapolation_factor={self.extrapolation_factor}, "
            f"use_confidence={self.use_confidence})"
        )

    def __str__(self) -> str:
        """
        Return human-readable string representation.

        Returns
        -------
        str
            Descriptive string of the predictor.

        Examples
        --------
        >>> from procela.core.reasoning import TrendPredictor
        >>>
        >>> predictor = TrendPredictor(extrapolation_factor=0.8)
        >>> str(predictor)
        'TrendPredictor(extrapolation_factor=0.8, use_confidence=True)'
        """
        return (
            f"TrendPredictor(extrapolation_factor={self.extrapolation_factor}, "
            f"use_confidence={self.use_confidence})"
        )
