"""Tests for CandidateState enum and CandidateRecord dataclass."""

from __future__ import annotations

from dataclasses import is_dataclass
from enum import Enum
from unittest.mock import Mock, patch

import pytest

from procela.core.key_authority import KeyAuthority
from procela.core.memory import CandidateRecord, CandidateState, VariableRecord
from procela.symbols.key import Key


def create_record() -> VariableRecord:
    return VariableRecord(value=13.8, confidence=0.96)


class TestCandidateState:
    """Test suite for CandidateState enum."""

    def test_enum_is_enum(self) -> None:
        """Test that CandidateState is an Enum subclass."""
        assert issubclass(CandidateState, Enum)

    def test_all_members_exist(self) -> None:
        """Test that all expected enum members exist."""
        members = list(CandidateState)
        member_names = [member.name for member in members]

        expected_names = ["PROPOSED", "VALIDATED", "REJECTED"]
        assert set(member_names) == set(expected_names)
        assert len(members) == 3

    def test_member_values(self) -> None:
        """Test that members have unique auto-generated values."""
        values = [member.value for member in CandidateState]
        assert len(set(values)) == len(values)
        assert all(isinstance(value, int) for value in values)
        assert sorted(values) == [1, 2, 3]

    def test_member_access(self) -> None:
        """Test accessing enum members by name and value."""
        # Access by name
        assert CandidateState.PROPOSED.name == "PROPOSED"
        assert CandidateState.VALIDATED.name == "VALIDATED"
        assert CandidateState.REJECTED.name == "REJECTED"

        # Access by value
        proposed_value = CandidateState.PROPOSED.value
        validated_value = CandidateState.VALIDATED.value
        rejected_value = CandidateState.REJECTED.value

        assert CandidateState(proposed_value) is CandidateState.PROPOSED
        assert CandidateState(validated_value) is CandidateState.VALIDATED
        assert CandidateState(rejected_value) is CandidateState.REJECTED

    def test_iteration(self) -> None:
        """Test iterating over enum members."""
        members = list(CandidateState)
        assert len(members) == 3
        assert members[0] is CandidateState.PROPOSED
        assert members[1] is CandidateState.VALIDATED
        assert members[2] is CandidateState.REJECTED


class TestCandidateRecord:
    """Test suite for CandidateRecord dataclass."""

    def test_is_dataclass(self) -> None:
        """Test that CandidateRecord is a dataclass."""
        assert is_dataclass(CandidateRecord)

    def test_is_frozen(self) -> None:
        """Test that CandidateRecord is frozen (immutable)."""
        # Create VariableRecord
        record = create_record()

        candidate = CandidateRecord(state=CandidateState.PROPOSED, record=record)

        # Should not be able to modify attributes
        with pytest.raises(AttributeError):
            del CandidateState.VALIDATED
            candidate.record = None

    def test_key(self) -> None:
        """Test the key."""
        record = create_record()

        candidate = CandidateRecord(state=CandidateState.VALIDATED, record=record)

        assert isinstance(candidate.key(), Key)

    def test_initialization_with_record(self) -> None:
        """Test initialization with a VariableRecord."""
        record = create_record()

        candidate = CandidateRecord(state=CandidateState.VALIDATED, record=record)

        assert candidate.state is CandidateState.VALIDATED
        assert candidate.record is record

    def test_initialization_with_none_record(self) -> None:
        """Test initialization with None record."""
        candidate = CandidateRecord(state=CandidateState.REJECTED, record=None)

        assert candidate.state is CandidateState.REJECTED
        assert candidate.record is None

    def test_post_init_validation_valid(self) -> None:
        """Test __post_init__ with valid inputs."""
        record = create_record()

        # Should not raise
        candidate = CandidateRecord(state=CandidateState.PROPOSED, record=record)

        assert candidate.state is CandidateState.PROPOSED
        assert candidate.record is record

    def test_post_init_invalid_state(self) -> None:
        """Test __post_init__ raises TypeError for invalid state."""
        record = create_record()

        with pytest.raises(TypeError, match="`state` should be a CandidateState"):
            CandidateRecord(state="INVALID_STATE", record=record)

    def test_post_init_invalid_record_type(self) -> None:
        """Test __post_init__ raises TypeError for invalid record type."""
        with pytest.raises(TypeError, match="`record` should be a VariableRecord"):
            CandidateRecord(
                state=CandidateState.PROPOSED,
                record="not_a_variable_record",  # String instead of VariableRecord
            )

    def test_key_generation(self) -> None:
        """Test that _key is generated by KeyAuthority."""
        record = create_record()
        key = Mock()

        # Mock KeyAuthority.issue to return a predictable key
        with patch.object(KeyAuthority, "issue", return_value=key) as mock_issue:
            candidate = CandidateRecord(state=CandidateState.PROPOSED, record=record)

            # Verify KeyAuthority was called
            mock_issue.assert_called_once_with(candidate)

            # Verify _key attribute was set
            assert candidate._key is key

    def test_key_not_in_repr(self) -> None:
        """Test that _key is excluded from repr."""
        record = create_record()

        candidate = CandidateRecord(state=CandidateState.PROPOSED, record=record)

        repr_str = repr(candidate)

        # Should contain class name and fields but not _key
        assert "CandidateRecord" in repr_str
        assert "state=" in repr_str
        assert "PROPOSED" in repr_str
        assert "record=" in repr_str
        assert "_key=" not in repr_str  # Should be excluded

    def test_equality_with_same_data(self) -> None:
        """Test equality comparison between instances with same data."""
        record1 = create_record()
        record2 = create_record()

        candidate1 = CandidateRecord(state=CandidateState.VALIDATED, record=record1)

        candidate2 = CandidateRecord(state=CandidateState.VALIDATED, record=record2)

        # Different objects should not be equal
        assert candidate1 != candidate2
        assert candidate1 is not candidate2

        # But they should have the same state
        assert candidate1.state == candidate2.state

    def test_equality_with_none_records(self) -> None:
        """Test equality with None records."""
        candidate1 = CandidateRecord(state=CandidateState.REJECTED, record=None)

        candidate2 = CandidateRecord(state=CandidateState.REJECTED, record=None)

        # Different objects with same data
        assert candidate1 != candidate2
        assert candidate1.state == candidate2.state
        assert candidate1.record == candidate2.record  # Both None

    def test_dataclass_replace(self) -> None:
        """Test using dataclasses.replace with CandidateRecord."""
        from dataclasses import replace

        record1 = create_record()
        record2 = create_record()

        original = CandidateRecord(state=CandidateState.PROPOSED, record=record1)

        # Create a new instance with different state using replace
        modified = replace(original, state=CandidateState.VALIDATED)

        assert original.state is CandidateState.PROPOSED
        assert modified.state is CandidateState.VALIDATED
        assert original.record is record1
        assert modified.record is record1

        # Create instance with different record
        modified2 = replace(original, record=record2)
        assert original.record is record1
        assert modified2.record is record2

    def test_state_transition_pattern(self) -> None:
        """Test typical state transition usage pattern."""
        record = create_record()

        # Simulate state transitions
        proposed = CandidateRecord(state=CandidateState.PROPOSED, record=record)

        # After validation passes
        validated = CandidateRecord(state=CandidateState.VALIDATED, record=record)

        # After validation fails
        rejected = CandidateRecord(
            state=CandidateState.REJECTED,
            record=None,  # Rejected candidates might have no record
        )

        assert proposed.state is CandidateState.PROPOSED
        assert validated.state is CandidateState.VALIDATED
        assert rejected.state is CandidateState.REJECTED


class TestCandidateRecordEdgeCases:
    """Test edge cases for CandidateRecord."""

    def test_record_can_be_none_for_rejected(self) -> None:
        """Test that record can be None, especially for REJECTED state."""
        # This should be valid
        candidate = CandidateRecord(state=CandidateState.REJECTED, record=None)

        assert candidate.state is CandidateState.REJECTED
        assert candidate.record is None

    def test_record_can_be_none_for_other_states(self) -> None:
        """Test that record can be None for any state."""
        # Should work for any state
        for state in CandidateState:
            candidate = CandidateRecord(state=state, record=None)
            assert candidate.state is state
            assert candidate.record is None


class TestCandidateRecordIntegration:
    """Integration tests for CandidateRecord."""

    def test_used_in_resolution_context(self) -> None:
        """Test CandidateRecord in a resolution context."""

        # Mock a resolution pipeline
        class ResolutionPipeline:
            def __init__(self):
                self.candidates = []

            def add_candidate(self, record, initial_state=CandidateState.PROPOSED):
                candidate = CandidateRecord(state=initial_state, record=record)
                self.candidates.append(candidate)
                return candidate

            def validate_candidate(self, candidate):
                if candidate.record is not None:
                    return CandidateRecord(
                        state=CandidateState.VALIDATED, record=candidate.record
                    )
                return candidate

        # Test the pipeline
        pipeline = ResolutionPipeline()
        record = create_record()

        # Add proposed candidate
        proposed = pipeline.add_candidate(record)
        assert proposed.state is CandidateState.PROPOSED

        # Validate it
        validated = pipeline.validate_candidate(proposed)
        assert validated.state is CandidateState.VALIDATED
        assert validated.record is record

    def test_pattern_matching_usage(self) -> None:
        """Test CandidateRecord usage with pattern matching."""
        record = create_record()

        candidate = CandidateRecord(state=CandidateState.VALIDATED, record=record)

        # Test with if-elif (since match-case requires Python 3.10+)
        if candidate.state is CandidateState.PROPOSED:
            action = "queue_for_validation"
        elif candidate.state is CandidateState.VALIDATED:
            action = "ready_for_resolution"
        elif candidate.state is CandidateState.REJECTED:
            action = "discard"
        else:
            action = "unknown"

        assert action == "ready_for_resolution"
