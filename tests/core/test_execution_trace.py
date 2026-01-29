"""Tests for ExecutionTrace class."""

from __future__ import annotations

from typing import Iterator

import pytest

from procela.core.execution import ExecutionStepTrace, ExecutionTrace
from procela.core.memory import VariableRecord
from procela.symbols.key import Key


@pytest.fixture
def sample_key() -> Key:
    return Key()


@pytest.fixture
def sample_variable_record() -> VariableRecord:
    return VariableRecord(value="test_value")


@pytest.fixture
def sample_execution_step_trace(
    sample_key, sample_variable_record
) -> ExecutionStepTrace:
    return ExecutionStepTrace(
        step=1,
        proposed={sample_key: [sample_variable_record]},
        validated={sample_key: [sample_variable_record]},
        resolved={sample_key: sample_variable_record},
        proposing_mechanisms={sample_key: [sample_key]},
    )


class TestExecutionTrace:
    """Test suite for ExecutionTrace class."""

    def test_initialization(self) -> None:
        """Test basic initialization."""

        trace = ExecutionTrace()
        assert len(trace) == 0
        assert list(trace) == []

    def test_append_and_len(self, sample_execution_step_trace) -> None:
        """Test append method and length property."""

        trace = ExecutionTrace()
        assert len(trace) == 0

        trace.append(sample_execution_step_trace)
        assert len(trace) == 1

        # Append another trace
        another_trace = ExecutionStepTrace(
            step=2, proposed={}, validated={}, resolved={}, proposing_mechanisms={}
        )
        trace.append(another_trace)
        assert len(trace) == 2

    def test_iteration(self, sample_execution_step_trace) -> None:
        """Test iteration over traces."""

        trace = ExecutionTrace()
        trace.append(sample_execution_step_trace)

        # Create another trace
        another_trace = ExecutionStepTrace(
            step=2, proposed={}, validated={}, resolved={}, proposing_mechanisms={}
        )
        trace.append(another_trace)

        # Test iteration
        steps = list(trace)
        assert len(steps) == 2
        assert steps[0] == sample_execution_step_trace
        assert steps[1] == another_trace

        # Test iterator type
        iterator = iter(trace)
        assert isinstance(iterator, Iterator)
        assert next(iterator) == sample_execution_step_trace
        assert next(iterator) == another_trace

        # Test exhaustion
        with pytest.raises(StopIteration):
            next(iterator)

    def test_last_with_no_steps(self) -> None:
        """Test last() method when no steps are present."""

        trace = ExecutionTrace()
        assert trace.last() is None

    def test_last_with_one_step(self, sample_execution_step_trace) -> None:
        """Test last() method with one step."""

        trace = ExecutionTrace()
        trace.append(sample_execution_step_trace)
        assert trace.last() == sample_execution_step_trace

    def test_last_with_multiple_steps(self, sample_execution_step_trace) -> None:
        """Test last() method with multiple steps."""

        trace = ExecutionTrace()

        # Add first trace
        trace.append(sample_execution_step_trace)
        assert trace.last() == sample_execution_step_trace

        # Add second trace
        second_trace = ExecutionStepTrace(
            step=2, proposed={}, validated={}, resolved={}, proposing_mechanisms={}
        )
        trace.append(second_trace)
        assert trace.last() == second_trace

        # Add third trace
        third_trace = ExecutionStepTrace(
            step=3, proposed={}, validated={}, resolved={}, proposing_mechanisms={}
        )
        trace.append(third_trace)
        assert trace.last() == third_trace

    def test_sequential_operations(self) -> None:
        """Test sequential operations to ensure proper state management."""

        trace = ExecutionTrace()

        # Initial state
        assert len(trace) == 0
        assert trace.last() is None
        assert list(trace) == []

        # Add first step
        step1 = ExecutionStepTrace(
            step=1, proposed={}, validated={}, resolved={}, proposing_mechanisms={}
        )
        trace.append(step1)

        assert len(trace) == 1
        assert trace.last() == step1
        assert list(trace) == [step1]

        # Add second step
        step2 = ExecutionStepTrace(
            step=2, proposed={}, validated={}, resolved={}, proposing_mechanisms={}
        )
        trace.append(step2)

        assert len(trace) == 2
        assert trace.last() == step2
        assert list(trace) == [step1, step2]

        # Test iteration after multiple appends
        iteration_count = 0
        for i, step in enumerate(trace):
            if i == 0:
                assert step == step1
            elif i == 1:
                assert step == step2
            iteration_count += 1
        assert iteration_count == 2

    def test_empty_iteration(self) -> None:
        """Test iteration when trace is empty."""

        trace = ExecutionTrace()
        steps = list(trace)
        assert steps == []

        # Manual iteration
        iterator = iter(trace)
        with pytest.raises(StopIteration):
            next(iterator)

    def test_is_sequence_like(self) -> None:
        """Test that ExecutionTrace behaves like a sequence."""

        trace = ExecutionTrace()

        # It should support len()
        assert len(trace) == 0

        # It should be iterable
        assert hasattr(trace, "__iter__")

        # Add items and test
        step1 = ExecutionStepTrace(
            step=1, proposed={}, validated={}, resolved={}, proposing_mechanisms={}
        )
        step2 = ExecutionStepTrace(
            step=2, proposed={}, validated={}, resolved={}, proposing_mechanisms={}
        )

        trace.append(step1)
        trace.append(step2)

        # Convert to list
        steps_list = list(trace)
        assert isinstance(steps_list, list)
        assert steps_list == [step1, step2]

    def test_multiple_appends_same_trace(self, sample_execution_step_trace) -> None:
        """Test appending the same trace multiple times."""

        trace = ExecutionTrace()

        # Append same trace multiple times
        trace.append(sample_execution_step_trace)
        trace.append(sample_execution_step_trace)
        trace.append(sample_execution_step_trace)

        assert len(trace) == 3
        assert list(trace) == [
            sample_execution_step_trace,
            sample_execution_step_trace,
            sample_execution_step_trace,
        ]

        # Last should be the last appended (even if same object)
        assert trace.last() == sample_execution_step_trace


class TestExecutionTraceTypeAnnotations:
    """Test type-related aspects of ExecutionTrace."""

    def test_append_type_safety(self) -> None:
        """Test that append only accepts ExecutionStepTrace."""

        trace = ExecutionTrace()

        # Valid append
        step_trace = ExecutionStepTrace(
            step=1, proposed={}, validated={}, resolved={}, proposing_mechanisms={}
        )
        trace.append(step_trace)  # This should work

        # Type checker would catch this, but we can test runtime behavior
        # Note: Python runtime doesn't enforce type hints without a type checker
        assert len(trace) == 1

    def test_iter_return_type(self) -> None:
        """Test that __iter__ returns an Iterator."""

        trace = ExecutionTrace()
        iterator = trace.__iter__()

        # Check it's an iterator by protocol
        assert hasattr(iterator, "__next__")
        assert hasattr(iterator, "__iter__")

        # Iterator should return itself when iter is called on it
        assert iter(iterator) is iterator
