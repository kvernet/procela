"""
Pytest module for procela.core.reasoning.diagnosis.anomaly.

Tests the AnomalyDiagnoser class with 100% coverage.
"""

from unittest.mock import Mock

import pytest

from procela.core.assessment import (
    AnomalyResult,
    DiagnosisResult,
    StatisticsResult,
    TrendResult,
)
from procela.core.memory import MemoryStatistics
from procela.core.reasoning import AnomalyDiagnoser
from procela.core.variable import VariableEpistemic


class TestAnomalyDiagnoserInitialization:
    """Tests for AnomalyDiagnoser initialization."""

    def test_default_initialization(self) -> None:
        """Test creation with default parameters."""
        diagnoser = AnomalyDiagnoser()
        assert diagnoser.name == "AnomalyDiagnoser"
        assert diagnoser.severity_threshold == 2.0
        assert diagnoser.include_generic_causes is True

    def test_custom_initialization(self) -> None:
        """Test creation with custom parameters."""
        diagnoser = AnomalyDiagnoser(
            severity_threshold=1.5,
            include_generic_causes=False,
        )
        assert diagnoser.severity_threshold == 1.5
        assert diagnoser.include_generic_causes is False

    def test_invalid_severity_threshold(self) -> None:
        """Test that non-positive severity_threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be > 0"):
            AnomalyDiagnoser(severity_threshold=0.0)
        with pytest.raises(ValueError, match="must be > 0"):
            AnomalyDiagnoser(severity_threshold=-1.0)

    def test_name_is_class_attribute(self) -> None:
        """Test that name is a class attribute."""
        assert AnomalyDiagnoser.name == "AnomalyDiagnoser"
        diagnoser = AnomalyDiagnoser()
        assert diagnoser.name == "AnomalyDiagnoser"


class TestAnomalyDiagnoserDiagnoseMethod:
    """Tests for the diagnose method."""

    def test_diagnose_with_minor_anomaly(self) -> None:
        """Test diagnosis with minor anomaly (below threshold)."""
        diagnoser = AnomalyDiagnoser(severity_threshold=3.0)

        # Create mock view with minor anomaly
        mock_anomaly = Mock(spec=AnomalyResult)
        mock_anomaly.is_anomaly = True
        mock_anomaly.score = 1.5  # Below threshold
        mock_anomaly.method = "ewma"

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.anomaly = mock_anomaly
        view.stats = None
        view.trend = None

        result = diagnoser.diagnose(view)

        # Should use generic causes for minor anomaly
        assert len(result.causes) > 0
        assert "Unidentified system anomaly" in result.causes[0]
        assert result.confidence == 0.3  # Generic causes confidence

    def test_diagnose_without_anomaly(self) -> None:
        """Test diagnosis when no anomaly is present."""
        diagnoser = AnomalyDiagnoser()

        # Create mock view without anomaly
        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.anomaly = None
        view.stats = Mock(spec=MemoryStatistics)
        view.trend = None

        result = diagnoser.diagnose(view)

        assert len(result.causes) == 1  # Generic cause
        assert result.confidence == 0.3
        assert result.metadata["anomaly_present"] is False

    def test_diagnose_without_generic_causes(self) -> None:
        """Test diagnosis with generic causes disabled."""
        diagnoser = AnomalyDiagnoser(
            severity_threshold=3.0,
            include_generic_causes=False,
        )

        # Minor anomaly that won't trigger specific analysis
        anomaly = AnomalyResult(
            is_anomaly=True,
            score=1.0,
            method="z-score",
        )

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.anomaly = anomaly
        view.stats = None
        view.trend = None

        result = diagnoser.diagnose(view)

        # Should have no causes when generic causes disabled
        assert len(result.causes) == 0
        assert result.confidence == 0.0

    def test_diagnose_with_extreme_anomaly(self) -> None:
        """Test diagnosis with extreme anomaly score."""
        diagnoser = AnomalyDiagnoser(severity_threshold=1.0)

        anomaly = Mock(spec=AnomalyResult)
        anomaly.is_anomaly = True
        anomaly.score = 7.5  # Extreme
        anomaly.method = "z-score"

        stats = MemoryStatistics(
            count=10,
            sum=48,
            sumsq=25230.4,
        ).result()

        trend = TrendResult(
            value=None,
            direction="down",
            threshold=3.0,
        )

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.anomaly = anomaly
        view.stats = stats
        view.trend = trend

        result = diagnoser.diagnose(view)

        causes_text = " ".join(result.causes).lower()
        assert "extreme" in causes_text or "critical" in causes_text
        assert "downward trend" in causes_text.lower()
        assert result.confidence > 0.5  # Should have decent confidence

    def test_diagnose_wrong_view_type(self) -> None:
        """Test diagnose fails with wrong input type."""
        diagnoser = AnomalyDiagnoser()

        with pytest.raises(TypeError, match="view must be VariableView, got str"):
            diagnoser.diagnose("not a view")  # type: ignore

    def test_diagnose_metadata_completeness(self) -> None:
        """Test that diagnose returns comprehensive metadata."""
        diagnoser = AnomalyDiagnoser()

        mock_anomaly = Mock(spec=AnomalyResult)
        mock_anomaly.is_anomaly = True
        mock_anomaly.score = 3.0
        mock_anomaly.method = "ewma"

        view = Mock(spec=VariableEpistemic)
        view.key = None
        view.reasoning = None
        view.anomaly = mock_anomaly
        view.stats = None
        view.trend = None

        result = diagnoser.diagnose(view)

        # Check metadata fields
        metadata = result.metadata
        assert "diagnoser" in metadata
        assert "severity_threshold" in metadata
        assert "anomaly_present" in metadata
        assert "anomaly_score" in metadata
        assert "met_severity_threshold" in metadata
        assert "causes_identified" in metadata
        assert "confidence" in metadata
        assert "generic_causes_used" in metadata

        assert metadata["diagnoser"] == "AnomalyDiagnoser"
        assert metadata["severity_threshold"] == 2.0
        assert metadata["anomaly_present"] is True
        assert metadata["anomaly_score"] == 3.0
        assert metadata["met_severity_threshold"] is True


class TestAnomalyDiagnoserInternalMethods:
    """Tests for internal methods."""

    def test_analyze_anomaly_pattern(self) -> None:
        """Test pattern analysis logic."""
        diagnoser = AnomalyDiagnoser()

        # Test with z-score anomaly and upward trend
        anomaly = AnomalyResult(
            is_anomaly=True,
            score=4.0,
            method="z-score",
        )

        stats = StatisticsResult(
            count=2,
            sum=20.7,
            mean=None,
            std=10.0,
        )

        trend = TrendResult(value=None, direction="up", threshold=3.0)

        causes = diagnoser._analyze_pattern(anomaly, stats, trend)

        assert len(causes) >= 2
        # Should identify these patterns
        causes_text = " ".join(causes).lower()
        assert "statistical deviation" in causes_text
        assert "upward trend" in causes_text

    def test_analyze_anomaly_pattern_high_variance(self) -> None:
        """Test pattern analysis with high statistical variance."""
        diagnoser = AnomalyDiagnoser()

        anomaly = AnomalyResult(
            is_anomaly=False,
            score=3.0,
            threshold=None,
            metadata="z-score",
        )

        stats = StatisticsResult(
            count=2,
            sum=12,
            std=150.0,
        )

        trend = TrendResult(
            value=1.8,
            direction="stable",
            threshold=3.0,
        )

        causes = diagnoser._analyze_pattern(anomaly, stats, trend)

        causes_text = " ".join(causes).lower()
        assert "minor anomaly may indicate early warning" in causes_text

    def test_calculate_confidence(self) -> None:
        """Test confidence calculation."""
        diagnoser = AnomalyDiagnoser()

        # Test with multiple specific causes and high anomaly score
        causes = [
            "Extreme anomaly suggests critical failure",
            "Statistical deviation from historical norms",
        ]
        confidence = diagnoser._calculate_confidence(causes, 6.0)

        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should have decent confidence

        # Test with no causes
        confidence_empty = diagnoser._calculate_confidence([], 5.0)
        assert confidence_empty == 0.0

        # Test with tentative causes
        tentative_causes = ["Minor anomaly may indicate early warning"]
        confidence_tentative = diagnoser._calculate_confidence(tentative_causes, 2.0)
        assert 0.0 < confidence_tentative < 0.7  # Should be moderate

    def test_get_generic_causes(self) -> None:
        """Test generic cause generation."""
        diagnoser = AnomalyDiagnoser()

        # Test with significant anomaly
        mock_anomaly = Mock()
        mock_anomaly.is_anomaly = True
        mock_anomaly.score = 4.0

        view_with_anomaly = Mock()
        view_with_anomaly.anomaly = mock_anomaly

        causes_significant = diagnoser._generic_causes(view_with_anomaly)
        assert "Requires manual investigation" in causes_significant

        # Test with minor anomaly
        mock_anomaly_minor = Mock()
        mock_anomaly_minor.is_anomaly = True
        mock_anomaly_minor.score = 1.5

        view_minor = Mock()
        view_minor.anomaly = mock_anomaly_minor

        causes_minor = diagnoser._generic_causes(view_minor)
        assert "Monitor for recurrence" in causes_minor

        # Test without anomaly
        view_no_anomaly = Mock()
        view_no_anomaly.anomaly = None

        causes_no_anomaly = diagnoser._generic_causes(view_no_anomaly)
        assert len(causes_no_anomaly) == 1
        assert "Unidentified system anomaly" in causes_no_anomaly[0]


class TestAnomalyDiagnoserIntegration:
    """Integration tests for AnomalyDiagnoser."""

    def test_inherits_from_diagnoser(self) -> None:
        """Test AnomalyDiagnoser is a proper Diagnoser subclass."""
        diagnoser = AnomalyDiagnoser()
        from procela.core.reasoning.diagnosis.base import Diagnoser

        assert isinstance(diagnoser, Diagnoser)

        # Should have required attributes
        assert hasattr(diagnoser, "name")
        assert hasattr(diagnoser, "diagnose")
        assert callable(diagnoser.diagnose)

    def test_full_diagnostic_workflow(self) -> None:
        """Test complete diagnostic workflow."""
        diagnoser = AnomalyDiagnoser(
            severity_threshold=2.5,
            include_generic_causes=True,
        )

        # Simulate a realistic scenario
        # from procela.core.reasoning.result import AnomalyResult, TrendResult

        # Create a mock view
        class MockView:
            key = None
            reasoning = None
            anomaly = AnomalyResult(
                is_anomaly=True,
                score=4.2,
                threshold=3.0,
                method="z-score",
                metadata={"z_score": 4.2},
            )

            trend = TrendResult(value=2.5, direction="up", threshold=0.5)
            stats = MemoryStatistics(count=1, sum=None, sumsq=None).result()

        # Mock to pass isinstance check
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr("procela.core.variable.VariableEpistemic", MockView)
            view = MockView()
            result = diagnoser.diagnose(view)  # type: ignore

            assert isinstance(result, DiagnosisResult)
            assert len(result.causes) > 0
            assert 0.0 <= result.confidence <= 1.0

            # Verify metadata
            assert result.metadata["diagnoser"] == "AnomalyDiagnoser"
            assert result.metadata["severity_threshold"] == 2.5
            assert result.metadata["anomaly_present"] is True
            assert result.metadata["anomaly_score"] == 4.2

    def test_string_representations(self) -> None:
        """Test __repr__ and __str__ methods."""
        diagnoser = AnomalyDiagnoser(severity_threshold=1.8)

        assert "AnomalyDiagnoser" in repr(diagnoser)
        assert "severity_threshold=1.8" in repr(diagnoser)

        assert "Anomaly Diagnostic Reasoner" in str(diagnoser)
        assert "threshold=1.8" in str(diagnoser)


def test_module_import() -> None:
    """Test module import."""
    from procela.core.reasoning.diagnosis.anomaly import AnomalyDiagnoser

    assert AnomalyDiagnoser.__name__ == "AnomalyDiagnoser"


if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.reasoning.diagnosis.anomaly",
            "--cov-report=term-missing",
        ]
    )
