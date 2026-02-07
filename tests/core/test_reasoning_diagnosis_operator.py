"""
Test suite for procela.core.reasoning.diagnosis.operator module.
100% coverage for the exact code at:
https://procela.org/python/core/reasoning/diagnosis/operator.html
"""

from unittest.mock import Mock, patch

import pytest

from procela.core.assessment import DiagnosisResult, TrendResult
from procela.core.memory import MemoryStatistics
from procela.core.reasoning import (
    DiagnosisOperator,
    DiagnosisOperatorThreshold,
    TrendOperator,
    TrendOperatorThreshold,
)
from procela.core.variable import VariableEpistemic


class TestTrendOperator:
    """Test cases for the TrendOperator abstract base class."""

    def test_abstract_class_cannot_be_instantiated(self):
        """Test that TrendOperator cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            TrendOperator()

        assert "abstract" in str(exc_info.value).lower()
        assert "analyze" in str(exc_info.value)

    def test_abstract_method_exists(self):
        """Test that analyze method is properly defined as abstract."""
        assert "analyze" in TrendOperator.__abstractmethods__

        import inspect

        method = inspect.signature(TrendOperator.analyze)
        assert len(method.parameters) == 2  # self + stats
        assert list(method.parameters.keys()) == ["self", "stats"]

        # Check the annotation
        annotations = TrendOperator.analyze.__annotations__
        assert annotations["stats"] == "StatisticsResult"
        assert annotations["return"] == "TrendResult | None"


class TestTrendOperatorThreshold:
    """Test cases for the TrendOperatorThreshold concrete class."""

    @pytest.fixture
    def mock_history_statistics(self):
        """Create a mock MemoryStatistics object with required attributes."""
        stats = MemoryStatistics(count=10, ewma=50.0)
        return stats

    @pytest.fixture
    def mock_history_statistics_mean(self, mock_history_statistics):
        """Add mean method to mock."""
        return mock_history_statistics

    def test_init_with_default_threshold(self):
        """Test initialization with default threshold."""
        operator = TrendOperatorThreshold()
        assert operator.threshold == 3.0

    def test_init_with_custom_threshold(self):
        """Test initialization with custom threshold."""
        operator = TrendOperatorThreshold(threshold=5.0)
        assert operator.threshold == 5.0

    def test_init_with_none_threshold(self):
        """Test initialization with None threshold."""
        operator = TrendOperatorThreshold(threshold=None)
        assert operator.threshold is None

    def test_analyze_with_none_threshold(self, mock_history_statistics_mean):
        """Test analyze when threshold is None."""
        operator = TrendOperatorThreshold(threshold=None)
        result = operator.analyze(mock_history_statistics_mean)
        assert result is None

    def test_analyze_with_none_stats(self):
        """Test analyze when stats is None."""
        operator = TrendOperatorThreshold()
        result = operator.analyze(None)
        assert result is None

    def test_analyze_with_wrong_stats_type(self):
        """Test analyze when stats is not a MemoryStatistics instance."""
        operator = TrendOperatorThreshold()

        with pytest.raises(TypeError) as exc_info:
            operator.analyze("not a MemoryStatistics")

        assert "MemoryStatistics" in str(exc_info.value)
        assert "got" in str(exc_info.value)

    def test_analyze_with_count_less_than_2(self):
        """Test analyze when stats.count < 2."""
        stats = MemoryStatistics(
            count=1,
            ewma=50.0,
        )

        operator = TrendOperatorThreshold()
        result = operator.analyze(stats.result())
        assert result is None

    def test_analyze_with_none_ewma(self):
        """Test analyze when stats.ewma is None."""
        stats = MemoryStatistics(
            count=10,
            ewma=None,
        )

        operator = TrendOperatorThreshold()
        result = operator.analyze(stats.result())
        assert result is None

    def test_analyze_with_none_mean(self, mock_history_statistics):
        """Test analyze when mean() returns None."""
        operator = TrendOperatorThreshold()
        result = operator.analyze(mock_history_statistics.result())
        assert result is None

    def test_analyze_stable_trend(self):
        """Test analyze when delta is within threshold (stable trend)."""
        stats = MemoryStatistics(
            count=10,
            sum=485.0,
            sumsq=23772.5,
            ewma=50.0,
        )

        operator = TrendOperatorThreshold(threshold=3.0)
        result = operator.analyze(stats.result())

        assert result is not None
        assert isinstance(result, TrendResult)
        assert result.value == 1.5  # 50.0 - 48.5
        assert result.direction == "stable"
        assert result.threshold == 3.0

    def test_analyze_upward_trend(self):
        """Test analyze when delta is positive and exceeds threshold (upward trend)."""
        stats = MemoryStatistics(
            count=10,
            sum=480.0,
            sumsq=23290.0,
            ewma=55.0,
        )

        operator = TrendOperatorThreshold(threshold=3.0)
        result = operator.analyze(stats.result())

        assert result is not None
        assert result.value == 7.0
        assert result.direction == "up"
        assert result.threshold == 3.0

    def test_analyze_downward_trend(self):
        """Test analyze when delta is negative and exceeds threshold."""
        stats = MemoryStatistics(
            count=10,
            sum=500.0,
            sumsq=25250.0,
            ewma=42.0,
        )

        operator = TrendOperatorThreshold(threshold=3.0)
        result = operator.analyze(stats.result())

        assert result is not None
        assert result.value == -8.0
        assert result.direction == "down"
        assert result.threshold == 3.0

    def test_analyze_exact_at_threshold(self):
        """Test analyze when delta equals exactly the threshold."""
        stats = MemoryStatistics(
            count=10,
            sum=500.0,
            sumsq=25250.0,
            ewma=53.0,
        )

        operator = TrendOperatorThreshold(threshold=3.0)
        result = operator.analyze(stats.result())

        # Should be up
        assert result is not None
        assert result.value == 3.0
        assert result.direction == "up"

    def test_analyze_negative_threshold_edge_case(self):
        """Test analyze with negative threshold (edge case)."""
        stats = MemoryStatistics(
            count=10,
            sum=480.0,
            sumsq=23290.0,
            ewma=50.0,
        )

        operator = TrendOperatorThreshold(threshold=-5.0)  # Negative threshold!
        with pytest.raises(ValueError):
            operator.analyze(stats.result())

    def test_analyze_zero_threshold(self):
        """Test analyze with zero threshold."""
        stats = MemoryStatistics(
            count=10,
            sum=500.0,
            sumsq=25250.0,
            ewma=50.1,
        )

        operator = TrendOperatorThreshold(threshold=0.0)
        with pytest.raises(ValueError, match="Threshold must be positive, got 0.0"):
            operator.analyze(stats.result())

    def test_analyze_with_realistic_values(self):
        """Test analyze with realistic statistical values."""
        stats = MemoryStatistics(
            count=100,
            sum=4520.0,
            sumsq=206804.0,
            ewma=42.75,
        )

        operator = TrendOperatorThreshold(threshold=2.5)
        result = operator.analyze(stats.result())

        assert result is not None
        assert abs(result.value - (-2.45)) < 0.001
        assert result.direction == "stable"

    def test_is_concrete_implementation(self):
        """Test that TrendOperatorThreshold is a concrete implementation."""
        operator = TrendOperatorThreshold()

        # Check inheritance
        assert isinstance(operator, TrendOperator)
        assert issubclass(TrendOperatorThreshold, TrendOperator)

        # Verify it has implemented all abstract methods
        assert (
            not hasattr(TrendOperatorThreshold, "__abstractmethods__")
            or len(TrendOperatorThreshold.__abstractmethods__) == 0
        )


class TestDiagnosisOperator:
    """Test cases for the DiagnosisOperator abstract base class."""

    def test_abstract_class_cannot_be_instantiated(self):
        """Test that DiagnosisOperator cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            DiagnosisOperator()

        assert "abstract" in str(exc_info.value).lower()
        assert "diagnose" in str(exc_info.value)

    def test_abstract_method_exists(self):
        """Test that diagnose method is properly defined as abstract."""
        assert "diagnose" in DiagnosisOperator.__abstractmethods__

        import inspect

        method = inspect.signature(DiagnosisOperator.diagnose)
        assert len(method.parameters) == 2  # self + view
        assert list(method.parameters.keys()) == ["self", "view"]

        # Check the annotation
        annotations = DiagnosisOperator.diagnose.__annotations__
        assert annotations["view"] == "VariableView"
        assert annotations["return"] == "DiagnosisResult"


class TestDiagnosisOperatorThreshold:
    """Test cases for the DiagnosisOperatorThreshold concrete class."""

    @pytest.fixture
    def mock_diagnoser(self):
        """Create a mock diagnoser."""
        diagnoser = Mock()
        diagnoser.diagnose.return_value = Mock(spec=DiagnosisResult)
        return diagnoser

    @pytest.fixture
    def mock_diagnosis_view(self):
        """Create a mock VariableEpistemic."""
        return Mock(spec=VariableEpistemic)

    @pytest.fixture
    def mock_diagnosis_result(self):
        """Create a mock DiagnosisResult."""
        return Mock(spec=DiagnosisResult)

    def test_init_with_name_and_kwargs(self, mock_diagnoser):
        """Test initialization with name and keyword arguments."""
        name = "threshold_diagnoser"
        kwargs = {"threshold": 0.95, "sensitivity": "high"}

        with patch(
            "procela.core.reasoning.diagnosis.operator.get_diagnoser",
            return_value=mock_diagnoser,
        ) as mock_get_diagnoser:
            operator = DiagnosisOperatorThreshold(name, **kwargs)

            # Verify get_diagnoser was called correctly
            mock_get_diagnoser.assert_called_once_with(name, **kwargs)

            # Verify diagnoser was assigned
            assert operator.diagnoser == mock_diagnoser

    def test_init_with_different_diagnoser_names(self):
        """Test initialization with various diagnoser names."""
        test_cases = [
            ("z_score_diagnoser", {"threshold": 3.0}),
            ("iqr_diagnoser", {"factor": 1.5}),
            ("percentile_diagnoser", {"lower": 5, "upper": 95}),
            ("simple_threshold", {"min_value": 0, "max_value": 100}),
        ]

        for name, kwargs in test_cases:
            with patch(
                "procela.core.reasoning.diagnosis.operator.get_diagnoser"
            ) as mock_get_diagnoser:
                mock_diagnoser = Mock()
                mock_get_diagnoser.return_value = mock_diagnoser

                operator = DiagnosisOperatorThreshold(name, **kwargs)

                mock_get_diagnoser.assert_called_once_with(name, **kwargs)
                assert operator.diagnoser == mock_diagnoser

    def test_diagnose_method(
        self, mock_diagnoser, mock_diagnosis_view, mock_diagnosis_result
    ):
        """Test the diagnose method delegates to the diagnoser."""
        mock_diagnoser.diagnose.return_value = mock_diagnosis_result

        with patch(
            "procela.core.reasoning.diagnosis.operator.get_diagnoser",
            return_value=mock_diagnoser,
        ):
            operator = DiagnosisOperatorThreshold("test_diagnoser")
            result = operator.diagnose(mock_diagnosis_view)

            mock_diagnoser.diagnose.assert_called_once_with(mock_diagnosis_view)
            assert result == mock_diagnosis_result

    def test_diagnose_with_concrete_view(self):
        """Test diagnose method with a more concrete view object."""
        mock_diagnoser = Mock()
        expected_result = Mock(spec=DiagnosisResult)
        mock_diagnoser.diagnose.return_value = expected_result

        # Create a realistic VariableEpistemic mock
        mock_view = Mock(spec=VariableEpistemic)
        mock_view.data = {
            "metric": "cpu_usage",
            "value": 85.5,
            "timestamp": "2024-01-15",
        }

        with patch(
            "procela.core.reasoning.diagnosis.operator.get_diagnoser",
            return_value=mock_diagnoser,
        ):
            operator = DiagnosisOperatorThreshold("statistical_diagnoser")
            result = operator.diagnose(mock_view)

            mock_diagnoser.diagnose.assert_called_once_with(mock_view)
            assert result == expected_result

    def test_diagnose_method_propagates_exceptions(
        self, mock_diagnoser, mock_diagnosis_view
    ):
        """Test that exceptions from diagnoser are propagated correctly."""
        test_exception = ValueError("Invalid view data")
        mock_diagnoser.diagnose.side_effect = test_exception

        with patch(
            "procela.core.reasoning.diagnosis.operator.get_diagnoser",
            return_value=mock_diagnoser,
        ):
            operator = DiagnosisOperatorThreshold("failing_diagnoser")

            with pytest.raises(ValueError) as exc_info:
                operator.diagnose(mock_diagnosis_view)

            assert str(exc_info.value) == "Invalid view data"
            mock_diagnoser.diagnose.assert_called_once_with(mock_diagnosis_view)

    def test_operator_is_concrete_implementation(self):
        """Test that DiagnosisOperatorThreshold is a concrete implementation."""
        with patch("procela.core.reasoning.diagnosis.operator.get_diagnoser"):
            operator = DiagnosisOperatorThreshold("test")

            # Check inheritance
            assert isinstance(operator, DiagnosisOperator)
            assert issubclass(DiagnosisOperatorThreshold, DiagnosisOperator)

            # Verify it has implemented all abstract methods
            assert (
                not hasattr(DiagnosisOperatorThreshold, "__abstractmethods__")
                or len(DiagnosisOperatorThreshold.__abstractmethods__) == 0
            )

    def test_type_annotations_preserved(self):
        """Test that type annotations are correctly defined."""
        import inspect

        # Check __init__ signature
        init_sig = inspect.signature(DiagnosisOperatorThreshold.__init__)
        init_params = list(init_sig.parameters.keys())

        assert init_params == ["self", "name", "kwargs"]
        assert init_sig.parameters["kwargs"].annotation == "Any"

        # Check diagnose signature
        diagnose_sig = inspect.signature(DiagnosisOperatorThreshold.diagnose)
        diagnose_params = list(diagnose_sig.parameters.keys())

        assert diagnose_params == ["self", "view"]
        assert diagnose_sig.parameters["view"].annotation == "VariableView"
        assert diagnose_sig.return_annotation == "DiagnosisResult"


class TestIntegration:
    """Integration tests for the operators."""

    def test_trend_operator_full_workflow(self):
        """Test complete trend analysis workflow."""
        # Create realistic statistics
        stats = MemoryStatistics(
            count=50,
            sum=6000.0,
            sumsq=721250.0,
            ewma=123.45,
        )

        # Test with threshold that makes it stable
        operator = TrendOperatorThreshold(threshold=5.0)
        result = operator.analyze(stats.result())

        assert result is not None
        assert abs(result.value - 3.45) < 1e-6
        assert result.direction == "stable"
        assert result.threshold == 5.0

        # Test with threshold that makes it upward trend
        operator2 = TrendOperatorThreshold(threshold=3.0)
        result2 = operator2.analyze(stats.result())

        assert result2 is not None
        assert abs(result2.value - 3.45) < 1e-6
        assert result2.direction == "up"  # 3.45 > 3.0
        assert result2.threshold == 3.0

    def test_diagnosis_operator_full_workflow(self):
        """Test complete diagnosis workflow."""
        # Create realistic mocks
        mock_view = Mock(spec=VariableEpistemic)
        mock_view.system_id = "server-001"
        mock_view.metrics = {"cpu": 85, "memory": 72, "disk": 45}

        mock_result = Mock(spec=DiagnosisResult)
        mock_result.is_healthy = False
        mock_result.score = 0.35
        mock_result.message = "High CPU usage detected"

        mock_diagnoser = Mock()
        mock_diagnoser.diagnose.return_value = mock_result

        with patch(
            "procela.core.reasoning.diagnosis.operator.get_diagnoser",
            return_value=mock_diagnoser,
        ):
            operator = DiagnosisOperatorThreshold(
                "threshold_diagnoser", warning_level=80, critical_level=90
            )

            result = operator.diagnose(mock_view)

            assert operator.diagnoser == mock_diagnoser
            mock_diagnoser.diagnose.assert_called_once_with(mock_view)
            assert result == mock_result
            assert result.is_healthy is False

    def test_multiple_operator_instances_independence(self):
        """Test that multiple operator instances work independently."""
        # Test TrendOperatorThreshold instances
        trend_op1 = TrendOperatorThreshold(threshold=2.0)
        trend_op2 = TrendOperatorThreshold(threshold=5.0)
        assert trend_op1.threshold == 2.0
        assert trend_op2.threshold == 5.0
        assert trend_op1.threshold != trend_op2.threshold

        # Test DiagnosisOperatorThreshold instances
        with patch(
            "procela.core.reasoning.diagnosis.operator.get_diagnoser"
        ) as mock_get_diagnoser:
            mock_diagnoser1 = Mock()
            mock_diagnoser2 = Mock()

            def get_diagnoser_side_effect(name, **kwargs):
                if name == "diagnoser1":
                    return mock_diagnoser1
                elif name == "diagnoser2":
                    return mock_diagnoser2
                return Mock()

            mock_get_diagnoser.side_effect = get_diagnoser_side_effect

            diag_op1 = DiagnosisOperatorThreshold("diagnoser1", param1="value1")
            diag_op2 = DiagnosisOperatorThreshold("diagnoser2", param2="value2")

            assert diag_op1.diagnoser == mock_diagnoser1
            assert diag_op2.diagnoser == mock_diagnoser2
            assert diag_op1.diagnoser != diag_op2.diagnoser


def test_coverage_edge_cases():
    """Additional tests to ensure 100% coverage of all edge cases."""

    # Test TrendOperatorThreshold with all None conditions
    operator = TrendOperatorThreshold(threshold=3.0)

    # Test with stats that has all required attributes but mean returns None
    stats = MemoryStatistics(count=10, sum=None, ewma=50.0)
    assert operator.analyze(stats.result()) is None

    # Test with stats that has ewma as 0.0
    stats2 = Mock(spec=MemoryStatistics)
    stats2 = MemoryStatistics(count=10, sum=0.0, ewma=0.0)
    result = operator.analyze(stats2.result())
    assert result is not None
    assert result.value == 0.0
    assert result.direction == "stable"

    # Test DiagnosisOperatorThreshold with empty kwargs
    with patch(
        "procela.core.reasoning.diagnosis.operator.get_diagnoser"
    ) as mock_get_diagnoser:
        mock_diagnoser = Mock()
        mock_get_diagnoser.return_value = mock_diagnoser

        operator = DiagnosisOperatorThreshold("empty_kwargs")  # No kwargs
        assert operator.diagnoser == mock_diagnoser
        mock_get_diagnoser.assert_called_once_with("empty_kwargs")

    # Test passing None as view (should be passed to diagnoser)
    with patch(
        "procela.core.reasoning.diagnosis.operator.get_diagnoser"
    ) as mock_get_diagnoser:
        mock_diagnoser = Mock()
        mock_get_diagnoser.return_value = mock_diagnoser

        operator = DiagnosisOperatorThreshold("test")
        operator.diagnose(None)
        mock_diagnoser.diagnose.assert_called_once_with(None)


def test_type_error_message_format():
    """Test the specific format of TypeError message."""
    operator = TrendOperatorThreshold()

    with pytest.raises(TypeError) as exc_info:
        operator.analyze({"not": "stats"})

    error_msg = str(exc_info.value)
    assert "stats should be a StatisticsResult instance" in error_msg
    assert "got" in error_msg
    assert "dict" in error_msg or "{'not': 'stats'}" in error_msg

    # Test with integer
    with pytest.raises(TypeError) as exc_info:
        operator.analyze(42)

    error_msg = str(exc_info.value)
    assert "stats should be a StatisticsResult instance" in error_msg
    assert "got" in error_msg
    assert "42" in error_msg or "int" in error_msg
