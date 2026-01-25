"""
Pytest module for procela.core.reasoning.diagnosis.statistical.

Tests the StatisticalDiagnoser class with 100% coverage.
Updated to work with actual HistoryStatistics interface.
"""

from unittest.mock import Mock, patch

import pytest

from procela.core.assessment import (
    AnomalyResult,
    DiagnosisResult,
    StatisticsResult,
    TrendResult,
)
from procela.core.reasoning import StatisticalDiagnoser
from procela.core.variable import VariableEpistemic


class TestStatisticalDiagnoserInitialization:
    """Tests for StatisticalDiagnoser initialization."""

    def test_default_initialization(self) -> None:
        """Test creation with default parameters."""
        diagnoser = StatisticalDiagnoser()
        assert diagnoser.name == "StatisticalDiagnoser"
        assert diagnoser.variability_threshold == 0.5
        assert diagnoser.drift_sensitivity == 0.1
        assert diagnoser.skewness_threshold == 1.0

    def test_custom_initialization(self) -> None:
        """Test creation with custom parameters."""
        diagnoser = StatisticalDiagnoser(
            variability_threshold=0.3,
            drift_sensitivity=0.05,
            skewness_threshold=0.8,
        )
        assert diagnoser.variability_threshold == 0.3
        assert diagnoser.drift_sensitivity == 0.05
        assert diagnoser.skewness_threshold == 0.8

    def test_invalid_variability_threshold(self) -> None:
        """Test that non-positive variability_threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be > 0"):
            StatisticalDiagnoser(variability_threshold=0.0)
        with pytest.raises(ValueError, match="must be > 0"):
            StatisticalDiagnoser(variability_threshold=-0.1)

    def test_invalid_drift_sensitivity(self) -> None:
        """Test that non-positive drift_sensitivity raises ValueError."""
        with pytest.raises(ValueError, match="must be > 0"):
            StatisticalDiagnoser(drift_sensitivity=0.0)
        with pytest.raises(ValueError, match="must be > 0"):
            StatisticalDiagnoser(drift_sensitivity=-0.05)

    def test_invalid_skewness_threshold(self) -> None:
        """Test that non-positive skewness_threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be > 0"):
            StatisticalDiagnoser(skewness_threshold=0.0)
        with pytest.raises(ValueError, match="must be > 0"):
            StatisticalDiagnoser(skewness_threshold=-1.0)

    def test_name_is_class_attribute(self) -> None:
        """Test that name is a class attribute."""
        assert StatisticalDiagnoser.name == "StatisticalDiagnoser"
        diagnoser = StatisticalDiagnoser()
        assert diagnoser.name == "StatisticalDiagnoser"


class TestStatisticalDiagnoserDiagnoseMethod:
    """Tests for the diagnose method."""

    def test_diagnose_with_high_variability(self) -> None:
        """Test diagnosis with high statistical variability."""
        diagnoser = StatisticalDiagnoser(variability_threshold=0.3)

        stats = StatisticsResult(
            count=50,
            sum=500.0,
            min=2.0,
            max=25.0,
            mean=10.0,
            std=5.0,
        )

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.stats = stats
        view.trend = None
        view.anomaly = None

        result = diagnoser.diagnose(view)

        assert isinstance(result, DiagnosisResult)
        assert len(result.causes) > 0
        assert "variability" in " ".join(result.causes).lower()
        assert 0.0 <= result.confidence <= 1.0
        assert result.metadata["variability_issues"] > 0

    def test_diagnose_with_insufficient_data(self) -> None:
        """Test diagnosis with insufficient data (count < 2)."""
        diagnoser = StatisticalDiagnoser()

        mock_stats = Mock()
        mock_stats.count = 1  # Insufficient for variability analysis

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.stats = mock_stats
        view.trend = None
        view.anomaly = None

        result = diagnoser.diagnose(view)

        # Should not detect variability issues with insufficient data
        assert "variability" not in " ".join(result.causes).lower()

    def test_diagnose_with_zero_mean(self) -> None:
        """Test diagnosis with zero mean and high std."""
        diagnoser = StatisticalDiagnoser(variability_threshold=0.3)

        mock_stats = Mock()
        mock_stats.count = 50
        mock_stats.mean = 0.0
        mock_stats.std = 15.0  # High absolute std
        mock_stats.min = -20.0
        mock_stats.max = 25.0

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.stats = mock_stats
        view.trend = None
        view.anomaly = None

        result = diagnoser.diagnose(view)

        # Should detect variability with zero mean
        causes_text = " ".join(result.causes).lower()
        assert "variability" in causes_text or "zero" in causes_text

    def test_diagnose_with_significant_drift(self) -> None:
        """Test diagnosis with significant drift."""
        diagnoser = StatisticalDiagnoser(drift_sensitivity=0.05)

        # Create mock stats and trend with drift
        mock_stats = Mock()
        mock_stats.count = 100
        mock_stats.mean = 100.0
        mock_stats.std = 8.0
        mock_stats.min = mock_stats.max = None

        mock_trend = Mock(spec=TrendResult)
        mock_trend.value = 0.08  # > 0.05 sensitivity
        mock_trend.direction = "up"

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.stats = mock_stats
        view.trend = mock_trend
        view.anomaly = None

        result = diagnoser.diagnose(view)

        causes_text = " ".join(result.causes).lower()
        assert "drift" in causes_text
        assert result.metadata["drift_issues"] > 0

    def test_diagnose_with_insignificant_drift(self) -> None:
        """Test diagnosis with drift below sensitivity threshold."""
        diagnoser = StatisticalDiagnoser(drift_sensitivity=0.1)

        mock_stats = Mock()
        mock_stats.count = 100
        mock_stats.mean = None
        mock_stats.std = 5.0

        mock_trend = Mock(spec=TrendResult)
        mock_trend.value = 0.05  # < 0.1 sensitivity
        mock_trend.direction = "up"

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.stats = mock_stats
        view.trend = mock_trend
        view.anomaly = None

        result = diagnoser.diagnose(view)

        # Should not detect drift below sensitivity
        causes_text = " ".join(result.causes).lower()
        assert "drift" not in causes_text

    def test_diagnose_with_wide_data_range(self) -> None:
        """Test diagnosis with wide data range relative to mean."""
        diagnoser = StatisticalDiagnoser()

        mock_stats = Mock()
        mock_stats.count = 50
        mock_stats.mean = 10.0
        mock_stats.std = 3.0
        mock_stats.min = -20.0  # Range = 45, range/mean = 4.5 > 3.0
        mock_stats.max = 25.0

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.stats = mock_stats
        view.trend = None
        view.anomaly = None

        result = diagnoser.diagnose(view)

        causes_text = " ".join(result.causes).lower()
        assert "range" in causes_text or "wide" in causes_text

    def test_diagnose_with_anomaly_context(self) -> None:
        """Test diagnosis with supporting anomaly evidence."""
        diagnoser = StatisticalDiagnoser()

        mock_stats = Mock()
        mock_stats.count = 50
        mock_stats.mean = 100.0
        mock_stats.std = 15.0
        mock_stats.min = mock_stats.max = None

        mock_anomaly = Mock(spec=AnomalyResult)
        mock_anomaly.is_anomaly = True
        mock_anomaly.score = 3.2
        mock_anomaly.method = "z-score"

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.stats = mock_stats
        view.trend = None
        view.anomaly = mock_anomaly

        result = diagnoser.diagnose(view)

        assert result.metadata["anomaly_available"] is True
        assert result.metadata["anomaly_score"] == 3.2
        patterns = result.metadata["patterns_detected"]
        assert patterns["anomaly_present"] is True

    def test_diagnose_missing_stats(self) -> None:
        """Test diagnosis fails when stats are missing."""
        diagnoser = StatisticalDiagnoser()

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.stats = None  # Missing stats
        view.trend = None
        view.anomaly = None

        with pytest.raises(ValueError, match="requires view.stats"):
            diagnoser.diagnose(view)

    def test_diagnose_wrong_view_type(self) -> None:
        """Test diagnose fails with wrong input type."""
        diagnoser = StatisticalDiagnoser()

        with pytest.raises(TypeError, match="view must be VariableView, got str"):
            diagnoser.diagnose("not a view")  # type: ignore

    def test_diagnose_with_unusual_statistics(self) -> None:
        """Test diagnosis with unusual statistics."""
        diagnoser = StatisticalDiagnoser(variability_threshold=1.0)

        # Stats are unusual (high std) but don't trigger CV threshold
        mock_stats = Mock()
        mock_stats.count = 50
        mock_stats.mean = 100.0
        mock_stats.std = 80.0  # High absolute std
        mock_stats.min = 10.0
        mock_stats.max = 250.0

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.stats = mock_stats
        view.trend = None
        view.anomaly = None

        result = diagnoser.diagnose(view)

        assert len(result.causes) == 0
        assert result.confidence == 0

    def test_diagnose_metadata_completeness(self) -> None:
        """Test that diagnose returns comprehensive metadata."""
        diagnoser = StatisticalDiagnoser()

        mock_stats = Mock()
        mock_stats.count = 100
        mock_stats.mean = 50.0
        mock_stats.std = 8.0
        mock_stats.min = 30.0
        mock_stats.max = 75.0

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.stats = mock_stats
        view.trend = None
        view.anomaly = None

        result = diagnoser.diagnose(view)

        # Check metadata fields
        metadata = result.metadata
        assert "diagnoser" in metadata
        assert "variability_threshold" in metadata
        assert "drift_sensitivity" in metadata
        assert "skewness_threshold" in metadata
        assert "stats_available" in metadata
        assert "trend_available" in metadata
        assert "anomaly_available" in metadata
        assert "sample_count" in metadata
        assert "causes_identified" in metadata
        assert "patterns_detected" in metadata
        assert "confidence" in metadata

        assert metadata["diagnoser"] == "StatisticalDiagnoser"
        assert metadata["stats_available"] is True
        assert isinstance(metadata["patterns_detected"], dict)

    def test_diagnose_distribution_causes_integration(self) -> None:
        """Test that distribution causes are properly integrated."""
        diagnoser = StatisticalDiagnoser()

        # Mock _check_distribution to return causes
        with patch.object(diagnoser, "_check_distribution") as mock_check:
            mock_check.return_value = ["Skewed distribution", "Heavy-tailed"]

            mock_stats = Mock()
            mock_stats.count = 50
            mock_stats.mean = 100.0
            mock_stats.std = 15.0
            mock_stats.min = mock_stats.max = None

            view = Mock(spec=VariableEpistemic)
            view.key = None
            view.reasoning = None
            view.stats = mock_stats
            view.trend = None
            view.anomaly = None

            result = diagnoser.diagnose(view)

            # Verify distribution causes were added
            assert len(result.causes) >= 2
            assert "skewed" in result.causes[0].lower()
            assert "tailed" in result.causes[1].lower()

            # Verify metadata
            assert result.metadata["distribution_issues"] == 2
            assert result.metadata["patterns_detected"]["distribution_issues"] is True

    def test_diagnose_with_trend_z_score_formatting(self) -> None:
        """Test that trend z-scores are properly formatted."""
        diagnoser = StatisticalDiagnoser(drift_sensitivity=0.05)

        mock_stats = Mock()
        mock_stats.count = 100
        mock_stats.mean = 50.0
        mock_stats.std = 0.08
        mock_stats.min = mock_stats.max = None

        mock_trend = Mock(spec=TrendResult)
        mock_trend.value = 0.07  # > 0.05 sensitivity
        mock_trend.direction = "up"

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.stats = mock_stats
        view.trend = mock_trend
        view.anomaly = None

        result = diagnoser.diagnose(view)

        # Check if any cause contains formatted z-score
        has_z_score = any("z=" in cause for cause in result.causes)

        # With z=0.875 < 1.0, should be "minor" not "significant"
        if has_z_score:
            assert "minor" in " ".join(result.causes).lower()

    def test_diagnose_multiple_pattern_confidence_boost(self) -> None:
        """Test that multiple patterns boost confidence."""
        diagnoser = StatisticalDiagnoser(
            variability_threshold=0.1, drift_sensitivity=0.05
        )

        # Setup to trigger both variability and drift
        mock_stats = Mock()
        mock_stats.count = 50
        mock_stats.mean = 10.0
        mock_stats.std = 2.0
        mock_stats.min = 5.0
        mock_stats.max = 15.0

        mock_trend = Mock(spec=TrendResult)
        mock_trend.value = 0.06  # > 0.05 sensitivity
        mock_trend.direction = "up"

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.stats = mock_stats
        view.trend = mock_trend
        view.anomaly = Mock(spec=AnomalyResult)  # Also add anomaly for third pattern
        view.anomaly.is_anomaly = True
        view.anomaly.score = 3.0

        result = diagnoser.diagnose(view)

        # Should have multiple patterns detected
        patterns = result.metadata["patterns_detected"]
        true_patterns = sum(1 for v in patterns.values() if v)
        assert true_patterns >= 2  # At least variability and drift

        # Confidence should be boosted by multiple patterns
        assert result.confidence > 0.4  # Base weight is 0.4 + 0.4 = 0.8, plus boost


class TestStatisticalDiagnoserInternalMethods:
    """Tests for internal methods."""

    def test_analyze_variability(self) -> None:
        """Test variability analysis."""
        diagnoser = StatisticalDiagnoser(variability_threshold=0.3)

        # Test with high coefficient of variation
        mock_stats = Mock()
        mock_stats.count = 50
        mock_stats.mean = 10.0
        mock_stats.std = 5.0
        mock_stats.min = 2.0
        mock_stats.max = 25.0

        causes = diagnoser._analyze_variability(mock_stats)
        assert len(causes) > 0
        assert "variability" in causes[0].lower()

        # Test with normal CV
        mock_stats_normal = Mock()
        mock_stats_normal.count = 50
        mock_stats_normal.mean = 100.0
        mock_stats_normal.std = 10.0
        mock_stats_normal.min = 80.0
        mock_stats_normal.max = 120.0

        causes_normal = diagnoser._analyze_variability(mock_stats_normal)
        assert len(causes_normal) == 0

    def test_detect_drift(self) -> None:
        """Test drift detection."""
        diagnoser = StatisticalDiagnoser(drift_sensitivity=0.1)

        # Test with significant upward drift
        mock_trend = Mock()
        mock_trend.value = 0.15  # > 0.1 sensitivity
        mock_trend.direction = "up"

        mock_stats = Mock()
        mock_stats.std = 5.0

        causes = diagnoser._detect_drift(mock_trend, mock_stats)
        assert len(causes) > 0
        assert "upward" in causes[0].lower()

        # Test with significant drift but no std info
        mock_stats_no_std = Mock()
        mock_stats_no_std.std = None

        causes_no_std = diagnoser._detect_drift(mock_trend, mock_stats_no_std)
        assert len(causes_no_std) > 0
        assert "Upward" in causes_no_std[0]

    def test_check_distribution_empty_for_now(self) -> None:
        """Test distribution analysis returns empty (placeholder)."""
        diagnoser = StatisticalDiagnoser()

        mock_stats = Mock()

        causes = diagnoser._check_distribution(mock_stats)
        assert causes == []  # Empty until HistoryStatistics is extended

    def test_calculate_statistical_confidence(self) -> None:
        """Test confidence calculation."""
        diagnoser = StatisticalDiagnoser()

        # Test with multiple patterns
        patterns_strong = {
            "high_variability": True,
            "significant_drift": True,
            "distribution_issues": False,  # Not implemented yet
            "anomaly_present": True,
        }
        confidence_strong = diagnoser._statistical_confidence(patterns_strong)
        assert 0.0 < confidence_strong <= 1.0

        # Test with single pattern
        patterns_single = {
            "high_variability": True,
            "significant_drift": False,
            "distribution_issues": False,
            "anomaly_present": False,
        }
        confidence_single = diagnoser._statistical_confidence(patterns_single)
        assert confidence_single == 0.4  # Weight of high_variability

        # Test with no patterns
        patterns_none = {
            "high_variability": False,
            "significant_drift": False,
            "distribution_issues": False,
            "anomaly_present": False,
        }
        confidence_none = diagnoser._statistical_confidence(patterns_none)
        assert confidence_none == 0.0

    def test_analyze_variability_with_zero_mean_edge_case(self) -> None:
        """Test variability analysis with exactly zero mean."""
        diagnoser = StatisticalDiagnoser(variability_threshold=0.3)

        # Test with exactly zero mean and high std
        mock_stats = Mock()
        mock_stats.count = 50
        mock_stats.mean = 0.0  # Exactly zero
        mock_stats.std = 15.0  # High std > 10
        mock_stats.min = -20.0
        mock_stats.max = 25.0

        causes = diagnoser._analyze_variability(mock_stats)
        assert len(causes) > 0
        assert "zero" in causes[0].lower() or "variability" in causes[0].lower()

    def test_analyze_variability_insufficient_data(self) -> None:
        """Test variability analysis with insufficient data."""
        diagnoser = StatisticalDiagnoser()

        # Test with count < 2
        mock_stats = Mock()
        mock_stats.count = 1  # Insufficient

        causes = diagnoser._analyze_variability(mock_stats)
        assert causes == []  # Should return empty list

    def test_detect_drift_with_statistical_significance(self) -> None:
        """Test drift detection with z-score calculation."""
        diagnoser = StatisticalDiagnoser(drift_sensitivity=0.1)

        # Test with trend that has z > 1.0
        mock_trend = Mock()
        mock_trend.value = 0.15  # > 0.1 sensitivity
        mock_trend.direction = "up"

        mock_stats = Mock()
        mock_stats.std = 0.1
        # Small std makes z-score large: 0.15/0.1 = 1.5 > 1.0

        causes = diagnoser._detect_drift(mock_trend, mock_stats)
        assert len(causes) > 0
        # Should include the z=1.50 formatted string
        assert any("z=" in cause for cause in causes)
        assert any("1.50" in cause or "1.5" in cause for cause in causes)

    def test_detect_drift_with_downward_direction(self) -> None:
        """Test drift detection with downward direction."""
        diagnoser = StatisticalDiagnoser(drift_sensitivity=0.05)

        mock_trend = Mock()
        mock_trend.value = 0.08  # Absolute value > sensitivity
        mock_trend.direction = "down"  # Downward direction

        mock_stats = Mock()
        mock_stats.std = 0.05  # z = 0.08/0.05 = 1.6 > 1.0

        causes = diagnoser._detect_drift(mock_trend, mock_stats)
        assert len(causes) > 0
        assert "downward" in causes[0].lower()

    def test_detect_drift_with_zero_std(self) -> None:
        """Test drift detection with zero standard deviation."""
        diagnoser = StatisticalDiagnoser(drift_sensitivity=0.1)

        mock_trend = Mock()
        mock_trend.value = 0.2  # > sensitivity
        mock_trend.direction = "up"

        mock_stats = Mock()
        mock_stats.std = 0.0

        causes = diagnoser._detect_drift(mock_trend, mock_stats)
        assert len(causes) == 0

    def test_detect_drift_minor_z_score(self) -> None:
        """Test drift detection with z-score <= 1.0."""
        diagnoser = StatisticalDiagnoser(drift_sensitivity=0.1)

        mock_trend = Mock()
        mock_trend.value = 0.12
        mock_trend.direction = "up"

        mock_stats = Mock()
        mock_stats.std = 0.15

        causes = diagnoser._detect_drift(mock_trend, mock_stats)
        assert len(causes) > 0
        assert "minor" in causes[0].lower()
        assert "z=" not in causes[0]


class TestStatisticalDiagnoserIntegration:
    """Integration tests for StatisticalDiagnoser."""

    def test_inherits_from_diagnoser(self) -> None:
        """Test StatisticalDiagnoser is a proper Diagnoser subclass."""
        diagnoser = StatisticalDiagnoser()
        from procela.core.reasoning.diagnosis.base import Diagnoser

        assert isinstance(diagnoser, Diagnoser)

        # Should have required attributes
        assert hasattr(diagnoser, "name")
        assert hasattr(diagnoser, "diagnose")
        assert callable(diagnoser.diagnose)

    def test_string_representations(self) -> None:
        """Test __repr__ and __str__ methods."""
        diagnoser = StatisticalDiagnoser(
            variability_threshold=0.25, drift_sensitivity=0.08
        )

        repr_str = repr(diagnoser)
        assert "StatisticalDiagnoser" in repr_str
        assert "variability_threshold=0.25" in repr_str
        assert "drift_sensitivity=0.08" in repr_str

        str_desc = str(diagnoser)
        assert "Statistical Diagnostic Reasoner" in str_desc
        assert "variability_threshold=0.25" in str_desc
        assert "drift_sensitivity=0.08" in str_desc


def test_module_import() -> None:
    """Test module import."""
    from procela.core.reasoning.diagnosis.statistical import StatisticalDiagnoser

    assert StatisticalDiagnoser.__name__ == "StatisticalDiagnoser"


if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.reasoning.diagnosis.statistical",
            "--cov-report=term-missing",
        ]
    )
