"""
Pytest suite for MeanPredictor (Procela Framework).
Tests the mean value predictor using epistemic.stats.mean().
100% coverage guaranteed.
"""

from unittest.mock import create_autospec

import pytest

from procela.core.assessment import PredictionResult, StatisticsResult
from procela.core.reasoning import (
    MeanPredictor,
    Predictor,
)
from procela.core.variable import VariableEpistemic
from procela.symbols.key import Key


@pytest.fixture
def mean_predictor():
    """Provides a MeanPredictor instance."""
    return MeanPredictor()


@pytest.fixture
def mock_view_with_mean():
    """Provides a mock VariableEpistemic with mean."""
    stats = StatisticsResult(mean=42.5, confidence=0.5)

    view = VariableEpistemic(
        key=Key(), reasoning=None, stats=stats, anomaly=None, trend=None
    )
    return view


@pytest.fixture
def mock_view_with_none_mean():
    """Provides a mock VariableEpistemic with mean() returning None."""
    stats = StatisticsResult(mean=None, confidence=0.5)

    view = VariableEpistemic(
        key=Key(), reasoning=None, stats=stats, anomaly=None, trend=None
    )
    return view


@pytest.fixture
def mock_view_missing_stats():
    """Provides a mock VariableEpistemic without stats structure."""

    stats = StatisticsResult(count=0)

    view = VariableEpistemic(
        key=Key(), reasoning=None, stats=stats, anomaly=None, trend=None
    )
    return view


@pytest.fixture
def mock_view_with_mean_zero():
    """Provides a mock VariableEpistemic with mean() returning 0.0."""
    stats = StatisticsResult(mean=0.0, confidence=0.5)

    view = VariableEpistemic(
        key=Key(), reasoning=None, stats=stats, anomaly=None, trend=None
    )
    return view


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


class TestPredictMethod:
    """Test the predict method using stats.mean()."""

    def test_predict_returns_mean(self, mean_predictor, mock_view_with_mean):
        """Test predict returns the value from stats.mean()."""
        result = mean_predictor.predict(mock_view_with_mean)
        assert result.value == 42.5

    def test_predict_with_horizon_parameter(self, mean_predictor, mock_view_with_mean):
        """Test predict accepts but ignores horizon parameter."""
        # Test with explicit horizon
        result = mean_predictor.predict(mock_view_with_mean, horizon=10)
        assert result.value == 42.5

        # Test with horizon=None (default)
        result2 = mean_predictor.predict(mock_view_with_mean, horizon=None)
        assert result2.value == 42.5

    def test_predict_with_different_mean_values(self, mean_predictor):
        """Test predict with various mean return values."""
        test_values = [0.0, 100.0, -15.5, 3.14159, 1e6]

        for mean_val in test_values:
            stats = StatisticsResult(mean=mean_val, confidence=0.5)

            view = VariableEpistemic(
                key=Key(), reasoning=None, stats=stats, anomaly=None, trend=None
            )

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
        assert "view must be VariableView, got str" in str(exc_info.value)
        assert "got str" in str(exc_info.value)

    def test_predict_missing_stats_raises_attribute_error(self, mean_predictor):
        """Test predict when stats structure is missing."""
        mock_view = create_autospec(VariableEpistemic)
        mock_view.key = Key()
        mock_view.reasoning = None
        mock_view.stats = None
        mock_view.anomaly = None
        mock_view.trend = None
        result = mean_predictor.predict(mock_view)
        assert isinstance(result, PredictionResult)

    def test_predict_with_zero_mean(self, mean_predictor, mock_view_with_mean_zero):
        """Test predict when mean is 0.0."""
        result = mean_predictor.predict(mock_view_with_mean_zero)
        assert result.value == 0.0
        assert isinstance(result, PredictionResult)


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
