"""
Pytest module for procela.core.action.validator.

Achieves 100% coverage for ProposalValidator and ConfidenceThresholdValidator,
testing abstract interface, concrete implementation, edge cases, and error conditions.
"""

from unittest.mock import Mock

import pytest

from procela.core.action import (
    ActionProposal,
    ConfidenceThresholdValidator,
    ProposalStatus,
    ProposalValidator,
)


class TestProposalValidator:
    """Tests for the abstract ProposalValidator base class."""

    def test_abstract_class_cannot_be_instantiated(self) -> None:
        """Test that ProposalValidator cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ProposalValidator()  # type: ignore

    def test_concrete_subclass_must_implement_validate(self) -> None:
        """Test that subclasses must implement the validate method."""

        class IncompleteValidator(ProposalValidator):
            pass  # Doesn't implement validate

        with pytest.raises(TypeError):
            IncompleteValidator()

    def test_concrete_subclass_with_validate_works(self) -> None:
        """Test that a subclass implementing validate can be instantiated."""

        class ConcreteValidator(ProposalValidator):
            def validate(self, proposal):
                return True

        validator = ConcreteValidator()
        assert isinstance(validator, ProposalValidator)
        assert validator.validate(None) is True  # type: ignore


class TestConfidenceThresholdValidator:
    """Comprehensive tests for ConfidenceThresholdValidator."""

    # --- Test Initialization ---
    @pytest.mark.parametrize("valid_threshold", [0.0, 0.5, 1.0, 0.001, 0.999])
    def test_init_valid_thresholds(self, valid_threshold: float) -> None:
        """Validator accepts threshold values in range [0.0, 1.0]."""
        validator = ConfidenceThresholdValidator(threshold=valid_threshold)
        assert validator.threshold == float(valid_threshold)

    @pytest.mark.parametrize("invalid_threshold", [-0.1, 1.1, -5.0, 2.0])
    def test_init_invalid_threshold_raises_valueerror(
        self, invalid_threshold: float
    ) -> None:
        """Validator raises ValueError for thresholds outside [0.0, 1.0]."""
        with pytest.raises(ValueError, match="must be between"):
            ConfidenceThresholdValidator(threshold=invalid_threshold)

    def test_init_invalid_threshold_type_raises_typeerror(self) -> None:
        """Validator raises TypeError for non-numeric thresholds."""
        with pytest.raises(TypeError, match="must be int or float"):
            ConfidenceThresholdValidator(threshold="high")  # type: ignore

    def test_init_converts_int_to_float(self) -> None:
        """Validator converts integer thresholds to float."""
        validator = ConfidenceThresholdValidator(threshold=1)  # int
        assert validator.threshold == 1.0
        assert isinstance(validator.threshold, float)

    # --- Test Validation Logic ---
    @pytest.mark.parametrize(
        "confidence, threshold, expected",
        [
            (0.8, 0.5, True),  # Confidence above threshold
            (0.8, 0.8, True),  # Confidence equal to threshold
            (0.3, 0.5, False),  # Confidence below threshold
            (1.0, 0.0, True),  # Max confidence, min threshold
            (0.0, 0.0, True),  # Min confidence, min threshold
            (0.0, 0.1, False),  # Min confidence above threshold
        ],
    )
    def test_validate_confidence_comparisons(
        self, confidence: float, threshold: float, expected: bool
    ) -> None:
        """Test various confidence-threshold comparison scenarios."""
        validator = ConfidenceThresholdValidator(threshold=threshold)
        proposal = ActionProposal(value="test", confidence=confidence)
        result = validator.validate(proposal)
        assert result == expected

    # --- Test Validate with Full Proposal ---
    def test_validate_ignores_other_proposal_attributes(self) -> None:
        """Validation should only depend on confidence, not other attributes."""
        validator = ConfidenceThresholdValidator(threshold=0.7)
        # Create proposals with different attributes but same confidence
        prop1 = ActionProposal(
            value=100,
            confidence=0.8,
            action="action1",
            rationale="Reason 1",
            status=ProposalStatus.PROPOSED,
        )
        prop2 = ActionProposal(
            value="different",
            confidence=0.8,
            action="action2",
            rationale="Reason 2",
            status=ProposalStatus.VALIDATED,
        )
        # Both should validate successfully despite other differences
        assert validator.validate(prop1) is True
        assert validator.validate(prop2) is True

    # --- Test Error Handling in Validate ---
    def test_validate_non_proposal_raises_typeerror(self) -> None:
        """validate() raises TypeError if input is not an ActionProposal."""
        validator = ConfidenceThresholdValidator(threshold=0.5)
        with pytest.raises(TypeError, match="must be an ActionProposal"):
            validator.validate("not a proposal")  # type: ignore
        with pytest.raises(TypeError, match="must be an ActionProposal"):
            validator.validate(None)  # type: ignore
        with pytest.raises(TypeError, match="must be an ActionProposal"):
            validator.validate({"confidence": 0.5})  # type: ignore

    def test_validate_proposal_with_none_confidence_raises(self) -> None:
        """validate() raises TypeError if proposal.confidence is None."""
        validator = ConfidenceThresholdValidator(threshold=0.5)
        # Create a mock proposal with None confidence
        mock_proposal = Mock(spec=ActionProposal)
        mock_proposal.confidence = None
        with pytest.raises(TypeError, match="must be numeric"):
            validator.validate(mock_proposal)

    def test_validate_proposal_with_non_numeric_confidence_raises(self) -> None:
        """validate() raises TypeError if confidence is not numeric."""
        validator = ConfidenceThresholdValidator(threshold=0.5)
        # Create a mock proposal with string confidence
        mock_proposal = Mock(spec=ActionProposal)
        mock_proposal.confidence = "very confident"  # type: ignore
        with pytest.raises(TypeError, match="must be numeric"):
            validator.validate(mock_proposal)

    def test_validate_proposal_with_out_of_range_confidence_raises(self) -> None:
        """validate() raises ValueError if confidence is outside [0,1]."""
        validator = ConfidenceThresholdValidator(threshold=0.5)
        # Create a mock proposal with invalid confidence
        mock_proposal = Mock(spec=ActionProposal)
        mock_proposal.confidence = 1.5  # Outside valid range
        with pytest.raises(ValueError, match="must be between"):
            validator.validate(mock_proposal)

    # --- Test Edge Cases ---
    def test_threshold_at_exact_boundary(self) -> None:
        """Test validation when confidence is exactly at threshold boundary."""
        validator = ConfidenceThresholdValidator(threshold=0.75)
        # Test exact match
        exact_proposal = ActionProposal(value="exact", confidence=0.75)
        assert validator.validate(exact_proposal) is True
        # Test just below
        below_proposal = ActionProposal(value="below", confidence=0.749999)
        assert validator.validate(below_proposal) is False
        # Test just above
        above_proposal = ActionProposal(value="above", confidence=0.750001)
        assert validator.validate(above_proposal) is True

    def test_float_precision_handling(self) -> None:
        """Test that floating-point precision doesn't break comparisons."""
        validator = ConfidenceThresholdValidator(threshold=0.1 + 0.2)  # ~0.3
        # 0.1 + 0.2 is not exactly 0.3 in floating point
        proposal = ActionProposal(value="test", confidence=0.3)
        # Both values have same floating point representation issue
        result = validator.validate(proposal)
        # The comparison should work correctly despite precision issues
        assert result is False  # 0.3 >= (0.1 + 0.2)

    # --- Test Property Access ---
    def test_threshold_property_is_readable(self) -> None:
        """Test that the threshold attribute can be read after initialization."""
        validator = ConfidenceThresholdValidator(threshold=0.42)
        assert validator.threshold == 0.42


# --- Integration and Smoke Tests ---
def test_import() -> None:
    """Test that the module can be imported correctly."""
    from procela.core.action.validator import (
        ConfidenceThresholdValidator,
        ProposalValidator,
    )

    assert ProposalValidator.__name__ == "ProposalValidator"
    assert ConfidenceThresholdValidator.__name__ == "ConfidenceThresholdValidator"


def test_validator_inheritance() -> None:
    """Verify ConfidenceThresholdValidator is a subclass of ProposalValidator."""
    validator = ConfidenceThresholdValidator(threshold=0.5)
    assert isinstance(validator, ProposalValidator)
    assert hasattr(validator, "validate")
    assert callable(validator.validate)


def test_integration_with_real_proposal() -> None:
    """Integration test with actual ActionProposal from the proposal module."""
    from procela.core.action.proposal import ActionProposal

    validator = ConfidenceThresholdValidator(threshold=0.8)
    proposal = ActionProposal(
        value={"temperature": 22.5},
        confidence=0.85,
        action="adjust",
        rationale="Maintain setpoint",
    )
    result = validator.validate(proposal)
    assert result is True


if __name__ == "__main__":
    # Run tests directly with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.action.validator",
            "--cov-report=term-missing",
        ]
    )
