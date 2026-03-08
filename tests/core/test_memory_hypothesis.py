"""Tests for HypothesisState enum and HypothesisRecord dataclass."""

from __future__ import annotations

from dataclasses import is_dataclass
from enum import Enum
from unittest.mock import Mock, patch

import pytest

from procela.core.key_authority import KeyAuthority
from procela.core.memory import HypothesisRecord, HypothesisState, VariableRecord
from procela.symbols.key import Key


def create_record() -> VariableRecord:
    return VariableRecord(value=13.8, confidence=0.96)


class TestHypothesisState:
    """Test suite for HypothesisState enum."""

    def test_enum_is_enum(self) -> None:
        """Test that HypothesisState is an Enum subclass."""
        assert issubclass(HypothesisState, Enum)

    def test_all_members_exist(self) -> None:
        """Test that all expected enum members exist."""
        members = list(HypothesisState)
        member_names = [member.name for member in members]

        expected_names = ["PROPOSED", "VALIDATED", "REJECTED"]
        assert set(member_names) == set(expected_names)
        assert len(members) == 3

    def test_member_values(self) -> None:
        """Test that members have unique auto-generated values."""
        values = [member.value for member in HypothesisState]
        assert len(set(values)) == len(values)
        assert all(isinstance(value, int) for value in values)
        assert sorted(values) == [1, 2, 3]

    def test_member_access(self) -> None:
        """Test accessing enum members by name and value."""
        # Access by name
        assert HypothesisState.PROPOSED.name == "PROPOSED"
        assert HypothesisState.VALIDATED.name == "VALIDATED"
        assert HypothesisState.REJECTED.name == "REJECTED"

        # Access by value
        proposed_value = HypothesisState.PROPOSED.value
        validated_value = HypothesisState.VALIDATED.value
        rejected_value = HypothesisState.REJECTED.value

        assert HypothesisState(proposed_value) is HypothesisState.PROPOSED
        assert HypothesisState(validated_value) is HypothesisState.VALIDATED
        assert HypothesisState(rejected_value) is HypothesisState.REJECTED

    def test_iteration(self) -> None:
        """Test iterating over enum members."""
        members = list(HypothesisState)
        assert len(members) == 3
        assert members[0] is HypothesisState.PROPOSED
        assert members[1] is HypothesisState.VALIDATED
        assert members[2] is HypothesisState.REJECTED


class TestHypothesisRecord:
    """Test suite for HypothesisRecord dataclass."""

    def test_is_dataclass(self) -> None:
        """Test that HypothesisRecord is a dataclass."""
        assert is_dataclass(HypothesisRecord)

    def test_is_frozen(self) -> None:
        """Test that HypothesisRecord is frozen (immutable)."""
        # Create VariableRecord
        record = create_record()

        candidate = HypothesisRecord(state=HypothesisState.PROPOSED, record=record)

        # Should not be able to modify attributes
        with pytest.raises(AttributeError):
            del HypothesisState.VALIDATED
            candidate.record = None

    def test_key(self) -> None:
        """Test the key."""
        record = create_record()

        candidate = HypothesisRecord(state=HypothesisState.VALIDATED, record=record)

        assert isinstance(candidate.key(), Key)

    def test_initialization_with_record(self) -> None:
        """Test initialization with a VariableRecord."""
        record = create_record()

        candidate = HypothesisRecord(state=HypothesisState.VALIDATED, record=record)

        assert candidate.state is HypothesisState.VALIDATED
        assert candidate.record is record

    def test_initialization_with_none_record(self) -> None:
        """Test initialization with None record."""
        candidate = HypothesisRecord(state=HypothesisState.REJECTED, record=None)

        assert candidate.state is HypothesisState.REJECTED
        assert candidate.record is None

    def test_post_init_validation_valid(self) -> None:
        """Test __post_init__ with valid inputs."""
        record = create_record()

        # Should not raise
        candidate = HypothesisRecord(state=HypothesisState.PROPOSED, record=record)

        assert candidate.state is HypothesisState.PROPOSED
        assert candidate.record is record

    def test_post_init_invalid_state(self) -> None:
        """Test __post_init__ raises TypeError for invalid state."""
        record = create_record()

        with pytest.raises(TypeError, match="`state` should be a HypothesisState"):
            HypothesisRecord(state="INVALID_STATE", record=record)

    def test_post_init_invalid_record_type(self) -> None:
        """Test __post_init__ raises TypeError for invalid record type."""
        with pytest.raises(TypeError, match="`record` should be a VariableRecord"):
            HypothesisRecord(
                state=HypothesisState.PROPOSED,
                record="not_a_variable_record",  # String instead of VariableRecord
            )

    def test_key_generation(self) -> None:
        """Test that _key is generated by KeyAuthority."""
        record = create_record()
        key = Mock()

        # Mock KeyAuthority.issue to return a predictable key
        with patch.object(KeyAuthority, "issue", return_value=key) as mock_issue:
            candidate = HypothesisRecord(state=HypothesisState.PROPOSED, record=record)

            # Verify KeyAuthority was called
            mock_issue.assert_called_once_with(candidate)

            # Verify _key attribute was set
            assert candidate._key is key

    def test_key_not_in_repr(self) -> None:
        """Test that _key is excluded from repr."""
        record = create_record()

        candidate = HypothesisRecord(state=HypothesisState.PROPOSED, record=record)

        repr_str = repr(candidate)

        # Should contain class name and fields but not _key
        assert "HypothesisRecord" in repr_str
        assert "state=" in repr_str
        assert "PROPOSED" in repr_str
        assert "record=" in repr_str
        assert "_key=" not in repr_str  # Should be excluded

    def test_equality_with_same_data(self) -> None:
        """Test equality comparison between instances with same data."""
        record1 = create_record()
        record2 = create_record()

        candidate1 = HypothesisRecord(state=HypothesisState.VALIDATED, record=record1)

        candidate2 = HypothesisRecord(state=HypothesisState.VALIDATED, record=record2)

        # Different objects should not be equal
        assert candidate1 != candidate2
        assert candidate1 is not candidate2

        # But they should have the same state
        assert candidate1.state == candidate2.state

    def test_equality_with_none_records(self) -> None:
        """Test equality with None records."""
        candidate1 = HypothesisRecord(state=HypothesisState.REJECTED, record=None)

        candidate2 = HypothesisRecord(state=HypothesisState.REJECTED, record=None)

        # Different objects with same data
        assert candidate1 != candidate2
        assert candidate1.state == candidate2.state
        assert candidate1.record == candidate2.record  # Both None

    def test_dataclass_replace(self) -> None:
        """Test using dataclasses.replace with HypothesisRecord."""
        from dataclasses import replace

        record1 = create_record()
        record2 = create_record()

        original = HypothesisRecord(state=HypothesisState.PROPOSED, record=record1)

        # Create a new instance with different state using replace
        modified = replace(original, state=HypothesisState.VALIDATED)

        assert original.state is HypothesisState.PROPOSED
        assert modified.state is HypothesisState.VALIDATED
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
        proposed = HypothesisRecord(state=HypothesisState.PROPOSED, record=record)

        # After validation passes
        validated = HypothesisRecord(state=HypothesisState.VALIDATED, record=record)

        # After validation fails
        rejected = HypothesisRecord(
            state=HypothesisState.REJECTED,
            record=None,  # Rejected candidates might have no record
        )

        assert proposed.state is HypothesisState.PROPOSED
        assert validated.state is HypothesisState.VALIDATED
        assert rejected.state is HypothesisState.REJECTED


class TestHypothesisRecordEdgeCases:
    """Test edge cases for HypothesisRecord."""

    def test_record_can_be_none_for_rejected(self) -> None:
        """Test that record can be None, especially for REJECTED state."""
        # This should be valid
        candidate = HypothesisRecord(state=HypothesisState.REJECTED, record=None)

        assert candidate.state is HypothesisState.REJECTED
        assert candidate.record is None

    def test_record_can_be_none_for_other_states(self) -> None:
        """Test that record can be None for any state."""
        # Should work for any state
        for state in HypothesisState:
            candidate = HypothesisRecord(state=state, record=None)
            assert candidate.state is state
            assert candidate.record is None


class TestHypothesisRecordIntegration:
    """Integration tests for HypothesisRecord."""

    def test_used_in_resolution_context(self) -> None:
        """Test HypothesisRecord in a resolution context."""

        # Mock a resolution pipeline
        class ResolutionPipeline:
            def __init__(self):
                self.candidates = []

            def add_candidate(self, record, initial_state=HypothesisState.PROPOSED):
                candidate = HypothesisRecord(state=initial_state, record=record)
                self.candidates.append(candidate)
                return candidate

            def validate_candidate(self, candidate):
                if candidate.record is not None:
                    return HypothesisRecord(
                        state=HypothesisState.VALIDATED, record=candidate.record
                    )
                return candidate

        # Test the pipeline
        pipeline = ResolutionPipeline()
        record = create_record()

        # Add proposed candidate
        proposed = pipeline.add_candidate(record)
        assert proposed.state is HypothesisState.PROPOSED

        # Validate it
        validated = pipeline.validate_candidate(proposed)
        assert validated.state is HypothesisState.VALIDATED
        assert validated.record is record

    def test_pattern_matching_usage(self) -> None:
        """Test HypothesisRecord usage with pattern matching."""
        record = create_record()

        candidate = HypothesisRecord(state=HypothesisState.VALIDATED, record=record)

        # Test with if-elif (since match-case requires Python 3.10+)
        if candidate.state is HypothesisState.PROPOSED:
            action = "queue_for_validation"
        elif candidate.state is HypothesisState.VALIDATED:
            action = "ready_for_resolution"
        elif candidate.state is HypothesisState.REJECTED:
            action = "discard"
        else:
            action = "unknown"

        assert action == "ready_for_resolution"
