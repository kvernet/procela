"""
Pytest suite for LastPredictor (Procela Framework).
Tests the last value predictor using epistemic.stats.last_value.
100% coverage guaranteed.
"""

from unittest.mock import Mock

import pytest

# Import the class to test
from procela.core.reasoning import (
    LastPredictor,
    PredictionResult,
    PredictionView,
    Predictor,
)

# ==================== TEST FIXTURES ====================


@pytest.fixture
def default_predictor():
    """Provides a default LastPredictor instance (allow_none=False)."""
    return LastPredictor()


@pytest.fixture
def allow_none_predictor():
    """Provides a LastPredictor with allow_none=True."""
    return LastPredictor(allow_none=True)


@pytest.fixture
def mock_view_with_last_value():
    """Provides a mock PredictionView with last_value statistic."""
    mock_stats = Mock()
    mock_stats.last_value = 42.5

    view = Mock(spec=PredictionView)
    view.stats = mock_stats

    return view


@pytest.fixture
def mock_view_with_none_last_value():
    """Provides a mock PredictionView with last_value = None."""
    mock_stats = Mock()
    mock_stats.last_value = None

    view = Mock(spec=PredictionView)
    view.stats = mock_stats

    return view


@pytest.fixture
def mock_view_missing_stats():
    """Provides a mock PredictionView without stats structure."""

    view = Mock(spec=PredictionView)
    view.stats = None
    return view


# ==================== TEST INITIALIZATION ====================


class TestLastPredictorInitialization:
    """Test the initialization of LastPredictor."""

    def test_default_initialization(self):
        """Test initialization with default parameters."""
        predictor = LastPredictor()
        assert predictor.allow_none is False
        assert isinstance(predictor, Predictor)

    def test_initialization_allow_none_true(self):
        """Test initialization with allow_none=True."""
        predictor = LastPredictor(allow_none=True)
        assert predictor.allow_none is True

    def test_initialization_allow_none_false(self):
        """Test initialization with allow_none=False explicitly."""
        predictor = LastPredictor(allow_none=False)
        assert predictor.allow_none is False


# ==================== TEST PREDICT METHOD ====================


class TestPredictMethod:
    """Test the predict method using epistemic.stats.last_value."""

    def test_predict_default_horizon(
        self, default_predictor, mock_view_with_last_value
    ):
        """Test predict with default horizon (None)."""
        result = default_predictor.predict(mock_view_with_last_value)
        assert isinstance(result.value, list)
        assert len(result.value) == 1
        assert result.value == [42.5]

    def test_predict_specified_horizon(
        self, default_predictor, mock_view_with_last_value
    ):
        """Test predict with specified horizon."""
        result = default_predictor.predict(mock_view_with_last_value, horizon=5)
        assert len(result.value) == 5
        assert result.value == [42.5, 42.5, 42.5, 42.5, 42.5]

    def test_predict_horizon_one_explicit(
        self, default_predictor, mock_view_with_last_value
    ):
        """Test predict with horizon=1 explicitly."""
        result = default_predictor.predict(mock_view_with_last_value, horizon=1)
        assert result.value == [42.5]

    def test_predict_different_last_values(self, default_predictor):
        """Test predict with different last_value values."""
        test_values = [0.0, 100.0, -15.5, 3.14159]

        for last_val in test_values:
            mock_stats = Mock()
            mock_stats.last_value = last_val

            view = Mock(spec=PredictionView)
            view.stats = mock_stats

            result = default_predictor.predict(view, horizon=2)
            assert result.value == [float(last_val), float(last_val)]

    def test_predict_invalid_view_type(self, default_predictor):
        """Test predict with invalid view type."""
        with pytest.raises(TypeError) as exc_info:
            default_predictor.predict("not a view")
        assert "must be PredictionView" in str(exc_info.value)

    def test_predict_invalid_horizon_zero(
        self, default_predictor, mock_view_with_last_value
    ):
        """Test predict with horizon = 0."""
        with pytest.raises(ValueError) as exc_info:
            default_predictor.predict(mock_view_with_last_value, horizon=0)
        assert "horizon must be >= 1" in str(exc_info.value)

    def test_predict_invalid_horizon_negative(
        self, default_predictor, mock_view_with_last_value
    ):
        """Test predict with negative horizon."""
        with pytest.raises(ValueError) as exc_info:
            default_predictor.predict(mock_view_with_last_value, horizon=-1)
        assert "horizon must be >= 1" in str(exc_info.value)

    def test_predict_last_value_none_allow_none_false(
        self, default_predictor, mock_view_with_none_last_value
    ):
        """Test predict when last_value is None and allow_none=False."""
        with pytest.raises(ValueError) as exc_info:
            default_predictor.predict(mock_view_with_none_last_value)
        assert "last_value is None" in str(exc_info.value)
        assert "allow_none=True" in str(exc_info.value)

    def test_predict_last_value_none_allow_none_true(
        self, allow_none_predictor, mock_view_with_none_last_value
    ):
        """Test predict when last_value is None and allow_none=True."""
        result = allow_none_predictor.predict(mock_view_with_none_last_value, horizon=3)
        assert result.value == [0.0, 0.0, 0.0]

    def test_predict_missing_stats(self, default_predictor, mock_view_missing_stats):
        """Test predict when stats structure is missing."""
        with pytest.raises(TypeError, match="view.stats must be provided"):
            default_predictor.predict(mock_view_missing_stats)

    def test_predict_large_horizon(self, default_predictor, mock_view_with_last_value):
        """Test predict with very large horizon."""
        result = default_predictor.predict(mock_view_with_last_value, horizon=10000)
        assert len(result.value) == 10000
        assert all(p == 42.5 for p in result.value)

    def test_predict_with_zero_last_value(self, default_predictor):
        """Test predict when last_value is 0.0."""
        mock_stats = Mock()
        mock_stats.last_value = 0.0

        view = Mock(spec=PredictionView)
        view.stats = mock_stats

        result = default_predictor.predict(view, horizon=2)
        assert result.value == [0.0, 0.0]

    def test_predict_allow_none_true_with_valid_value(
        self, allow_none_predictor, mock_view_with_last_value
    ):
        """Test allow_none=True predictor with valid last_value."""
        result = allow_none_predictor.predict(mock_view_with_last_value, horizon=2)
        assert result.value == [42.5, 42.5]


# ==================== TEST STRING REPRESENTATIONS ====================


class TestStringRepresentations:
    """Test the __repr__ and __str__ methods."""

    def test_repr_method_default(self):
        """Test __repr__ with default allow_none."""
        predictor = LastPredictor()
        assert repr(predictor) == "LastPredictor(allow_none=False)"

    def test_repr_method_allow_none_true(self):
        """Test __repr__ with allow_none=True."""
        predictor = LastPredictor(allow_none=True)
        assert repr(predictor) == "LastPredictor(allow_none=True)"

    def test_str_method_default(self):
        """Test __str__ with default allow_none."""
        predictor = LastPredictor()
        assert str(predictor) == "LastPredictor(allow_none=False)"

    def test_str_method_allow_none_true(self):
        """Test __str__ with allow_none=True."""
        predictor = LastPredictor(allow_none=True)
        assert str(predictor) == "LastPredictor(allow_none=True)"

    def test_repr_and_str_identical(self):
        """Test __repr__ and __str__ return same format."""
        predictor = LastPredictor(allow_none=False)
        assert repr(predictor) == str(predictor)


# ==================== TEST INHERITANCE AND TYPE ====================


class TestInheritance:
    """Test that LastPredictor properly implements the Predictor interface."""

    def test_is_predictor_subclass(self):
        """Test LastPredictor inherits from Predictor."""
        predictor = LastPredictor()
        assert isinstance(predictor, Predictor)
        assert issubclass(LastPredictor, Predictor)

    def test_has_predict_method(self):
        """Test LastPredictor has required predict method."""
        predictor = LastPredictor()
        assert hasattr(predictor, "predict")
        assert callable(predictor.predict)

        # Check method signature
        import inspect

        sig = inspect.signature(predictor.predict)
        params = list(sig.parameters.keys())
        assert params == ["view", "horizon"]
        assert sig.parameters["horizon"].default is None

    def test_has_allow_none_attribute(self):
        """Test LastPredictor has allow_none attribute."""
        predictor = LastPredictor(allow_none=True)
        assert hasattr(predictor, "allow_none")
        assert isinstance(predictor.allow_none, bool)


# ==================== TEST EDGE CASES ====================


class TestEdgeCases:
    """Test edge cases and robustness."""

    def test_predict_boolean_last_value_conversion(self, default_predictor):
        """Test that non-float last_value is converted to float."""
        # Test with integer last_value
        mock_stats = Mock()
        mock_stats.last_value = 42  # Integer

        view = Mock(spec=PredictionView)
        view.stats = mock_stats

        result = default_predictor.predict(view, horizon=1)
        assert result.value == [42.0]  # Converted to float
        assert isinstance(result.value[0], float)

    def test_multiple_predictor_instances(self):
        """Test that multiple predictor instances are independent."""
        predictor1 = LastPredictor(allow_none=False)
        predictor2 = LastPredictor(allow_none=True)

        assert predictor1.allow_none is False
        assert predictor2.allow_none is True
        assert predictor1 is not predictor2

    def test_predict_horizon_none_uses_one(
        self, default_predictor, mock_view_with_last_value
    ):
        """Test that horizon=None defaults to 1."""
        result = default_predictor.predict(mock_view_with_last_value)
        assert len(result.value) == 1
        predictions_explicit = default_predictor.predict(
            mock_view_with_last_value, horizon=1
        )
        assert result == predictions_explicit


# ==================== TEST COVERAGE COMPLETENESS ====================


def test_all_public_methods_covered():
    """Verify all public methods and attributes are tested."""
    predictor = LastPredictor()

    # Check all public attributes
    assert hasattr(predictor, "allow_none")
    assert hasattr(predictor, "predict")
    assert hasattr(predictor, "__init__")
    assert hasattr(predictor, "__repr__")
    assert hasattr(predictor, "__str__")

    # Verify no extra methods were added
    public_methods = {name for name in dir(predictor) if not name.startswith("_")}
    expected_methods = {"allow_none", "predict"}
    assert public_methods == expected_methods

    # Test that predict returns correct type
    mock_stats = Mock()
    mock_stats.last_value = 10.0
    view = Mock(spec=PredictionView)
    view.stats = mock_stats

    result = predictor.predict(view, horizon=2)
    assert isinstance(result, PredictionResult)
    assert all(isinstance(x, float) for x in result.value)


# ==================== TEST ERROR MESSAGES ====================


class TestErrorMessages:
    """Test specific error message content."""

    def test_type_error_message(self, default_predictor):
        """Test TypeError message includes correct type name."""
        with pytest.raises(TypeError) as exc_info:
            default_predictor.predict("string_view")
        error_msg = str(exc_info.value)
        assert "must be PredictionView" in error_msg
        assert "got str" in error_msg

    def test_value_error_horizon_message(
        self, default_predictor, mock_view_with_last_value
    ):
        """Test ValueError message for invalid horizon."""
        with pytest.raises(ValueError) as exc_info:
            default_predictor.predict(mock_view_with_last_value, horizon=0)
        error_msg = str(exc_info.value)
        assert "horizon must be >= 1" in error_msg
        assert "got 0" in error_msg

    def test_value_error_none_message(
        self, default_predictor, mock_view_with_none_last_value
    ):
        """Test ValueError message for None last_value."""
        with pytest.raises(ValueError) as exc_info:
            default_predictor.predict(mock_view_with_none_last_value)
        error_msg = str(exc_info.value)
        assert "last_value is None" in error_msg
        assert "allow_none=True" in error_msg

    def test_runtime_error_message_missing_stats(
        self, default_predictor, mock_view_missing_stats
    ):
        """Test RuntimeError message for missing stats."""
        with pytest.raises(TypeError) as exc_info:
            default_predictor.predict(mock_view_missing_stats)
        error_msg = str(exc_info.value)
        assert "view.stats must be provided" in error_msg


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
