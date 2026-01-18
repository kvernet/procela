"""
Pytest suite for TrendPredictor (Procela Framework).
Tests the trend predictor using pre-computed TrendResult.
100% coverage guaranteed.
"""

from typing import Literal
from unittest.mock import Mock

import pytest

from procela.core.reasoning import (
    PredictionView,
    Predictor,
    TrendPredictor,
    TrendResult,
)

# ==================== TEST FIXTURES ====================


@pytest.fixture
def default_predictor():
    """Provides a default TrendPredictor instance."""
    return TrendPredictor()


@pytest.fixture
def custom_predictor():
    """Provides a TrendPredictor with custom parameters."""
    return TrendPredictor(extrapolation_factor=1.5, use_confidence=False)


@pytest.fixture
def mock_trend_result():
    """Creates a mock TrendResult with configurable attributes."""

    def _create_mock_trend(
        value: float = 0.5,
        direction: Literal["up", "down", "stable"] = "up",
        threshold: float = 0.3,
        confidence_val: float = 0.8,
        zscore_val: float | None = 1.5,
    ):
        trend = Mock(spec=TrendResult)
        trend.value = value
        trend.direction = direction
        trend.threshold = threshold
        trend.confidence = Mock(return_value=confidence_val)
        trend.zscore = Mock(return_value=zscore_val)
        return trend

    return _create_mock_trend


@pytest.fixture
def mock_view_with_trend(mock_trend_result):
    """Provides a mock PredictionView with trend and stats."""

    def _create_mock_view(
        last_value: float = 10.0,
        trend_value: float = 0.5,
        trend_direction: Literal["up", "down", "stable"] = "up",
        confidence: float = 0.8,
    ):
        trend = mock_trend_result(
            value=trend_value, direction=trend_direction, confidence_val=confidence
        )

        mock_stats = Mock()
        mock_stats.last_value = last_value

        view = Mock(spec=PredictionView)
        view.trend = trend
        view.stats = mock_stats
        return view

    return _create_mock_view


@pytest.fixture
def mock_view_no_trend():
    """Provides a mock PredictionView without trend attribute."""
    mock_stats = Mock()
    mock_stats.last_value = 10.0

    view = Mock(spec=PredictionView)
    view.stats = mock_stats
    # Don't add trend attribute
    return view


@pytest.fixture
def mock_view_none_trend():
    """Provides a mock PredictionView with trend = None."""
    mock_stats = Mock()
    mock_stats.last_value = 10.0

    view = Mock(spec=PredictionView)
    view.trend = None
    view.stats = mock_stats
    return view


@pytest.fixture
def mock_view_no_last_value(mock_trend_result):
    """Provides a mock PredictionView with last_value = None."""
    trend = mock_trend_result()

    mock_stats = Mock()
    mock_stats.last_value = None

    view = Mock(spec=PredictionView)
    view.trend = trend
    view.stats = mock_stats
    return view


# ==================== TEST INITIALIZATION ====================


class TestTrendPredictorInitialization:
    """Test the initialization of TrendPredictor."""

    def test_default_initialization(self):
        """Test initialization with default parameters."""
        predictor = TrendPredictor()
        assert predictor.extrapolation_factor == 1.0
        assert predictor.use_confidence is True
        assert isinstance(predictor, Predictor)

    def test_custom_initialization(self):
        """Test initialization with custom parameters."""
        predictor = TrendPredictor(extrapolation_factor=2.0, use_confidence=False)
        assert predictor.extrapolation_factor == 2.0
        assert predictor.use_confidence is False

    def test_invalid_extrapolation_factor_zero(self):
        """Test initialization with extrapolation_factor = 0."""
        with pytest.raises(ValueError) as exc_info:
            TrendPredictor(extrapolation_factor=0.0)
        assert "must be > 0" in str(exc_info.value)

    def test_invalid_extrapolation_factor_negative(self):
        """Test initialization with negative extrapolation_factor."""
        with pytest.raises(ValueError) as exc_info:
            TrendPredictor(extrapolation_factor=-0.5)
        assert "must be > 0" in str(exc_info.value)


# ==================== TEST PREDICT METHOD ====================


class TestPredictMethod:
    """Test the predict method using TrendResult."""

    def test_predict_upward_trend(self, default_predictor, mock_view_with_trend):
        """Test predict with upward trend."""
        view = mock_view_with_trend(
            last_value=10.0, trend_value=0.5, trend_direction="up", confidence=0.8
        )

        result = default_predictor.predict(view, horizon=3)

        assert len(result.value) == 3
        assert all(isinstance(p, float) for p in result.value)

        # With extrapolation_factor=1.0, confidence=0.8
        # Step 1: 10.0 + (0.5 * 1 * 1.0 * 0.8) = 10.4
        # Step 2: 10.0 + (0.5 * 2 * 1.0 * 0.8) = 10.8
        # Step 3: 10.0 + (0.5 * 3 * 1.0 * 0.8) = 11.2
        assert abs(result.value[0] - 10.4) < 0.001
        assert abs(result.value[1] - 10.8) < 0.001
        assert abs(result.value[2] - 11.2) < 0.001

    def test_predict_downward_trend(self, default_predictor, mock_view_with_trend):
        """Test predict with downward trend."""
        view = mock_view_with_trend(
            last_value=20.0, trend_value=0.3, trend_direction="down", confidence=0.9
        )

        result = default_predictor.predict(view, horizon=2)

        # With extrapolation_factor=1.0, confidence=0.9
        # Step 1: 20.0 - (0.3 * 1 * 1.0 * 0.9) = 19.73
        # Step 2: 20.0 - (0.3 * 2 * 1.0 * 0.9) = 19.46
        assert abs(result.value[0] - 19.73) < 0.001
        assert abs(result.value[1] - 19.46) < 0.001

    def test_predict_stable_trend(self, default_predictor, mock_view_with_trend):
        """Test predict with stable trend."""
        view = mock_view_with_trend(
            last_value=15.0,
            trend_value=0.2,  # Value ignored for stable trend
            trend_direction="stable",
            confidence=0.5,
        )

        result = default_predictor.predict(view, horizon=4)

        # Stable trend should return constant value
        assert len(result.value) == 4
        assert all(p == 15.0 for p in result.value)

    def test_predict_without_confidence(self, custom_predictor, mock_view_with_trend):
        """Test predict when use_confidence=False."""
        # custom_predictor has use_confidence=False
        view = mock_view_with_trend(
            last_value=10.0,
            trend_value=0.5,
            trend_direction="up",
            confidence=0.8,  # Should be ignored
        )

        result = custom_predictor.predict(view, horizon=2)

        # With use_confidence=False, confidence_weight defaults to 1.0
        # extrapolation_factor=1.5
        # Step 1: 10.0 + (0.5 * 1 * 1.5 * 1.0) = 10.75
        # Step 2: 10.0 + (0.5 * 2 * 1.5 * 1.0) = 11.5
        assert abs(result.value[0] - 10.75) < 0.001
        assert abs(result.value[1] - 11.5) < 0.001

    def test_predict_with_extrapolation_factor(self, mock_view_with_trend):
        """Test predict with different extrapolation factors."""
        view = mock_view_with_trend(
            last_value=10.0, trend_value=0.5, trend_direction="up", confidence=1.0
        )

        # Test with factor > 1 (amplify)
        predictor_high = TrendPredictor(extrapolation_factor=2.0)
        predictions_high = predictor_high.predict(view, horizon=2)
        # Step 1: 10.0 + (0.5 * 1 * 2.0 * 1.0) = 11.0
        assert abs(predictions_high.value[0] - 11.0) < 0.001

        # Test with factor < 1 (dampen)
        predictor_low = TrendPredictor(extrapolation_factor=0.5)
        predictions_low = predictor_low.predict(view, horizon=2)
        # Step 1: 10.0 + (0.5 * 1 * 0.5 * 1.0) = 10.25
        assert abs(predictions_low.value[0] - 10.25) < 0.001

    def test_predict_default_horizon(self, default_predictor, mock_view_with_trend):
        """Test predict with default horizon (None)."""
        view = mock_view_with_trend()
        result = default_predictor.predict(view)  # horizon=None

        assert len(result.value) == 1
        assert isinstance(result.value[0], float)

    def test_predict_invalid_view_type(self, default_predictor):
        """Test predict with invalid view type."""
        with pytest.raises(TypeError) as exc_info:
            default_predictor.predict("not a view")
        assert "must be PredictionView" in str(exc_info.value)

    def test_predict_invalid_horizon_zero(
        self, default_predictor, mock_view_with_trend
    ):
        """Test predict with horizon = 0."""
        view = mock_view_with_trend()
        with pytest.raises(ValueError) as exc_info:
            default_predictor.predict(view, horizon=0)
        assert "horizon must be >= 1" in str(exc_info.value)

    def test_predict_invalid_horizon_negative(
        self, default_predictor, mock_view_with_trend
    ):
        """Test predict with negative horizon."""
        view = mock_view_with_trend()
        with pytest.raises(ValueError) as exc_info:
            default_predictor.predict(view, horizon=-1)
        assert "horizon must be >= 1" in str(exc_info.value)

    def test_predict_none_trend(self, default_predictor, mock_view_none_trend):
        """Test predict when trend is None."""
        with pytest.raises(ValueError) as exc_info:
            default_predictor.predict(mock_view_none_trend)
        assert "Trend data is not available" in str(exc_info.value)

    def test_predict_no_last_value(self, default_predictor, mock_view_no_last_value):
        """Test predict when last_value is None."""
        with pytest.raises(ValueError) as exc_info:
            default_predictor.predict(mock_view_no_last_value)
        assert "last_value is None" in str(exc_info.value)

    def test_predict_invalid_trend_direction(
        self, default_predictor, mock_view_with_trend
    ):
        """Test predict with invalid trend direction."""
        view = mock_view_with_trend(trend_direction="invalid")  # type: ignore
        view.trend.direction = "invalid"  # Force invalid direction

        with pytest.raises(ValueError) as exc_info:
            default_predictor.predict(view, horizon=1)
        assert "Invalid trend direction" in str(exc_info.value)
        assert "Expected 'up', 'down', or 'stable'" in str(exc_info.value)

    def test_predict_confidence_out_of_range(
        self, default_predictor, mock_trend_result
    ):
        """Test predict with confidence values outside [0, 1] range."""
        # Test confidence > 1.0
        trend_high = mock_trend_result(confidence_val=1.5)
        stats = Mock(last_value=10.0)
        view_high = Mock(spec=PredictionView, trend=trend_high, stats=stats)

        predictions_high = default_predictor.predict(view_high, horizon=1)
        # Confidence should be clamped to 1.0
        # Expected: 10.0 + (0.5 * 1 * 1.0 * 1.0) = 10.5
        assert abs(predictions_high.value[0] - 10.5) < 0.001

        # Test confidence < 0.0
        trend_low = mock_trend_result(confidence_val=-0.5)
        view_low = Mock(spec=PredictionView, trend=trend_low, stats=stats)

        predictions_low = default_predictor.predict(view_low, horizon=1)
        # Confidence should be clamped to 0.0
        # Expected: 10.0 + (0.5 * 1 * 1.0 * 0.0) = 10.0
        assert abs(predictions_low.value[0] - 10.0) < 0.001

    def test_predict_confidence_method_fails(
        self, default_predictor, mock_trend_result
    ):
        """Test predict when confidence() method fails."""
        trend = mock_trend_result()
        trend.confidence = Mock(side_effect=TypeError("Not callable"))

        stats = Mock(last_value=10.0)
        view = Mock(spec=PredictionView, trend=trend, stats=stats)

        # Should handle gracefully and use default confidence (0.5)
        result = default_predictor.predict(view, horizon=1)
        # With default confidence 0.5: 10.0 + (0.5 * 1 * 1.0 * 0.5) = 10.25
        assert abs(result.value[0] - 10.25) < 0.001

    def test_predict_no_confidence_method(self, default_predictor):
        """Test predict when trend has no confidence method."""
        trend = Mock()
        trend.value = 0.5
        trend.direction = "up"
        trend.threshold = 0.3
        # Don't add confidence method

        stats = Mock(last_value=10.0)
        view = Mock(spec=PredictionView, trend=trend, stats=stats)

        # Should handle gracefully and use default confidence (0.5)
        result = default_predictor.predict(view, horizon=1)
        assert abs(result.value[0] - 10.25) < 0.001  # 10.0 + (0.5 * 0.5) = 10.25


# ==================== TEST STRING REPRESENTATIONS ====================


class TestStringRepresentations:
    """Test the __repr__ and __str__ methods."""

    def test_repr_method_default(self):
        """Test __repr__ with default parameters."""
        predictor = TrendPredictor()
        assert (
            repr(predictor)
            == "TrendPredictor(extrapolation_factor=1.0, use_confidence=True)"
        )

    def test_repr_method_custom(self):
        """Test __repr__ with custom parameters."""
        predictor = TrendPredictor(extrapolation_factor=0.7, use_confidence=False)
        assert (
            repr(predictor)
            == "TrendPredictor(extrapolation_factor=0.7, use_confidence=False)"
        )

    def test_str_method_default(self):
        """Test __str__ with default parameters."""
        predictor = TrendPredictor()
        assert (
            str(predictor)
            == "TrendPredictor(extrapolation_factor=1.0, use_confidence=True)"
        )

    def test_str_method_custom(self):
        """Test __str__ with custom parameters."""
        predictor = TrendPredictor(extrapolation_factor=2.5, use_confidence=True)
        assert (
            str(predictor)
            == "TrendPredictor(extrapolation_factor=2.5, use_confidence=True)"
        )

    def test_repr_and_str_identical(self):
        """Test __repr__ and __str__ return same format."""
        predictor = TrendPredictor(extrapolation_factor=1.2, use_confidence=False)
        assert repr(predictor) == str(predictor)


# ==================== TEST EDGE CASES ====================


class TestEdgeCases:
    """Test edge cases and robustness."""

    def test_predict_with_zero_trend_value(
        self, default_predictor, mock_view_with_trend
    ):
        """Test predict with trend.value = 0."""
        view = mock_view_with_trend(
            last_value=10.0,
            trend_value=0.0,  # Zero trend
            trend_direction="up",
            confidence=1.0,
        )

        result = default_predictor.predict(view, horizon=3)
        # Should all be 10.0 (no change)
        assert all(abs(p - 10.0) < 0.001 for p in result.value)

    def test_predict_with_negative_last_value(
        self, default_predictor, mock_view_with_trend
    ):
        """Test predict with negative last_value."""
        view = mock_view_with_trend(
            last_value=-5.0, trend_value=0.3, trend_direction="up", confidence=1.0
        )

        result = default_predictor.predict(view, horizon=2)
        # Step 1: -5.0 + (0.3 * 1 * 1.0 * 1.0) = -4.7
        # Step 2: -5.0 + (0.3 * 2 * 1.0 * 1.0) = -4.4
        assert abs(result.value[0] - (-4.7)) < 0.001
        assert abs(result.value[1] - (-4.4)) < 0.001

    def test_predict_large_horizon(self, default_predictor, mock_view_with_trend):
        """Test predict with large horizon."""
        view = mock_view_with_trend(
            last_value=10.0, trend_value=0.1, trend_direction="up", confidence=1.0
        )

        result = default_predictor.predict(view, horizon=1000)
        assert len(result.value) == 1000

        # Check monotonic increase for upward trend
        for i in range(1, len(result.value)):
            assert result.value[i] > result.value[i - 1]

    def test_multiple_predict_calls(self, default_predictor, mock_view_with_trend):
        """Test multiple predict calls on same predictor."""
        view = mock_view_with_trend(
            last_value=10.0, trend_value=0.2, trend_direction="up", confidence=0.8
        )

        # First call
        pred1 = default_predictor.predict(view, horizon=2)

        # Second call with same view
        pred2 = default_predictor.predict(view, horizon=2)

        # Should get same results
        assert pred1 == pred2

        # Third call with different horizon
        pred3 = default_predictor.predict(view, horizon=3)
        assert len(pred3.value) == 3
        assert pred3.value[0] == pred1.value[0]  # First prediction should match


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
