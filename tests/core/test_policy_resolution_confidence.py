"""Test confidence policies."""

from unittest.mock import Mock, create_autospec

import pytest

from procela.core.memory import HypothesisRecord, VariableRecord
from procela.core.policy import HighestConfidencePolicy, WeightedConfidencePolicy
from procela.symbols.key import Key


@pytest.fixture
def mock_hypothesis_with_confidence():
    """Create a mock hypothesis record with a specific confidence value."""

    def _create(confidence_value, record_value=42.0):
        hypothesis = create_autospec(HypothesisRecord)
        # Create a mock record attribute with confidence and value
        record_mock = Mock()
        record_mock.confidence = confidence_value
        record_mock.value = record_value
        hypothesis.record = record_mock
        return hypothesis

    return _create


@pytest.fixture
def mock_hypothesis_with_weight():
    """Create a mock hypothesis with weight in metadata."""

    def _create(confidence_value, weight=1.0, record_value=42.0):
        hypothesis = create_autospec(HypothesisRecord)
        record_mock = Mock()
        record_mock.confidence = confidence_value
        record_mock.value = record_value
        record_mock.metadata = {"weight": weight}
        hypothesis.record = record_mock
        return hypothesis

    return _create


# -----------------------------------------------------------------------------
# Tests for HighestConfidencePolicy
# -----------------------------------------------------------------------------


class TestHighestConfidencePolicy:
    """Test suite for HighestConfidencePolicy."""

    def test_initialization(self):
        """Test policy can be initialized with custom name."""
        policy = HighestConfidencePolicy(name="CustomHighConf")
        assert policy.name == "CustomHighConf"
        assert isinstance(policy.key(), Key)

    def test_resolve_empty_hypotheses(self):
        """Test resolve returns None for empty input."""
        policy = HighestConfidencePolicy()
        result = policy.resolve([])
        assert result is None

    def test_resolve_single_hypothesis(self, mock_hypothesis_with_confidence):
        """Test resolve with single hypothesis."""
        policy = HighestConfidencePolicy()
        hypothesis = mock_hypothesis_with_confidence(0.8, 100.0)

        result = policy.resolve([hypothesis])

        assert isinstance(result, VariableRecord)
        assert result.value == 100.0
        assert result.confidence == 0.8
        assert result.source == policy.key()
        assert result.explanation == "Weighted confidence resolution"

    def test_resolve_selects_highest_confidence(self, mock_hypothesis_with_confidence):
        """Test policy selects hypothesis with highest confidence."""
        policy = HighestConfidencePolicy()

        hypotheses = [
            mock_hypothesis_with_confidence(0.5, 10.0),
            mock_hypothesis_with_confidence(0.9, 20.0),
            mock_hypothesis_with_confidence(0.3, 30.0),
        ]

        result = policy.resolve(hypotheses)

        assert result.value == 20.0
        assert result.confidence == 0.9

    def test_resolve_with_confidence_none(self, mock_hypothesis_with_confidence):
        """Test hypotheses with None confidence are treated as 0.0."""
        policy = HighestConfidencePolicy()

        hypothesis_none = mock_hypothesis_with_confidence(None, 10.0)
        hypothesis_with_conf = mock_hypothesis_with_confidence(0.7, 20.0)

        result = policy.resolve([hypothesis_none, hypothesis_with_conf])

        # Should select the one with actual confidence
        assert result.value == 20.0
        assert result.confidence == 0.7

    def test_resolve_all_none_confidence(self, mock_hypothesis_with_confidence):
        """Test when all confidences are None, first hypothesis is selected."""
        policy = HighestConfidencePolicy()

        hypotheses = [
            mock_hypothesis_with_confidence(None, 10.0),
            mock_hypothesis_with_confidence(None, 20.0),
        ]

        result = policy.resolve(hypotheses)

        # max() with default 0.0 will pick the first one
        assert result.value == 10.0
        assert result.confidence is None

    def test_resolve_invalid_input_type(self):
        """Test TypeError raised for non-HypothesisRecord input."""
        policy = HighestConfidencePolicy()

        with pytest.raises(TypeError, match="All items must be HypothesisRecord"):
            policy.resolve(["not_a_hypothesis"])

    def test_resolve_invalid_confidence_type(self, mock_hypothesis_with_confidence):
        """Test ValueError raised for uncomparable confidence values."""
        policy = HighestConfidencePolicy()

        # Create hypothesis with string confidence that can't be compared
        hypothesis = mock_hypothesis_with_confidence("invalid", 10.0)

        with pytest.raises(ValueError, match="Cannot compare proposals"):
            policy.resolve([hypothesis])


# -----------------------------------------------------------------------------
# Tests for WeightedConfidencePolicy
# -----------------------------------------------------------------------------


class TestWeightedConfidencePolicy:
    """Test suite for WeightedConfidencePolicy."""

    def test_initialization(self):
        """Test policy can be initialized."""
        policy = WeightedConfidencePolicy(name="CustomWeighted")
        assert policy.name == "CustomWeighted"
        assert isinstance(policy.key(), Key)

    def test_resolve_empty_hypotheses(self):
        """Test resolve returns None for empty input."""
        policy = WeightedConfidencePolicy()
        result = policy.resolve([])
        assert result is None

    def test_resolve_with_hypotheses_without_record(self):
        """Test hypotheses with None record are filtered out."""
        policy = WeightedConfidencePolicy()

        valid_hyp = create_autospec(HypothesisRecord)
        valid_hyp.record = Mock(confidence=0.8, value=10.0, source=Mock())

        invalid_hyp = create_autospec(HypothesisRecord)
        invalid_hyp.record = None

        result = policy.resolve([invalid_hyp, valid_hyp])

        assert result is not None
        assert result.value == 10.0

    def test_weighted_average_basic(self, mock_hypothesis_with_confidence):
        """Test basic weighted average calculation."""
        policy = WeightedConfidencePolicy()

        # All hypotheses have same weight (confidence acts as weight)
        hypotheses = [
            mock_hypothesis_with_confidence(0.5, 10.0),
            mock_hypothesis_with_confidence(0.5, 20.0),
        ]

        result = policy.resolve(hypotheses)

        # Weighted average: (10*0.5 + 20*0.5) / (0.5+0.5) = 15
        assert result.value == 15.0
        # Confidence = weight_sum / n = 1.0 / 2 = 0.5
        assert result.confidence == 0.5

    def test_weighted_average_different_confidences(
        self, mock_hypothesis_with_confidence
    ):
        """Test weighted average with different confidence values."""
        policy = WeightedConfidencePolicy()

        hypotheses = [
            mock_hypothesis_with_confidence(0.9, 10.0),
            mock_hypothesis_with_confidence(0.1, 20.0),
        ]

        result = policy.resolve(hypotheses)

        # Weighted average: (10*0.9 + 20*0.1) / (0.9+0.1) = 11
        # Confidence = (0.9+0.1) / 2 = 0.5
        assert pytest.approx(result.value) == 11.0
        assert result.confidence == 0.5

    def test_weight_sum_zero_fallback_to_mean(self, mock_hypothesis_with_confidence):
        """Test when weight_sum is zero, fallback to simple mean."""
        policy = WeightedConfidencePolicy()

        # All confidences are 0.0, so weight_sum = 0
        hypotheses = [
            mock_hypothesis_with_confidence(0.0, 10.0),
            mock_hypothesis_with_confidence(0.0, 20.0),
            mock_hypothesis_with_confidence(0.0, 30.0),
        ]

        result = policy.resolve(hypotheses)

        # Should fall back to mean: (10+20+30)/3 = 20
        assert result.value == 20.0
        assert result.confidence == 0.0

    def test_resolve_filters_none_confidence(self, mock_hypothesis_with_confidence):
        """Test hypotheses with None confidence are skipped."""
        policy = WeightedConfidencePolicy()

        hypotheses = [
            mock_hypothesis_with_confidence(None, 10.0),
            mock_hypothesis_with_confidence(0.8, 20.0),
        ]

        result = policy.resolve(hypotheses)

        # Should only use the valid hypothesis
        assert result.value == 20.0
        assert result.confidence == 0.8 / 1  # sum_weights / 1

    def test_confidence_range_validation(self, mock_hypothesis_with_confidence):
        """Test ValueError raised for confidence outside [0,1]."""
        policy = WeightedConfidencePolicy()

        hypotheses = [
            mock_hypothesis_with_confidence(1.5, 10.0),  # Invalid confidence
        ]

        with pytest.raises(ValueError, match="Confidence should be in \\[0, 1\\]"):
            policy.resolve(hypotheses)

    def test_invalid_input_type(self):
        """Test TypeError raised for non-HypothesisRecord input."""
        policy = WeightedConfidencePolicy()

        with pytest.raises(TypeError, match="All items must be HypothesisRecord"):
            policy.resolve(["not_a_hypothesis"])

    def test_resolve_all_hypotheses_none_record(self):
        """Test hypotheses with None record are filtered out."""
        policy = WeightedConfidencePolicy()
        hypothesis = HypothesisRecord(
            VariableRecord(value=None, confidence=0.0, metadata={"weight": 0.0})
        )

        result = policy.resolve([hypothesis])
        assert result is None

    def test_output_format(self, mock_hypothesis_with_confidence):
        """Test output VariableRecord has expected structure."""
        policy = WeightedConfidencePolicy()

        hypotheses = [
            mock_hypothesis_with_confidence(0.7, 15.0),
        ]

        result = policy.resolve(hypotheses)

        assert isinstance(result, VariableRecord)
        assert result.source == policy.key()
        assert result.explanation == "Weighted confidence resolution"
        assert result.metadata == {"weighted_resolution": True}
