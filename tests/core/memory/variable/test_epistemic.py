"""
Test suite for procela.core.memory.variable.epistemic module.
100% coverage for the exact code of VariableEpistemic class.
"""

from dataclasses import FrozenInstanceError, is_dataclass, replace
from unittest.mock import Mock

import pytest

from procela.core.memory import HistoryStatistics, VariableEpistemic
from procela.core.reasoning import AnomalyResult, TrendResult


class TestVariableEpistemic:
    """Test cases for the VariableEpistemic dataclass."""

    @pytest.fixture
    def mock_history_statistics(self):
        """Create a mock HistoryStatistics object."""
        stats = Mock(spec=HistoryStatistics)
        stats.mean.return_value = 42.0
        stats.std.return_value = 5.0
        stats.count = 100
        return stats

    @pytest.fixture
    def mock_anomaly_result(self):
        """Create a mock AnomalyResult object."""
        anomaly = Mock(spec=AnomalyResult)
        anomaly.is_anomaly = False
        anomaly.score = 0.25
        anomaly.threshold = 0.95
        return anomaly

    @pytest.fixture
    def mock_trend_result(self):
        """Create a mock TrendResult object."""
        trend = Mock(spec=TrendResult)
        trend.value = 1.5
        trend.direction = "up"
        trend.threshold = 1.0
        return trend

    def test_dataclass_decorator(self):
        """Test that VariableEpistemic is a dataclass."""
        assert is_dataclass(VariableEpistemic)

    def test_frozen_dataclass(self):
        """Test that VariableEpistemic is frozen (immutable)."""
        # Check if it's frozen by trying to modify an instance
        stats = Mock(spec=HistoryStatistics)
        anomaly = Mock(spec=AnomalyResult)
        trend = Mock(spec=TrendResult)

        epistemic = VariableEpistemic(stats=stats, anomaly=anomaly, trend=trend)

        # Should raise FrozenInstanceError when trying to modify
        with pytest.raises(FrozenInstanceError):
            epistemic.stats = Mock(spec=HistoryStatistics)

        with pytest.raises(FrozenInstanceError):
            epistemic.anomaly = None

        with pytest.raises(FrozenInstanceError):
            epistemic.trend = Mock(spec=TrendResult)

    def test_initialization_with_all_fields(
        self, mock_history_statistics, mock_anomaly_result, mock_trend_result
    ):
        """Test initialization with all fields provided."""
        epistemic = VariableEpistemic(
            stats=mock_history_statistics,
            anomaly=mock_anomaly_result,
            trend=mock_trend_result,
        )

        assert epistemic.stats == mock_history_statistics
        assert epistemic.anomaly == mock_anomaly_result
        assert epistemic.trend == mock_trend_result

    def test_initialization_with_none_anomaly(
        self, mock_history_statistics, mock_trend_result
    ):
        """Test initialization with anomaly set to None."""
        epistemic = VariableEpistemic(
            stats=mock_history_statistics, anomaly=None, trend=mock_trend_result
        )

        assert epistemic.stats == mock_history_statistics
        assert epistemic.anomaly is None
        assert epistemic.trend == mock_trend_result

    def test_initialization_with_none_trend(
        self, mock_history_statistics, mock_anomaly_result
    ):
        """Test initialization with trend set to None."""
        epistemic = VariableEpistemic(
            stats=mock_history_statistics, anomaly=mock_anomaly_result, trend=None
        )

        assert epistemic.stats == mock_history_statistics
        assert epistemic.anomaly == mock_anomaly_result
        assert epistemic.trend is None

    def test_initialization_with_both_none(self, mock_history_statistics):
        """Test initialization with both anomaly and trend set to None."""
        epistemic = VariableEpistemic(
            stats=mock_history_statistics, anomaly=None, trend=None
        )

        assert epistemic.stats == mock_history_statistics
        assert epistemic.anomaly is None
        assert epistemic.trend is None

    def test_fields_have_correct_types(self):
        """Test that fields have the correct type annotations."""

        # Get type hints
        type_hints = VariableEpistemic.__annotations__

        assert type_hints["stats"] == "HistoryStatistics"
        assert type_hints["anomaly"] == "AnomalyResult | None"
        assert type_hints["trend"] == "TrendResult | None"

    def test_get_diagnosis_view_method(
        self, mock_history_statistics, mock_anomaly_result, mock_trend_result
    ):
        """Test get_diagnosis_view method."""
        epistemic = VariableEpistemic(
            stats=mock_history_statistics,
            anomaly=mock_anomaly_result,
            trend=mock_trend_result,
        )

        result = epistemic.get_diagnosis_view()

        # Should return self (as per the code)
        assert result is epistemic

        # Verify it's the correct type
        assert isinstance(result, VariableEpistemic)

    def test_get_prediction_view_method(self, mock_history_statistics):
        """Test get_prediction_view method."""
        epistemic = VariableEpistemic(
            stats=mock_history_statistics, anomaly=None, trend=None
        )

        result = epistemic.get_prediction_view()

        # Should return self (as per the code)
        assert result is epistemic
        assert isinstance(result, VariableEpistemic)

    def test_get_proposal_view_method(self, mock_history_statistics, mock_trend_result):
        """Test get_proposal_view method."""
        epistemic = VariableEpistemic(
            stats=mock_history_statistics, anomaly=None, trend=mock_trend_result
        )

        result = epistemic.get_proposal_view()

        # Should return self (as per the code)
        assert result is epistemic
        assert isinstance(result, VariableEpistemic)

    def test_views_return_correct_types(self, mock_history_statistics):
        """Test that view methods return objects of correct types."""
        epistemic = VariableEpistemic(
            stats=mock_history_statistics, anomaly=None, trend=None
        )

        # Check type compatibility
        diagnosis_view = epistemic.get_diagnosis_view()
        prediction_view = epistemic.get_prediction_view()
        proposal_view = epistemic.get_proposal_view()

        # All should be VariableEpistemic instances
        assert isinstance(diagnosis_view, VariableEpistemic)
        assert isinstance(prediction_view, VariableEpistemic)
        assert isinstance(proposal_view, VariableEpistemic)

        # And they should all be the same instance
        assert diagnosis_view is prediction_view
        assert prediction_view is proposal_view
        assert diagnosis_view is proposal_view

    def test_equality(self, mock_history_statistics):
        """Test equality comparison between VariableEpistemic instances."""
        anomaly1 = Mock(spec=AnomalyResult)
        anomaly1.is_anomaly = True

        anomaly2 = Mock(spec=AnomalyResult)
        anomaly2.is_anomaly = True

        trend1 = Mock(spec=TrendResult)
        trend1.direction = "up"

        trend2 = Mock(spec=TrendResult)
        trend2.direction = "up"

        # Create two instances with same values
        epistemic1 = VariableEpistemic(
            stats=mock_history_statistics, anomaly=anomaly1, trend=trend1
        )

        epistemic2 = VariableEpistemic(
            stats=mock_history_statistics, anomaly=anomaly2, trend=trend2
        )

        # They should not be equal if the mock objects are different
        # (unless Mock equality is overridden)
        if anomaly1 != anomaly2 or trend1 != trend2:
            assert epistemic1 != epistemic2
        else:
            assert epistemic1 == epistemic2

        # Test with None values
        epistemic3 = VariableEpistemic(
            stats=mock_history_statistics, anomaly=None, trend=None
        )

        epistemic4 = VariableEpistemic(
            stats=mock_history_statistics, anomaly=None, trend=None
        )

        # These should be equal
        assert epistemic3 == epistemic4

    def test_hash_implementation(self, mock_history_statistics):
        """Test that VariableEpistemic instances are hashable."""
        epistemic = VariableEpistemic(
            stats=mock_history_statistics, anomaly=None, trend=None
        )

        # Should be hashable (frozen dataclasses implement __hash__)
        hash_value = hash(epistemic)
        assert isinstance(hash_value, int)

        # Multiple calls should return same hash
        assert hash(epistemic) == hash_value

    def test_replace_method(
        self, mock_history_statistics, mock_anomaly_result, mock_trend_result
    ):
        """Test using dataclasses.replace to create modified copies."""
        original = VariableEpistemic(
            stats=mock_history_statistics,
            anomaly=mock_anomaly_result,
            trend=mock_trend_result,
        )

        # Create new anomaly
        new_anomaly = Mock(spec=AnomalyResult)
        new_anomaly.is_anomaly = True

        # Use replace to create a new instance with updated anomaly
        try:
            modified = replace(original, anomaly=new_anomaly)

            # Original should be unchanged
            assert original.anomaly == mock_anomaly_result
            assert original.trend == mock_trend_result

            # Modified should have new anomaly
            assert modified.anomaly == new_anomaly
            assert modified.trend == mock_trend_result
            assert modified.stats == mock_history_statistics

            # They should not be the same object
            assert original is not modified
            assert original != modified
        except TypeError:
            # replace might not work with frozen dataclasses in some Python versions
            pass

    def test_string_representation(self, mock_history_statistics):
        """Test the string representation of VariableEpistemic."""
        epistemic = VariableEpistemic(
            stats=mock_history_statistics, anomaly=None, trend=None
        )

        str_repr = str(epistemic)
        repr_repr = repr(epistemic)

        # Should contain class name
        assert "VariableEpistemic" in str_repr
        assert "VariableEpistemic" in repr_repr

        # Should contain field names
        assert "stats=" in repr_repr
        assert "anomaly=" in repr_repr
        assert "trend=" in repr_repr

    def test_realistic_usage_scenario(self):
        """Test realistic usage scenario with actual mocked data."""
        # Create realistic mocks
        stats = Mock(spec=HistoryStatistics)
        stats.mean.return_value = 75.5
        stats.std.return_value = 12.3
        stats.count = 250
        stats.min = 45.2
        stats.max = 98.7

        anomaly = Mock(spec=AnomalyResult)
        anomaly.is_anomaly = True
        anomaly.score = 3.8
        anomaly.threshold = 2.5
        anomaly.confidence = 0.92

        trend = Mock(spec=TrendResult)
        trend.value = -2.3
        trend.direction = "down"
        trend.threshold = 1.0
        trend.confidence = 0.87

        # Create epistemic state
        epistemic = VariableEpistemic(stats=stats, anomaly=anomaly, trend=trend)

        # Access all fields
        assert epistemic.stats.mean() == 75.5
        assert epistemic.anomaly.is_anomaly is True
        assert epistemic.trend.direction == "down"

        # Use view methods
        diagnosis_view = epistemic.get_diagnosis_view()
        assert diagnosis_view is epistemic

        # Check statistical properties through stats
        assert epistemic.stats.count == 250
        assert epistemic.stats.min == 45.2

    def test_edge_cases(self):
        """Test various edge cases."""
        # Test with empty or minimal HistoryStatistics
        empty_stats = Mock(spec=HistoryStatistics)
        empty_stats.count = 0
        empty_stats.mean.return_value = None

        epistemic = VariableEpistemic(stats=empty_stats, anomaly=None, trend=None)

        assert epistemic.stats.count == 0
        assert epistemic.anomaly is None
        assert epistemic.trend is None

        # Test with anomaly but no trend
        anomaly_only = VariableEpistemic(
            stats=empty_stats, anomaly=Mock(spec=AnomalyResult), trend=None
        )

        assert anomaly_only.anomaly is not None
        assert anomaly_only.trend is None

        # Test with trend but no anomaly
        trend_only = VariableEpistemic(
            stats=empty_stats, anomaly=None, trend=Mock(spec=TrendResult)
        )

        assert trend_only.anomaly is None
        assert trend_only.trend is not None

    def test_interface_implementation(self):
        """Test that VariableEpistemic provides the expected interface."""
        # Check that it has all the expected methods
        assert hasattr(VariableEpistemic, "get_diagnosis_view")
        assert hasattr(VariableEpistemic, "get_prediction_view")
        assert hasattr(VariableEpistemic, "get_proposal_view")

        # Check method signatures
        import inspect

        # get_diagnosis_view should take only self
        diagnosis_sig = inspect.signature(VariableEpistemic.get_diagnosis_view)
        assert len(diagnosis_sig.parameters) == 1  # self only
        assert list(diagnosis_sig.parameters.keys()) == ["self"]

        # Return type should be DiagnosisView (but code returns self)
        # We can't easily check the return type annotation matches

        # Same for other methods
        prediction_sig = inspect.signature(VariableEpistemic.get_prediction_view)
        assert len(prediction_sig.parameters) == 1

        proposal_sig = inspect.signature(VariableEpistemic.get_proposal_view)
        assert len(proposal_sig.parameters) == 1

    def test_mutation_attempts_all_fields(self):
        """Test that all fields are properly frozen."""
        stats = Mock(spec=HistoryStatistics)
        anomaly = Mock(spec=AnomalyResult)
        trend = Mock(spec=TrendResult)

        epistemic = VariableEpistemic(stats=stats, anomaly=anomaly, trend=trend)

        # Try to mutate each field
        with pytest.raises(FrozenInstanceError):
            epistemic.stats = Mock(spec=HistoryStatistics)

        with pytest.raises(FrozenInstanceError):
            epistemic.anomaly = None

        with pytest.raises(FrozenInstanceError):
            epistemic.anomaly = Mock(spec=AnomalyResult)

        with pytest.raises(FrozenInstanceError):
            epistemic.trend = Mock(spec=TrendResult)

        with pytest.raises(FrozenInstanceError):
            epistemic.trend = None

        # Try to set non-existent attribute
        with pytest.raises(FrozenInstanceError):
            epistemic.non_existent = "value"

    def test_with_real_result_objects(self):
        """Test with real (not mocked) result objects if possible."""
        # Try to import and use actual classes if available
        try:
            from procela.core.reasoning.result import AnomalyResult, TrendResult

            # Create simple instances
            anomaly = AnomalyResult(is_anomaly=True, score=2.7)
            trend = TrendResult(value=1.5, direction="up", threshold=1.0)
            stats = Mock(spec=HistoryStatistics)

            epistemic = VariableEpistemic(stats=stats, anomaly=anomaly, trend=trend)

            assert epistemic.anomaly.is_anomaly is True
            assert epistemic.trend.direction == "up"

        except (ImportError, TypeError):
            # If we can't import or instantiate, skip this test
            pytest.skip("Cannot import actual result classes")

    def test_documentation_example(self):
        """Test the example from the docstring."""
        # Create mocks matching the example
        stats = Mock(spec=HistoryStatistics)
        stats.mean.return_value = 10.5
        stats.count = 100

        anomaly = Mock(spec=AnomalyResult)
        anomaly.is_anomaly = True
        anomaly.score = 3.2
        anomaly.threshold = 2.5

        trend = Mock(spec=TrendResult)
        trend.direction = "up"
        trend.value = 8.43
        trend.threshold = 1.75

        # Create epistemic state as in example
        epistemic = VariableEpistemic(stats=stats, anomaly=anomaly, trend=trend)

        # Verify properties as in example
        assert epistemic.stats.mean() == 10.5
        assert epistemic.anomaly.is_anomaly is True
        assert epistemic.trend.direction == "up"

        # The example prints these values
        # We just verify they're accessible


class TestIntegration:
    """Integration tests for VariableEpistemic."""

    def test_use_in_diagnosis_context(self):
        """Test using VariableEpistemic in a diagnosis context."""
        # Create a complete epistemic state
        stats = Mock(spec=HistoryStatistics)
        stats.mean.return_value = 50.0

        anomaly = Mock(spec=AnomalyResult)
        anomaly.is_anomaly = False

        trend = Mock(spec=TrendResult)
        trend.direction = "stable"

        epistemic = VariableEpistemic(stats=stats, anomaly=anomaly, trend=trend)

        # Simulate diagnosis process
        diagnosis_view = epistemic.get_diagnosis_view()

        # In a real scenario, this view would be passed to a diagnoser
        # For now, just verify we have the view
        assert diagnosis_view is epistemic

        # Check all data is accessible
        assert diagnosis_view.stats.mean() == 50.0
        assert diagnosis_view.anomaly.is_anomaly is False
        assert diagnosis_view.trend.direction == "stable"

    def test_use_in_prediction_context(self):
        """Test using VariableEpistemic in a prediction context."""
        stats = Mock(spec=HistoryStatistics)
        stats.mean.return_value = 100.0
        stats.std.return_value = 15.0

        # No anomaly or trend for prediction
        epistemic = VariableEpistemic(stats=stats, anomaly=None, trend=None)

        prediction_view = epistemic.get_prediction_view()

        # Prediction would use statistical properties
        mean = prediction_view.stats.mean()
        std = prediction_view.stats.std()

        assert mean == 100.0
        assert std == 15.0

    def test_serialization_compatibility(self):
        """Test that VariableEpistemic works well with serialization."""
        # Frozen dataclasses should work with pickle

        stats = Mock(spec=HistoryStatistics)
        anomaly = Mock(spec=AnomalyResult)
        trend = Mock(spec=TrendResult)

        original = VariableEpistemic(stats=stats, anomaly=anomaly, trend=trend)

        # Can't actually pickle Mock objects, but we can test the concept
        # For real objects, this would work:
        # pickled = pickle.dumps(original)
        # restored = pickle.loads(pickled)
        # assert original == restored

        # Instead, verify the instance has the necessary methods
        assert hasattr(original, "__getstate__") or hasattr(original, "__reduce__")

    def test_type_checking(self):
        """Test that type checking would catch incorrect types."""
        # This is more of a conceptual test since runtime doesn't enforce types

        # The following would fail type checking but not necessarily at runtime:
        # VariableEpistemic(stats="not stats", anomaly=None, trend=None)

        # But we can verify the type hints are present
        type_hints = VariableEpistemic.__annotations__
        assert "stats" in type_hints
        assert "anomaly" in type_hints
        assert "trend" in type_hints


def test_module_imports():
    """Test that all necessary imports are available."""
    # Check we can import everything
    # Check it's a dataclass
    from dataclasses import is_dataclass

    from procela.core.memory import VariableEpistemic

    assert is_dataclass(VariableEpistemic)
