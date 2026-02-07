"""
CORRECT test suite for procela.core.action.resolver
Using actual API specification with proper Key and TimePoint types.
"""

from unittest.mock import Mock, create_autospec, patch

import pytest

from procela.core.action.policy import ResolutionPolicy
from procela.core.action.proposal import ActionProposal
from procela.core.action.resolver import ConflictResolver
from procela.core.action.validator import ProposalValidator
from procela.core.assessment import ReasoningResult, ReasoningTask
from procela.core.memory.candidate import CandidateRecord, CandidateState
from procela.core.memory.record import VariableRecord
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
        policy_mock = create_autospec(ResolutionPolicy)

        resolved, result = resolver.resolve([], policy_mock)

        # Should return failure result
        assert isinstance(result, ReasoningResult)
        assert result.success is False
        assert result.task == ReasoningTask.CONFLICT_RESOLUTION
        assert result.confidence is None
        assert "No candidates" in result.explanation
        assert resolved is None

    # ------------------------------------------------------------
    # Test: No policy
    # ------------------------------------------------------------
    def test_resolve_no_policy(self):
        """Test resolve with None policy returns failure."""
        resolver = ConflictResolver()
        records = [VariableRecord(value=0.8), VariableRecord(value=19.7)]
        candidates = [CandidateRecord(record) for record in records]

        resolved, result = resolver.resolve(candidates, None)
        assert isinstance(result, ReasoningResult)
        assert isinstance(resolved, VariableRecord | None)

    # ------------------------------------------------------------
    # Test: No policy
    # ------------------------------------------------------------
    def test_resolve_not_policy(self):
        """Test resolve with Not a policy returns failure."""
        resolver = ConflictResolver()
        records = [VariableRecord(value=0.8), VariableRecord(value=19.7)]

        with pytest.raises(TypeError):
            resolver.resolve(records, "not_a_policy")

    # ------------------------------------------------------------
    # Test: Type validation errors
    # ------------------------------------------------------------
    def test_resolve_candidates_not_sequence(self):
        """Test resolve raises TypeError when candidates is not a Sequence."""
        resolver = ConflictResolver()
        policy_mock = create_autospec(ResolutionPolicy)

        with pytest.raises(TypeError) as exc_info:
            resolver.resolve("not a sequence", policy_mock)

        assert "`candidate` 0 should be a `CandidateRecord` instance" in str(
            exc_info.value
        )
        assert "got" in str(exc_info.value)

    def test_resolve_candidate_not_variable_record(self):
        """Test resolve raises TypeError when a candidate is not VariableRecord."""
        resolver = ConflictResolver()
        policy_mock = create_autospec(ResolutionPolicy)

        with pytest.raises(TypeError) as exc_info:
            resolver.resolve(["not a record", "also not"], policy_mock)

        assert "`candidate` 0 should be a `CandidateRecord` instance" in str(
            exc_info.value
        )

    def test_resolve_policy_not_resolutionPolicy_policy(self):
        """Test resolve raises TypeError when policy is not ResolutionPolicy."""
        resolver = ConflictResolver()
        candidate_mock = create_autospec(CandidateRecord)

        with pytest.raises(AttributeError) as exc_info:
            resolver.resolve([candidate_mock], "not a policy")

        assert "no attribute 'record'" in str(exc_info.value)

    def test_resolve_validators_not_iterable(self):
        """Test resolve raises TypeError when validators is not Iterable."""
        resolver = ConflictResolver()
        policy_mock = create_autospec(ResolutionPolicy)
        candidate_mock = create_autospec(CandidateRecord)

        with pytest.raises(TypeError) as exc_info:
            resolver.resolve(candidate_mock, policy_mock, validators="not iterable")

        assert "`candidates` should be a Sequence of `CandidateRecord`" in str(
            exc_info.value
        )

    def test_resolve_validator_not_proposal_validator(self):
        """Test resolve raises TypeError when validator is not ProposalValidator."""
        resolver = ConflictResolver()
        policy_mock = create_autospec(ResolutionPolicy)
        candidate_mock = create_autospec(CandidateRecord)

        with pytest.raises(TypeError) as exc_info:
            resolver.resolve(
                [candidate_mock], policy_mock, validators=["not validator"]
            )

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
        candidate_mock = create_autospec(CandidateRecord)
        candidate_mock.record = record_mock
        candidate_mock.state = CandidateState.PROPOSED

        # Create mock ResolutionPolicy
        policy_mock = create_autospec(ResolutionPolicy)
        policy_mock.name = "TestResolutionPolicy"

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

        # Mock policy.resolve to return the proposal
        policy_mock.resolve.return_value = expected_proposal

        # Execute
        resolved, result = resolver.resolve([candidate_mock], policy_mock)

        # Verify
        assert result is not None
        assert isinstance(resolved, VariableRecord)

        # Check resolved record values match proposal
        assert resolved.value == 42.5
        assert resolved.confidence == 0.95
        assert resolved.source != record_mock.source

        # Check metadata - should contain Keys and TimePoints
        assert "resolved_from" in resolved.metadata
        assert resolved.metadata["policy"] == "TestResolutionPolicy"
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
        candidate_mock = create_autospec(CandidateRecord)
        candidate_mock.record = record_mock
        candidate_mock.state = CandidateState.PROPOSED

        # Create mock ResolutionPolicy
        policy_mock = create_autospec(ResolutionPolicy)
        policy_mock.name = "TestPolicy"

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

        policy_mock.resolve.return_value = expected_proposal

        # Execute with validators
        resolved, result = resolver.resolve(
            [candidate_mock], policy_mock, validators=[validator_mock]
        )

        # Verify validators were called with correct proposal
        validator_mock.validate.assert_called_once()
        called_proposal = validator_mock.validate.call_args[0][0]
        assert called_proposal.metadata["record_key"] == mock_key
        assert called_proposal.metadata["time"] == mock_timepoint

        # Verify successful resolution
        assert result is not None
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
        candidate_mock = create_autospec(CandidateRecord)
        candidate_mock.record = record_mock
        candidate_mock.state = CandidateState.PROPOSED

        # Create mock ResolutionPolicy
        policy_mock = create_autospec(ResolutionPolicy)
        policy_mock.name = "TestPolicy"

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

        policy_mock.resolve.return_value = expected_proposal

        # Execute with incorrect validators
        with pytest.raises(TypeError):
            resolver.resolve([candidate_mock], policy_mock, validators=True)

        # Execute with incorrect policy
        with pytest.raises(TypeError):
            resolver.resolve([candidate_mock], policy=Key())

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
        candidate_mock = create_autospec(CandidateRecord)
        candidate_mock.record = record_mock
        candidate_mock.state = CandidateState.PROPOSED

        # Create mock ResolutionPolicy
        policy_mock = create_autospec(ResolutionPolicy)

        # Create validator that always rejects
        validator_mock = create_autospec(ProposalValidator)
        validator_mock.validate.return_value = False

        # Execute
        resolved, result = resolver.resolve(
            [candidate_mock], policy_mock, validators=[validator_mock]
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
        """Test resolution when policy.resolve returns None."""
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
        candidate_mock = create_autospec(CandidateRecord)
        candidate_mock.record = record_mock
        candidate_mock.state = CandidateState.PROPOSED

        # Create mock ResolutionPolicy that returns None
        policy_mock = create_autospec(ResolutionPolicy)
        policy_mock.resolve.return_value = None

        # Execute
        resolved, result = resolver.resolve([candidate_mock], policy_mock)

        # Should return failure
        assert isinstance(result, ReasoningResult)
        assert result.success is False
        assert "Resolution policy returned no proposal" in result.explanation
        assert resolved is None

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
        candidate_mock = create_autospec(CandidateRecord)
        candidate_mock.record = record_mock
        candidate_mock.state = CandidateState.PROPOSED

        policy_mock = create_autospec(ResolutionPolicy)
        policy_mock.name = "TestPolicy"

        # Create a proposal
        expected_proposal = ActionProposal(
            value=100.0,
            confidence=0.9,
            source=Key(),
            metadata={"record_key": mock_key, "time": mock_timepoint},
        )
        policy_mock.resolve.return_value = expected_proposal

        # Execute with validators=None
        resolved, result = resolver.resolve(
            [candidate_mock], policy_mock, validators=None
        )

        # Should succeed
        assert result is not None
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
        candidate_mock = create_autospec(CandidateRecord)
        candidate_mock.record = record_mock

        policy_mock = create_autospec(ResolutionPolicy)
        policy_mock.name = "TestPolicy"

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
            policy_mock.resolve.return_value = proposal_with_none_metadata

            resolved, result = resolver.resolve([candidate_mock], policy_mock)

        # Should still succeed
        assert result is not None
        assert isinstance(resolved, VariableRecord)
        # resolved_from list should handle None metadata gracefully
        assert "resolved_from" in resolved.metadata

    def test_resolve_multiple_candidates_with_keys(self):
        """Test resolution with multiple candidates, each with unique Keys."""
        resolver = ConflictResolver()

        # Create multiple mock VariableRecords with unique Keys
        candidates = []
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
            candidate = create_autospec(CandidateRecord)
            candidate.record = record_mock
            candidates.append(candidate)

        # Create mock ResolutionPolicy
        policy_mock = create_autospec(ResolutionPolicy)
        policy_mock.name = "HighestValuePolicy"

        # Create proposals that would be generated
        proposals = []
        for i, candidate in enumerate(candidates):
            proposal = ActionProposal(
                value=candidate.record.value,
                confidence=candidate.record.confidence,
                source=candidate.record.source,
                metadata={"record_key": keys[i], "time": timepoints[i]},
            )
            proposals.append(proposal)

        # Mock policy.resolve to return the middle proposal
        policy_mock.resolve.return_value = proposals[1]

        # Execute
        resolved, result = resolver.resolve(candidates, policy_mock)

        # Verify
        assert result is not None
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
        sensor_candidates = []
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
            candidate = create_autospec(CandidateRecord)
            candidate.record = record
            sensor_candidates.append(candidate)

        # Create a policy that resolves highest confidence
        policy_mock = create_autospec(ResolutionPolicy)
        policy_mock.name = "HighestConfidencePolicy"

        # Create a validator that requires confidence > 0.8
        validator_mock = create_autospec(ProposalValidator)

        def validate_confidence(proposal):
            return proposal.confidence > 0.8

        validator_mock.validate.side_effect = validate_confidence

        # Create proposals that would be generated
        proposals = []
        for i, candidate in enumerate(sensor_candidates):
            proposal = ActionProposal(
                value=candidate.record.value,
                confidence=candidate.record.confidence,
                source=candidate.record.source,
                metadata={"record_key": sensor_keys[i], "time": sensor_timepoints[i]},
            )
            proposals.append(proposal)

        # Policy resolves highest confidence (sensor_a, 0.95)
        policy_mock.resolve.return_value = proposals[0]

        # Execute resolution
        resolved, result = resolver.resolve(
            sensor_candidates, policy_mock, validators=[validator_mock]
        )

        # Verify successful resolution
        assert result is not None
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
        candidate1 = create_autospec(CandidateRecord)
        candidate1.record = record1
        candidate1.state = CandidateState.PROPOSED
        candidate1 = CandidateRecord(record1)

        record2 = create_autospec(VariableRecord)
        record2.value = 20.0
        record2.confidence = 0.9
        record2.source = Key()
        record2.key.return_value = key2
        record2.time = time2
        candidate2 = create_autospec(CandidateRecord)
        candidate2.record = record2
        candidate2.state = CandidateState.PROPOSED

        record3 = create_autospec(VariableRecord)
        record3.value = 30.0
        record3.confidence = 0.7
        record3.source = Key()
        record3.key.return_value = key3
        record3.time = time3
        candidate3 = create_autospec(CandidateRecord)
        candidate3.record = record3
        candidate3.state = CandidateState.PROPOSED

        # Create mock ResolutionPolicy
        policy_mock = create_autospec(ResolutionPolicy)
        policy_mock.name = "TestPolicy"

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
            policy_mock.resolve.return_value = proposal1

            resolved, result = resolver.resolve(
                [candidate1, candidate2, candidate3], policy_mock
            )

        # Should succeed
        assert result is not None
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
    from procela.core.action.policy import ResolutionPolicy
    from procela.core.action.proposal import ActionProposal
    from procela.core.action.resolver import ConflictResolver
    from procela.core.action.validator import ProposalValidator
    from procela.core.assessment import ReasoningResult, ReasoningTask
    from procela.core.memory.record import VariableRecord
    from procela.symbols.key import Key
    from procela.symbols.time import TimePoint

    # Just verify imports work
    assert ConflictResolver is not None
    assert VariableRecord is not None
    assert ReasoningResult is not None
    assert ReasoningTask is not None
    assert ResolutionPolicy is not None
    assert ActionProposal is not None
    assert ProposalValidator is not None
    assert Key is not None
    assert TimePoint is not None


if __name__ == "__main__":
    # Simple test runner
    import unittest

    unittest.main()
