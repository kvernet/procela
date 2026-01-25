"""
Pytest module for procela.core.action.proposal.

Achieves 100% coverage for ProposalStatus and ActionProposal,
testing initialization, validation, immutability, the with_status method,
and all edge cases.
"""

from datetime import datetime, timezone
from typing import Any

import pytest

from procela.core.action import (
    ActionEffect,
    ActionProposal,
    ProposalStatus,
)
from procela.symbols.key import Key


class TestProposalStatus:
    """Tests for the ProposalStatus enumeration."""

    def test_enum_values(self) -> None:
        """Test that all enum members have correct string values."""
        assert ProposalStatus.PROPOSED.value == "proposed"
        assert ProposalStatus.VALIDATED.value == "validated"
        assert ProposalStatus.SELECTED.value == "selected"
        assert ProposalStatus.EXECUTING.value == "executing"
        assert ProposalStatus.COMPLETED.value == "completed"
        assert ProposalStatus.REJECTED.value == "rejected"
        assert ProposalStatus.CANCELED.value == "canceled"

    def test_enum_iteration(self) -> None:
        """Test the enum can be iterated and has the correct number of members."""
        members = list(ProposalStatus)
        assert len(members) == 7
        assert all(isinstance(m, ProposalStatus) for m in members)

    def test_enum_comparison(self) -> None:
        """Test equality and identity comparisons between enum members."""
        assert ProposalStatus.PROPOSED is ProposalStatus.PROPOSED
        assert ProposalStatus.PROPOSED == ProposalStatus.PROPOSED
        assert ProposalStatus.PROPOSED != ProposalStatus.COMPLETED


class TestActionProposal:
    """Comprehensive tests for the ActionProposal dataclass."""

    # --- Test Basic Initialization & Defaults ---
    def test_minimal_initialization(self) -> None:
        """Test creation with only required fields (value and confidence)."""
        proposal = ActionProposal(value=100, confidence=0.75)
        assert proposal.value == 100
        assert proposal.confidence == 0.75
        assert proposal.status == ProposalStatus.PROPOSED
        assert proposal.timestamp is not None
        assert isinstance(proposal.timestamp, datetime)
        assert proposal.timestamp.tzinfo is not None  # Should be timezone-aware

    def test_full_initialization(self) -> None:
        """Test creation with all fields provided."""
        test_key = Key()
        test_effect = ActionEffect(description="Test effect")
        test_time = datetime(2025, 1, 12, 12, 0, 0, tzinfo=timezone.utc)
        test_metadata = {"priority": "high", "cost": 50}

        proposal = ActionProposal(
            value={"temperature": 22.5},
            confidence=0.92,
            source=test_key,
            action="set_value",
            rationale="Optimization cycle #42",
            effect=test_effect,
            metadata=test_metadata,
            timestamp=test_time,
            status=ProposalStatus.VALIDATED,
        )

        assert proposal.value == {"temperature": 22.5}
        assert proposal.confidence == 0.92
        assert proposal.source == test_key
        assert proposal.action == "set_value"
        assert proposal.rationale == "Optimization cycle #42"
        assert proposal.effect == test_effect
        assert proposal.metadata == test_metadata
        assert proposal.timestamp == test_time
        assert proposal.status == ProposalStatus.VALIDATED

    # --- Test __post_init__ Validation ---
    @pytest.mark.parametrize("valid_confidence", [0.0, 0.5, 1.0, 0.001, 0.999])
    def test_valid_confidence_boundaries(self, valid_confidence: float) -> None:
        """Test that confidence accepts values in [0.0, 1.0] inclusive."""
        proposal = ActionProposal(value=0, confidence=valid_confidence)
        assert proposal.confidence == valid_confidence

    @pytest.mark.parametrize("invalid_confidence", [-0.1, 1.1, -5.0, 2.0])
    def test_invalid_confidence_raises_valueerror(
        self, invalid_confidence: float
    ) -> None:
        """Test that confidence outside [0.0, 1.0] raises ValueError."""
        with pytest.raises(ValueError, match="must be between"):
            ActionProposal(value=0, confidence=invalid_confidence)

    def test_invalid_confidence_type_raises_typeerror(self) -> None:
        """Test that non-numeric confidence raises TypeError."""
        with pytest.raises(TypeError, match="must be int or float"):
            ActionProposal(value=0, confidence="high")  # type: ignore

    def test_invalid_timestamp_type_raises_typeerror(self) -> None:
        """Test that non-datetime timestamp raises TypeError."""
        with pytest.raises(TypeError, match="must be a datetime"):
            ActionProposal(value=0, confidence=0.5, timestamp="2025-01-01")  # type: ignore

    def test_invalid_status_type_raises_typeerror(self) -> None:
        """Test that non-ProposalStatus status raises TypeError."""
        with pytest.raises(TypeError, match="must be a ProposalStatus"):
            ActionProposal(value=0, confidence=0.5, status="invalid_status")  # type: ignore

    def test_naive_timestamp_gets_timezone(self) -> None:
        """Test that a naive datetime gets assigned UTC timezone."""
        naive_time = datetime(2025, 1, 1, 12, 0, 0)
        proposal = ActionProposal(value=0, confidence=0.5, timestamp=naive_time)
        assert proposal.timestamp.tzinfo is timezone.utc
        assert proposal.timestamp.replace(tzinfo=None) == naive_time

    # --- Test with_status Method ---
    def test_with_status_creates_new_instance(self) -> None:
        """Test that with_status returns a new instance with updated status."""
        original = ActionProposal(
            value=10, confidence=0.8, status=ProposalStatus.PROPOSED
        )
        new = original.with_status(ProposalStatus.SELECTED)

        # Verify it's a new object
        assert original is not new
        # Verify status changed
        assert new.status == ProposalStatus.SELECTED
        assert original.status == ProposalStatus.PROPOSED
        # Verify other fields are equal
        assert new.value == original.value
        assert new.confidence == original.confidence
        assert new.timestamp == original.timestamp

    def test_with_status_invalid_status_raises(self) -> None:
        """Test that with_status rejects non-ProposalStatus arguments."""
        proposal = ActionProposal(value=0, confidence=0.5)
        with pytest.raises(TypeError, match="must be a ProposalStatus"):
            proposal.with_status("invalid_status")  # type: ignore

    @pytest.mark.parametrize("target_status", list(ProposalStatus))
    def test_with_status_all_enum_values(self, target_status: ProposalStatus) -> None:
        """Test with_status works for every possible ProposalStatus value."""
        original = ActionProposal(value="test", confidence=0.3)
        new = original.with_status(target_status)
        assert new.status == target_status

    # --- Test Frozen (Immutable) Behavior ---
    def test_immutability_assignment_raises(self) -> None:
        """Test that fields cannot be modified (frozen dataclass)."""
        proposal = ActionProposal(value=5, confidence=0.5)
        with pytest.raises(AttributeError):
            proposal.value = 10  # type: ignore
        with pytest.raises(AttributeError):
            proposal.status = ProposalStatus.COMPLETED  # type: ignore

    # --- Test Dataclass Features ---
    def test_equality_and_hash(self) -> None:
        """Test that two proposals with same data are equal and have same hash."""
        effect = ActionEffect(description="Same")
        time = datetime.now(timezone.utc)

        prop1 = ActionProposal(
            value=100,
            confidence=0.9,
            effect=effect,
            timestamp=time,
            status=ProposalStatus.PROPOSED,
        )
        prop2 = ActionProposal(
            value=100,
            confidence=0.9,
            effect=effect,
            timestamp=time,
            status=ProposalStatus.PROPOSED,
        )

        assert prop1 == prop2
        assert hash(prop1) == hash(prop2)

    def test_inequality(self) -> None:
        """Test that proposals with different data are not equal."""
        base = ActionProposal(value=100, confidence=0.9)
        different = ActionProposal(value=200, confidence=0.9)
        assert base != different

    # --- Test Flexible Value Field ---
    @pytest.mark.parametrize("value", [42, "string", {"key": "value"}, [1, 2, 3], None])
    def test_value_accepts_any_type(self, value: Any) -> None:
        """Test that the 'value' field can hold various types."""
        proposal = ActionProposal(value=value, confidence=0.5)
        assert proposal.value == value

    # --- Test Timestamp Default Factory ---
    def test_default_timestamp_is_utc_now(self) -> None:
        """Test that default timestamp is roughly 'now' in UTC."""
        before = datetime.now(timezone.utc)
        proposal = ActionProposal(value=0, confidence=0.5)
        after = datetime.now(timezone.utc)

        assert before <= proposal.timestamp <= after
        assert proposal.timestamp.tzinfo == timezone.utc

    def test_custom_timestamp_preserved(self) -> None:
        """Test that explicitly provided timestamp is used, not default."""
        custom_time = datetime(2024, 6, 15, 10, 30, 0, tzinfo=timezone.utc)
        proposal = ActionProposal(value=0, confidence=0.5, timestamp=custom_time)
        assert proposal.timestamp == custom_time


# --- Integration Tests ---
def test_import() -> None:
    """Test that the module can be imported correctly."""
    from procela.core.action.proposal import ActionProposal, ProposalStatus

    assert ActionProposal.__name__ == "ActionProposal"
    assert ProposalStatus.__name__ == "ProposalStatus"


def test_proposal_with_effect_integration() -> None:
    """Integration test with ActionEffect."""
    from procela.core.action.effect import ActionEffect

    effect = ActionEffect(
        description="Increase pressure",
        expected_outcome={"pressure_psi": 150},
        confidence=0.85,
    )
    proposal = ActionProposal(
        value=150,
        confidence=0.9,
        action="adjust_pressure",
        rationale="Reach target operating range.",
        effect=effect,
    )

    assert proposal.effect is effect
    assert proposal.effect.description == "Increase pressure"


if __name__ == "__main__":
    # Run tests directly with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.action.proposal",
            "--cov-report=term-missing",
        ]
    )
