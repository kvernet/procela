"""Pytest module for procela.core.assessment.trend."""

from typing import Any

import pytest

from procela.core.assessment import TrendResult


class TestTrendResult:
    """Tests for the TrendResult dataclass."""

    def test_basic_initialization(self) -> None:
        """Test basic creation."""
        result = TrendResult(
            value=2.5,
            direction="up",
            threshold=0.5,
        )
        assert result.value == 2.5
        assert result.direction == "up"
        assert result.threshold == 0.5

    # --- Validation Tests ---
    @pytest.mark.parametrize("invalid_direction", ["left", "right", "", None])
    def test_invalid_direction_raises(self, invalid_direction: Any) -> None:
        """Test that invalid direction raises ValueError."""
        with pytest.raises(ValueError, match="must be"):
            TrendResult(
                value=1.0,
                direction=invalid_direction,  # type: ignore
                threshold=0.5,
            )

    def test_negative_threshold_raises(self) -> None:
        """Test that negative threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            TrendResult(value=1.0, direction="up", threshold=-0.5)

    def test_zero_threshold_raises(self) -> None:
        """Test that zero threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            TrendResult(value=1.0, direction="up", threshold=0.0)

    # --- confidence() Method Tests ---
    @pytest.mark.parametrize(
        "value,direction,threshold,expected",
        [
            (2.5, "up", 0.5, 1.0),  # Large value, capped
            (0.3, "up", 0.5, 0.6),  # Small value
            (-0.8, "down", 0.5, 1.0),  # Negative value, large magnitude
            (0.0, "stable", 0.5, 0.0),  # Stable direction
            (0.4, "stable", 0.5, 0.0),  # Stable despite value > 0
        ],
    )
    def test_confidence_calculation(
        self, value: float, direction: str, threshold: float, expected: float
    ) -> None:
        """Test confidence calculation."""
        result = TrendResult(value=value, direction=direction, threshold=threshold)
        assert result.confidence() == pytest.approx(expected, rel=1e-6)

    def test_confidence_with_tiny_threshold(self) -> None:
        """Test confidence with very small threshold."""
        result = TrendResult(value=1e-6, direction="up", threshold=1e-9)
        confidence = result.confidence()
        # abs(1e-6) / max(1e-9, 1e-9) = 1e-6 / 1e-9 = 1000, capped at 1.0
        assert confidence == 1.0

    # --- zscore() Method Tests ---
    def test_zscore_calculation(self) -> None:
        """Test zscore calculation."""
        result = TrendResult(value=2.5, direction="up", threshold=0.5)
        assert result.zscore(std=1.25) == 2.0  # 2.5 / 1.25 = 2.0

    def test_zscore_with_none_std(self) -> None:
        """Test zscore with None standard deviation."""
        result = TrendResult(value=2.5, direction="up", threshold=0.5)
        assert result.zscore(std=None) is None

    def test_zscore_with_zero_std(self) -> None:
        """Test zscore with zero standard deviation."""
        result = TrendResult(value=2.5, direction="up", threshold=0.5)
        assert result.zscore(std=0.0) is None

    def test_zscore_negative_std_raises(self) -> None:
        """Test that negative standard deviation raises ValueError."""
        result = TrendResult(value=2.5, direction="up", threshold=0.5)
        with pytest.raises(ValueError, match="must be positive"):
            result.zscore(std=-1.25)

    # --- Edge Cases ---
    def test_immutability(self) -> None:
        """Test that fields cannot be modified."""
        result = TrendResult(value=1.0, direction="up", threshold=0.5)
        with pytest.raises(AttributeError):
            result.value = 2.0  # type: ignore


def test_import() -> None:
    """Test that the module can be imported correctly."""
    assert TrendResult.__name__ == "TrendResult"


def test_frozen_dataclass_behavior() -> None:
    """Test that all dataclasses are frozen (immutable)."""
    result = TrendResult(value=1.0, direction="up", threshold=0.5)

    # Verify all are immutable
    with pytest.raises(AttributeError):
        # Try to modify a field
        result.__dict__["_dummy"] = "test"  # type: ignore


if __name__ == "__main__":
    # Run tests directly with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.assessment.trend",
            "--cov-report=term-missing",
        ]
    )
