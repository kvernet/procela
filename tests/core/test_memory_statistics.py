"""Test suite for procela.core.memory.variable.statistics module."""

import math
from unittest.mock import Mock

import pytest

from procela.core.assessment import StatisticsResult
from procela.core.memory import MemoryStatistics, VariableRecord
from procela.symbols.key import Key


class TestMemoryStatistics:
    """Test suite for MemoryStatistics class."""

    def test_empty_factory_method(self):
        """Test the empty() factory method creates correct empty instance."""
        stats = MemoryStatistics.empty()

        assert stats.count == 0
        assert stats.sum is None
        assert stats.sumsq is None
        assert stats.min is None
        assert stats.max is None
        assert stats.last_value is None
        assert stats.confidence_sum == 0.0
        assert stats.ewma is None
        assert stats.sources == frozenset()

    def test_default_initialization(self):
        """Test default initialization values."""
        stats = MemoryStatistics()

        assert stats.count == 0
        assert stats.sum is None
        assert stats.sumsq is None
        assert stats.min is None
        assert stats.max is None
        assert stats.last_value is None
        assert stats.confidence_sum == 0.0
        assert stats.ewma is None
        assert stats.sources == frozenset()

    def test_initialization_with_values(self):
        """Test initialization with custom values."""
        key1 = Key()
        key2 = Key()
        sources = frozenset([key1, key2])

        stats = MemoryStatistics(
            count=5,
            sum=25.0,
            sumsq=155.0,
            min=3.0,
            max=7.0,
            last_value=6.5,
            confidence_sum=4.2,
            ewma=5.8,
            sources=sources,
        )

        assert stats.count == 5
        assert stats.sum == 25.0
        assert stats.sumsq == 155.0
        assert stats.min == 3.0
        assert stats.max == 7.0
        assert stats.last_value == 6.5
        assert stats.confidence_sum == 4.2
        assert stats.ewma == 5.8
        assert stats.sources == sources
        assert len(stats.sources) == 2

    def test_update_no_record(self):
        """Test update method with no record."""

        # Start with empty statistics
        initial_stats = MemoryStatistics.empty()
        updated_stats = initial_stats.update(None)

        result = updated_stats.result()
        assert isinstance(result, StatisticsResult)
        assert result.count == 1

    def test_update_with_numeric_value(self):
        """Test update method with numeric value."""
        # Create a mock record with numeric value
        mock_record = Mock(spec=VariableRecord)
        mock_record.value = 10.5
        mock_record.confidence = 0.8
        mock_record.source = None

        # Start with empty statistics
        initial_stats = MemoryStatistics.empty()
        updated_stats = initial_stats.update(mock_record)

        assert updated_stats.count == 1
        assert updated_stats.sum == 10.5
        assert updated_stats.sumsq == 10.5**2
        assert updated_stats.min == 10.5
        assert updated_stats.max == 10.5
        assert updated_stats.last_value == 10.5
        assert updated_stats.confidence_sum == 0.8
        assert updated_stats.ewma == 10.5  # First value, so EWMA = value
        assert updated_stats.sources == frozenset()

    def test_update_with_non_numeric_value(self):
        """Test update method with non-numeric value."""
        # Create a mock record with non-numeric value
        mock_record = Mock(spec=VariableRecord)
        mock_record.value = "not a number"
        mock_record.confidence = 0.8
        mock_record.source = None

        # Start with some initial statistics
        initial_stats = MemoryStatistics(
            count=3,
            sum=15.0,
            sumsq=85.0,
            min=4.0,
            max=6.0,
            last_value=5.0,
            confidence_sum=2.4,
            ewma=5.2,
            sources=frozenset(),
        )

        updated_stats = initial_stats.update(mock_record)

        assert updated_stats.count == 4
        assert updated_stats.sum == 15.0
        assert updated_stats.sumsq == 85.0
        assert updated_stats.min == 4.0
        assert updated_stats.max == 6.0
        assert updated_stats.last_value != 5.0
        assert updated_stats.confidence_sum == 3.2
        assert updated_stats.ewma == 5.2

    def test_update_with_source(self):
        """Test update method adds source to sources set."""
        key = Key()

        mock_record = Mock(spec=VariableRecord)
        mock_record.value = 15.0
        mock_record.confidence = 0.9
        mock_record.source = key

        initial_stats = MemoryStatistics.empty()
        updated_stats = initial_stats.update(mock_record)

        assert key in updated_stats.sources
        assert len(updated_stats.sources) == 1

    def test_update_multiple_with_sources(self):
        """Test multiple updates accumulate sources correctly."""
        key1 = Key()
        key2 = Key()

        # First update with source1
        mock_record1 = Mock(spec=VariableRecord)
        mock_record1.value = 10.0
        mock_record1.confidence = 0.8
        mock_record1.source = key1

        stats = MemoryStatistics.empty()
        stats = stats.update(mock_record1)

        assert key1 in stats.sources
        assert len(stats.sources) == 1

        # Second update with source2
        mock_record2 = Mock(spec=VariableRecord)
        mock_record2.value = 20.0
        mock_record2.confidence = 0.9
        mock_record2.source = key2

        stats = stats.update(mock_record2)

        assert key1 in stats.sources
        assert key2 in stats.sources
        assert len(stats.sources) == 2

        # Third update with existing source1 (should not duplicate)
        mock_record3 = Mock(spec=VariableRecord)
        mock_record3.value = 15.0
        mock_record3.confidence = 0.7
        mock_record3.source = key1

        stats = stats.update(mock_record3)

        assert key1 in stats.sources
        assert key2 in stats.sources
        assert len(stats.sources) == 2  # Still 2 unique sources

    def test_update_ewma_calculation(self):
        """Test EWMA calculation with custom alpha."""
        # Test with default alpha (0.3)
        mock_record1 = Mock(spec=VariableRecord)
        mock_record1.value = 10.0
        mock_record1.confidence = 1.0
        mock_record1.source = None

        stats = MemoryStatistics.empty()
        stats = stats.update(mock_record1)
        assert stats.ewma == 10.0  # First value

        mock_record2 = Mock(spec=VariableRecord)
        mock_record2.value = 20.0
        mock_record2.confidence = 1.0
        mock_record2.source = None

        stats = stats.update(mock_record2)  # alpha = 0.3
        expected_ewma = 0.3 * 20.0 + 0.7 * 10.0
        assert stats.ewma == expected_ewma

        # Test with custom alpha
        mock_record3 = Mock(spec=VariableRecord)
        mock_record3.value = 30.0
        mock_record3.confidence = 1.0
        mock_record3.source = None

        stats = stats.update(mock_record3, alpha=0.5)
        expected_ewma = 0.5 * 30.0 + 0.5 * expected_ewma
        assert stats.ewma == expected_ewma

    def test_update_with_negative_alpha_raises_error(self):
        """Test that negative alpha raises ValueError."""
        mock_record = Mock(spec=VariableRecord)
        mock_record.value = 10.0
        mock_record.confidence = 1.0
        mock_record.source = None

        stats = MemoryStatistics.empty()

        with pytest.raises(ValueError, match="alpha should be non-negative"):
            stats.update(mock_record, alpha=-0.1)

    def test_mean_with_data(self):
        """Test mean calculation with data."""
        stats = MemoryStatistics(
            count=4,
            sum=20.0,
            sumsq=120.0,
            min=3.0,
            max=7.0,
            last_value=5.0,
            confidence_sum=3.2,
            ewma=5.5,
            sources=frozenset(),
        )

        assert stats.mean() == 5.0  # 20.0 / 4

    def test_mean_empty(self):
        """Test mean calculation with empty statistics."""
        stats = MemoryStatistics.empty()
        assert stats.mean() is None

        # Also test with count=0 but sum=None (edge case)
        stats2 = MemoryStatistics(count=0, sum=None, sumsq=0.0)
        assert stats2.mean() is None

    def test_std_with_sufficient_data(self):
        """Test standard deviation calculation with sufficient data."""
        # Example data: [3, 5, 7, 5]
        # Mean = 5, Variance = 2, Std = sqrt(2) ≈ 1.414
        stats = MemoryStatistics(
            count=4,
            sum=20.0,  # 3+5+7+5
            sumsq=108.0,  # 9+25+49+25
            min=3.0,
            max=7.0,
            last_value=5.0,
            confidence_sum=3.0,
            ewma=5.0,
            sources=frozenset(),
        )

        std = stats.std()
        expected_std = math.sqrt(2.0)  # Variance = (108/4) - 5² = 27 - 25 = 2

        assert std is not None
        assert math.isclose(std, expected_std, rel_tol=1e-10)

    def test_std_insufficient_data(self):
        """Test standard deviation with insufficient data."""
        # Test with count < 2
        stats1 = MemoryStatistics.empty()
        assert stats1.std() is None

        stats2 = MemoryStatistics(count=1, sum=10.0, sumsq=100.0)
        assert stats2.std() is None

        # Test with count >= 2 but mean is None
        stats3 = MemoryStatistics(count=2, sum=None, sumsq=50.0)
        assert stats3.std() is None

    def test_std_zero_variance(self):
        """Test standard deviation with zero variance."""
        # All values are the same: [5, 5, 5, 5]
        stats = MemoryStatistics(
            count=4,
            sum=20.0,  # 5*4
            sumsq=100.0,  # 25*4
            min=5.0,
            max=5.0,
            last_value=5.0,
            confidence_sum=4.0,
            ewma=5.0,
            sources=frozenset(),
        )

        std = stats.std()
        assert std is not None
        assert math.isclose(std, 0.0, abs_tol=1e-10)

    def test_confidence_with_data(self):
        """Test confidence calculation with data."""
        stats = MemoryStatistics(
            count=5,
            sum=25.0,
            sumsq=155.0,
            min=3.0,
            max=7.0,
            last_value=6.0,
            confidence_sum=3.5,
            ewma=5.5,
            sources=frozenset(),
        )

        assert stats.confidence() == 0.7  # 3.5 / 5

    def test_confidence_empty(self):
        """Test confidence calculation with empty statistics."""
        stats = MemoryStatistics.empty()
        assert stats.confidence() is None

        # Edge case: count=0 but confidence_sum=None
        stats2 = MemoryStatistics(count=0, confidence_sum=None)
        assert stats2.confidence() is None

    def test_immutability(self):
        """Test that MemoryStatistics is immutable (frozen dataclass)."""
        # Import dataclasses for FrozenInstanceError test
        import dataclasses

        stats = MemoryStatistics.empty()

        # Should not be able to modify attributes
        with pytest.raises(dataclasses.FrozenInstanceError):
            stats.count = 5

        with pytest.raises(dataclasses.FrozenInstanceError):
            stats.sum = 10.0

    def test_repr_string(self):
        """Test the __repr__ method."""
        # Create statistics with some data
        key = Key()
        stats = MemoryStatistics(
            count=3,
            sum=15.0,
            sumsq=85.0,
            min=4.0,
            max=6.0,
            last_value=5.0,
            confidence_sum=2.4,
            ewma=5.2,
            sources=frozenset([key]),
        )

        repr_str = repr(stats)

        # Check that all key components are in the repr
        assert "MemoryStatistics" in repr_str
        assert "count=3" in repr_str
        assert "mean=5.0" in repr_str  # 15/3
        assert "min=4.0" in repr_str
        assert "max=6.0" in repr_str
        assert "sources=1" in repr_str

        # The repr should call mean() and std() methods
        # So we can verify those are calculated correctly
        mean = stats.mean()
        std = stats.std()

        if mean is not None:
            assert f"mean={mean}" in repr_str

        if std is not None:
            # Note: std might be formatted with limited precision
            assert "std=" in repr_str

    def test_repr_empty(self):
        """Test __repr__ with empty statistics."""
        stats = MemoryStatistics.empty()
        repr_str = repr(stats)

        assert "MemoryStatistics" in repr_str
        assert "count=0" in repr_str
        assert "mean=None" in repr_str or "mean=0" in repr_str
        assert "std=None" in repr_str or "std=0" in repr_str
        assert "sources=0" in repr_str

    def test_update_min_max_calculation(self):
        """Test min and max calculations during updates."""
        # Create a sequence of records with different values
        records = []
        for i, value in enumerate([15.0, 5.0, 25.0, 10.0, 20.0]):
            mock_record = Mock(spec=VariableRecord)
            mock_record.value = value
            mock_record.confidence = 0.8
            mock_record.source = None
            records.append(mock_record)

        # Apply updates sequentially
        stats = MemoryStatistics.empty()
        for record in records:
            stats = stats.update(record)

        assert stats.min == 5.0
        assert stats.max == 25.0
        assert stats.count == 5

    def test_update_confidence_sum(self):
        """Test confidence sum accumulation."""
        # Create records with different confidence values
        records = []
        confidences = [0.5, 0.8, 0.3, 0.9, 0.6]
        for conf in confidences:
            mock_record = Mock(spec=VariableRecord)
            mock_record.value = 10.0  # Same value for all
            mock_record.confidence = conf
            mock_record.source = None
            records.append(mock_record)

        # Apply updates
        stats = MemoryStatistics.empty()
        for record in records:
            stats = stats.update(record)

        assert stats.confidence_sum == sum(confidences)
        assert stats.confidence() == sum(confidences) / len(confidences)

    def test_update_with_none_confidence(self):
        """Test update with None confidence (should add 0.0)."""
        mock_record = Mock(spec=VariableRecord)
        mock_record.value = 10.0
        mock_record.confidence = None  # Explicitly None
        mock_record.source = None

        stats = MemoryStatistics.empty()
        stats = stats.update(mock_record)

        assert stats.confidence_sum == 0.0

    def test_integration_multiple_updates(self):
        """Integration test with multiple updates."""
        keys = [Key() for _ in range(3)]
        values = [10.0, 20.0, 15.0, 25.0, 5.0]
        confidences = [0.7, 0.8, 0.9, 0.6, 0.5]

        stats = MemoryStatistics.empty()

        for i, (value, confidence) in enumerate(zip(values, confidences)):
            mock_record = Mock(spec=VariableRecord)
            mock_record.value = value
            mock_record.confidence = confidence
            mock_record.source = keys[i % len(keys)]  # Cycle through sources

            stats = stats.update(mock_record, alpha=0.2)

        # Verify final state
        assert stats.count == 5
        assert stats.sum == sum(values)
        assert stats.sumsq == sum(v**2 for v in values)
        assert stats.min == min(values)
        assert stats.max == max(values)
        assert stats.last_value == values[-1]
        assert stats.confidence_sum == sum(confidences)
        assert len(stats.sources) == 3  # All 3 unique sources

        # Verify calculated statistics
        assert stats.mean() == sum(values) / len(values)
        assert stats.confidence() == sum(confidences) / len(confidences)

    def test_dataclass_equality(self):
        """Test that two instances with same values are equal."""
        key1 = Key()
        key2 = Key()
        sources = frozenset([key1, key2])

        stats1 = MemoryStatistics(
            count=3,
            sum=15.0,
            sumsq=85.0,
            min=4.0,
            max=6.0,
            last_value=5.0,
            confidence_sum=2.4,
            ewma=5.2,
            sources=sources,
        )

        stats2 = MemoryStatistics(
            count=3,
            sum=15.0,
            sumsq=85.0,
            min=4.0,
            max=6.0,
            last_value=5.0,
            confidence_sum=2.4,
            ewma=5.2,
            sources=sources,
        )

        assert stats1 == stats2

        # Different values should not be equal
        stats3 = MemoryStatistics(
            count=4,  # Different count
            sum=15.0,
            sumsq=85.0,
            min=4.0,
            max=6.0,
            last_value=5.0,
            confidence_sum=2.4,
            ewma=5.2,
            sources=sources,
        )

        assert stats1 != stats3

    def test_hashable(self):
        """Test that MemoryStatistics is hashable (frozen dataclass)."""
        stats = MemoryStatistics.empty()

        # Should be able to create a hash
        hash_val = hash(stats)
        assert isinstance(hash_val, int)

        # Can be used as dictionary key
        stats_dict = {stats: "test"}
        assert stats_dict[stats] == "test"


if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=procela.core.memory.variable.statistics",
            "--cov-report=term-missing",
        ]
    )
