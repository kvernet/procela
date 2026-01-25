"""Pytest module for procela.core.assessment.diagnosis."""

import pytest

from procela.core.assessment import DiagnosisResult


class TestDiagnosisResult:
    """Tests for the DiagnosisResult dataclass."""

    def test_basic_initialization(self) -> None:
        """Test basic creation."""
        result = DiagnosisResult(
            causes=["Sensor fault", "Calibration drift"],
            confidence=0.75,
            metadata={"method": "fault_tree"},
        )
        assert result.causes == ["Sensor fault", "Calibration drift"]
        assert result.confidence == 0.75
        assert result.metadata == {"method": "fault_tree"}

    def test_empty_causes(self) -> None:
        """Test creation with empty causes list."""
        result = DiagnosisResult(causes=[])
        assert result.causes == []
        assert result.confidence is None
        assert result.metadata == {}

    # --- Validation Tests ---
    def test_non_list_causes_raises(self) -> None:
        """Test that non-list causes raises TypeError."""
        with pytest.raises(TypeError, match="must be a list"):
            DiagnosisResult(causes="Sensor fault")  # type: ignore

    def test_non_string_cause_raises(self) -> None:
        """Test that non-string cause raises TypeError."""
        with pytest.raises(TypeError, match="must be strings"):
            DiagnosisResult(causes=[123, "Sensor fault"])  # type: ignore

    @pytest.mark.parametrize("invalid_confidence", [-0.1, 1.1, -5.0, 2.0])
    def test_invalid_confidence_raises(self, invalid_confidence: float) -> None:
        """Test that confidence outside [0,1] raises ValueError."""
        with pytest.raises(ValueError, match="must be between"):
            DiagnosisResult(
                causes=["Sensor fault"],
                confidence=invalid_confidence,
            )

    def test_invalid_confidence_type_raises(self) -> None:
        """Test that non-numeric confidence raises TypeError."""
        with pytest.raises(TypeError, match="must be int or float"):
            DiagnosisResult(
                causes=["Sensor fault"],
                confidence="high",  # type: ignore
            )

    # --- Edge Cases ---
    def test_immutability(self) -> None:
        """Test that fields cannot be modified."""
        result = DiagnosisResult(causes=["Cause"])
        with pytest.raises(AttributeError):
            result.causes = ["New cause"]  # type: ignore


def test_import() -> None:
    """Test that the module can be imported correctly."""
    assert DiagnosisResult.__name__ == "DiagnosisResult"


def test_frozen_dataclass_behavior() -> None:
    """Test that all dataclasses are frozen (immutable)."""
    dr = DiagnosisResult(causes=["cause"])

    # Verify all are immutable
    with pytest.raises(AttributeError):
        # Try to modify a field
        dr.__dict__["_dummy"] = "test"  # type: ignore


if __name__ == "__main__":
    # Run tests directly with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.assessment.diagnosis",
            "--cov-report=term-missing",
        ]
    )
