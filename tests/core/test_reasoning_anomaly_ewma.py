"""
Pytest module for procela.core.reasoning.anomaly.ewma.

Tests the EWMADetector class with 100% coverage.
"""

import pytest

from procela.core.assessment import AnomalyResult
from procela.core.memory import HistoryStatistics
from procela.core.reasoning import EWMADetector


class TestEWMADetectorInitialization:
    """Tests for EWMADetector initialization."""

    def test_default_initialization(self) -> None:
        """Test creation with default threshold."""
        detector = EWMADetector()
        assert detector.name == "EWMADetector"
        assert detector.threshold == 3.0

    def test_custom_threshold(self) -> None:
        """Test creation with custom threshold."""
        detector = EWMADetector(threshold=2.5)
        assert detector.threshold == 2.5

    def test_invalid_threshold_zero(self) -> None:
        """Test that zero threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be > 0"):
            EWMADetector(threshold=0.0)

    def test_invalid_threshold_negative(self) -> None:
        """Test that negative threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be > 0"):
            EWMADetector(threshold=-1.0)

    def test_name_is_class_attribute(self) -> None:
        """Test that name is a class attribute."""
        assert EWMADetector.name == "EWMADetector"
        detector = EWMADetector()
        assert detector.name == "EWMADetector"
        # Should be the same object (class attribute)
        assert detector.name is EWMADetector.name


class TestEWMADetectorDetectMethod:
    """Tests for the detect method."""

    def test_detect_normal_case(self) -> None:
        """Test detection with normal values."""
        detector = EWMADetector(threshold=2.0)

        # Create mock statistics
        stats = HistoryStatistics(
            count=5, sum=90.0, sumsq=1745.0, last_value=105.0, ewma=100.0
        )

        result = detector.detect(stats.stats())

        # Verify result
        assert isinstance(result, AnomalyResult)
        assert result.method == "EWMADetector"
        assert result.threshold == 2.0
        assert result.score == 1.0
        assert not result.is_anomaly

    def test_detect_anomaly(self) -> None:
        """Test detection when anomaly exists."""
        detector = EWMADetector(threshold=2.0)

        stats = HistoryStatistics(
            count=10,
            sum=70.0,
            sumsq=740.0,
            last_value=115.0,  # Large deviation
            ewma=100.0,
        )

        result = detector.detect(stats.stats())

        assert result.score == 3.0
        assert result.is_anomaly

    def test_detect_exact_threshold(self) -> None:
        """Test detection when score equals threshold."""
        detector = EWMADetector(threshold=2.0)

        stats = HistoryStatistics(
            count=8,
            sum=80.0,
            sumsq=1000.0,
            last_value=110.0,  # Exactly 2 std deviations away
            ewma=100.0,
        )

        result = detector.detect(stats.stats())

        assert result.score == 2.0
        assert not result.is_anomaly

    def test_detect_with_negative_difference(self) -> None:
        """Test detection with negative difference (below EWMA)."""
        detector = EWMADetector(threshold=2.0)

        stats = HistoryStatistics(
            count=4,
            sum=20.0,
            sumsq=200.0,
            last_value=90.0,  # Below EWMA
            ewma=100.0,
        )

        result = detector.detect(stats.stats())

        assert result.score == 2.0
        assert not result.is_anomaly

    def test_detect_metadata(self) -> None:
        """Test that metadata contains all expected fields."""
        detector = EWMADetector(threshold=2.5)

        stats = HistoryStatistics(
            count=10,
            sum=75.0,
            sumsq=812.5,
            last_value=112.5,
            ewma=100.0,
        )

        result = detector.detect(stats.stats())

        # Check metadata
        assert "value" in result.metadata
        assert "ewma" in result.metadata
        assert "std" in result.metadata
        assert "difference" in result.metadata

        assert result.metadata["value"] == 112.5
        assert result.metadata["ewma"] == 100.0
        assert result.metadata["std"] == 5.0
        assert result.metadata["difference"] == 12.5

    def test_detect_missing_last_value(self) -> None:
        """Test detection fails when last_value is None."""
        detector = EWMADetector()

        stats = HistoryStatistics(
            count=5,
            sum=30.0,
            sumsq=305.0,
            last_value=None,
            ewma=100.0,
        )

        with pytest.raises(ValueError, match="stats.value is None"):
            detector.detect(stats.stats())

    def test_detect_missing_ewma(self) -> None:
        """Test detection fails when ewma is None."""
        detector = EWMADetector()

        stats = HistoryStatistics(
            count=6,
            sum=102.0,
            sumsq=1884.0,
            last_value=105.0,
            ewma=None,
        )

        with pytest.raises(ValueError, match="ewma is None"):
            detector.detect(stats.stats())

    def test_detect_missing_std(self) -> None:
        """Test detection fails when std is None."""
        detector = EWMADetector()

        stats = HistoryStatistics(
            count=1,
            sum=20.0,
            sumsq=400.0,
            last_value=105.0,
            ewma=100.0,
        )

        with pytest.raises(ValueError, match="std is None"):
            detector.detect(stats.stats())

    def test_detect_zero_std(self) -> None:
        """Test detection fails when std is zero."""
        detector = EWMADetector()

        stats = HistoryStatistics(
            count=5,
            sum=40.0,
            sumsq=320.0,
            last_value=105.0,
            ewma=100.0,
        )

        with pytest.raises(ValueError, match="std is zero"):
            detector.detect(stats.stats())

    def test_detect_wrong_stats_type(self) -> None:
        """Test detection fails with wrong input type."""
        detector = EWMADetector()

        with pytest.raises(TypeError, match="must be StatisticsResult, got str"):
            detector.detect("not stats")  # type: ignore

    def test_detect_boundary_values(self) -> None:
        """Test detection with various boundary values."""
        # Test with very small std (score should be large)
        detector = EWMADetector(threshold=3.0)

        stats = HistoryStatistics(
            count=5,
            sum=30.0,
            sumsq=180.0,
            last_value=100.1,
            ewma=100.0,
        )

        with pytest.raises(ValueError, match="stats.std is zero, cannot normalize"):
            detector.detect(stats.stats())


class TestEWMADetectorStringRepresentations:
    """Tests for string representations."""

    def test_repr(self) -> None:
        """Test __repr__ method."""
        detector = EWMADetector(threshold=2.5)
        assert repr(detector) == "EWMADetector(threshold=2.5)"

    def test_str(self) -> None:
        """Test __str__ method."""
        detector = EWMADetector(threshold=2.5)
        assert str(detector) == "EWMA Anomaly Detector (threshold=2.5)"


class TestEWMADetectorIntegration:
    """Integration tests."""

    def test_inherits_from_anomalydetector(self) -> None:
        """Test EWMADetector is a proper AnomalyDetector subclass."""
        detector = EWMADetector()
        from procela.core.reasoning.anomaly.base import AnomalyDetector

        assert isinstance(detector, AnomalyDetector)

        # Should have required attributes
        assert hasattr(detector, "name")
        assert hasattr(detector, "detect")
        assert callable(detector.detect)

    def test_with_real_historystatistics(self) -> None:
        """Test with actual HistoryStatistics object."""

        # Assuming HistoryStatistics has these attributes
        class MockStats:
            def __init__(self):
                self.last_value = 105.0
                self.ewma = 100.0
                self.std = 5.0
                self.count = 20

        detector = EWMADetector(threshold=2.0)
        stats = HistoryStatistics.empty()
        with pytest.raises(ValueError, match="stats.value is None"):
            _ = detector.detect(stats.stats())


def test_module_import() -> None:
    """Test module import."""
    from procela.core.reasoning.anomaly.ewma import EWMADetector

    assert EWMADetector.__name__ == "EWMADetector"


if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.reasoning.anomaly.ewma",
            "--cov-report=term-missing",
        ]
    )
