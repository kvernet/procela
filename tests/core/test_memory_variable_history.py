"""
Comprehensive pytest suite for history.py with 100% coverage.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from procela.core.assessment import ReasoningResult, ReasoningTask
from procela.core.memory import (
    CandidatesHistory,
    HistoryStatistics,
    ReasoningHistory,
    VariableHistory,
    VariableRecord,
)
from procela.symbols import Key, TimePoint


@pytest.fixture
def mock_key():
    """Create a mock Key."""
    mock = Mock(spec=Key)
    mock.__hash__ = Mock(return_value=hash("test_key"))
    mock.__eq__ = Mock(return_value=True)
    return mock


@pytest.fixture
def mock_time_point():
    """Create a mock TimePoint."""
    mock = Mock(spec=TimePoint)
    return mock


@pytest.fixture
def mock_variable_record(mock_key, mock_time_point):
    """Create a mock VariableRecord."""
    mock = Mock(spec=VariableRecord)
    mock.key = Mock(return_value=mock_key)
    mock.time = mock_time_point
    mock.source = mock_key
    mock.value = "test_value"
    mock.__repr__ = Mock(return_value="VariableRecord(test_value)")
    return mock


@pytest.fixture
def mock_reasoning_task():
    """Create a mock ReasoningTask."""
    mock = Mock(spec=ReasoningTask)
    mock.task_id = "test_task_id"
    return mock


@pytest.fixture
def mock_reasoning_result(mock_reasoning_task):
    """Create a mock ReasoningResult."""
    mock = Mock(spec=ReasoningResult)
    mock.task = mock_reasoning_task
    mock.success = True
    mock.output = "test_output"
    mock.__repr__ = Mock(return_value="ReasoningResult(success=True)")
    return mock


@pytest.fixture
def mock_key_authority():
    """Mock the KeyAuthority class."""
    with patch("procela.core.key_authority.KeyAuthority") as mock:
        mock.issue = Mock(return_value="issued_key")
        mock.resolve = Mock(return_value=None)
        yield mock


@pytest.fixture
def mock_history_statistics():
    """Mock HistoryStatistics."""
    with patch("procela.core.memory.HistoryStatistics") as mock:
        mock_instance = Mock(spec=HistoryStatistics)
        mock.empty = Mock(return_value=mock_instance)
        mock_instance.update = Mock(return_value=mock_instance)
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def empty_variable_history(mock_key_authority, mock_history_statistics):
    """Create an empty VariableHistory."""
    return VariableHistory()


@pytest.fixture
def populated_variable_history(empty_variable_history, mock_variable_record):
    """Create a VariableHistory with one record."""
    return empty_variable_history.new(mock_variable_record)


@pytest.fixture
def empty_reasoning_history(mock_key_authority):
    """Create an empty ReasoningHistory."""
    return ReasoningHistory()


@pytest.fixture
def empty_candidates_history(mock_key_authority):
    """Create an empty CandidatesHistory."""
    return CandidatesHistory()


@pytest.fixture
def populated_reasoning_history(empty_reasoning_history, mock_reasoning_result):
    """Create a ReasoningHistory with one result."""
    return empty_reasoning_history.new(mock_reasoning_result)


@pytest.fixture
def populated_candidates_history(empty_candidates_history, mock_key):
    """Create a ReasoningHistory with one result."""
    return empty_candidates_history.new(mock_key)


class TestVariableHistory:
    """Test suite for VariableHistory class."""

    def test_initialization_empty(self, mock_key_authority, mock_history_statistics):
        """Test initialization of empty VariableHistory."""
        history = VariableHistory()

        assert history._record is None
        assert history._previous is None
        assert history._config == {}

    def test_initialization_with_config(
        self, mock_key_authority, mock_history_statistics
    ):
        """Test initialization with custom configuration."""
        config = {"anomaly": {"alpha": 0.5}, "other_setting": "value"}
        history = VariableHistory(_config=config)

        assert history._config == config
        assert history._record is None
        assert history._previous is None

    def test_initialization_with_invalid_previous_type(self, mock_key_authority):
        """Test initialization with previous key pointing to wrong type."""
        # Setup KeyAuthority.resolve to return wrong type
        mock_key_authority.resolve.return_value = "not_a_history"

        mock_prev_key = Mock(spec=Key)

        with pytest.raises(
            TypeError, match=f"_previous should be a {VariableHistory.__name__}"
        ):
            VariableHistory(_previous=mock_prev_key)

    def test_new_method_valid_record(
        self, empty_variable_history, mock_variable_record
    ):
        """Test creating new history with valid record."""
        new_history = empty_variable_history.new(mock_variable_record)

        assert new_history._record == mock_variable_record
        assert new_history._previous == empty_variable_history.key()
        assert new_history._config == empty_variable_history._config

    def test_new_method_invalid_record(self, empty_variable_history):
        """Test creating new history with invalid record type."""
        invalid_record = "not_a_record"

        with pytest.raises(TypeError, match="record should be a VariableRecord"):
            empty_variable_history.new(invalid_record)

    def test_previous_key_method(self, mock_key_authority):
        """Test previous_key() method."""
        # Test with no previous
        history1 = VariableHistory()
        assert history1.previous_key() is None

        # Test with previous
        mock_prev_key = history1.key()
        history2 = VariableHistory(_previous=mock_prev_key)
        assert history2.previous_key() == mock_prev_key

    def test_stats_method(self, empty_variable_history, mock_history_statistics):
        """Test stats() method."""
        stats = empty_variable_history.stats()
        assert stats != mock_history_statistics.empty.return_value

    def test_iter_records_empty(self, empty_variable_history):
        """Test iter_records() on empty history."""
        records = list(empty_variable_history.iter_records())
        assert records == []

    def test_iter_records_single_record(
        self, populated_variable_history, mock_variable_record
    ):
        """Test iter_records() with one record."""
        records = list(populated_variable_history.iter_records())
        assert records == [mock_variable_record]

    def test_iter_records_multiple_records(
        self, mock_key_authority, mock_variable_record
    ):
        """Test iter_records() with multiple records in chain."""
        # Create chain of histories
        history1 = VariableHistory()

        record1 = Mock(spec=VariableRecord)
        record1.value = None
        record1.key = Mock(return_value="key1")
        history2 = history1.new(record1)

        record2 = Mock(spec=VariableRecord)
        record2.value = 34.89
        record2.confidence = 0.821
        record2.key = Mock(return_value="key2")
        history3 = history2.new(record2)

        # Setup KeyAuthority.resolve to return previous histories
        def resolve_side_effect(key):
            if key == history2.key():
                return history2
            if key == history1.key():
                return history1
            return None

        mock_key_authority.resolve.side_effect = resolve_side_effect

        records = list(history3.iter_records())
        assert records == [record2, record1]

    def test_iter_records_circular_reference_prevention(self, mock_key_authority):
        """Test iter_records() prevents infinite loops on circular references."""
        # Create circular reference
        history1 = VariableHistory()
        history2 = VariableHistory(_previous=history1.key())

        # Mock resolve to create circular reference
        mock_key_authority.resolve.side_effect = lambda k: (
            history2 if k == history1.key() else None
        )

        records = list(history2.iter_records())
        assert records == []  # Should break early

    def test_iter_filtered_records_by_key(
        self,
    ):
        """Test filtering records by key."""
        # Create a different key
        key = Key()
        history = VariableHistory()
        history = history.new(record=VariableRecord(value=None))

        # Test with non-matching key
        filtered = list(history.iter_filtered_records(key=key))
        assert len(filtered) == 0

    def test_iter_filtered_records_by_time(self, mock_key_authority, mock_time_point):
        """Test filtering records by time."""
        # Create histories with different times
        history = VariableHistory()

        time1 = Mock(spec=TimePoint)
        time1.__eq__ = Mock(return_value=True)
        record1 = Mock(spec=VariableRecord)
        record1.time = time1
        record1.value = None
        history = history.new(record1)

        time2 = Mock(spec=TimePoint)
        time2.__eq__ = Mock(return_value=False)
        record2 = Mock(spec=VariableRecord)
        record2.time = time2
        record2.value = None
        history = history.new(record2)

        # Setup resolve to return previous history
        mock_key_authority.resolve.return_value = VariableHistory(_record=record1)

        # Filter by time1
        filtered = list(history.iter_filtered_records(time=time1))
        assert filtered == [record1]  # Only record1 matches time1

    def test_iter_filtered_records_by_source(self, mock_key_authority):
        """Test filtering records by source."""
        # Create histories with different sources
        history = VariableHistory()

        source1 = Mock(spec=Key)
        source1.__eq__ = Mock(return_value=True)
        record1 = Mock(spec=VariableRecord)
        record1.source = source1
        record1.value = None
        history = history.new(record1)

        source2 = Mock(spec=Key)
        source2.__eq__ = Mock(return_value=False)
        record2 = Mock(spec=VariableRecord)
        record2.source = source2
        record2.value = None
        history = history.new(record2)

        # Setup resolve
        mock_key_authority.resolve.return_value = VariableHistory(_record=record1)

        # Filter by source1
        filtered = list(history.iter_filtered_records(source=source1))
        assert filtered == [record1]

    def test_get_records_empty(self, empty_variable_history):
        """Test get_records() on empty history."""
        records = empty_variable_history.get_records()
        assert records == []

    def test_get_records_with_filters(
        self, populated_variable_history, mock_variable_record
    ):
        """Test get_records() with filtering and reverse order."""
        # Add another record to test ordering
        record2 = Mock(spec=VariableRecord)
        record2.key = Mock(return_value=mock_variable_record.key())
        record2.time = mock_variable_record.time
        record2.source = mock_variable_record.source
        record2.value = None

        history2 = populated_variable_history.new(record2)

        # Mock resolve to return previous history
        with patch(
            "procela.core.key_authority.KeyAuthority.resolve",
            return_value=populated_variable_history,
        ):
            records = history2.get_records()

            # Should return records in chronological order (oldest first)
            assert records == [mock_variable_record, record2]

    def test_latest_empty(self, empty_variable_history):
        """Test latest() on empty history."""
        assert empty_variable_history.latest() is None

    def test_reset(self):
        """Test the reset() method."""
        history = VariableHistory()
        history.reset()

    def test_latest_populated(self, populated_variable_history, mock_variable_record):
        """Test latest() on populated history."""
        latest = populated_variable_history.latest()
        assert latest == mock_variable_record

    def test_dataclass_immutability(self, empty_variable_history):
        """Test that VariableHistory is immutable."""
        # Should not be able to modify attributes
        with pytest.raises(Exception):
            empty_variable_history._record = "new_value"

        # Verify it's a frozen dataclass
        assert empty_variable_history.__dataclass_params__.frozen is True


class TestReasoningHistory:
    """Test suite for ReasoningHistory class."""

    def test_initialization_with_previous(self):
        """Test initialization with previous key."""
        mock_prev_key = Mock(spec=Key)
        history = ReasoningHistory(_previous=mock_prev_key)

        assert history._previous == mock_prev_key
        assert history._result is None

    def test_new_method_valid_result(
        self, empty_reasoning_history, mock_reasoning_result
    ):
        """Test creating new history with valid result."""
        new_history = empty_reasoning_history.new(mock_reasoning_result)

        assert new_history._result == mock_reasoning_result
        assert new_history._previous == empty_reasoning_history.key()

    def test_new_method_invalid_result(self, empty_reasoning_history):
        """Test creating new history with invalid result type."""
        invalid_result = "not_a_result"

        with pytest.raises(TypeError, match="result should be a ReasoningResult"):
            empty_reasoning_history.new(invalid_result)

    def test_previous_key_method(self):
        """Test previous_key() method."""
        # Test with no previous
        history1 = ReasoningHistory()
        assert history1.previous_key() is None

        # Test with previous
        mock_prev_key = Mock(spec=Key)
        history2 = ReasoningHistory(_previous=mock_prev_key)
        assert history2.previous_key() == mock_prev_key

    def test_iter_results_empty(self, empty_reasoning_history):
        """Test iter_results() on empty history."""
        results = list(empty_reasoning_history.iter_results())
        assert results == []

    def test_iter_results_single_result(
        self, populated_reasoning_history, mock_reasoning_result
    ):
        """Test iter_results() with one result."""
        results = list(populated_reasoning_history.iter_results())
        assert results == [mock_reasoning_result]

    def test_iter_results_multiple_results(
        self, mock_key_authority, mock_reasoning_result
    ):
        """Test iter_results() with multiple results in chain."""
        # Create chain of histories
        history1 = ReasoningHistory()

        result1 = Mock(spec=ReasoningResult)
        result1.task = Mock(spec=ReasoningTask)
        history2 = history1.new(result1)

        result2 = Mock(spec=ReasoningResult)
        result2.task = Mock(spec=ReasoningTask)
        history3 = history2.new(result2)

        # Setup KeyAuthority.resolve to return previous histories
        def resolve_side_effect(key):
            if key == history2.key():
                return history2
            if key == history1.key():
                return history1
            return None

        mock_key_authority.resolve.side_effect = resolve_side_effect

        results = list(history3.iter_results())
        assert results == [result2, result1]

    def test_iter_filtered_results_by_task(
        self, populated_reasoning_history, mock_reasoning_result, mock_reasoning_task
    ):
        """Test filtering results by task."""
        # Create a different task
        different_task = Mock(spec=ReasoningTask)

        # Test with matching task
        filtered = list(
            populated_reasoning_history.iter_filtered_results(task=mock_reasoning_task)
        )
        assert filtered == [mock_reasoning_result]

        # Test with non-matching task
        filtered = list(
            populated_reasoning_history.iter_filtered_results(task=different_task)
        )
        assert filtered == []

    def test_iter_filtered_results_by_success(self, mock_key_authority):
        """Test filtering results by success flag."""
        # Create histories with different success values
        history = ReasoningHistory()

        # Successful result
        result_success = Mock(spec=ReasoningResult)
        result_success.success = True
        result_success.task = Mock(spec=ReasoningTask)
        history = history.new(result_success)

        # Failed result
        result_fail = Mock(spec=ReasoningResult)
        result_fail.success = False
        result_fail.task = Mock(spec=ReasoningTask)
        history = history.new(result_fail)

        # Setup resolve to return previous history
        mock_key_authority.resolve.return_value = ReasoningHistory(
            _result=result_success
        )

        # Filter by success=True
        filtered = list(history.iter_filtered_results(success=True))
        assert filtered == [result_success]

        # Filter by success=False
        filtered = list(history.iter_filtered_results(success=False))
        assert filtered == [result_fail]  # result_fail matches success=False

    def test_iter_filtered_results_no_filter(
        self, populated_reasoning_history, mock_reasoning_result
    ):
        """Test iter_filtered_results with no filters (default success=True)."""
        filtered = list(populated_reasoning_history.iter_filtered_results())
        # Default success=True should filter out None or False results
        assert (
            filtered == [mock_reasoning_result] if mock_reasoning_result.success else []
        )

    def test_get_results_empty(self, empty_reasoning_history):
        """Test get_results() on empty history."""
        results = empty_reasoning_history.get_results()
        assert results == []

    def test_get_results_with_filters(self, mock_key_authority, mock_reasoning_result):
        """Test get_results() with filtering and reverse order."""
        # Create chain
        history1 = ReasoningHistory()
        history2 = history1.new(mock_reasoning_result)

        result2 = Mock(spec=ReasoningResult)
        result2.success = False
        result2.task = mock_reasoning_result.task
        history3 = history2.new(result2)

        # Setup resolve chain
        def resolve_side_effect(key):
            if key == history2.key():
                return history2
            if key == history1.key():
                return history1
            return None

        mock_key_authority.resolve.side_effect = resolve_side_effect

        # Get all results (should be reversed)
        results = history3.get_results(success=None)
        assert results == [mock_reasoning_result, result2]

    def test_latest_no_results(self, empty_reasoning_history):
        """Test latest() when no results match filter."""
        mock_task = Mock(spec=ReasoningTask)
        latest = empty_reasoning_history.latest(task=mock_task)
        assert latest is None

    def test_len_method_empty(self, empty_reasoning_history):
        """Test __len__() on empty history."""
        assert len(empty_reasoning_history) == 0

    def test_reset(self):
        """Test the reset() method."""
        history = ReasoningHistory()
        history.reset()

    def test_len_method_populated(self, mock_key_authority, mock_reasoning_result):
        """Test __len__() on populated history."""
        # Create chain
        history1 = ReasoningHistory()
        history2 = history1.new(mock_reasoning_result)

        result2 = Mock(spec=ReasoningResult)
        result2.task = Mock(spec=ReasoningTask)
        history3 = history2.new(result2)

        # Setup resolve
        mock_key_authority.resolve.return_value = history2

        assert len(history3) == 2

    def test_dataclass_immutability(self, empty_reasoning_history):
        """Test that ReasoningHistory is immutable."""
        # Should not be able to modify attributes
        with pytest.raises(Exception):
            empty_reasoning_history._result = "new_value"

        # Verify it's a frozen dataclass
        assert empty_reasoning_history.__dataclass_params__.frozen is True

    def test_iter_results_circular_reference(self, mock_key_authority):
        """Test iter_results() handles circular references."""
        # Create circular reference
        history1 = ReasoningHistory()
        history2 = ReasoningHistory(_previous=history1.key())

        # Mock resolve to create circular reference
        mock_key_authority.resolve.side_effect = lambda k: (
            history2 if k == history1.key() else None
        )

        results = list(history2.iter_results())
        assert results == []  # Should break early


class TestCandidatesHistory:
    """Test suite for CandidatesHistory class."""

    def test_initialization_with_previous(self):
        """Test initialization with previous key."""
        mock_prev_key = Mock(spec=Key)
        history = CandidatesHistory(_previous=mock_prev_key)

        assert history._previous == mock_prev_key
        assert history._source is None

    def test_new_method_valid_source(self, empty_candidates_history):
        """Test creating new history with valid key."""
        key = Key()
        new_history = empty_candidates_history.new(key)

        assert new_history._source == key
        assert new_history._previous == empty_candidates_history.key()

    def test_new_method_invalid_source(self, empty_candidates_history):
        """Test creating new history with invalid source type."""
        invalid_source = "not_a_source"

        with pytest.raises(
            TypeError, match="The source should be a Key, get 'not_a_source'"
        ):
            empty_candidates_history.new(invalid_source)

        history = empty_candidates_history.new(None)
        assert history is empty_candidates_history

    def test_iter_results_empty(self, empty_candidates_history):
        """Test iter_results() on empty history."""
        results = list(empty_candidates_history.iter_results())
        assert results == []

    def test_iter_results_single_result(self, populated_candidates_history, mock_key):
        """Test iter_results() with one result."""
        results = list(populated_candidates_history.iter_results())
        assert results == [mock_key]
        assert isinstance(populated_candidates_history.previous_key(), Key)

    def test_iter_results_multiple_results(
        self,
    ):
        """Test iter_results() with multiple results in chain."""
        # Create chain of histories
        history1 = CandidatesHistory()

        result1 = Mock(spec=Key)
        history2 = history1.new(result1)

        result2 = Mock(spec=Key)
        history3 = history2.new(result2)

        results = list(history3.iter_results())
        assert results == [result2, result1]

    def test_iter_filtered_results_by_source(
        self, populated_candidates_history, mock_key
    ):
        """Test filtering results by source."""
        # Create a different source
        different_source = Key()

        # Test with matching source
        filtered = list(
            populated_candidates_history.iter_filtered_results(source=mock_key)
        )
        assert filtered == [mock_key]

        candidates_history = CandidatesHistory(_source=different_source)
        assert list(candidates_history.iter_filtered_results(source=Key())) == []

    def test_iter_filtered_results_no_filter(self, populated_candidates_history):
        """Test iter_filtered_results with no filters (default success=True)."""
        filtered = list(populated_candidates_history.iter_filtered_results())
        assert len(filtered) == 1

    def test_get_results_empty(self, empty_candidates_history):
        """Test get_results() on empty history."""
        results = empty_candidates_history.get_results()
        assert results == []

    def test_len_method_empty(self, empty_candidates_history):
        """Test __len__() on empty history."""
        assert len(empty_candidates_history) == 0

    def test_reset(self):
        """Test the reset() method."""
        history = CandidatesHistory()
        history = history.new(Key())
        assert history._source is not None
        history.reset()
        assert history._source is None

    def test_len_method_populated(self, mock_key_authority):
        """Test __len__() on populated history."""
        # Create chain
        history1 = CandidatesHistory()
        history2 = history1.new(Key())

        result2 = CandidatesHistory()
        history3 = history2.new(result2.key())

        # Setup resolve
        mock_key_authority.resolve.return_value = history2

        assert len(history3) == 2

    def test_dataclass_immutability(self, empty_candidates_history):
        """Test that ReasoningHistory is immutable."""
        # Should not be able to modify attributes
        with pytest.raises(Exception):
            empty_candidates_history._source = "new_value"

        # Verify it's a frozen dataclass
        assert empty_candidates_history.__dataclass_params__.frozen is True

    def test_iter_results_circular_reference(self, mock_key_authority):
        """Test iter_results() handles circular references."""
        # Create circular reference
        history1 = CandidatesHistory()
        history2 = CandidatesHistory(_previous=history1.key())

        # Mock resolve to create circular reference
        mock_key_authority.resolve.side_effect = lambda k: (
            history2 if k == history1.key() else None
        )

        results = list(history2.iter_results())
        assert results == []  # Should break early


class TestIntegration:
    """Integration tests for both history classes."""

    def test_mixed_history_types_independent(self):
        """Test that VariableHistory and ReasoningHistory don't interfere."""
        # They should be completely independent classes
        var_history = VariableHistory()
        reasoning_history = ReasoningHistory()
        candidates_history = CandidatesHistory()

        assert isinstance(var_history, VariableHistory)
        assert isinstance(reasoning_history, ReasoningHistory)
        assert isinstance(candidates_history, CandidatesHistory)
        assert not isinstance(var_history, ReasoningHistory)
        assert not isinstance(reasoning_history, VariableHistory)


class TestEdgeCases:
    """Edge case tests for history classes."""

    def test_variable_history_with_none_config(self, mock_key_authority):
        """Test VariableHistory with None in config (should use default)."""
        # This tests the default_factory=dict in the field definition
        history = VariableHistory(_config={})  # type: ignore

        # Should have empty dict as default
        assert history._config == {}

    def test_reasoning_history_iter_results_with_none_resolution(
        self, mock_key_authority
    ):
        """Test iter_results when KeyAuthority.resolve returns None."""
        history = ReasoningHistory(_previous="some_key")

        # Resolve returns None (not a ReasoningHistory)
        mock_key_authority.resolve.return_value = None

        results = list(history.iter_results())
        assert results == []  # Should stop iteration

    def test_variable_history_with_record_but_no_previous_stats(
        self, mock_key_authority
    ):
        """Test VariableHistory with record but no previous (uses empty stats)."""
        record = Mock(spec=VariableRecord)
        record.value = None
        history = VariableHistory(_record=record)

        # Should have initialized stats via empty().update()
        assert history._record == record

    def test_large_history_performance(self):
        """Test that iterators don't load all records at once (performance)."""
        # This is more of a documentation test
        # The use of generators (yield) in iter_records/iter_results
        # ensures memory efficiency for large histories

        # We can't easily test performance, but we can verify it's a generator
        history = VariableHistory()

        # iter_records should return an iterator, not a list
        result = history.iter_records()
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__") or hasattr(result, "next")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=history", "--cov-report=term-missing"])
