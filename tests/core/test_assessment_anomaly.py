"""Pytest module for procela.core.assessment.anomaly."""

import pytest

from procela.core.assessment import AnomalyResult


class TestAnomalyResult:
    """Tests for the AnomalyResult dataclass."""

    def test_basic_initialization(self) -> None:
        """Test basic creation."""
        result = AnomalyResult(
            is_anomaly=True,
            score=3.2,
            threshold=3.0,
            method="zscore",
            metadata={"zscore": 3.2},
        )
        assert result.is_anomaly is True
        assert result.score == 3.2
        assert result.threshold == 3.0
        assert result.method == "zscore"
        assert result.metadata == {"zscore": 3.2}

    def test_minimal_initialization(self) -> None:
        """Test creation with minimal fields."""
        result = AnomalyResult(is_anomaly=False)
        assert result.is_anomaly is False
        assert result.score is None
        assert result.threshold is None
        assert result.method is None
        assert result.metadata is None

    # --- Validation Tests ---
    def test_negative_threshold_raises(self) -> None:
        """Test that negative threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            AnomalyResult(is_anomaly=True, threshold=-1.0)

    def test_zero_threshold_raises(self) -> None:
        """Test that zero threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            AnomalyResult(is_anomaly=True, threshold=0.0)

    # --- confidence() Method Tests ---
    @pytest.mark.parametrize(
        "is_anomaly,score,threshold,expected",
        [
            (True, 3.2, 3.0, 1.0),  # Score > threshold, capped at 1.0
            (True, 2.5, 3.0, 0.83333333),  # Score < threshold
            (True, 3.0, 3.0, 1.0),  # Score == threshold
            (True, 0.0, 1.0, 0.0),  # Zero score
            (False, 3.2, 3.0, None),  # No anomaly
            (True, None, 3.0, None),  # Missing score
            (True, 3.2, None, None),  # Missing threshold
            (True, None, None, None),  # Both missing
        ],
    )
    def test_confidence_calculation(
        self,
        is_anomaly: bool,
        score: float | None,
        threshold: float | None,
        expected: float | None,
    ) -> None:
        """Test confidence calculation under various conditions."""
        result = AnomalyResult(
            is_anomaly=is_anomaly,
            score=score,
            threshold=threshold,
        )
        confidence = result.confidence()
        if expected is None:
            assert confidence is None
        else:
            assert confidence == pytest.approx(expected, rel=1e-6)

    def test_confidence_with_zero_threshold_edge_case(self) -> None:
        """Test confidence with extremely small threshold (avoid division by zero)."""
        result = AnomalyResult(is_anomaly=True, score=0.5, threshold=1e-10)
        # threshold gets adjusted to 1e-9 in calculation
        confidence = result.confidence()
        assert confidence == 1.0

    def test_confidence_with_very_small_threshold(self) -> None:
        """Test confidence when threshold is very small."""
        result = AnomalyResult(is_anomaly=True, score=1e-6, threshold=1e-9)
        confidence = result.confidence()
        assert confidence == 1.0  # Capped at 1.0

    # --- Edge Cases ---
    def test_immutability(self) -> None:
        """Test that fields cannot be modified."""
        result = AnomalyResult(is_anomaly=True)
        with pytest.raises(AttributeError):
            result.is_anomaly = False  # type: ignore


def test_import() -> None:
    """Test that the module can be imported correctly."""
    assert AnomalyResult.__name__ == "AnomalyResult"


def test_frozen_dataclass_behavior() -> None:
    """Test that all dataclasses are frozen (immutable)."""
    # Test AnomalyResult
    ar = AnomalyResult(is_anomaly=True)
    with pytest.raises(AttributeError):
        ar.is_anomaly = False  # type: ignore


if __name__ == "__main__":
    # Run tests directly with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.assessment.anomaly",
            "--cov-report=term-missing",
        ]
    )
