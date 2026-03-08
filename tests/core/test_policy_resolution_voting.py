# test_voting_policy.py

from unittest.mock import Mock, create_autospec

import pytest

from procela.core.memory import HypothesisRecord, VariableRecord
from procela.core.policy import WeightedVotingPolicy
from procela.symbols.key import Key


@pytest.fixture
def mock_hypothesis():
    """Create a mock hypothesis record with configurable attributes."""

    def _create(
        confidence: float | None = 0.5,
        value: float = 42.0,
        weight: float | None = None,
        metadata: dict | None = None,
    ):
        hypothesis = create_autospec(HypothesisRecord)
        record_mock = Mock()
        record_mock.confidence = confidence
        record_mock.value = value
        record_mock.source = Mock()  # Non-None source

        # Set up metadata with weight
        if metadata is None:
            metadata = {}
        if weight is not None:
            metadata["weight"] = weight
        record_mock.metadata = metadata

        hypothesis.record = record_mock
        return hypothesis

    return _create


@pytest.fixture
def policy():
    """Create a WeightedVotingPolicy instance."""
    return WeightedVotingPolicy(name="TestVotingPolicy")


# -----------------------------------------------------------------------------
# Basic Tests
# -----------------------------------------------------------------------------


class TestWeightedVotingPolicy:
    """Test suite for WeightedVotingPolicy."""

    def test_initialization(self, policy):
        """Test policy can be initialized with custom name."""
        assert policy.name == "TestVotingPolicy"
        assert isinstance(policy.key(), Key)

    def test_resolve_empty_hypotheses(self, policy):
        """Test resolve returns None for empty input."""
        result = policy.resolve([])
        assert result is None

    def test_resolve_all_hypotheses_none_record(self, policy, mock_hypothesis):
        """Test hypotheses with None record are filtered out."""
        hypothesis = mock_hypothesis()
        hypothesis.record = None

        result = policy.resolve([hypothesis])
        assert result is None


# -----------------------------------------------------------------------------
# Weighted Voting Calculation Tests
# -----------------------------------------------------------------------------


class TestWeightedVotingCalculations:
    """Test the weighted voting calculation logic."""

    def test_single_hypothesis(self, policy, mock_hypothesis):
        """Test with a single hypothesis."""
        hypothesis = mock_hypothesis(confidence=0.8, value=100.0, weight=2.0)

        result = policy.resolve([hypothesis])

        assert isinstance(result, VariableRecord)
        assert result.value == 100.0
        assert result.confidence == 0.8  # confidence = (0.8*2)/2 = 0.8
        assert result.source == policy.key()
        assert result.explanation == "Weighted voting resolution"
        assert result.metadata == {"voting_resolution": True}

    def test_equal_weights(self, policy, mock_hypothesis):
        """Test with equal weights (should behave like simple average)."""
        hypotheses = [
            mock_hypothesis(confidence=0.7, value=10.0, weight=1.0),
            mock_hypothesis(confidence=0.9, value=20.0, weight=1.0),
            mock_hypothesis(confidence=0.5, value=30.0, weight=1.0),
        ]

        result = policy.resolve(hypotheses)

        # Expected value: (10+20+30)/3 = 20
        # Expected confidence: (0.7+0.9+0.5)/3 = 0.7
        assert result.value == 20.0
        assert pytest.approx(result.confidence) == 0.7

    def test_different_weights(self, policy, mock_hypothesis):
        """Test with different weights for each hypothesis."""
        hypotheses = [
            mock_hypothesis(confidence=0.8, value=10.0, weight=3.0),
            mock_hypothesis(confidence=0.6, value=20.0, weight=1.0),
            mock_hypothesis(confidence=0.4, value=30.0, weight=1.0),
        ]

        result = policy.resolve(hypotheses)

        expected_value = 80.0 / 5.0  # = 16.0
        expected_confidence = 3.4 / 5.0  # = 0.68

        assert result.value == expected_value
        assert pytest.approx(result.confidence) == expected_confidence

    def test_default_weight_when_missing(self, policy, mock_hypothesis):
        """Test that weight defaults to 1.0 when not provided."""
        hypotheses = [
            mock_hypothesis(confidence=0.9, value=10.0),  # No weight specified
            mock_hypothesis(confidence=0.5, value=20.0, weight=2.0),
        ]

        result = policy.resolve(hypotheses)

        expected_value = 50.0 / 3.0  # ≈ 16.667
        expected_confidence = 1.9 / 3.0  # ≈ 0.633

        assert pytest.approx(result.value) == expected_value
        assert pytest.approx(result.confidence) == expected_confidence

    def test_metadata_weight_overrides_default(self, policy, mock_hypothesis):
        """Test that weight from metadata is used correctly."""
        hypotheses = [
            mock_hypothesis(confidence=0.7, value=15.0, metadata={"weight": 2.5}),
            mock_hypothesis(confidence=0.8, value=25.0, weight=1.5),
        ]

        result = policy.resolve(hypotheses)

        assert result.value == 75.0 / 4.0  # = 18.75
        assert pytest.approx(result.confidence) == 2.95 / 4.0  # = 0.7375


# -----------------------------------------------------------------------------
# Edge Cases and Error Handling
# -----------------------------------------------------------------------------


class TestWeightedVotingEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_total_weight_fallback_to_mean(self, policy, mock_hypothesis):
        """Test fallback to simple mean when total weight is zero."""
        # All weights are zero
        hypotheses = [
            mock_hypothesis(confidence=0.9, value=10.0, weight=0.0),
            mock_hypothesis(confidence=0.7, value=20.0, weight=0.0),
            mock_hypothesis(confidence=0.5, value=30.0, weight=0.0),
        ]

        result = policy.resolve(hypotheses)

        assert result.value == 20.0
        assert pytest.approx(result.confidence) == 0.7

    def test_filter_none_confidence(self, policy, mock_hypothesis):
        """Test hypotheses with None confidence are skipped."""
        hypotheses = [
            mock_hypothesis(confidence=None, value=10.0, weight=1.0),
            mock_hypothesis(confidence=0.8, value=20.0, weight=2.0),
            mock_hypothesis(confidence=0.6, value=30.0, weight=1.0),
        ]

        result = policy.resolve(hypotheses)

        expected_value = 70.0 / 3.0  # ≈ 23.333
        expected_confidence = 2.2 / 3.0  # ≈ 0.733

        assert pytest.approx(result.value) == expected_value
        assert pytest.approx(result.confidence) == expected_confidence

    def test_filter_hypotheses_without_record(self, policy, mock_hypothesis):
        """Test hypotheses with None record are filtered out."""
        valid_hyp = mock_hypothesis(confidence=0.8, value=20.0, weight=2.0)

        invalid_hyp = mock_hypothesis()
        invalid_hyp.record = None

        result = policy.resolve([invalid_hyp, valid_hyp])

        assert result.value == 20.0
        assert result.confidence == 0.8

    def test_negative_weight_raises_error(self, policy, mock_hypothesis):
        """Test that negative weight raises ValueError."""
        hypotheses = [
            mock_hypothesis(confidence=0.8, value=10.0, weight=-1.0),
        ]

        with pytest.raises(ValueError, match="Weight should be >= 0"):
            policy.resolve(hypotheses)

    def test_confidence_out_of_range_raises_error(self, policy, mock_hypothesis):
        """Test that confidence outside [0,1] raises ValueError."""
        hypotheses = [
            mock_hypothesis(confidence=1.5, value=10.0, weight=1.0),
        ]

        with pytest.raises(ValueError, match="Confidence should be in \\[0, 1\\]"):
            policy.resolve(hypotheses)

    def test_invalid_input_type(self, policy):
        """Test TypeError raised for non-HypothesisRecord input."""
        with pytest.raises(TypeError, match="All items must be HypothesisRecord"):
            policy.resolve(["not_a_hypothesis"])


# -----------------------------------------------------------------------------
# Complex Scenarios
# -----------------------------------------------------------------------------


class TestWeightedVotingComplex:
    """Test more complex scenarios."""

    def test_mixed_validity_hypotheses(self, policy, mock_hypothesis):
        """Test with mix of valid and invalid hypotheses."""
        hypotheses = [
            mock_hypothesis(confidence=0.9, value=10.0, weight=1.0),
            mock_hypothesis(confidence=None, value=20.0, weight=1.0),
            mock_hypothesis(confidence=0.7, value=30.0, weight=0.0),
        ]

        result = policy.resolve(hypotheses)

        assert result.value == 10.0
        assert result.confidence == 0.9

    def test_output_structure(self, policy, mock_hypothesis):
        """Test that output VariableRecord has correct structure."""
        hypothesis = mock_hypothesis(confidence=0.8, value=15.0, weight=1.0)

        result = policy.resolve([hypothesis])

        assert isinstance(result, VariableRecord)
        assert hasattr(result, "value")
        assert hasattr(result, "confidence")
        assert hasattr(result, "source")
        assert hasattr(result, "explanation")
        assert hasattr(result, "metadata")

        assert result.source == policy.key()
        assert result.explanation == "Weighted voting resolution"
        assert result.metadata == {"voting_resolution": True}
