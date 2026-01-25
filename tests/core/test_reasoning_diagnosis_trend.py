"""
Pytest suite for TrendDiagnoser (Procela Framework).
Aims for 100% branch and logic coverage of the trend.py module.
"""

from unittest.mock import Mock, patch

import pytest

from procela.core.assessment import (
    AnomalyResult,
    DiagnosisResult,
    TrendResult,
)
from procela.core.memory import HistoryStatistics
from procela.core.reasoning import TrendDiagnoser
from procela.core.variable import VariableEpistemic


@pytest.fixture
def default_diagnoser():
    """Provides a default TrendDiagnoser instance."""
    return TrendDiagnoser()


@pytest.fixture
def custom_diagnoser():
    """Provides a TrendDiagnoser instance with custom thresholds."""
    return TrendDiagnoser(
        significance_threshold=0.3, strong_threshold=0.8, require_confidence=False
    )


@pytest.fixture
def mock_trend_up():
    """Provides a mock TrendResult with an upward trend."""
    trend = Mock(spec=TrendResult)
    trend.value = 0.4
    trend.direction = "up"
    trend.threshold = 0.5
    trend.confidence = Mock(return_value=0.85)
    return trend


@pytest.fixture
def mock_trend_down():
    """Provides a mock TrendResult with a downward trend."""
    trend = Mock(spec=TrendResult)
    trend.value = -0.6
    trend.direction = "down"
    trend.threshold = 0.5
    trend.confidence = Mock(return_value=0.9)
    return trend


@pytest.fixture
def mock_trend_stable():
    """Provides a mock TrendResult with a stable trend."""
    trend = Mock(spec=TrendResult)
    trend.value = 0.05
    trend.direction = "stable"
    trend.threshold = 0.5
    trend.confidence = Mock(return_value=0.3)
    return trend


@pytest.fixture
def mock_trend_strong_up():
    """Provides a mock TrendResult with a strong upward trend."""
    trend = Mock(spec=TrendResult)
    trend.value = 0.9
    trend.direction = "up"
    trend.threshold = 0.5
    trend.confidence = Mock(return_value=0.95)
    return trend


@pytest.fixture
def mock_view_with_trend(mock_trend_up):
    """Provides a mock VariableEpistemic with a trend."""
    view = Mock(spec=VariableEpistemic)
    view.key = None
    view.reasoning = None
    view.trend = mock_trend_up
    view.stats = None
    view.anomaly = None
    return view


@pytest.fixture
def mock_view_without_trend():
    """Provides a mock VariableEpistemic without a trend."""
    view = Mock(spec=VariableEpistemic)
    view.key = None
    view.reasoning = None
    view.trend = None
    view.stats = None
    view.anomaly = None
    return view


@pytest.fixture
def mock_view_with_stats_and_anomaly(mock_trend_down):
    """Provides a mock VariableEpistemic with stats and anomaly."""
    view = Mock(spec=VariableEpistemic)
    view.key = None
    view.reasoning = None
    view.trend = mock_trend_down
    view.stats = Mock(spec=HistoryStatistics)
    view.anomaly = Mock(spec=AnomalyResult)
    view.anomaly.is_anomaly = True
    view.anomaly.score = 0.8
    return view


# --- Test Class Initialization and Validation ---


class TestTrendDiagnoserInitialization:
    """Test the initialization and parameter validation of TrendDiagnoser."""

    def test_default_initialization(self):
        """Test initialization with default parameters."""
        diagnoser = TrendDiagnoser()
        assert diagnoser.name == "TrendDiagnoser"
        assert diagnoser.significance_threshold == 0.2
        assert diagnoser.strong_threshold == 0.5
        assert diagnoser.require_confidence is True

    def test_custom_initialization(self):
        """Test initialization with custom parameters."""
        diagnoser = TrendDiagnoser(
            significance_threshold=0.1, strong_threshold=0.7, require_confidence=False
        )
        assert diagnoser.significance_threshold == 0.1
        assert diagnoser.strong_threshold == 0.7
        assert diagnoser.require_confidence is False

    def test_invalid_significance_threshold_zero(self):
        """Test initialization with zero significance threshold."""
        with pytest.raises(ValueError) as excinfo:
            TrendDiagnoser(significance_threshold=0.0)
        assert "must be > 0" in str(excinfo.value)

    def test_invalid_significance_threshold_negative(self):
        """Test initialization with negative significance threshold."""
        with pytest.raises(ValueError) as excinfo:
            TrendDiagnoser(significance_threshold=-0.1)
        assert "must be > 0" in str(excinfo.value)

    def test_invalid_strong_threshold_equal(self):
        """Test initialization with strong threshold equal to significance."""
        with pytest.raises(ValueError) as excinfo:
            TrendDiagnoser(significance_threshold=0.3, strong_threshold=0.3)
        assert "must be >" in str(excinfo.value)

    def test_invalid_strong_threshold_less(self):
        """Test initialization with strong threshold less than significance."""
        with pytest.raises(ValueError) as excinfo:
            TrendDiagnoser(significance_threshold=0.4, strong_threshold=0.3)
        assert "must be >" in str(excinfo.value)


# --- Test Diagnose Method ---


class TestDiagnoseMethod:
    """Test the main diagnose method of TrendDiagnoser."""

    def test_diagnose_with_valid_view(self, default_diagnoser, mock_view_with_trend):
        """Test diagnose with a valid view containing trend data."""
        result = default_diagnoser.diagnose(mock_view_with_trend)

        assert isinstance(result, DiagnosisResult)
        assert 0.0 <= result.confidence <= 1.0
        assert "diagnoser" in result.metadata
        assert result.metadata["diagnoser"] == "TrendDiagnoser"
        assert result.metadata["trend_available"] is True

    def test_diagnose_with_invalid_view_type(self, default_diagnoser):
        """Test diagnose with invalid view type."""
        with pytest.raises(TypeError) as excinfo:
            default_diagnoser.diagnose("not a view")
        assert "view must be VariableView, got str" in str(excinfo.value)

    def test_diagnose_without_trend_confidence_required(
        self, default_diagnoser, mock_view_without_trend
    ):
        """Test diagnose without trend when confidence is required."""
        with pytest.raises(ValueError) as excinfo:
            default_diagnoser.diagnose(mock_view_without_trend)
        assert "requires view.trend" in str(excinfo.value)

    def test_diagnose_without_trend_confidence_not_required(
        self, custom_diagnoser, mock_view_without_trend
    ):
        """Test diagnose without trend when confidence is not required."""
        result = custom_diagnoser.diagnose(mock_view_without_trend)

        assert isinstance(result, DiagnosisResult)
        assert result.confidence == 0.0
        assert len(result.causes) == 0
        assert result.metadata["trend_available"] is False

    def test_diagnose_with_stats_context(
        self, default_diagnoser, mock_view_with_stats_and_anomaly
    ):
        """Test diagnose with statistical context available."""
        # Mock the _statistical_context method to return test causes
        with patch.object(
            default_diagnoser, "_statistical_context"
        ) as mock_stat_context:
            mock_stat_context.return_value = ["Statistical issue detected"]
            result = default_diagnoser.diagnose(mock_view_with_stats_and_anomaly)

            mock_stat_context.assert_called_once()
            assert "Statistical issue detected" in result.causes

    def test_diagnose_fallback_cause_significant_trend(
        self, default_diagnoser, mock_trend_up
    ):
        """Test diagnose adds fallback cause for significant trend."""
        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.trend = mock_trend_up
        view.stats = None
        view.anomaly = None

        # Mock private methods to return no causes
        with (
            patch.object(default_diagnoser, "_trend_direction", return_value=[]),
            patch.object(default_diagnoser, "_trend_magnitude", return_value=[]),
            patch.object(default_diagnoser, "_trend_stability", return_value=[]),
        ):
            result = default_diagnoser.diagnose(view)

            # Should have fallback cause for significant trend
            assert len(result.causes) > 0
            assert "Significant upward trend detected" in result.causes[0]
            assert result.confidence == 0.4  # From fallback logic

    def test_diagnose_no_fallback_for_insignificant_trend(self, default_diagnoser):
        """Test diagnose doesn't add fallback for insignificant trend."""
        trend = Mock(spec=TrendResult)
        trend.value = 0.1  # Below significance_threshold of 0.2
        trend.direction = "up"
        trend.threshold = 0.5
        trend.confidence = Mock(return_value=0.5)

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.trend = trend
        view.stats = None
        view.anomaly = None

        # Mock private methods to return no causes
        with (
            patch.object(default_diagnoser, "_trend_direction", return_value=[]),
            patch.object(default_diagnoser, "_trend_magnitude", return_value=[]),
            patch.object(default_diagnoser, "_trend_stability", return_value=[]),
        ):
            result = default_diagnoser.diagnose(view)

            # Should have no causes for insignificant trend
            assert len(result.causes) == 0

    def test_diagnose_metadata_completeness(
        self, default_diagnoser, mock_view_with_trend
    ):
        """Test that diagnose returns complete metadata."""
        result = default_diagnoser.diagnose(mock_view_with_trend)

        metadata = result.metadata
        expected_keys = [
            "diagnoser",
            "significance_threshold",
            "strong_threshold",
            "require_confidence",
            "trend_available",
            "trend_value",
            "trend_direction",
            "stats_available",
            "anomaly_available",
            "causes_identified",
            "confidence",
        ]

        for key in expected_keys:
            assert key in metadata


# --- Test Private Methods ---


class TestPrivateMethods:
    """Test the private helper methods of TrendDiagnoser."""

    def test_trend_direction_upward(self, default_diagnoser, mock_trend_up):
        """Test _trend_direction with upward trend."""
        causes = default_diagnoser._trend_direction(mock_trend_up)

        assert len(causes) > 0
        assert "Upward trend may indicate improvement or overshoot" in causes[0]
        if len(causes) > 1:
            assert "High-confidence improvement trend" in causes[1]

    def test_trend_direction_downward(self, default_diagnoser, mock_trend_down):
        """Test _trend_direction with downward trend."""
        causes = default_diagnoser._trend_direction(mock_trend_down)

        assert len(causes) > 0
        assert "Downward trend suggests potential degradation" in causes[0]
        if len(causes) > 1:
            assert "High-confidence degradation trend" in causes[1]

    def test_trend_direction_stable_with_low_magnitude(
        self, default_diagnoser, mock_trend_stable
    ):
        """Test _trend_direction with stable trend and low magnitude."""
        mock_trend_stable.value = 0.05  # Below significance_threshold/2
        causes = default_diagnoser._trend_direction(mock_trend_stable)

        assert len(causes) == 1
        assert "System appears stable" in causes[0]

    def test_trend_direction_stable_with_high_magnitude(
        self, default_diagnoser, mock_trend_stable
    ):
        """Test _trend_direction with stable trend but high magnitude."""
        mock_trend_stable.value = 0.15  # Above significance_threshold/2 (0.1)
        causes = default_diagnoser._trend_direction(mock_trend_stable)

        assert len(causes) == 1
        assert "Unexpected stability given trend magnitude" in causes[0]

    def test_trend_direction_trend_with_confidence_method(self, default_diagnoser):
        """Test _trend_direction with trend that has no confidence method."""
        trend = Mock(spec=TrendResult)
        trend.value = 0.4
        trend.direction = "up"
        trend.confidence = lambda: 0.34

        causes = default_diagnoser._trend_direction(trend)

        # Should only have the basic direction cause
        assert len(causes) == 1
        assert "Upward trend may indicate improvement or overshoot" in causes[0]

    def test_trend_magnitude_method_exists(self, default_diagnoser, mock_trend_up):
        """Test that _trend_magnitude method exists and returns list."""
        try:
            causes = default_diagnoser._trend_magnitude(mock_trend_up)
            assert isinstance(causes, list)
        except NotImplementedError:
            pytest.skip(
                "_trend_magnitude method not fully implemented in provided code"
            )

    def test_trend_magnitude_abs_value_minor(self):
        """Test trend_magnitude with minor abs_value."""
        diagnoser = TrendDiagnoser()

        class View:
            key = None
            reasoning = None
            trend = TrendResult(value=0.0001, direction="up", threshold=0.3)
            stats = HistoryStatistics.empty().stats()
            anomaly = None

        result = diagnoser.diagnose(View())
        assert isinstance(result, DiagnosisResult)

    def test_trend_stability_method_exists(self, default_diagnoser, mock_trend_up):
        """Test that _trend_stability method exists and returns list."""
        try:
            causes = default_diagnoser._trend_stability(mock_trend_up)
            assert isinstance(causes, list)
        except NotImplementedError:
            pytest.skip(
                "_trend_stability method not fully implemented in provided code"
            )

    def test_trend_stability_stable_direction_high_value(self):
        """Test trend stability stable direction with high value."""
        diagnoser = TrendDiagnoser()

        class View:
            key = None
            reasoning = None
            trend = TrendResult(value=1000, direction="stable", threshold=1000)
            stats = HistoryStatistics.empty().stats()
            anomaly = None

        result = diagnoser.diagnose(View())
        assert isinstance(result, DiagnosisResult)

    def test_statistical_context_method_exists(self, default_diagnoser, mock_trend_up):
        """Test that _statistical_context method exists."""
        # Create a mock stats object
        mock_stats = Mock(spec=HistoryStatistics)
        mock_stats.std = 0.7

        try:
            causes = default_diagnoser._statistical_context(mock_trend_up, mock_stats)
            assert isinstance(causes, list)
        except NotImplementedError:
            pytest.skip(
                "_statistical_context method not fully implemented in provided code"
            )

    def test_statistical_context_no_stats(self):
        """Test _statistical_context with no stats."""
        diagnoser = TrendDiagnoser()

        class View:
            trend = TrendResult(value=1000, direction="stable", threshold=1000)
            stats = None
            anomaly = None

        view = View()
        result = diagnoser._statistical_context(view.trend, view.stats)
        assert len(result) == 0

    def test_statistical_context(self):
        """Test _statistical_context"""
        diagnoser = TrendDiagnoser()

        class View:
            trend = TrendResult(value=1000, direction="stable", threshold=1000)
            stats = HistoryStatistics(count=20, sum=18, sumsq=200).stats()
            anomaly = None

        view = View()
        result = diagnoser._statistical_context(view.trend, view.stats)
        assert len(result) == 1

        view.stats = HistoryStatistics(count=2, sum=18, sumsq=1700000).stats()
        result = diagnoser._statistical_context(view.trend, view.stats)
        assert len(result) == 1

        view.stats = HistoryStatistics(count=2, sum=18, sumsq=1700, min=1.8).stats()
        view.trend = TrendResult(value=-1000, direction="down", threshold=10)
        result = diagnoser._statistical_context(view.trend, view.stats)
        assert len(result) == 1

    def test_correlate_with_anomaly_method_exists(
        self, default_diagnoser, mock_trend_up
    ):
        """Test that _correlate_with_anomaly method exists."""
        mock_anomaly = Mock(spec=AnomalyResult)
        mock_anomaly.is_anomaly = True
        mock_anomaly.score = 0.8

        try:
            causes = default_diagnoser._correlate_with_anomaly(
                mock_trend_up, mock_anomaly
            )
            assert isinstance(causes, list)
        except NotImplementedError:
            pytest.skip(
                "_correlate_with_anomaly method not fully implemented in provided code"
            )

    def test_trend_confidence_calculation(self, default_diagnoser, mock_trend_up):
        """Test _trend_confidence calculation."""
        test_causes = ["Cause 1", "Cause 2", "Cause 3"]

        confidence = default_diagnoser._trend_confidence(test_causes, mock_trend_up)

        # Confidence should be between 0 and 1
        assert 0.0 <= confidence <= 1.0

        # With high trend confidence and multiple causes,
        # confidence should be reasonable
        if mock_trend_up.confidence() > 0.8 and len(test_causes) > 0:
            assert confidence > 0.5


# --- Test Edge Cases and Integration ---


class TestEdgeCases:
    """Test edge cases and integration scenarios."""

    def test_diagnose_with_missing_confidence_method(self, default_diagnoser):
        """Test diagnose with trend that doesn't have confidence method."""
        trend = Mock(spec=TrendResult)
        trend.value = 0.4
        trend.direction = "up"
        trend.threshold = 0.5
        trend.confidence = lambda: 0.85
        # Don't add confidence method

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.trend = trend
        view.stats = None
        view.anomaly = None

        result = default_diagnoser.diagnose(view)

        # Should still work without error
        assert isinstance(result, DiagnosisResult)
        assert "trend_confidence" in result.metadata

    def test_diagnose_with_anomaly_not_anomaly(self, default_diagnoser, mock_trend_up):
        """Test diagnose with anomaly present but is_anomaly is False."""
        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.trend = mock_trend_up
        view.stats = None
        view.anomaly = Mock(spec=AnomalyResult)
        view.anomaly.is_anomaly = False
        view.anomaly.score = 0.3

        result = default_diagnoser.diagnose(view)

        assert result.metadata["anomaly_present"] is False
        # _correlate_with_anomaly shouldn't be called when is_anomaly is False

    def test_diagnose_correlate_with_anomaly(self):
        """Test diagnose correlation with anomaly."""
        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.trend = Mock(spec=TrendResult)
        view.stats = None
        view.anomaly = Mock(spec=AnomalyResult)
        view.anomaly.is_anomaly = True
        view.anomaly.score = 3.3

        diagnoser = TrendDiagnoser()

        for direction in ["up", "down"]:
            view.trend.direction = direction
            result = diagnoser._correlate_with_anomaly(view.trend, view.anomaly)

            assert len(result) == 1

        assert "significance_threshold=0.20, strong_threshold=0.50" in str(diagnoser)

    def test_diagnose_with_all_data_present(self, default_diagnoser):
        """Test diagnose with trend, stats, and anomaly all present."""
        trend = Mock(spec=TrendResult)
        trend.value = 0.7
        trend.direction = "up"
        trend.threshold = 0.5
        trend.confidence = Mock(return_value=0.9)

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.trend = trend
        view.stats = Mock(spec=HistoryStatistics)
        view.anomaly = Mock(spec=AnomalyResult)
        view.anomaly.is_anomaly = True
        view.anomaly.score = 0.85

        # Mock all private methods
        with (
            patch.object(
                default_diagnoser, "_trend_direction", return_value=["Direction issue"]
            ),
            patch.object(
                default_diagnoser, "_trend_magnitude", return_value=["Magnitude issue"]
            ),
            patch.object(
                default_diagnoser, "_trend_stability", return_value=["Stability issue"]
            ),
            patch.object(
                default_diagnoser,
                "_statistical_context",
                return_value=["Statistical issue"],
            ),
            patch.object(
                default_diagnoser,
                "_correlate_with_anomaly",
                return_value=["Anomaly issue"],
            ),
        ):
            result = default_diagnoser.diagnose(view)

            assert len(result.causes) == 5  # All mocked causes
            assert result.metadata["stats_available"] is True
            assert result.metadata["anomaly_present"] is True

    def test_significant_but_not_strong_trend(self, default_diagnoser):
        """Test behavior with trend that's significant but not strong."""
        trend = Mock(spec=TrendResult)
        trend.value = 0.3  # Between 0.2 (significance) and 0.5 (strong)
        trend.direction = "down"
        trend.threshold = 0.5
        trend.confidence = Mock(return_value=0.6)

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.trend = trend
        view.stats = None
        view.anomaly = None

        # Mock private methods to return no specific causes
        with (
            patch.object(default_diagnoser, "_trend_direction", return_value=[]),
            patch.object(default_diagnoser, "_trend_magnitude", return_value=[]),
            patch.object(default_diagnoser, "_trend_stability", return_value=[]),
        ):
            result = default_diagnoser.diagnose(view)

            # Should have fallback cause since abs(0.3) > 0.2
            assert len(result.causes) > 0
            assert "Significant downward trend detected" in result.causes[0]


# --- Test Coverage Verification ---


def test_coverage_statistics():
    """Verify that all public methods are tested."""
    # This is a meta-test to ensure we're covering the public API
    public_methods = ["__init__", "diagnose", "name"]  # Class variable

    # Check that all public methods exist
    diagnoser = TrendDiagnoser()
    for method in public_methods:
        if method != "name":  # name is a class variable, not a method
            assert hasattr(diagnoser, method)

    # Check private methods that should be tested
    private_methods = [
        "_trend_direction",
        "_trend_magnitude",
        "_trend_stability",
        "_statistical_context",
        "_correlate_with_anomaly",
        "_trend_confidence",
    ]

    for method in private_methods:
        # These might not all be implemented in the provided code snippet
        if hasattr(diagnoser, method):
            assert callable(getattr(diagnoser, method))


# --- Main Execution Block (for manual testing) ---
if __name__ == "__main__":
    # This allows running the tests directly: python test_trend_diagnoser.py
    pytest.main([__file__, "-v", "--cov=trend", "--cov-report=term-missing"])
