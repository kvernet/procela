import pytest

from procela.core.assessment import ReasoningResult, ReasoningTask
from procela.core.memory import HypothesisRecord, VariableMemory, VariableRecord
from procela.core.variable import Variable
from procela.symbols.key import Key
from procela.symbols.time import TimePoint


@pytest.fixture
def sample_candidate_record() -> VariableRecord:
    """Sample candidate record"""
    return HypothesisRecord(VariableRecord(value=18.67, confidence=0.74))


@pytest.fixture
def sample_variable_record() -> Variable:
    """Sample variable record"""
    return VariableRecord(value=19.67, confidence=0.82)


@pytest.fixture
def sample_reasoning_result() -> ReasoningResult:
    """Sample reasoning result"""
    return ReasoningResult(
        task=ReasoningTask.ANOMALY_DETECTION, success=False, result=None
    )


@pytest.fixture
def sample_time_point() -> TimePoint:
    """Sample time point"""
    return TimePoint()


@pytest.fixture
def sample_key() -> Key:
    """Sample key"""
    return Key()


class TestVariableMemory:
    """Test suite for VariableMemory class."""

    def test_initialization_with_all_fields(
        self,
        sample_candidate_record,
        sample_variable_record,
        sample_reasoning_result,
        sample_key,
    ):
        """Test initialization with all fields provided."""
        hypotheses = (sample_candidate_record,)
        config = {"test": "value"}

        memory = VariableMemory(
            hypotheses=hypotheses,
            conclusion=sample_variable_record,
            reasoning=sample_reasoning_result,
            config=config,
            previous=sample_key,
        )

        assert memory.hypotheses == hypotheses
        assert memory.conclusion == sample_variable_record
        assert memory.reasoning == sample_reasoning_result
        assert memory.config == config
        assert memory.previous == sample_key
        assert memory.key() is not None

    def test_initialization_with_defaults(self, sample_candidate_record):
        """Test initialization with default values."""
        hypotheses = (sample_candidate_record,)

        memory = VariableMemory(hypotheses=hypotheses, conclusion=None, reasoning=None)

        assert memory.hypotheses == hypotheses
        assert memory.conclusion is None
        assert memory.reasoning is None
        assert memory.config == {}
        assert memory.previous is None
        assert memory.key() is not None

    def test_new_method_creates_linked_memory(
        self, sample_candidate_record, sample_variable_record, sample_reasoning_result
    ):
        """Test that new() creates a linked memory node."""
        initial_hypotheses = (sample_candidate_record,)

        memory1 = VariableMemory(
            hypotheses=initial_hypotheses, conclusion=None, reasoning=None
        )

        # Create new hypotheses for the next node
        new_hypotheses = (sample_candidate_record, sample_candidate_record)

        memory2 = memory1.new(
            hypotheses=new_hypotheses,
            conclusion=sample_variable_record,
            reasoning=sample_reasoning_result,
        )

        assert memory2.hypotheses == new_hypotheses
        assert memory2.conclusion == sample_variable_record
        assert memory2.reasoning == sample_reasoning_result
        assert memory2.previous == memory1.key()
        assert memory2.config == {}  # Should inherit config from memory1
        assert memory2.key() != memory1.key()

    def test_latest_returns_current_state(
        self,
        sample_candidate_record,
        sample_variable_record,
        sample_reasoning_result,
        sample_time_point,
    ):
        """Test that latest() returns the current node's data."""
        hypotheses = (sample_candidate_record,)

        memory = VariableMemory(
            hypotheses=hypotheses,
            conclusion=sample_variable_record,
            reasoning=sample_reasoning_result,
            time=sample_time_point,
        )

        latest_hypotheses, latest_conclusion, latest_reasoning, latest_time = (
            memory.latest()
        )

        assert latest_hypotheses == hypotheses
        assert latest_conclusion == sample_variable_record
        assert latest_reasoning == sample_reasoning_result
        assert latest_time == sample_time_point

    def test_reset_method(self, sample_candidate_record, sample_variable_record):
        """Test that reset() clears the memory state."""
        hypotheses = (sample_candidate_record,)

        memory = VariableMemory(
            hypotheses=hypotheses, conclusion=sample_variable_record, reasoning=None
        )

        # Store key before reset
        original_key = memory.key()

        # Reset the memory
        memory.reset()

        assert memory.hypotheses == ()
        assert memory.conclusion is None
        assert memory.reasoning is None
        assert memory.previous is None
        assert memory.config == {}
        # Key should remain the same object even after reset
        assert memory.key() == original_key

    def test_iter_method_empty_memory(self):
        """Test iter() on a memory with no previous nodes."""
        memory = VariableMemory(hypotheses=(), conclusion=None, reasoning=None)

        nodes = list(memory.iter())
        assert len(nodes) == 1
        assert nodes[0] == ((), None, None, None)

    def test_iter_method_with_filtering(
        self,
        sample_candidate_record,
        sample_variable_record,
        sample_reasoning_result,
        sample_time_point,
    ):
        """Test iter() with source filtering."""
        # Create a memory with a specific source
        memory = VariableMemory(
            hypotheses=(sample_candidate_record,),
            conclusion=sample_variable_record,
            reasoning=sample_reasoning_result,
            time=sample_time_point,
        )

        # Test with matching source filter
        nodes = list(memory.iter(source=sample_variable_record.source))
        assert len(nodes) == 1

        # Test with non-matching source filter
        nodes = list(memory.iter(source="non_existent_source"))
        assert len(nodes) == 0

        # Test with task and success
        nodes = list(memory.iter(task=ReasoningTask.CONFLICT_RESOLUTION, success=False))
        assert len(nodes) == 0

        memory = VariableMemory(
            hypotheses=(sample_candidate_record,),
            conclusion=None,
            reasoning=sample_reasoning_result,
            time=sample_time_point,
        )

        nodes = list(memory.iter(task=None, success=True))
        assert len(nodes) == 0

        nodes = list(memory.iter(time=sample_time_point))
        assert len(nodes) == 1

        nodes = list(
            memory.iter(
                time=TimePoint(),
            )
        )
        assert len(nodes) == 0

    def test_records_method_reverses_order(self, sample_candidate_record):
        """Test that records() returns nodes in chronological order."""
        # Create a chain: memory1 -> memory2 -> memory3
        memory1 = VariableMemory(
            hypotheses=(sample_candidate_record,), conclusion=None, reasoning=None
        )

        memory2 = memory1.new(
            hypotheses=(sample_candidate_record, sample_candidate_record),
            conclusion=None,
            reasoning=None,
        )

        memory3 = memory2.new(
            hypotheses=(
                sample_candidate_record,
                sample_candidate_record,
                sample_candidate_record,
            ),
            conclusion=None,
            reasoning=None,
        )

        # records() should return in chronological order: memory1, memory2, memory3
        records = memory3.records()
        assert len(records) == 3
        assert len(records[0][0]) == 1  # memory1 has 1 hypothesis
        assert len(records[1][0]) == 2  # memory2 has 2 hypotheses
        assert len(records[2][0]) == 3  # memory3 has 3 hypotheses

    def test_previous_key_method(self, sample_candidate_record, sample_key):
        """Test previous_key() returns correct key or None."""
        # Memory without previous
        memory1 = VariableMemory(
            hypotheses=(sample_candidate_record,),
            conclusion=None,
            reasoning=None,
            previous=None,
        )
        assert memory1.previous_key() is None

        # Memory with previous
        memory2 = VariableMemory(
            hypotheses=(sample_candidate_record,),
            conclusion=None,
            reasoning=None,
            previous=sample_key,
        )
        assert memory2.previous_key() == sample_key

    def test_validation_errors(
        self, sample_candidate_record, sample_variable_record, sample_reasoning_result
    ):
        """Test type validation errors in constructor."""
        # Test invalid hypotheses (not a tuple)
        with pytest.raises(TypeError, match="`hypotheses` should be a tuple"):
            VariableMemory(
                hypotheses=[sample_candidate_record],  # List instead of tuple
                conclusion=None,
                reasoning=None,
            )

        # Test invalid conclusion type
        with pytest.raises(TypeError):
            VariableMemory(
                hypotheses=(sample_candidate_record,),
                conclusion="not_a_record",  # Wrong type
                reasoning=None,
            )

        # Test invalid reasoning type
        with pytest.raises(TypeError):
            VariableMemory(
                hypotheses=(sample_candidate_record,),
                conclusion=sample_variable_record,
                reasoning="not_reasoning",  # Wrong type
            )

        # Test invalid time point
        with pytest.raises(TypeError):
            VariableMemory(
                hypotheses=(sample_candidate_record,),
                conclusion=sample_variable_record,
                reasoning=None,
                time="not_a_time",  # Wrong type
            )

        # Test invalid config type
        with pytest.raises(TypeError):
            VariableMemory(
                hypotheses=(sample_candidate_record,),
                conclusion=None,
                reasoning=None,
                config="not_a_dict",  # Wrong type
            )

        # Test invalid previous type
        with pytest.raises(TypeError):
            VariableMemory(
                hypotheses=(sample_candidate_record,),
                conclusion=None,
                reasoning=None,
                previous="not_a_key",  # Wrong type
            )

    def test_validation_in_new_method(self, sample_candidate_record):
        """Test validation errors in new() method."""
        memory = VariableMemory(
            hypotheses=(sample_candidate_record,), conclusion=None, reasoning=None
        )

        # Test passing invalid hypotheses to new()
        with pytest.raises(TypeError, match="`hypotheses` should be a tuple"):
            memory.new(
                hypotheses=[sample_candidate_record],  # List instead of tuple
                conclusion=None,
                reasoning=None,
            )

    def test_hypothesis_element_validation(self):
        """Test validation of individual hypothesis elements."""
        # Test with a non-HypothesisRecord in hypotheses
        with pytest.raises(
            TypeError, match="`hypothesis` at index 0 should be a HypothesisRecord"
        ):
            VariableMemory(
                hypotheses=("not_a_candidate_record",),  # Wrong type
                conclusion=None,
                reasoning=None,
            )
