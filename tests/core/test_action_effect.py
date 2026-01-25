"""
Pytest module for procela.core.action.effect.

Aims for 100% coverage of the ActionEffect class, testing initialization,
validation, immutability, and dataclass behaviors.
"""

import pytest

from procela.core.action import ActionEffect


class TestActionEffect:
    """Test suite for the ActionEffect dataclass."""

    # --- Test Basic Initialization & Properties ---
    def test_init_minimal(self) -> None:
        """Test creation with only the required description field."""
        effect = ActionEffect(description="Minimal test effect")
        assert effect.description == "Minimal test effect"
        assert effect.expected_outcome is None
        assert effect.confidence is None

    def test_init_with_all_fields(self) -> None:
        """Test creation with all fields provided."""
        expected = {"result": "success"}
        effect = ActionEffect(
            description="Full effect", expected_outcome=expected, confidence=0.95
        )
        assert effect.description == "Full effect"
        assert effect.expected_outcome == expected
        assert effect.confidence == 0.95

    @pytest.mark.parametrize("confidence", [0.0, 0.5, 1.0, 0.999])
    def test_init_valid_confidence_boundaries(self, confidence: float) -> None:
        """Test confidence accepts valid boundary and intermediate values."""
        effect = ActionEffect(description="Boundary test", confidence=confidence)
        assert effect.confidence == confidence

    # --- Test Validation in __post_init__ ---
    @pytest.mark.parametrize("invalid_confidence", [-0.1, 1.1, -5.0, 2.5])
    def test_init_invalid_confidence_raises(self, invalid_confidence: float) -> None:
        """Test that confidence outside [0.0, 1.0] raises ValueError."""
        with pytest.raises(ValueError, match="must be between"):
            ActionEffect(description="Invalid", confidence=invalid_confidence)

    def test_init_invalid_confidence_type_raises(self) -> None:
        """Test that non-numeric confidence raises TypeError."""
        with pytest.raises(TypeError, match="must be int or float"):
            ActionEffect(description="Invalid", confidence="high")  # type: ignore

    # --- Test Frozen (Immutable) Behavior ---
    def test_immutability_assignment_raises(self) -> None:
        """Test that fields cannot be modified (frozen dataclass)."""
        effect = ActionEffect(description="Immutable test")
        with pytest.raises(AttributeError):
            effect.description = "A new description"  # type: ignore

    # --- Test Dataclass Features ---
    def test_equality(self) -> None:
        """Test that two effects with same data are equal."""
        effect1 = ActionEffect(description="Same", expected_outcome=42, confidence=0.8)
        effect2 = ActionEffect(description="Same", expected_outcome=42, confidence=0.8)
        assert effect1 == effect2
        # Also test hash equality for use in sets/dicts
        assert hash(effect1) == hash(effect2)

    def test_inequality(self) -> None:
        """Test that effects with different data are not equal."""
        base = ActionEffect(description="Test", confidence=0.5)
        different = ActionEffect(description="Test", confidence=0.7)
        assert base != different

    def test_repr_contains_info(self) -> None:
        """Test the string representation includes all fields."""
        effect = ActionEffect(
            description="Test repr", expected_outcome=[1, 2, 3], confidence=0.3
        )
        repr_str = repr(effect)
        assert "Test repr" in repr_str
        assert "expected_outcome=[1, 2, 3]" in repr_str
        assert "confidence=0.3" in repr_str

    # --- Test Edge Cases & Type Flexibility ---
    def test_expected_outcome_various_types(self) -> None:
        """Test that expected_outcome can handle diverse types."""
        # Test with integer
        effect_int = ActionEffect(description="Int", expected_outcome=100)
        assert effect_int.expected_outcome == 100

        # Test with custom object
        class CustomOutcome:
            pass

        custom_obj = CustomOutcome()
        effect_custom = ActionEffect(description="Custom", expected_outcome=custom_obj)
        assert effect_custom.expected_outcome is custom_obj
        # Test with None
        effect_none = ActionEffect(description="None", expected_outcome=None)
        assert effect_none.expected_outcome is None


# --- Code Coverage Boilerplate & Integration Test ---
def test_import() -> None:
    """Simple test to ensure the module can be imported correctly."""
    from procela.core.action.effect import ActionEffect

    assert ActionEffect.__name__ == "ActionEffect"


if __name__ == "__main__":
    # This allows running the tests directly for quick verification.
    pytest.main([__file__, "-v", "--tb=short", "--cov=procela.core.action.effect"])
