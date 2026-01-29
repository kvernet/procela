"""Test for execution step trace."""

from dataclasses import FrozenInstanceError, is_dataclass
from typing import Mapping

import pytest

from procela.core.execution import ExecutionStepTrace
from procela.core.memory import VariableRecord
from procela.symbols.key import Key


@pytest.fixture
def sample_key() -> Key:
    """Create a real Key instance."""
    return Key()


@pytest.fixture
def sample_variable_record(sample_key) -> VariableRecord:
    """Create a real VariableRecord instance."""
    return VariableRecord(value="test_value")


@pytest.fixture
def sample_execution_step_trace(
    sample_key, sample_variable_record
) -> ExecutionStepTrace:
    """Create a real ExecutionStepTrace instance."""
    return ExecutionStepTrace(
        step=1,
        proposed={sample_key: [sample_variable_record]},
        validated={sample_key: [sample_variable_record]},
        resolved={sample_key: sample_variable_record},
        proposing_mechanisms={sample_key: [sample_key]},
    )


class TestExecutionStepTrace:
    """Test suite for ExecutionStepTrace dataclass."""

    def test_is_dataclass(self) -> None:
        """Test that ExecutionStepTrace is a dataclass."""
        assert is_dataclass(ExecutionStepTrace)

    def test_initialization(self, sample_key, sample_variable_record) -> None:
        """Test basic initialization with real objects."""
        trace = ExecutionStepTrace(
            step=0, proposed={}, validated={}, resolved={}, proposing_mechanisms={}
        )

        assert trace.step == 0
        assert trace.proposed == {}
        assert trace.validated == {}
        assert trace.resolved == {}
        assert trace.proposing_mechanisms == {}

    def test_initialization_with_data(self, sample_key, sample_variable_record) -> None:
        """Test initialization with actual data."""
        # Create multiple VariableRecords for testing sequences
        record2 = VariableRecord(value="another_value")

        trace = ExecutionStepTrace(
            step=42,
            proposed={sample_key: [sample_variable_record, record2]},
            validated={sample_key: [sample_variable_record]},
            resolved={sample_key: None},  # Testing None value
            proposing_mechanisms={sample_key: [sample_key, None]},
        )

        assert trace.step == 42
        assert len(trace.proposed[sample_key]) == 2
        assert len(trace.validated[sample_key]) == 1
        assert trace.resolved[sample_key] is None
        assert len(trace.proposing_mechanisms[sample_key]) == 2

    def test_immutability(self, sample_execution_step_trace) -> None:
        """Test that the dataclass is immutable (frozen)."""
        trace = sample_execution_step_trace

        # Should not be able to modify attributes
        with pytest.raises(FrozenInstanceError):
            trace.step = 999

        with pytest.raises(FrozenInstanceError):
            trace.proposed = {}

    def test_slots(self) -> None:
        """Test that the dataclass uses __slots__."""
        # Check that __slots__ is defined
        assert hasattr(ExecutionStepTrace, "__slots__")

        # Verify slots prevent dynamic attribute creation
        trace = ExecutionStepTrace(
            step=1, proposed={}, validated={}, resolved={}, proposing_mechanisms={}
        )

        with pytest.raises(TypeError):
            trace.non_existent_attribute = "should fail"

    def test_equality(self, sample_key, sample_variable_record) -> None:
        """Test equality comparison between instances."""
        trace1 = ExecutionStepTrace(
            step=1,
            proposed={sample_key: [sample_variable_record]},
            validated={sample_key: [sample_variable_record]},
            resolved={sample_key: sample_variable_record},
            proposing_mechanisms={sample_key: [sample_key]},
        )

        trace2 = ExecutionStepTrace(
            step=1,
            proposed={sample_key: [sample_variable_record]},
            validated={sample_key: [sample_variable_record]},
            resolved={sample_key: sample_variable_record},
            proposing_mechanisms={sample_key: [sample_key]},
        )

        assert trace1 == trace2

    def test_inequality_different_step(
        self, sample_key, sample_variable_record
    ) -> None:
        """Test inequality when steps differ."""
        trace1 = ExecutionStepTrace(
            step=1,
            proposed={sample_key: [sample_variable_record]},
            validated={sample_key: [sample_variable_record]},
            resolved={sample_key: sample_variable_record},
            proposing_mechanisms={sample_key: [sample_key]},
        )

        trace2 = ExecutionStepTrace(
            step=2,  # Different step
            proposed={sample_key: [sample_variable_record]},
            validated={sample_key: [sample_variable_record]},
            resolved={sample_key: sample_variable_record},
            proposing_mechanisms={sample_key: [sample_key]},
        )

        assert trace1 != trace2

    def test_repr(self, sample_execution_step_trace) -> None:
        """Test string representation."""
        repr_str = repr(sample_execution_step_trace)
        assert "ExecutionStepTrace" in repr_str
        assert "step=" in repr_str
        # Additional checks can be added based on actual repr output

    def test_empty_sequences_and_mappings(self) -> None:
        """Test with empty containers."""
        trace = ExecutionStepTrace(
            step=0, proposed={}, validated={}, resolved={}, proposing_mechanisms={}
        )

        assert isinstance(trace.proposed, Mapping)
        assert isinstance(trace.validated, Mapping)
        assert isinstance(trace.resolved, Mapping)
        assert isinstance(trace.proposing_mechanisms, Mapping)

    def test_none_resolved_value(self, sample_key) -> None:
        """Test that resolved values can be None."""
        trace = ExecutionStepTrace(
            step=1,
            proposed={sample_key: []},
            validated={sample_key: []},
            resolved={sample_key: None},
            proposing_mechanisms={sample_key: []},
        )

        assert trace.resolved[sample_key] is None

    def test_multiple_keys(self, sample_key, sample_variable_record) -> None:
        """Test with multiple keys in mappings."""
        key2 = Key()
        record2 = VariableRecord(value="value2")

        trace = ExecutionStepTrace(
            step=1,
            proposed={sample_key: [sample_variable_record], key2: [record2]},
            validated={sample_key: [sample_variable_record], key2: [record2]},
            resolved={sample_key: sample_variable_record, key2: record2},
            proposing_mechanisms={sample_key: [sample_key], key2: [key2]},
        )

        assert len(trace.proposed) == 2
        assert len(trace.validated) == 2
        assert len(trace.resolved) == 2
        assert len(trace.proposing_mechanisms) == 2


# Edge cases and type validation tests
class TestExecutionStepTraceEdgeCases:
    """Test edge cases and type validation."""

    def test_none_in_sequences(self, sample_key, sample_variable_record) -> None:
        """Test that sequences can contain None values."""
        trace = ExecutionStepTrace(
            step=1,
            proposed={sample_key: [sample_variable_record, None]},
            validated={sample_key: [None, sample_variable_record]},
            resolved={sample_key: sample_variable_record},
            proposing_mechanisms={sample_key: [None, sample_key]},
        )

        assert None in trace.proposed[sample_key]
        assert None in trace.validated[sample_key]
        assert None in trace.proposing_mechanisms[sample_key]

    def test_empty_sequences_in_mappings(self, sample_key) -> None:
        """Test mappings with empty sequences."""
        trace = ExecutionStepTrace(
            step=1,
            proposed={sample_key: []},
            validated={sample_key: []},
            resolved={sample_key: None},
            proposing_mechanisms={sample_key: []},
        )

        assert trace.proposed[sample_key] == []
        assert trace.validated[sample_key] == []
        assert trace.proposing_mechanisms[sample_key] == []
