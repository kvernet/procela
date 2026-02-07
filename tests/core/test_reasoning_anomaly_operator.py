"""
Test suite for procela.core.reasoning.anomaly.operator module.
This test suite achieves 100% coverage of the operator.py file.
"""

from unittest.mock import Mock, patch

import pytest

from procela.core.assessment import AnomalyResult
from procela.core.memory import MemoryStatistics
from procela.core.reasoning import (
    AnomalyOperator,
    AnomalyOperatorThreshold,
)


class TestAnomalyOperator:
    """Test cases for the abstract base class AnomalyOperator."""

    def test_abstract_class_cannot_be_instantiated(self):
        """Test that AnomalyOperator cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            # Attempt to instantiate abstract class should fail
            AnomalyOperator()

        # Verify the error message indicates abstract method
        assert "abstract" in str(exc_info.value).lower()
        assert "detect" in str(exc_info.value)

    def test_abstract_method_exists(self):
        """Test that detect method is properly defined as abstract."""
        # Check that detect is an abstract method
        assert "detect" in AnomalyOperator.__abstractmethods__

        # Verify the method signature in the class
        import inspect

        method = inspect.signature(AnomalyOperator.detect)
        assert len(method.parameters) == 2  # self + stats
        assert list(method.parameters.keys()) == ["self", "stats"]

        # Check the annotation
        annotations = AnomalyOperator.detect.__annotations__
        assert annotations["stats"] == "StatisticsResult"
        assert annotations["return"] == "AnomalyResult"


class TestAnomalyOperatorThreshold:
    """Test cases for the concrete class AnomalyOperatorThreshold."""

    @pytest.fixture
    def mock_detector(self):
        """Create a mock detector for testing."""
        detector = Mock()
        detector.detect.return_value = Mock(spec=AnomalyResult)
        return detector

    @pytest.fixture
    def mock_history_statistics(self):
        """Create a mock MemoryStatistics object."""
        return Mock(spec=MemoryStatistics)

    @pytest.fixture
    def mock_anomaly_result(self):
        """Create a mock AnomalyResult object."""
        return Mock(spec=AnomalyResult)

    def test_init_with_detector_name(self, mock_detector):
        """Test initialization with a detector name and parameters."""
        detector_name = "threshold_detector"
        kwargs = {"threshold": 0.95, "sensitivity": "high"}

        with patch(
            "procela.core.reasoning.anomaly.operator.get_detector",
            return_value=mock_detector,
        ) as mock_get_detector:
            # Create instance
            operator = AnomalyOperatorThreshold(detector_name, **kwargs)

            # Verify get_detector was called correctly
            mock_get_detector.assert_called_once_with(detector_name, **kwargs)

            # Verify detector was assigned
            assert operator.detector == mock_detector

    def test_init_with_different_detector_names(self):
        """Test initialization with various detector names."""
        test_cases = [
            ("z_score", {"threshold": 3.0}),
            ("iqr", {"factor": 1.5}),
            ("percentile", {"lower": 5, "upper": 95}),
            ("simple_threshold", {"min_value": 0, "max_value": 100}),
        ]

        for detector_name, kwargs in test_cases:
            with patch(
                "procela.core.reasoning.anomaly.operator.get_detector"
            ) as mock_get_detector:
                mock_detector = Mock()
                mock_get_detector.return_value = mock_detector

                # Create instance
                operator = AnomalyOperatorThreshold(detector_name, **kwargs)

                # Verify the call
                mock_get_detector.assert_called_once_with(detector_name, **kwargs)
                assert operator.detector == mock_detector

    def test_detect_method(
        self, mock_detector, mock_history_statistics, mock_anomaly_result
    ):
        """Test the detect method delegates to the detector."""
        # Setup mock return value
        mock_detector.detect.return_value = mock_anomaly_result

        with patch(
            "procela.core.reasoning.anomaly.operator.get_detector",
            return_value=mock_detector,
        ):
            # Create operator
            operator = AnomalyOperatorThreshold("test_detector")

            # Call detect
            result = operator.detect(mock_history_statistics)

            # Verify detector.detect was called with correct argument
            mock_detector.detect.assert_called_once_with(mock_history_statistics)

            # Verify the result
            assert result == mock_anomaly_result

    def test_detect_method_with_concrete_statistics(self):
        """Test detect method with a more concrete statistics object."""
        # Create a more realistic mock
        mock_detector = Mock()
        expected_result = Mock(spec=AnomalyResult)
        mock_detector.detect.return_value = expected_result

        # Create a realistic MemoryStatistics mock
        mock_stats = Mock(spec=MemoryStatistics)
        mock_stats.mean = 100.0
        mock_stats.std = 15.0
        mock_stats.count = 50

        with patch(
            "procela.core.reasoning.anomaly.operator.get_detector",
            return_value=mock_detector,
        ):
            operator = AnomalyOperatorThreshold("statistical_detector")
            result = operator.detect(mock_stats)

            # Verify the call
            mock_detector.detect.assert_called_once_with(mock_stats)
            assert result == expected_result

    def test_detect_method_propagates_exceptions(
        self, mock_detector, mock_history_statistics
    ):
        """Test that exceptions from detector are propagated correctly."""
        # Setup detector to raise an exception
        test_exception = ValueError("Invalid statistics data")
        mock_detector.detect.side_effect = test_exception

        with patch(
            "procela.core.reasoning.anomaly.operator.get_detector",
            return_value=mock_detector,
        ):
            operator = AnomalyOperatorThreshold("failing_detector")

            # Verify the exception is propagated
            with pytest.raises(ValueError) as exc_info:
                operator.detect(mock_history_statistics)

            assert str(exc_info.value) == "Invalid statistics data"
            mock_detector.detect.assert_called_once_with(mock_history_statistics)

    def test_operator_is_concrete_implementation(self):
        """Test that AnomalyOperatorThreshold is a concrete implementation."""
        # Verify it can be instantiated without abstract methods
        with patch("procela.core.reasoning.anomaly.operator.get_detector"):
            operator = AnomalyOperatorThreshold("test")

            # Check inheritance
            assert isinstance(operator, AnomalyOperator)
            assert issubclass(AnomalyOperatorThreshold, AnomalyOperator)

            # Verify it has implemented all abstract methods
            assert (
                not hasattr(AnomalyOperatorThreshold, "__abstractmethods__")
                or len(AnomalyOperatorThreshold.__abstractmethods__) == 0
            )

    def test_type_annotations_preserved(self):
        """Test that type annotations are correctly defined."""
        import inspect

        # Check __init__ signature
        init_sig = inspect.signature(AnomalyOperatorThreshold.__init__)
        init_params = list(init_sig.parameters.keys())

        assert init_params == ["self", "name", "kwargs"]
        assert init_sig.parameters["name"].annotation == "str"
        assert init_sig.parameters["kwargs"].annotation == "Any"

        # Check detect signature
        detect_sig = inspect.signature(AnomalyOperatorThreshold.detect)
        detect_params = list(detect_sig.parameters.keys())

        assert detect_params == ["self", "stats"]
        assert detect_sig.parameters["stats"].annotation == "StatisticsResult"
        assert detect_sig.return_annotation == "AnomalyResult"


class TestIntegration:
    """Integration tests for the anomaly operator."""

    def test_full_workflow_integration(self):
        """Test a complete workflow from initialization to detection."""
        # Create realistic mocks
        mock_stats = Mock(spec=MemoryStatistics)
        mock_stats.mean = 42.0
        mock_stats.values = [40, 41, 42, 43, 44]

        mock_result = Mock(spec=AnomalyResult)
        mock_result.is_anomaly = True
        mock_result.score = 0.98
        mock_result.message = "Value exceeds threshold"

        mock_detector = Mock()
        mock_detector.detect.return_value = mock_result

        with patch(
            "procela.core.reasoning.anomaly.operator.get_detector",
            return_value=mock_detector,
        ):
            # Initialize operator
            operator = AnomalyOperatorThreshold(
                "threshold_detector", threshold=0.95, window_size=10
            )

            # Perform detection
            result = operator.detect(mock_stats)

            # Verify full workflow
            assert operator.detector == mock_detector
            mock_detector.detect.assert_called_once_with(mock_stats)
            assert result == mock_result
            assert result.is_anomaly is True
            assert result.score == 0.98

    def test_multiple_operator_instances(self):
        """Test that multiple operator instances work independently."""
        with patch(
            "procela.core.reasoning.anomaly.operator.get_detector"
        ) as mock_get_detector:
            # Create two different mock detectors
            mock_detector1 = Mock()
            mock_detector2 = Mock()

            # Configure get_detector to return different detectors
            def get_detector_side_effect(name, **kwargs):
                if name == "detector1":
                    return mock_detector1
                elif name == "detector2":
                    return mock_detector2
                return Mock()

            mock_get_detector.side_effect = get_detector_side_effect

            # Create two operators with different configurations
            operator1 = AnomalyOperatorThreshold("detector1", threshold=0.9)
            operator2 = AnomalyOperatorThreshold("detector2", threshold=0.99)

            # Verify they have different detectors
            assert operator1.detector == mock_detector1
            assert operator2.detector == mock_detector2
            assert operator1.detector != operator2.detector

            # Test they work independently
            mock_stats = Mock(spec=MemoryStatistics)

            result1 = Mock()
            result2 = Mock()
            mock_detector1.detect.return_value = result1
            mock_detector2.detect.return_value = result2

            assert operator1.detect(mock_stats) == result1
            assert operator2.detect(mock_stats) == result2


def test_coverage_completeness():
    """Additional tests to ensure 100% coverage of all code paths."""

    # Test that the __init__ method properly stores the detector
    with patch(
        "procela.core.reasoning.anomaly.operator.get_detector"
    ) as mock_get_detector:
        mock_detector = Mock()
        mock_get_detector.return_value = mock_detector

        operator = AnomalyOperatorThreshold(
            "test_detector", param1="value1", param2=123
        )

        # Verify constructor arguments passed correctly
        mock_get_detector.assert_called_once_with(
            "test_detector", param1="value1", param2=123
        )
        assert hasattr(operator, "detector")
        assert operator.detector == mock_detector

    # Test detect method with None statistics (edge case)
    with patch(
        "procela.core.reasoning.anomaly.operator.get_detector"
    ) as mock_get_detector:
        mock_detector = Mock()
        mock_get_detector.return_value = mock_detector

        operator = AnomalyOperatorThreshold("test_detector")

        # This would likely cause an exception in the detector, but we're testing
        # that the operator properly delegates the call
        mock_detector.detect.side_effect = TypeError("Expected MemoryStatistics")

        with pytest.raises(TypeError) as exc_info:
            operator.detect(None)  # Passing None should cause detector to fail

        assert "Expected MemoryStatistics" in str(exc_info.value)
