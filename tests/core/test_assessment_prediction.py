"""Pytest module for procela.core.assessment.prediction."""

import pytest

from procela.core.assessment import PredictionResult


class TestPredictionResult:
    """Tests for the PredictionResult dataclass."""

    def test_basic_initialization(self) -> None:
        """Test basic creation."""
        result = PredictionResult(
            value=42.5,
            horizon=5,
            confidence=0.88,
            metadata={"model": "ARIMA"},
        )
        assert result.value == 42.5
        assert result.horizon == 5
        assert result.confidence == 0.88
        assert result.metadata == {"model": "ARIMA"}

    def test_minimal_initialization(self) -> None:
        """Test creation with minimal fields."""
        result = PredictionResult(value="rainy")
        assert result.value == "rainy"
        assert result.horizon is None
        assert result.confidence is None
        assert result.metadata == {}

    # --- Validation Tests ---
    def test_non_integer_horizon_raises(self) -> None:
        """Test that non-integer horizon raises TypeError."""
        with pytest.raises(TypeError, match="must be an integer"):
            PredictionResult(value=100, horizon=3.5)  # type: ignore

    def test_non_positive_horizon_raises(self) -> None:
        """Test that non-positive horizon raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            PredictionResult(value=100, horizon=0)

        with pytest.raises(ValueError, match="must be positive"):
            PredictionResult(value=100, horizon=-5)

    @pytest.mark.parametrize("invalid_confidence", [-0.1, 1.1])
    def test_invalid_confidence_raises(self, invalid_confidence: float) -> None:
        """Test that confidence outside [0,1] raises ValueError."""
        with pytest.raises(ValueError, match="must be between"):
            PredictionResult(value=100, confidence=invalid_confidence)

    def test_invalid_confidence_type_raises(self) -> None:
        """Test that non-numeric confidence raises TypeError."""
        with pytest.raises(TypeError, match="must be int or float"):
            PredictionResult(value=100, confidence="high")  # type: ignore

    # --- Edge Cases ---
    def test_complex_value_types(self) -> None:
        """Test that complex value types are accepted."""
        # Test with dict
        result_dict = PredictionResult(value={"temp": 22.5, "humidity": 0.6})
        assert result_dict.value == {"temp": 22.5, "humidity": 0.6}

        # Test with list
        result_list = PredictionResult(value=[1, 2, 3])
        assert result_list.value == [1, 2, 3]

        # Test with None
        result_none = PredictionResult(value=None)
        assert result_none.value is None

    def test_immutability(self) -> None:
        """Test that fields cannot be modified."""
        result = PredictionResult(value=100)
        with pytest.raises(AttributeError):
            result.value = 200  # type: ignore


def test_import() -> None:
    """Test that the module can be imported correctly."""
    assert PredictionResult.__name__ == "PredictionResult"


def test_frozen_dataclass_behavior() -> None:
    """Test that all dataclasses are frozen (immutable)."""
    result = PredictionResult(value=100)

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
            "--cov=procela.core.assessment.prediction",
            "--cov-report=term-missing",
        ]
    )
