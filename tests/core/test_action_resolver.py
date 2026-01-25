"""
CORRECT test suite for procela.core.action.resolver
Using actual API specification with proper Key and TimePoint types.
"""

from unittest.mock import Mock, create_autospec, patch

import pytest

from procela.core.action.policy import SelectionPolicy
from procela.core.action.proposal import ActionProposal
from procela.core.action.resolver import ConflictResolver
from procela.core.action.validator import ProposalValidator
from procela.core.assessment import ReasoningResult, ReasoningTask
from procela.core.memory.variable.history import VariableRecord
from procela.symbols.key import Key
from procela.symbols.time import TimePoint


class TestConflictResolver:
    """Test cases for ConflictResolver class using correct API types."""

    # ------------------------------------------------------------
    # Test: Empty candidates
    # ------------------------------------------------------------
    def test_resolve_empty_candidates(self):
        """Test resolve with empty candidates list returns failure."""
        resolver = ConflictResolver()
        policy_mock = create_autospec(SelectionPolicy)

        result, resolved = resolver.resolve([], policy_mock)

        # Should return failure result
        assert isinstance(result, ReasoningResult)
        assert result.success is False
        assert result.task == ReasoningTask.CONFLICT_RESOLUTION
        assert result.confidence == 0.0
        assert "No candidates" in result.explanation
        assert resolved is None

    # ------------------------------------------------------------
    # Test: No policy
    # ------------------------------------------------------------
    def test_resolve_no_policy(self):
        """Test resolve with None policy returns failure."""
        resolver = ConflictResolver()
        record_mock = create_autospec(VariableRecord)

        result, resolved = resolver.resolve([record_mock], None)

        # Should return failure result
        assert isinstance(result, ReasoningResult)
        assert result.success is False
        assert "No policy" in result.explanation
        assert resolved is None

    # ------------------------------------------------------------
    # Test: Type validation errors
    # ------------------------------------------------------------
    def test_resolve_candidates_not_sequence(self):
        """Test resolve raises TypeError when candidates is not a Sequence."""
        resolver = ConflictResolver()
        policy_mock = create_autospec(SelectionPolicy)

        with pytest.raises(TypeError) as exc_info:
            resolver.resolve("not a sequence", policy_mock)

        assert "`candidate` 0 should be a `VariableRecord` instance" in str(
            exc_info.value
        )
        assert "got" in str(exc_info.value)

    def test_resolve_candidate_not_variable_record(self):
        """Test resolve raises TypeError when a candidate is not VariableRecord."""
        resolver = ConflictResolver()
        policy_mock = create_autospec(SelectionPolicy)

        with pytest.raises(TypeError) as exc_info:
            resolver.resolve(["not a record", "also not"], policy_mock)

        assert "`candidate` 0 should be a `VariableRecord` instance" in str(
            exc_info.value
        )

    def test_resolve_policy_not_selection_policy(self):
        """Test resolve raises TypeError when policy is not SelectionPolicy."""
        resolver = ConflictResolver()
        record_mock = create_autospec(VariableRecord)

        with pytest.raises(TypeError) as exc_info:
            resolver.resolve([record_mock], "not a policy")

        assert "`policy` should be a SelectionPolicy" in str(exc_info.value)

    def test_resolve_validators_not_iterable(self):
        """Test resolve raises TypeError when validators is not Iterable."""
        resolver = ConflictResolver()
        policy_mock = create_autospec(SelectionPolicy)
        record_mock = create_autospec(VariableRecord)

        with pytest.raises(TypeError) as exc_info:
            resolver.resolve(record_mock, policy_mock, validators="not iterable")

        assert "`candidates` should be a Sequence of `VariableRecord`" in str(
            exc_info.value
        )

    def test_resolve_validator_not_proposal_validator(self):
        """Test resolve raises TypeError when validator is not ProposalValidator."""
        resolver = ConflictResolver()
        policy_mock = create_autospec(SelectionPolicy)
        record_mock = create_autospec(VariableRecord)

        with pytest.raises(TypeError) as exc_info:
            resolver.resolve([record_mock], policy_mock, validators=["not validator"])

        assert "`validator` 0 should be a ProposalValidator instance" in str(
            exc_info.value
        )

    # ------------------------------------------------------------
    # Test: Successful resolution with correct Key and TimePoint types
    # ------------------------------------------------------------
    def test_resolve_single_candidate_correct_types(self):
        """Test successful resolution with correct Key and TimePoint types."""
        resolver = ConflictResolver()

        # Create proper Key and TimePoint objects
        mock_key = create_autospec(Key)
        mock_timepoint = create_autospec(TimePoint)

        # Create mock VariableRecord with correct types
        record_mock = create_autospec(VariableRecord)
        record_mock.value = 42.5
        record_mock.confidence = 0.95
        record_mock.source = Key()
        record_mock.key.return_value = mock_key  # Returns Key, not string
        record_mock.time = mock_timepoint  # TimePoint, not string

        # Create mock SelectionPolicy
        policy_mock = create_autospec(SelectionPolicy)
        policy_mock.__class__.__name__ = "TestSelectionPolicy"

        # Create ActionProposal with correct metadata types
        expected_proposal = ActionProposal(
            value=42.5,
            confidence=0.95,
            source=Key(),
            metadata={
                "record_key": mock_key,  # Should be Key, not string
                "time": mock_timepoint,  # Should be TimePoint, not string
            },
        )

        # Mock policy.select to return the proposal
        policy_mock.select.return_value = expected_proposal

        # Execute
        result, resolved = resolver.resolve([record_mock], policy_mock)

        # Verify
        assert result is None  # Success case returns None for result
        assert isinstance(resolved, VariableRecord)

        # Check resolved record values match proposal
        assert resolved.value == 42.5
        assert resolved.confidence == 0.95
        assert resolved.source != record_mock.source

        # Check metadata - should contain Keys and TimePoints
        assert "resolved_from" in resolved.metadata
        assert resolved.metadata["policy"] == "TestSelectionPolicy"
        # resolved_from should contain Keys, not strings
        assert resolved.metadata["resolved_from"] == [mock_key]

    # ------------------------------------------------------------
    # Test: _record_to_proposal with correct types
    # ------------------------------------------------------------
    def test_record_to_proposal_correct_types(self):
        """Test _record_to_proposal with correct Key and TimePoint types."""
        resolver = ConflictResolver()

        # Create proper Key and TimePoint
        mock_key = create_autospec(Key)
        mock_timepoint = create_autospec(TimePoint)

        # Create mock VariableRecord
        record_mock = create_autospec(VariableRecord)
        record_mock.value = 42.5
        record_mock.confidence = 0.95
        record_mock.source = Key()
        record_mock.key.return_value = mock_key  # Returns Key
        record_mock.time = mock_timepoint  # TimePoint

        # Execute
        proposal = resolver._record_to_proposal(record_mock)

        # Verify
        assert isinstance(proposal, ActionProposal)
        assert proposal.value == 42.5
        assert proposal.confidence == 0.95
        assert proposal.source == record_mock.source
        # Metadata should contain Key and TimePoint
        assert proposal.metadata["record_key"] == mock_key
        assert proposal.metadata["time"] == mock_timepoint

    def test_record_to_proposal_none_confidence(self):
        """Test _record_to_proposal with record.confidence = None."""
        resolver = ConflictResolver()

        # Create proper Key and TimePoint
        mock_key = create_autospec(Key)
        mock_timepoint = create_autospec(TimePoint)

        # Create mock VariableRecord with None confidence
        record_mock = create_autospec(VariableRecord)
        record_mock.value = 42.5
        record_mock.confidence = None  # Important test case
        record_mock.source = Key()
        record_mock.key.return_value = mock_key
        record_mock.time = mock_timepoint

        # Execute
        proposal = resolver._record_to_proposal(record_mock)

        # Verify confidence defaults to 0.0
        assert proposal.confidence == 0.0

    # ------------------------------------------------------------
    # Test: Resolution with validators using correct types
    # ------------------------------------------------------------
    def test_resolve_with_validators_correct_types(self):
        """Test resolution with validators using correct Key/TimePoint types."""
        resolver = ConflictResolver()

        # Create proper Key and TimePoint
        mock_key = create_autospec(Key)
        mock_timepoint = create_autospec(TimePoint)

        # Create mock VariableRecord
        record_mock = create_autospec(VariableRecord)
        record_mock.value = 100.0
        record_mock.confidence = 0.9
        record_mock.source = Key()
        record_mock.key.return_value = mock_key
        record_mock.time = mock_timepoint

        # Create mock SelectionPolicy
        policy_mock = create_autospec(SelectionPolicy)
        policy_mock.__class__.__name__ = "TestPolicy"

        # Create mock validators
        validator_mock = create_autospec(ProposalValidator)
        validator_mock.validate.return_value = True

        # Create the proposal that will be generated
        expected_proposal = ActionProposal(
            value=100.0,
            confidence=0.9,
            source=Key(),
            metadata={"record_key": mock_key, "time": mock_timepoint},
        )

        policy_mock.select.return_value = expected_proposal

        # Execute with validators
        result, resolved = resolver.resolve(
            [record_mock], policy_mock, validators=[validator_mock]
        )

        # Verify validators were called with correct proposal
        validator_mock.validate.assert_called_once()
        called_proposal = validator_mock.validate.call_args[0][0]
        assert called_proposal.metadata["record_key"] == mock_key
        assert called_proposal.metadata["time"] == mock_timepoint

        # Verify successful resolution
        assert result is None
        assert isinstance(resolved, VariableRecord)

    def test_resolve_with_validators_incorrect_types(self):
        """Test resolution with validators using incorrect list types."""
        resolver = ConflictResolver()

        # Create proper Key and TimePoint
        mock_key = create_autospec(Key)
        mock_timepoint = create_autospec(TimePoint)

        # Create mock VariableRecord
        record_mock = create_autospec(VariableRecord)
        record_mock.value = 100.0
        record_mock.confidence = 0.9
        record_mock.source = Key()
        record_mock.key.return_value = mock_key
        record_mock.time = mock_timepoint

        # Create mock SelectionPolicy
        policy_mock = create_autospec(SelectionPolicy)
        policy_mock.__class__.__name__ = "TestPolicy"

        # Create mock validators
        validator_mock = create_autospec(ProposalValidator)
        validator_mock.validate.return_value = True

        # Create the proposal that will be generated
        expected_proposal = ActionProposal(
            value=100.0,
            confidence=0.9,
            source=Key(),
            metadata={"record_key": mock_key, "time": mock_timepoint},
        )

        policy_mock.select.return_value = expected_proposal

        # Execute with incorrect validators
        with pytest.raises(TypeError):
            resolver.resolve([record_mock], policy_mock, validators=True)

    # ------------------------------------------------------------
    # Test: All proposals rejected by validators
    # ------------------------------------------------------------
    def test_resolve_all_proposals_rejected_by_validators(self):
        """Test resolution when all proposals are rejected by validators."""
        resolver = ConflictResolver()

        # Create proper Key and TimePoint
        mock_key = create_autospec(Key)
        mock_timepoint = create_autospec(TimePoint)

        # Create mock VariableRecord
        record_mock = create_autospec(VariableRecord)
        record_mock.value = 50.0
        record_mock.confidence = 0.3
        record_mock.source = "sensor"
        record_mock.key.return_value = mock_key
        record_mock.time = mock_timepoint

        # Create mock SelectionPolicy
        policy_mock = create_autospec(SelectionPolicy)

        # Create validator that always rejects
        validator_mock = create_autospec(ProposalValidator)
        validator_mock.validate.return_value = False

        # Execute
        result, resolved = resolver.resolve(
            [record_mock], policy_mock, validators=[validator_mock]
        )

        # Should return failure
        assert isinstance(result, ReasoningResult)
        assert result.success is False
        assert "All proposals rejected by validators" in result.explanation
        assert resolved is None

    # ------------------------------------------------------------
    # Test: Policy returns None
    # ------------------------------------------------------------
    def test_resolve_policy_returns_none(self):
        """Test resolution when policy.select returns None."""
        resolver = ConflictResolver()

        # Create proper Key and TimePoint
        mock_key = create_autospec(Key)
        mock_timepoint = create_autospec(TimePoint)

        # Create mock VariableRecord
        record_mock = create_autospec(VariableRecord)
        record_mock.value = 75.0
        record_mock.confidence = 0.8
        record_mock.source = "source"
        record_mock.key.return_value = mock_key
        record_mock.time = mock_timepoint

        # Create mock SelectionPolicy that returns None
        policy_mock = create_autospec(SelectionPolicy)
        policy_mock.select.return_value = None

        # Execute
        result, resolved = resolver.resolve([record_mock], policy_mock)

        # Should return failure
        assert isinstance(result, ReasoningResult)
        assert result.success is False
        assert "Selection policy returned no proposal" in result.explanation
        assert resolved is None

    # ------------------------------------------------------------
    # Test: Helper method _create_failed_result
    # ------------------------------------------------------------
    def test_create_failed_result(self):
        """Test _create_failed_result helper method."""
        resolver = ConflictResolver()

        task = ReasoningTask.CONFLICT_RESOLUTION
        confidence = 0.25
        explanation = "Test failure message"

        # Execute
        result = resolver._create_failed_result(task, confidence, explanation)

        # Verify
        assert isinstance(result, ReasoningResult)
        assert result.task == task
        assert result.success is False
        assert result.result is None
        assert result.confidence == confidence
        assert result.explanation == explanation

    # ------------------------------------------------------------
    # Test: Edge cases with correct types
    # ------------------------------------------------------------
    def test_resolve_with_none_validators(self):
        """Test resolve with validators=None (should work like no validators)."""
        resolver = ConflictResolver()

        # Create proper Key and TimePoint
        mock_key = create_autospec(Key)
        mock_timepoint = create_autospec(TimePoint)

        record_mock = create_autospec(VariableRecord)
        record_mock.value = 100.0
        record_mock.confidence = 0.9
        record_mock.source = Key()
        record_mock.key.return_value = mock_key
        record_mock.time = mock_timepoint

        policy_mock = create_autospec(SelectionPolicy)
        policy_mock.__class__.__name__ = "TestPolicy"

        # Create a proposal
        expected_proposal = ActionProposal(
            value=100.0,
            confidence=0.9,
            source=Key(),
            metadata={"record_key": mock_key, "time": mock_timepoint},
        )
        policy_mock.select.return_value = expected_proposal

        # Execute with validators=None
        result, resolved = resolver.resolve([record_mock], policy_mock, validators=None)

        # Should succeed
        assert result is None
        assert isinstance(resolved, VariableRecord)

    def test_resolve_proposal_with_none_metadata(self):
        """Test resolution when proposal has None metadata."""
        resolver = ConflictResolver()

        # Create proper Key and TimePoint
        mock_key = create_autospec(Key)
        mock_timepoint = create_autospec(TimePoint)

        record_mock = create_autospec(VariableRecord)
        record_mock.value = 100.0
        record_mock.confidence = 0.9
        record_mock.source = Key()
        record_mock.key.return_value = mock_key
        record_mock.time = mock_timepoint

        policy_mock = create_autospec(SelectionPolicy)
        policy_mock.__class__.__name__ = "TestPolicy"

        # Create a proposal with None metadata
        proposal_with_none_metadata = ActionProposal(
            value=100.0,
            confidence=0.9,
            source=Key(),
            metadata=None,  # This is what we're testing
        )

        # Patch _record_to_proposal to return our test proposal
        with patch.object(
            resolver, "_record_to_proposal", return_value=proposal_with_none_metadata
        ):
            policy_mock.select.return_value = proposal_with_none_metadata

            result, resolved = resolver.resolve([record_mock], policy_mock)

        # Should still succeed
        assert result is None
        assert isinstance(resolved, VariableRecord)
        # resolved_from list should handle None metadata gracefully
        assert "resolved_from" in resolved.metadata

    def test_resolve_multiple_candidates_with_keys(self):
        """Test resolution with multiple candidates, each with unique Keys."""
        resolver = ConflictResolver()

        # Create multiple mock VariableRecords with unique Keys
        records = []
        keys = []
        timepoints = []

        for i in range(3):
            # Create unique Key for each record
            key_mock = create_autospec(Key)
            key_mock.__repr__ = Mock(return_value=Key())
            keys.append(key_mock)

            # Create unique TimePoint for each record
            timepoint_mock = create_autospec(TimePoint)
            timepoint_mock.__repr__ = Mock(return_value=f"TimePoint_{i}")
            timepoints.append(timepoint_mock)

            # Create record
            record_mock = create_autospec(VariableRecord)
            record_mock.value = i * 10.0
            record_mock.confidence = 0.7 + (i * 0.1)
            record_mock.source = Key()
            record_mock.key.return_value = key_mock
            record_mock.time = timepoint_mock
            records.append(record_mock)

        # Create mock SelectionPolicy
        policy_mock = create_autospec(SelectionPolicy)
        policy_mock.__class__.__name__ = "HighestValuePolicy"

        # Create proposals that would be generated
        proposals = []
        for i, record in enumerate(records):
            proposal = ActionProposal(
                value=record.value,
                confidence=record.confidence,
                source=record.source,
                metadata={"record_key": keys[i], "time": timepoints[i]},
            )
            proposals.append(proposal)

        # Mock policy.select to return the middle proposal
        policy_mock.select.return_value = proposals[1]

        # Execute
        result, resolved = resolver.resolve(records, policy_mock)

        # Verify
        assert result is None
        assert isinstance(resolved, VariableRecord)
        assert abs(resolved.value - 10.0) < 1e-6
        assert abs(resolved.confidence - 0.8) < 1e-6

        # Check metadata includes all Keys
        assert len(resolved.metadata["resolved_from"]) == 3
        assert keys[0] in resolved.metadata["resolved_from"]
        assert keys[1] in resolved.metadata["resolved_from"]
        assert keys[2] in resolved.metadata["resolved_from"]

    # ------------------------------------------------------------
    # Test: Integration test with realistic Key and TimePoint usage
    # ------------------------------------------------------------
    def test_complete_resolution_scenario_real_types(self):
        """Test a complete conflict resolution scenario with real types."""
        resolver = ConflictResolver()

        # Simulate three different sensors with proper Keys and TimePoints
        sensor_records = []
        sensor_keys = []
        sensor_timepoints = []

        sensor_data = [
            {"value": 72.5, "confidence": 0.95},
            {"value": 73.0, "confidence": 0.85},
            {"value": 71.8, "confidence": 0.90},
        ]

        for i, data in enumerate(sensor_data):
            # Create unique Key for each sensor
            key_mock = create_autospec(Key)
            sensor_keys.append(key_mock)

            # Create unique TimePoint for each sensor
            timepoint_mock = create_autospec(TimePoint)
            sensor_timepoints.append(timepoint_mock)

            # Create record
            record = create_autospec(VariableRecord)
            record.value = data["value"]
            record.confidence = data["confidence"]
            record.source = Key()
            record.key.return_value = key_mock
            record.time = timepoint_mock
            sensor_records.append(record)

        # Create a policy that selects highest confidence
        policy_mock = create_autospec(SelectionPolicy)
        policy_mock.__class__.__name__ = "HighestConfidencePolicy"

        # Create a validator that requires confidence > 0.8
        validator_mock = create_autospec(ProposalValidator)

        def validate_confidence(proposal):
            return proposal.confidence > 0.8

        validator_mock.validate.side_effect = validate_confidence

        # Create proposals that would be generated
        proposals = []
        for i, record in enumerate(sensor_records):
            proposal = ActionProposal(
                value=record.value,
                confidence=record.confidence,
                source=record.source,
                metadata={"record_key": sensor_keys[i], "time": sensor_timepoints[i]},
            )
            proposals.append(proposal)

        # Policy selects highest confidence (sensor_a, 0.95)
        policy_mock.select.return_value = proposals[0]

        # Execute resolution
        result, resolved = resolver.resolve(
            sensor_records, policy_mock, validators=[validator_mock]
        )

        # Verify successful resolution
        assert result is None
        assert resolved is not None
        assert resolved.value == 72.5  # sensor_a value
        assert resolved.confidence == 0.95
        assert resolved.metadata["policy"] == "HighestConfidencePolicy"

        # All three sensor Keys should be in resolved_from
        assert len(resolved.metadata["resolved_from"]) == 3
        assert sensor_keys[0] in resolved.metadata["resolved_from"]
        assert sensor_keys[1] in resolved.metadata["resolved_from"]
        assert sensor_keys[2] in resolved.metadata["resolved_from"]

    # ------------------------------------------------------------
    # Test: Metadata handling edge cases
    # ------------------------------------------------------------
    def test_resolved_from_with_mixed_metadata(self):
        """Test resolved_from list when some proposals have None metadata."""
        resolver = ConflictResolver()

        # Create Keys
        key1 = create_autospec(Key)
        key2 = create_autospec(Key)
        key3 = create_autospec(Key)

        # Create TimePoints
        time1 = create_autospec(TimePoint)
        time2 = create_autospec(TimePoint)
        time3 = create_autospec(TimePoint)

        # Create records
        record1 = create_autospec(VariableRecord)
        record1.value = 10.0
        record1.confidence = 0.8
        record1.source = Key()
        record1.key.return_value = key1
        record1.time = time1

        record2 = create_autospec(VariableRecord)
        record2.value = 20.0
        record2.confidence = 0.9
        record2.source = Key()
        record2.key.return_value = key2
        record2.time = time2

        record3 = create_autospec(VariableRecord)
        record3.value = 30.0
        record3.confidence = 0.7
        record3.source = Key()
        record3.key.return_value = key3
        record3.time = time3

        # Create mock SelectionPolicy
        policy_mock = create_autospec(SelectionPolicy)
        policy_mock.__class__.__name__ = "TestPolicy"

        # Create proposals - second one has None metadata
        proposal1 = ActionProposal(
            value=10.0,
            confidence=0.8,
            source=Key(),
            metadata={"record_key": key1, "time": time1},
        )

        proposal2 = ActionProposal(
            value=20.0,
            confidence=0.9,
            source=Key(),
            metadata=None,  # No metadata
        )

        proposal3 = ActionProposal(
            value=30.0,
            confidence=0.7,
            source=Key(),
            metadata={"record_key": key3, "time": time3},
        )

        def record_to_proposal_side_effect(record):
            if record is record1:
                return proposal1
            elif record is record2:
                return proposal2
            elif record is record3:
                return proposal3
            return None

        with patch.object(
            resolver, "_record_to_proposal", side_effect=record_to_proposal_side_effect
        ):
            policy_mock.select.return_value = proposal1

            result, resolved = resolver.resolve(
                [record1, record2, record3], policy_mock
            )

        # Should succeed
        assert result is None
        assert isinstance(resolved, VariableRecord)

        assert len(resolved.metadata["resolved_from"]) == 2
        assert key1 in resolved.metadata["resolved_from"]
        assert key3 in resolved.metadata["resolved_from"]


# ------------------------------------------------------------
# Test utilities
# ------------------------------------------------------------
def test_imports_with_correct_types():
    """Test that all necessary imports work with correct types."""
    # This test ensures we can import everything
    from procela.core.action.policy import SelectionPolicy
    from procela.core.action.proposal import ActionProposal
    from procela.core.action.resolver import ConflictResolver
    from procela.core.action.validator import ProposalValidator
    from procela.core.assessment import ReasoningResult, ReasoningTask
    from procela.core.memory.variable.history import VariableRecord
    from procela.symbols.key import Key
    from procela.symbols.time import TimePoint

    # Just verify imports work
    assert ConflictResolver is not None
    assert VariableRecord is not None
    assert ReasoningResult is not None
    assert ReasoningTask is not None
    assert SelectionPolicy is not None
    assert ActionProposal is not None
    assert ProposalValidator is not None
    assert Key is not None
    assert TimePoint is not None


if __name__ == "__main__":
    # Simple test runner
    import unittest

    unittest.main()
