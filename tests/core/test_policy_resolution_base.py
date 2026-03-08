"""Test resolution policy."""

from unittest.mock import Mock, create_autospec

import pytest

from procela.core.memory import HypothesisRecord
from procela.core.policy import ResolutionPolicy
from procela.symbols.key import Key

# Import these from your actual codebase
# from your_module import ResolutionPolicy, HypothesisRecord, VariableRecord, Key


def test_abstract_class_cannot_be_instantiated():
    """Test that ResolutionPolicy cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ResolutionPolicy()


def test_concrete_subclass_must_implement_resolve():
    """Test that subclasses must implement the resolve method."""

    # Create a concrete subclass without implementing resolve
    class IncompletePolicy(ResolutionPolicy):
        pass

    with pytest.raises(TypeError):
        IncompletePolicy()


def test_concrete_subclass_with_resolve_implementation():
    """Test that a subclass implementing resolve works correctly."""

    class ConcretePolicy(ResolutionPolicy):
        def resolve(self, hypotheses):
            # Minimal implementation for testing
            return next(iter(hypotheses), None) if hypotheses else None

    policy = ConcretePolicy(name="TestPolicy")
    assert policy.name == "TestPolicy"
    assert isinstance(policy.key(), Key)


def test_resolve_with_empty_hypotheses():
    """Test resolve method with empty hypotheses iterable."""

    class ConcretePolicy(ResolutionPolicy):
        def resolve(self, hypotheses):
            # Policy should handle empty iterable gracefully
            return None

    policy = ConcretePolicy()
    result = policy.resolve([])
    assert result is None


def test_resolve_with_mock_hypotheses():
    """Test resolve method with mock hypothesis records."""

    class ConfidencePolicy(ResolutionPolicy):
        def resolve(self, hypotheses):
            # Simple implementation that returns the first hypothesis
            for h in hypotheses:
                return h
            return None

    policy = ConfidencePolicy()

    # Create mock hypothesis records
    mock_hyp1 = create_autospec(HypothesisRecord)
    mock_hyp2 = create_autospec(HypothesisRecord)

    result = policy.resolve([mock_hyp1, mock_hyp2])
    assert result == mock_hyp1


def test_policy_initialization_with_custom_name():
    """Test policy initialization with custom name."""

    class ConcretePolicy(ResolutionPolicy):
        def resolve(self, hypotheses):
            return None

    custom_name = "MyCustomPolicy"
    policy = ConcretePolicy(name=custom_name)
    assert policy.name == custom_name


def test_policy_initialization_without_name():
    """Test policy initialization defaults to class name."""

    class ConcretePolicy(ResolutionPolicy):
        def resolve(self, hypotheses):
            return None

    policy = ConcretePolicy()
    assert policy.name == "ConcretePolicy"


def test_key_uniqueness():
    """Test that different policies have unique keys."""

    class ConcretePolicy(ResolutionPolicy):
        def resolve(self, hypotheses):
            return None

    policy1 = ConcretePolicy()
    policy2 = ConcretePolicy()

    assert policy1.key() != policy2.key()
    assert isinstance(policy1.key(), Key)


@pytest.mark.parametrize(
    "hypotheses_list,expected_count",
    [
        ([], 0),
        ([Mock(spec=HypothesisRecord)], 1),
        ([Mock(spec=HypothesisRecord), Mock(spec=HypothesisRecord)], 2),
    ],
)
def test_resolve_with_various_input_sizes(hypotheses_list, expected_count):
    """Test resolve with different sizes of hypotheses iterables."""

    class CountingPolicy(ResolutionPolicy):
        def resolve(self, hypotheses):
            # Just verify we can iterate through hypotheses
            _ = sum(1 for _ in hypotheses)
            return None

    policy = CountingPolicy()

    # This test just ensures the method can be called with different input sizes
    # The actual assertion will depend on your implementation
    result = policy.resolve(hypotheses_list)
    assert result is None
