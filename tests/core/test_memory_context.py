import pytest

from procela.core.assessment import ReasoningResult, ReasoningTask
from procela.core.memory import (
    CandidateRecord,
    CandidateState,
    ResolutionContext,
    VariableRecord,
)
from procela.symbols.key import Key


def test_initialization_defaults() -> None:
    """Test ResolutionContext initialization with default values."""
    context = ResolutionContext()
    assert context.hypotheses == []
    assert context.conclusion is None
    assert context.reasoning is None
    assert context.policy is None
    assert hasattr(context, "_key")


def test_initialization_with_values() -> None:
    """Test ResolutionContext initialization with provided values."""
    # Create real objects
    key = Key()
    var_record = VariableRecord(value="test_value")
    candidate = CandidateRecord(state=CandidateState.PROPOSED, record=var_record)
    reasoning = ReasoningResult(task=ReasoningTask.NONE, success=False, result=None)

    context = ResolutionContext(
        hypotheses=[candidate], conclusion=var_record, reasoning=reasoning, policy=key
    )

    assert context.hypotheses == [candidate]
    assert context.conclusion == var_record
    assert context.reasoning == reasoning
    assert context.policy == key


def test_post_init_validation_hypotheses_type_error() -> None:
    """Test __post_init__ raises TypeError for invalid hypotheses type."""
    with pytest.raises(TypeError, match="`hypotheses` should be a list"):
        ResolutionContext(hypotheses="not_a_list")


def test_post_init_validation_hypotheses_content_error() -> None:
    """Test __post_init__ raises TypeError for non-CandidateRecord in hypotheses."""

    var_record = VariableRecord(value="test_value")

    with pytest.raises(
        TypeError, match="`hypothesis` at index 0 should be a CandidateRecord"
    ):
        ResolutionContext(hypotheses=[var_record])


def test_post_init_validation_conclusion_error() -> None:
    """Test __post_init__ raises TypeError for invalid conclusion type."""
    with pytest.raises(
        TypeError, match="`conclusion` should be a VariableRecord or None"
    ):
        ResolutionContext(conclusion="not_a_variable_record")


def test_post_init_validation_conclusion_not_in_hypotheses() -> None:
    """Test __post_init__ raises TypeError when conclusion not in hypotheses."""
    var_record1 = VariableRecord(value="value1")
    var_record2 = VariableRecord(value="value2")
    candidate = CandidateRecord(state=CandidateState.PROPOSED, record=var_record1)

    with pytest.raises(
        TypeError, match="`conclusion` should be included in `hypothesis`"
    ):
        ResolutionContext(
            hypotheses=[candidate],
            conclusion=var_record2,  # Different record, not in hypotheses
        )


def test_post_init_validation_reasoning_error() -> None:
    """Test __post_init__ raises TypeError for invalid reasoning type."""
    with pytest.raises(
        TypeError, match="`reasoning` should be a ReasoningResult or None"
    ):
        ResolutionContext(reasoning="not_a_reasoning_result")


def test_post_init_validation_policy_error() -> None:
    """Test __post_init__ raises TypeError for invalid policy type."""
    with pytest.raises(TypeError, match="`policy` should be a Key or None"):
        ResolutionContext(policy="not_a_key")


def test_key_method() -> None:
    """Test key() method returns the generated key."""
    context = ResolutionContext()
    key = context.key()
    assert key == context._key
    assert hasattr(key, "__hash__")


def test_in_hypotheses_with_none() -> None:
    """Test in_hypotheses() returns True when record is None."""

    var_record = VariableRecord(value="test_value")
    candidate = CandidateRecord(state=CandidateState.PROPOSED, record=var_record)

    context = ResolutionContext(hypotheses=[candidate])
    assert context.in_hypotheses(None) is True


def test_in_hypotheses_with_record_in_list() -> None:
    """Test in_hypotheses() returns True when record is in hypotheses."""
    var_record = VariableRecord(value="test_value")
    candidate = CandidateRecord(state=CandidateState.PROPOSED, record=var_record)

    context = ResolutionContext(hypotheses=[candidate])
    assert context.in_hypotheses(var_record) is True


def test_in_hypotheses_with_record_not_in_list() -> None:
    var_record1 = VariableRecord(value="value1")
    var_record2 = VariableRecord(value="value2")

    context = ResolutionContext()
    assert context.in_hypotheses(var_record1) is False
    assert context.in_hypotheses(var_record2) is False


def test_reset_method() -> None:
    """Test reset() method clears all fields."""
    key = Key()
    var_record = VariableRecord(value="test_value")
    candidate = CandidateRecord(state=CandidateState.PROPOSED, record=var_record)
    reasoning = ReasoningResult(task=ReasoningTask.NONE, success=False, result=None)

    context = ResolutionContext(
        hypotheses=[candidate], conclusion=var_record, reasoning=reasoning, policy=key
    )

    context.reset()

    assert context.hypotheses == []
    assert context.conclusion is None
    assert context.reasoning is None
    assert context.policy is key
    # _key should remain unchanged
    assert hasattr(context, "_key")


def test_mutability() -> None:
    """Test that ResolutionContext is mutable (not frozen)."""
    key = Key()
    var_record = VariableRecord(value="test_value")
    candidate = CandidateRecord(state=CandidateState.PROPOSED, record=var_record)
    reasoning = ReasoningResult(task=ReasoningTask.NONE, success=False, result=None)

    context = ResolutionContext()

    # Should be able to modify attributes
    context.hypotheses = [candidate]
    context.conclusion = var_record
    context.reasoning = reasoning
    context.policy = key

    assert context.hypotheses == [candidate]
    assert context.conclusion == var_record
    assert context.reasoning == reasoning
    assert context.policy == key


def test_hypotheses_list_mutability() -> None:
    """Test that hypotheses list can be modified."""
    var_record = VariableRecord(value="test_value")
    candidate = CandidateRecord(state=CandidateState.PROPOSED, record=var_record)

    context = ResolutionContext()
    context.hypotheses.append(candidate)

    assert context.hypotheses == [candidate]


def test_comprehensive_validation() -> None:
    """Test all validations pass with correct types."""
    key = Key()
    var_record1 = VariableRecord(value="value1")
    var_record2 = VariableRecord(value="value2")

    candidate1 = CandidateRecord(state=CandidateState.PROPOSED, record=var_record1)
    candidate2 = CandidateRecord(state=CandidateState.VALIDATED, record=var_record2)

    reasoning = ReasoningResult(task=ReasoningTask.NONE, success=False, result=None)

    # Should not raise any TypeError
    context = ResolutionContext(
        hypotheses=[candidate1, candidate2],
        conclusion=var_record1,
        reasoning=reasoning,
        policy=key,
    )

    assert len(context.hypotheses) == 2
    assert context.conclusion == var_record1
    assert context.reasoning == reasoning
    assert context.policy == key
