# test_resolver_policy.py

from typing import Callable
from unittest.mock import Mock, create_autospec

import pytest

from procela.core.assessment import ReasoningResult, ReasoningTask
from procela.core.memory import HypothesisRecord, VariableRecord
from procela.core.policy import ResolutionPolicy, ResolverPolicy


@pytest.fixture
def resolver():
    """Create a ResolverPolicy instance."""
    return ResolverPolicy()


@pytest.fixture
def mock_policy():
    """Create a mock resolution policy."""
    policy = create_autospec(ResolutionPolicy)
    return policy


@pytest.fixture
def mock_hypothesis():
    """Create a mock hypothesis record."""
    hypothesis = create_autospec(HypothesisRecord)
    return hypothesis


@pytest.fixture
def mock_validator():
    """Create a mock validator function."""
    return Mock(spec=Callable, return_value=True)


@pytest.fixture
def mock_variable_record():
    """Create a mock variable record."""
    record = create_autospec(VariableRecord)
    record.key.return_value = "test_key"
    record.confidence = 0.95
    return record


# -----------------------------------------------------------------------------
# Basic Tests
# -----------------------------------------------------------------------------


class TestResolverPolicyBasic:
    """Basic tests for ResolverPolicy."""

    def test_resolve_empty_hypotheses(self, resolver, mock_policy):
        """Test resolve returns failure result for empty hypotheses."""
        result, reasoning = resolver.resolve([], mock_policy)

        assert result is None
        assert isinstance(reasoning, ReasoningResult)
        assert reasoning.task == ReasoningTask.CONFLICT_RESOLUTION
        assert reasoning.success is False
        assert reasoning.explanation == "No hypothesis."

    def test_resolve_no_policy(self, resolver, mock_hypothesis):
        """Test resolve returns failure result when no policy provided."""
        result, reasoning = resolver.resolve([mock_hypothesis], None)

        assert result is None
        assert reasoning.success is False
        assert reasoning.explanation == "No policy."

    def test_resolve_invalid_hypotheses_type(self, resolver, mock_policy):
        """Test TypeError raised for non-iterable hypotheses."""
        with pytest.raises(TypeError, match="`hypotheses` should be an Iterable"):
            resolver.resolve(lambda: None, mock_policy)

    def test_resolve_invalid_hypothesis_element(self, resolver, mock_policy):
        """Test TypeError raised for non-HypothesisRecord element."""
        with pytest.raises(
            TypeError, match="`hypothesis` 0 should be a `HypothesisRecord`"
        ):
            resolver.resolve(["not_a_hypothesis"], mock_policy)

    def test_resolve_invalid_policy_type(self, resolver, mock_hypothesis):
        """Test TypeError raised for non-ResolutionPolicy policy."""
        with pytest.raises(TypeError, match="`policy` should be a ResolutionPolicy"):
            resolver.resolve([mock_hypothesis], "not_a_policy")


# -----------------------------------------------------------------------------
# Validator Tests
# -----------------------------------------------------------------------------


class TestResolverPolicyValidators:
    """Tests for validator functionality."""

    def test_validators_none(
        self, resolver, mock_policy, mock_hypothesis, mock_variable_record
    ):
        """Test with validators=None (all hypotheses pass through)."""
        mock_policy.resolve.return_value = mock_variable_record

        hypotheses = [mock_hypothesis, mock_hypothesis]
        result, reasoning = resolver.resolve(hypotheses, mock_policy, validators=None)

        mock_policy.resolve.assert_called_once_with(hypotheses=hypotheses)
        assert result == mock_variable_record
        assert reasoning.success is True

    def test_validators_empty_list(
        self, resolver, mock_policy, mock_hypothesis, mock_variable_record
    ):
        """Test with empty validators list (all hypotheses pass through)."""
        mock_policy.resolve.return_value = mock_variable_record

        hypotheses = [mock_hypothesis, mock_hypothesis]
        result, reasoning = resolver.resolve(hypotheses, mock_policy, validators=[])

        mock_policy.resolve.assert_called_once_with(hypotheses=hypotheses)
        assert result == mock_variable_record

    def test_single_validator_passes(
        self,
        resolver,
        mock_policy,
        mock_hypothesis,
        mock_validator,
        mock_variable_record,
    ):
        """Test with a single validator that passes all hypotheses."""
        mock_policy.resolve.return_value = mock_variable_record
        mock_validator.return_value = True

        hypotheses = [mock_hypothesis, mock_hypothesis]
        result, reasoning = resolver.resolve(
            hypotheses, mock_policy, validators=[mock_validator]
        )

        # Policy should receive the filtered hypotheses
        mock_policy.resolve.assert_called_once()
        assert mock_policy.resolve.call_args[1]["hypotheses"] == hypotheses
        assert result == mock_variable_record

    def test_single_validator_filters_some(
        self,
        resolver,
        mock_policy,
        mock_hypothesis,
        mock_validator,
        mock_variable_record,
    ):
        """Test with a validator that filters out some hypotheses."""
        mock_policy.resolve.return_value = mock_variable_record

        # First hypothesis passes, second fails
        mock_validator.side_effect = [True, False]

        hypotheses = [mock_hypothesis, mock_hypothesis]
        result, reasoning = resolver.resolve(
            hypotheses, mock_policy, validators=[mock_validator]
        )

        # Policy should receive only the first hypothesis
        mock_policy.resolve.assert_called_once()
        filtered = mock_policy.resolve.call_args[1]["hypotheses"]
        assert len(filtered) == 2
        assert filtered[0] == mock_hypothesis

    def test_multiple_validators_all_pass(
        self, resolver, mock_policy, mock_hypothesis, mock_variable_record
    ):
        """Test multiple validators where all pass."""
        mock_policy.resolve.return_value = mock_variable_record

        validator1 = Mock(return_value=True)
        validator2 = Mock(return_value=True)

        hypotheses = [mock_hypothesis, mock_hypothesis]
        result, reasoning = resolver.resolve(
            hypotheses, mock_policy, validators=[validator1, validator2]
        )

        # All hypotheses should pass
        mock_policy.resolve.assert_called_once()
        filtered = mock_policy.resolve.call_args[1]["hypotheses"]
        assert len(filtered) == 2
        assert validator1.call_count == 2
        assert validator2.call_count == 2

    def test_multiple_validators_one_fails(
        self, resolver, mock_policy, mock_hypothesis, mock_variable_record
    ):
        """Test multiple validators where one fails for a hypothesis."""
        mock_policy.resolve.return_value = mock_variable_record

        validator1 = Mock(return_value=True)
        validator2 = Mock(side_effect=[True, False])  # Pass for first, fail for second

        hypotheses = [mock_hypothesis, mock_hypothesis]
        result, reasoning = resolver.resolve(
            hypotheses, mock_policy, validators=[validator1, validator2]
        )

        # Only first hypothesis should pass both validators
        mock_policy.resolve.assert_called_once()
        filtered = mock_policy.resolve.call_args[1]["hypotheses"]
        assert len(filtered) == 2
        assert filtered[0] == mock_hypothesis

    def test_all_hypotheses_rejected(
        self, resolver, mock_policy, mock_hypothesis, mock_validator
    ):
        """Test when all hypotheses are rejected by validators."""
        mock_validator.return_value = False

        hypotheses = [mock_hypothesis, mock_hypothesis]
        result, reasoning = resolver.resolve(
            hypotheses, mock_policy, validators=[mock_validator]
        )

        assert result is None
        assert reasoning.success is False
        assert reasoning.explanation == "All hypotheses rejected by validators."
        mock_policy.resolve.assert_not_called()

    def test_invalid_validators_type(self, resolver, mock_policy, mock_hypothesis):
        """Test TypeError raised for non-iterable validators."""
        with pytest.raises(TypeError, match="`validators` should be an Iterable"):
            resolver.resolve([mock_hypothesis], mock_policy, validators=lambda: None)

    def test_invalid_validator_element(self, resolver, mock_policy, mock_hypothesis):
        """Test TypeError raised for non-callable validator."""
        with pytest.raises(TypeError, match="`validator` 0 should be a Callable"):
            resolver.resolve(
                [mock_hypothesis], mock_policy, validators=["not_callable"]
            )


# -----------------------------------------------------------------------------
# Policy Resolution Tests
# -----------------------------------------------------------------------------


class TestResolverPolicyResolution:
    """Tests for policy resolution behavior."""

    def test_policy_returns_record(
        self, resolver, mock_policy, mock_hypothesis, mock_variable_record
    ):
        """Test successful resolution when policy returns a record."""
        mock_policy.resolve.return_value = mock_variable_record

        hypotheses = [mock_hypothesis]
        result, reasoning = resolver.resolve(hypotheses, mock_policy)

        assert result == mock_variable_record
        assert reasoning.success is True
        assert reasoning.task == ReasoningTask.CONFLICT_RESOLUTION
        assert reasoning.result == mock_variable_record.key()
        assert reasoning.confidence == mock_variable_record.confidence
        assert "successfully" in reasoning.explanation
        assert hasattr(reasoning, "execution_time")

    def test_policy_returns_none(self, resolver, mock_policy, mock_hypothesis):
        """Test failure when policy returns None."""
        mock_policy.resolve.return_value = None

        hypotheses = [mock_hypothesis]
        result, reasoning = resolver.resolve(hypotheses, mock_policy)

        assert result is None
        assert reasoning.success is False
        assert reasoning.explanation == "Resolution policy returned no conclusion."

    def test_policy_raises_exception(self, resolver, mock_policy, mock_hypothesis):
        """Test that policy exceptions are propagated."""
        mock_policy.resolve.side_effect = ValueError("Policy error")

        with pytest.raises(ValueError, match="Policy error"):
            resolver.resolve([mock_hypothesis], mock_policy)


# -----------------------------------------------------------------------------
# Integration Tests
# -----------------------------------------------------------------------------


class TestResolverPolicyIntegration:
    """Integration-style tests combining multiple components."""

    def test_full_success_path_with_validators(
        self, resolver, mock_hypothesis, mock_variable_record
    ):
        """Test complete successful path with validators and policy."""

        # Create a concrete policy instead of mock for integration
        class ConcretePolicy(ResolutionPolicy):
            def resolve(self, hypotheses):
                return mock_variable_record

        policy = ConcretePolicy()

        # Create validators
        def validator1(h):
            return True

        def validator2(h):
            return h is not None

        hypotheses = [mock_hypothesis, mock_hypothesis]
        result, reasoning = resolver.resolve(
            hypotheses, policy, validators=[validator1, validator2]
        )

        assert result == mock_variable_record
        assert reasoning.success is True
        assert reasoning.task == ReasoningTask.CONFLICT_RESOLUTION


# -----------------------------------------------------------------------------
# ReasoningResult Tests
# -----------------------------------------------------------------------------


class TestResolverPolicyReasoningResult:
    """Tests for the ReasoningResult return value."""

    def test_success_result_structure(
        self, resolver, mock_policy, mock_hypothesis, mock_variable_record
    ):
        """Test structure of successful ReasoningResult."""
        mock_policy.resolve.return_value = mock_variable_record

        hypotheses = [mock_hypothesis]
        result, reasoning = resolver.resolve(hypotheses, mock_policy)

        assert isinstance(reasoning, ReasoningResult)
        assert reasoning.task == ReasoningTask.CONFLICT_RESOLUTION
        assert reasoning.success is True
        assert reasoning.result == mock_variable_record.key()
        assert reasoning.confidence == mock_variable_record.confidence
        assert reasoning.explanation == "Conflict resolved successfully."
        assert hasattr(reasoning, "execution_time")

    def test_failure_result_structure(self, resolver, mock_policy, mock_hypothesis):
        """Test structure of failed ReasoningResult."""
        mock_policy.resolve.return_value = None

        hypotheses = [mock_hypothesis]
        result, reasoning = resolver.resolve(hypotheses, mock_policy)

        assert isinstance(reasoning, ReasoningResult)
        assert reasoning.task == ReasoningTask.CONFLICT_RESOLUTION
        assert reasoning.success is False
        assert reasoning.result is None
        assert reasoning.confidence is None
        assert reasoning.explanation == "Resolution policy returned no conclusion."
