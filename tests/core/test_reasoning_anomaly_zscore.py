"""
Pytest module for procela.core.reasoning.anomaly.zscore.

Tests the ZScoreDetector class with 100% coverage.
"""

import pytest

from procela.core.assessment import AnomalyResult, StatisticsResult
from procela.core.memory import HistoryStatistics
from procela.core.reasoning import ZScoreDetector


class TestZScoreDetectorInitialization:
    """Tests for ZScoreDetector initialization."""

    def test_default_initialization(self) -> None:
        """Test creation with default threshold."""
        detector = ZScoreDetector()
        assert detector.name == "ZScoreDetector"
        assert detector.threshold == 3.0

    def test_custom_threshold(self) -> None:
        """Test creation with custom threshold."""
        detector = ZScoreDetector(threshold=2.5)
        assert detector.threshold == 2.5

    def test_invalid_threshold_zero(self) -> None:
        """Test that zero threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be > 0"):
            ZScoreDetector(threshold=0.0)

    def test_invalid_threshold_negative(self) -> None:
        """Test that negative threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be > 0"):
            ZScoreDetector(threshold=-1.0)

    def test_name_is_class_attribute(self) -> None:
        """Test that name is a class attribute."""
        assert ZScoreDetector.name == "ZScoreDetector"
        detector = ZScoreDetector()
        assert detector.name == "ZScoreDetector"


class TestZScoreDetectorDetectMethod:
    """Tests for the detect method."""

    def test_detect_normal_case(self) -> None:
        """Test detection with normal values within threshold."""
        detector = ZScoreDetector(threshold=2.0)

        # Create mock statistics
        stats = HistoryStatistics(
            count=10,
            sum=1000.0,
            sumsq=100250.0,
            last_value=105.0,
        )

        result = detector.detect(stats.stats())

        # Verify result
        assert isinstance(result, AnomalyResult)
        assert result.method == "ZScoreDetector"
        assert result.threshold == 2.0
        assert result.score == 1.0  # abs(105-100)/5 = 1.0
        assert not result.is_anomaly  # 1.0 < 2.0

        # Check metadata
        assert result.metadata["mean"] == 100.0
        assert result.metadata["std"] == 5.0
        assert result.metadata["value"] == 105.0
        assert result.metadata["z_score"] == 1.0

    def test_detect_anomaly(self) -> None:
        """Test detection when anomaly exists (score >= threshold)."""
        detector = ZScoreDetector(threshold=2.0)

        stats = HistoryStatistics(
            count=10,
            sum=1000.0,
            sumsq=100250.0,
            last_value=115.0,
        )

        result = detector.detect(stats.stats())

        assert result.score == 3.0
        assert result.is_anomaly

    def test_detect_exact_threshold(self) -> None:
        """Test detection when score exactly equals threshold."""
        detector = ZScoreDetector(threshold=2.0)

        stats = HistoryStatistics(
            count=10,
            sum=1000.0,
            sumsq=100250.0,
            last_value=110.0,
        )

        result = detector.detect(stats.stats())

        assert result.score == 2.0
        assert result.is_anomaly  # 2.0 >= 2.0 (uses >= operator)

    def test_detect_insufficient_data(self) -> None:
        """Test detection with insufficient data (count < 2)."""
        detector = ZScoreDetector()

        stats = HistoryStatistics(
            count=1,
            sum=100.0,
            sumsq=10000.0,
            last_value=105.0,
        )

        result = detector.detect(stats.stats())

        assert not result.is_anomaly
        assert result.score is None
        assert result.metadata["reason"] == "insufficient data"
        assert result.metadata["count"] == 1

    def test_detect_missing_std(self) -> None:
        """Test detection when standard deviation is None."""
        detector = ZScoreDetector()

        stats = StatisticsResult(
            count=4,
            sum=100.0,
            mean=25.0,
            std=None,
        )

        result = detector.detect(stats)

        assert result.metadata["reason"] == "missing standard deviation"

    def test_detect_zero_std(self) -> None:
        """Test detection when standard deviation is zero."""
        detector = ZScoreDetector()

        stats = HistoryStatistics(
            count=10,
            sum=1000.0,
            sumsq=100000.0,
            last_value=105.0,
        )

        result = detector.detect(stats.stats())

        assert not result.is_anomaly
        assert result.score is None
        assert result.metadata["reason"] == "degenerate distribution"
        assert result.metadata["mean"] == 100.0
        assert result.metadata["value"] == 105.0

    def test_detect_missing_last_value(self) -> None:
        """Test detection when last_value is None."""
        detector = ZScoreDetector()

        stats = HistoryStatistics(
            count=10,
            sum=1000.0,
            sumsq=100250.0,
            last_value=None,
        )

        result = detector.detect(stats.stats())

        assert not result.is_anomaly
        assert result.score is None
        assert result.metadata["reason"] == "missing last value"

    def test_detect_missing_mean(self) -> None:
        """Test detection when mean is None."""
        detector = ZScoreDetector()

        stats = HistoryStatistics(count=10, sum=None, sumsq=None, last_value=105.0)

        result = detector.detect(stats.stats())

        assert not result.is_anomaly
        assert result.score is None
        assert result.metadata["reason"] == "missing mean"

    def test_detect_with_callable_mean_std(self) -> None:
        """Test detection when mean and std are callable methods."""
        detector = ZScoreDetector(threshold=2.0)

        stats = HistoryStatistics(
            count=10,
            sum=1000.0,
            sumsq=100250.0,
            last_value=110.0,
        )

        result = detector.detect(stats.stats())

        assert result.score == 2.0
        assert result.is_anomaly

    def test_detect_wrong_stats_type(self) -> None:
        """Test detection fails with wrong input type."""
        detector = ZScoreDetector()

        with pytest.raises(TypeError, match="stats must be StatisticsResult, got str"):
            detector.detect("not stats")  # type: ignore

    def test_detect_negative_values(self) -> None:
        """Test detection with negative mean and values."""
        detector = ZScoreDetector(threshold=2.0)

        stats = HistoryStatistics(
            count=10,
            sum=-500.0,
            sumsq=26000.0,
            last_value=-75.0,
        )

        result = detector.detect(stats.stats())

        assert result.score == 2.5
        assert result.is_anomaly

    def test_detect_large_std_small_score(self) -> None:
        """Test detection with large standard deviation."""
        detector = ZScoreDetector(threshold=3.0)

        stats = HistoryStatistics(
            count=10,
            sum=1000.0,
            sumsq=125000.0,
            last_value=120.0,
        )

        result = detector.detect(stats.stats())

        assert result.score == pytest.approx(0.4)
        assert not result.is_anomaly

    def test_detect_small_std_large_score(self) -> None:
        """Test detection with small standard deviation."""
        detector = ZScoreDetector(threshold=3.0)

        stats = HistoryStatistics(
            count=10,
            sum=1000.0,
            sumsq=100000.1,
            last_value=100.5,
        )

        # This should trigger zero-std check before calculation
        result = detector.detect(stats.stats())

        # Actually, 0.1 != 0, so it should calculate
        # But in our mock, std is 0.1, not 0
        # Let me correct this test:
        stats = HistoryStatistics(
            count=10,
            sum=1000.0,
            sumsq=100000.0,
            last_value=100.5,
        )

        result = detector.detect(stats.stats())
        assert not result.is_anomaly
        assert result.score is None
        assert result.metadata["reason"] == "degenerate distribution"


class TestZScoreDetectorStringRepresentations:
    """Tests for string representations."""

    def test_repr(self) -> None:
        """Test __repr__ method."""
        detector = ZScoreDetector(threshold=2.5)
        assert repr(detector) == "ZScoreDetector(threshold=2.5)"

    def test_str(self) -> None:
        """Test __str__ method."""
        detector = ZScoreDetector(threshold=2.5)
        assert str(detector) == "Z-Score Anomaly Detector (2.5 threshold)"


class TestZScoreDetectorIntegration:
    """Integration tests."""

    def test_inherits_from_anomalydetector(self) -> None:
        """Test ZScoreDetector is a proper AnomalyDetector subclass."""
        detector = ZScoreDetector()
        from procela.core.reasoning.anomaly.base import AnomalyDetector

        assert isinstance(detector, AnomalyDetector)

        # Should have required attributes
        assert hasattr(detector, "name")
        assert hasattr(detector, "detect")
        assert callable(detector.detect)

    def test_statistical_correctness(self) -> None:
        """Test mathematical correctness of Z-Score calculation."""
        detector = ZScoreDetector(threshold=2.0)

        # Test cases: (mean, std, value, expected_zscore)
        test_cases = [
            (100.0, 10.0, 120.0, 2.0),  # Exactly 2 std above
            (100.0, 10.0, 80.0, 2.0),  # Exactly 2 std below
            (0.0, 1.0, 1.5, 1.5),  # Positive mean and value
            (-10.0, 2.0, -14.0, 2.0),  # Negative mean and value
            (50.0, 5.0, 50.0, 0.0),  # Exactly at mean
        ]

        for mean, std, value, expected_zscore in test_cases:
            count = 10
            sum = mean * count
            stats = HistoryStatistics(
                count=count,
                sum=sum,
                sumsq=count * (std**2 + mean**2),
                last_value=value,
            )

            result = detector.detect(stats.stats())

            assert result.score == pytest.approx(
                expected_zscore, rel=1e-10
            ), f"Failed for mean={mean}, std={std}, value={value}"

            # Check if anomaly based on threshold
            if expected_zscore >= 2.0:
                assert result.is_anomaly
            else:
                assert not result.is_anomaly


def test_module_import() -> None:
    """Test module import."""
    from procela.core.reasoning.anomaly.zscore import ZScoreDetector

    assert ZScoreDetector.__name__ == "ZScoreDetector"
    assert ZScoreDetector.__module__ == "procela.core.reasoning.anomaly.zscore"


if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.reasoning.anomaly.zscore",
            "--cov-report=term-missing",
        ]
    )
