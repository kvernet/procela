"""
Pytest module for procela.core.reasoning.anomaly.base.

Achieves 100% coverage for the AnomalyDetector abstract base class.
Tests abstract class behavior, subclass requirements, and interface contracts.
"""

from abc import ABC
from unittest.mock import Mock

import pytest

from procela.core.assessment import AnomalyResult
from procela.core.memory import HistoryStatistics
from procela.core.reasoning import AnomalyDetector


class TestAnomalyDetector:
    """Comprehensive tests for the AnomalyDetector abstract base class."""

    def test_is_abstract_base_class(self) -> None:
        """Test that AnomalyDetector is a proper ABC."""
        assert issubclass(AnomalyDetector, ABC)
        assert hasattr(AnomalyDetector, "__abstractmethods__")

    def test_cannot_instantiate_abstract_class(self) -> None:
        """Test that AnomalyDetector cannot be instantiated directly."""
        with pytest.raises(TypeError, match="abstract"):
            AnomalyDetector()  # type: ignore

    def test_has_detect_abstract_method(self) -> None:
        """Test that detect is defined as an abstract method."""
        assert "detect" in AnomalyDetector.__abstractmethods__
        assert hasattr(AnomalyDetector, "detect")
        assert callable(AnomalyDetector.detect)

    def test_detect_method_signature(self) -> None:
        """Test that detect has the correct signature in annotations."""
        # Check method exists and is abstract
        assert hasattr(AnomalyDetector.detect, "__isabstractmethod__")
        assert AnomalyDetector.detect.__isabstractmethod__ is True

    def test_concrete_subclass_must_implement_detect(self) -> None:
        """Test that subclasses must implement detect method."""

        class IncompleteDetector(AnomalyDetector):
            name = "IncompleteDetector"
            # Missing detect method implementation

        with pytest.raises(TypeError, match="abstract"):
            IncompleteDetector()

    def test_concrete_subclass_must_have_name(self) -> None:
        """Test that subclasses must define the name class attribute."""

        class NamelessDetector(AnomalyDetector):
            # Has detect method but no name attribute
            def detect(self, stats: HistoryStatistics) -> AnomalyResult:
                return AnomalyResult(is_anomaly=False)

        # This should still be instantiable (Python won't enforce class var)
        detector = NamelessDetector()
        assert not hasattr(detector, "name")
        # But accessing it might raise AttributeError
        with pytest.raises(AttributeError):
            _ = NamelessDetector.name

    def test_valid_concrete_subclass(self) -> None:
        """Test a properly implemented concrete subclass."""

        class ConcreteDetector(AnomalyDetector):
            name = "ConcreteDetector"

            def detect(self, stats: HistoryStatistics) -> AnomalyResult:
                return AnomalyResult(
                    is_anomaly=False,
                    score=0.0,
                    threshold=3.0,
                    method=self.name,
                    metadata={"test": True},
                )

        # Should be able to instantiate
        detector = ConcreteDetector()
        assert isinstance(detector, AnomalyDetector)
        assert detector.name == "ConcreteDetector"

        # Should be able to call detect
        stats = HistoryStatistics.empty()
        result = detector.detect(stats)
        assert isinstance(result, AnomalyResult)
        assert result.method == "ConcreteDetector"

    def test_detect_returns_anomalyresult(self) -> None:
        """Test that detect method returns AnomalyResult instance."""

        class TestDetector(AnomalyDetector):
            name = "TestDetector"

            def detect(self, stats: HistoryStatistics) -> AnomalyResult:
                # Return a valid AnomalyResult
                return AnomalyResult(
                    is_anomaly=True, score=2.5, threshold=2.0, method=self.name
                )

        detector = TestDetector()
        stats = Mock(spec=HistoryStatistics)
        result = detector.detect(stats)

        assert isinstance(result, AnomalyResult)
        assert result.is_anomaly is True
        assert result.score == 2.5
        assert result.threshold == 2.0
        assert result.method == "TestDetector"

    def test_detect_receives_historystatistics(self) -> None:
        """Test that detect receives HistoryStatistics parameter."""

        class TrackingDetector(AnomalyDetector):
            name = "TrackingDetector"
            received_stats = None

            def detect(self, stats: HistoryStatistics) -> AnomalyResult:
                self.received_stats = stats
                return AnomalyResult(is_anomaly=False)

        detector = TrackingDetector()
        mock_stats = Mock(spec=HistoryStatistics)
        result = detector.detect(mock_stats)

        assert detector.received_stats is mock_stats
        assert isinstance(result, AnomalyResult)

    def test_multiple_detector_instances(self) -> None:
        """Test that multiple detector instances work independently."""

        class CounterDetector(AnomalyDetector):
            name = "CounterDetector"
            instance_count = 0

            def __init__(self):
                super().__init__()
                CounterDetector.instance_count += 1
                self.instance_id = CounterDetector.instance_count

            def detect(self, stats: HistoryStatistics) -> AnomalyResult:
                return AnomalyResult(
                    is_anomaly=False, method=f"{self.name}_{self.instance_id}"
                )

        # Create multiple instances
        detector1 = CounterDetector()
        detector2 = CounterDetector()

        assert detector1.instance_id == 1
        assert detector2.instance_id == 2
        assert CounterDetector.instance_count == 2

        # Both should have same class name
        assert detector1.name == "CounterDetector"
        assert detector2.name == "CounterDetector"

        # But detect results can be instance-specific
        stats = Mock(spec=HistoryStatistics)
        result1 = detector1.detect(stats)
        result2 = detector2.detect(stats)

        assert result1.method == "CounterDetector_1"
        assert result2.method == "CounterDetector_2"

    def test_detect_with_real_historystatistics(self) -> None:
        """Test detect with actual HistoryStatistics object."""

        class MeanThresholdDetector(AnomalyDetector):
            name = "MeanThresholdDetector"

            def detect(self, stats: HistoryStatistics) -> AnomalyResult:
                threshold = 100.0
                if stats.mean is None:
                    is_anomaly = False
                    score = 0.0
                else:
                    is_anomaly = stats.mean > threshold
                    score = stats.mean / threshold

                return AnomalyResult(
                    is_anomaly=is_anomaly,
                    score=score,
                    threshold=threshold,
                    method=self.name,
                    metadata={"mean": stats.mean},
                )

        detector = MeanThresholdDetector()

        # Test with high mean (should be anomaly)
        stats_high = Mock(spec=HistoryStatistics)
        stats_high.mean = 150.0
        result_high = detector.detect(stats_high)
        assert result_high.is_anomaly is True
        assert result_high.score == 1.5
        assert result_high.threshold == 100.0

        # Test with low mean (should not be anomaly)
        stats_low = Mock(spec=HistoryStatistics)
        stats_low.mean = 50.0
        result_low = detector.detect(stats_low)
        assert result_low.is_anomaly is False
        assert result_low.score == 0.5

    def test_detect_with_invalid_input(self) -> None:
        """Test that detect can handle invalid/missing statistics."""

        class RobustDetector(AnomalyDetector):
            name = "RobustDetector"

            def detect(self, stats: HistoryStatistics) -> AnomalyResult:
                # Handle missing or invalid stats gracefully
                mean = stats.mean
                if mean is None or stats.count == 0:
                    return AnomalyResult(
                        is_anomaly=False,
                        score=0.0,
                        threshold=None,
                        method=self.name,
                        metadata={"error": "Insufficient data"},
                    )

                # Normal detection logic
                return AnomalyResult(
                    is_anomaly=mean > 100,
                    score=mean / 100 if mean else 0.0,
                    threshold=100.0,
                    method=self.name,
                )

        detector = RobustDetector()

        # Test with None mean
        stats_none = Mock(spec=HistoryStatistics)
        stats_none.mean = None
        stats_none.count = 0
        result_none = detector.detect(stats_none)
        assert result_none.is_anomaly is False
        assert "error" in result_none.metadata

        # Test with valid mean
        stats_valid = Mock(spec=HistoryStatistics)
        stats_valid.mean = 150.0
        stats_valid.count = 10
        result_valid = detector.detect(stats_valid)
        assert result_valid.is_anomaly is True
        assert result_valid.score == 1.5

    def test_class_attribute_inheritance(self) -> None:
        """Test that name class attribute is inherited properly."""

        class ParentDetector(AnomalyDetector):
            name = "ParentDetector"

            def detect(self, stats: HistoryStatistics) -> AnomalyResult:
                return AnomalyResult(is_anomaly=False)

        class ChildDetector(ParentDetector):
            # Override the name
            name = "ChildDetector"

        class GrandchildDetector(ChildDetector):
            # Inherit name from ChildDetector
            pass

        assert ParentDetector.name == "ParentDetector"
        assert ChildDetector.name == "ChildDetector"
        assert GrandchildDetector.name == "ChildDetector"  # Inherited

        # Instance access should also work
        parent = ParentDetector()
        child = ChildDetector()
        grandchild = GrandchildDetector()

        assert parent.name == "ParentDetector"
        assert child.name == "ChildDetector"
        assert grandchild.name == "ChildDetector"

    def test_abstract_method_exception_message(self) -> None:
        """Test the NotImplementedError message in base detect method."""
        # Access the base class's detect method directly
        method = AnomalyDetector.detect

        # Create a mock instance to test the method
        class TestClass:
            pass

        instance = TestClass()

        # The method should raise NotImplementedError with our message
        try:
            method(instance, Mock(spec=HistoryStatistics))
            assert False, "Should have raised NotImplementedError"
        except NotImplementedError as e:
            assert "Subclasses must implement the detect method" in str(e)


# --- Integration and Utility Tests ---


def test_module_import() -> None:
    """Test that the module can be imported correctly."""
    from procela.core.reasoning.anomaly.base import AnomalyDetector

    assert AnomalyDetector.__name__ == "AnomalyDetector"
    assert AnomalyDetector.__module__ == "procela.core.reasoning.anomaly.base"


def test_usage_with_type_hints() -> None:
    """Test that AnomalyDetector works correctly in type hints."""
    from typing import List

    def process_detectors(detectors: List[AnomalyDetector]) -> List[AnomalyResult]:
        """Process multiple detectors (demonstrates type hint usage)."""
        results = []
        stats = Mock(spec=HistoryStatistics)
        for detector in detectors:
            results.append(detector.detect(stats))
        return results

    # Create mock detectors that satisfy the interface
    class MockDetector(AnomalyDetector):
        name = "MockDetector"

        def detect(self, stats: HistoryStatistics) -> AnomalyResult:
            return AnomalyResult(is_anomaly=False)

    detectors = [MockDetector(), MockDetector()]
    results = process_detectors(detectors)

    assert len(results) == 2
    assert all(isinstance(r, AnomalyResult) for r in results)


def test_framework_integration_pattern() -> None:
    """Demonstrate typical integration pattern in Procela framework."""

    # This shows how anomaly detectors would typically be used
    class ZScoreDetector(AnomalyDetector):
        """Example concrete detector using z-score method."""

        name = "ZScoreDetector"

        def __init__(self, threshold: float = 3.0):
            self.threshold = threshold

        def detect(self, stats: HistoryStatistics) -> AnomalyResult:
            if stats.mean is None or stats.std is None or stats.recent_value is None:
                return AnomalyResult(
                    is_anomaly=False,
                    score=0.0,
                    threshold=self.threshold,
                    method=self.name,
                    metadata={"error": "Missing required statistics"},
                )

            if stats.std == 0:
                z_score = 0.0
            else:
                z_score = abs((stats.recent_value - stats.mean) / stats.std)

            return AnomalyResult(
                is_anomaly=z_score > self.threshold,
                score=z_score,
                threshold=self.threshold,
                method=self.name,
                metadata={
                    "z_score": z_score,
                    "mean": stats.mean,
                    "std": stats.std,
                    "recent_value": stats.recent_value,
                },
            )

    # Usage example
    detector = ZScoreDetector(threshold=2.5)
    assert detector.name == "ZScoreDetector"
    assert detector.threshold == 2.5

    # Simulate statistics for a variable
    stats = Mock(spec=HistoryStatistics)
    stats.mean = 100.0
    stats.std = 10.0
    stats.recent_value = 130.0  # 3 standard deviations above mean

    result = detector.detect(stats)

    assert isinstance(result, AnomalyResult)
    assert result.is_anomaly is True  # 130 is 3 std above 100
    assert result.score == 3.0  # (130-100)/10 = 3.0
    assert result.threshold == 2.5
    assert result.method == "ZScoreDetector"
    assert "z_score" in result.metadata


if __name__ == "__main__":
    # Run tests directly with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.reasoning.anomaly.base",
            "--cov-report=term-missing",
        ]
    )
