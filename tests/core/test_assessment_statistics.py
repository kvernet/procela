"""
Pytest module for procela.core.assessment.statistics."""

import math
from dataclasses import FrozenInstanceError, replace

import pytest

from procela.core.assessment import StatisticsResult


class TestStatisticsResult:
    """Test suite for StatisticsResult dataclass."""

    def test_default_initialization(self):
        """Test that StatisticsResult can be initialized with all default values."""
        result = StatisticsResult()

        assert result.count == 0
        assert result.sum is None
        assert result.min is None
        assert result.max is None
        assert result.mean is None
        assert result.std is None
        assert result.value is None
        assert result.ewma is None
        assert result.confidence is None

    def test_full_initialization(self):
        """Test that StatisticsResult can be initialized with all values provided."""
        result = StatisticsResult(
            count=10,
            sum=100.5,
            min=5.0,
            max=15.0,
            mean=10.05,
            std=2.5,
            value=12.0,
            ewma=10.2,
            confidence=0.95,
        )

        assert result.count == 10
        assert result.sum == 100.5
        assert result.min == 5.0
        assert result.max == 15.0
        assert result.mean == 10.05
        assert result.std == 2.5
        assert result.value == 12.0
        assert result.ewma == 10.2
        assert result.confidence == 0.95

    def test_partial_initialization(self):
        """Test that StatisticsResult can be initialized with only some values."""
        result = StatisticsResult(count=5, sum=25.0, mean=5.0, value=6.0)

        assert result.count == 5
        assert result.sum == 25.0
        assert result.mean == 5.0
        assert result.value == 6.0
        assert result.min is None
        assert result.max is None
        assert result.std is None
        assert result.ewma is None
        assert result.confidence is None

    def test_immutability(self):
        """Test that StatisticsResult is immutable (frozen)."""
        result = StatisticsResult(count=5, sum=25.0)

        # Attempting to modify attributes should raise FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            result.count = 10

        with pytest.raises(FrozenInstanceError):
            result.sum = 100.0

        with pytest.raises(FrozenInstanceError):
            result.mean = 5.0

    def test_dataclass_replace_method(self):
        """Test that we can create modified copies using replace()."""
        original = StatisticsResult(count=5, sum=25.0, mean=5.0)

        # Create a modified copy
        modified = replace(original, count=10, sum=50.0)

        # Original should remain unchanged
        assert original.count == 5
        assert original.sum == 25.0
        assert original.mean == 5.0

        # Modified should have new values
        assert modified.count == 10
        assert modified.sum == 50.0
        assert modified.mean == 5.0  # This should remain from original

    def test_slots_behavior(self):
        """Test that StatisticsResult uses slots for memory efficiency."""
        result = StatisticsResult()

        # With slots, we shouldn't be able to add new attributes
        with pytest.raises(TypeError):
            result.new_attribute = "test"

        # Verify __slots__ is defined
        assert hasattr(result, "__slots__")

        # Check that all attributes are in slots
        expected_slots = {
            "count",
            "sum",
            "min",
            "max",
            "mean",
            "std",
            "value",
            "ewma",
            "confidence",
        }
        actual_slots = set(result.__slots__)
        assert expected_slots.issubset(actual_slots)

    def test_equality(self):
        """Test equality comparison between StatisticsResult instances."""
        result1 = StatisticsResult(count=5, sum=25.0, mean=5.0)
        result2 = StatisticsResult(count=5, sum=25.0, mean=5.0)
        result3 = StatisticsResult(count=10, sum=50.0, mean=5.0)

        # Equal instances should be equal
        assert result1 == result2

        # Different instances should not be equal
        assert result1 != result3

        # Test with None values
        result4 = StatisticsResult()
        result5 = StatisticsResult()
        assert result4 == result5

    def test_hashability(self):
        """Test that StatisticsResult is hashable (required for frozen dataclass)."""
        result1 = StatisticsResult(count=5, sum=25.0)
        result2 = StatisticsResult(count=5, sum=25.0)

        # Same values should produce same hash
        assert hash(result1) == hash(result2)

        # Different values should produce different hash
        result3 = StatisticsResult(count=10, sum=50.0)
        assert hash(result1) != hash(result3)

        # Should be able to use in a set
        result_set = {result1, result2, result3}
        assert len(result_set) == 2  # result1 and result2 are equal

    def test_repr_string(self):
        """Test the string representation of StatisticsResult."""
        result = StatisticsResult(
            count=5,
            sum=25.0,
            min=1.0,
            max=9.0,
            mean=5.0,
            std=2.0,
            value=6.0,
            ewma=5.5,
            confidence=0.95,
        )

        repr_str = repr(result)

        # Check that all attributes appear in the repr
        assert "count=5" in repr_str
        assert "sum=25.0" in repr_str
        assert "min=1.0" in repr_str
        assert "max=9.0" in repr_str
        assert "mean=5.0" in repr_str
        assert "std=2.0" in repr_str
        assert "value=6.0" in repr_str
        assert "ewma=5.5" in repr_str
        assert "confidence=0.95" in repr_str

    def test_str_method(self):
        """Test the informal string representation."""
        result = StatisticsResult(count=5, sum=25.0, mean=5.0)
        str_result = str(result)

        # Should contain class name and some attribute info
        assert "StatisticsResult" in str_result
        assert "count=5" in str_result
        assert "sum=25.0" in str_result

    def test_type_annotations_preserved(self):
        """Test that type annotations are preserved and accessible."""
        from typing import get_type_hints

        type_hints = get_type_hints(StatisticsResult)

        assert type_hints["count"] == int
        assert type_hints["sum"] == float | None
        assert type_hints["min"] == float | None
        assert type_hints["max"] == float | None
        assert type_hints["mean"] == float | None
        assert type_hints["std"] == float | None
        assert type_hints["value"] == float | None
        assert type_hints["ewma"] == float | None
        assert type_hints["confidence"] == float | None

    def test_with_none_values(self):
        """Test handling of None values in all fields."""
        result = StatisticsResult(
            count=0,
            sum=0.0,
            min=None,
            max=None,
            mean=None,
            std=None,
            value=None,
            ewma=None,
            confidence=None,
        )

        assert result.count == 0
        assert result.sum == 0.0
        assert result.min is None
        assert result.max is None
        assert result.mean is None
        assert result.std is None
        assert result.value is None
        assert result.ewma is None
        assert result.confidence is None

    def test_negative_values(self):
        """Test that StatisticsResult can handle negative values."""
        result = StatisticsResult(
            count=3,
            sum=-15.0,
            min=-10.0,
            max=-2.0,
            mean=-5.0,
            std=4.0,
            value=-3.0,
            ewma=-4.5,
            confidence=0.90,
        )

        assert result.count == 3
        assert result.sum == -15.0
        assert result.min == -10.0
        assert result.max == -2.0
        assert result.mean == -5.0
        assert result.std == 4.0
        assert result.value == -3.0
        assert result.ewma == -4.5
        assert result.confidence == 0.90

    def test_zero_count_edge_case(self):
        """Test edge case with count=0 but other values provided."""
        result = StatisticsResult(
            count=0,
            sum=0.0,
            min=0.0,  # This might be unusual but should be allowed
            max=0.0,
            mean=0.0,
            std=0.0,
            value=0.0,
            ewma=0.0,
            confidence=0.0,
        )

        assert result.count == 0
        assert result.sum == 0.0
        assert result.min == 0.0
        assert result.max == 0.0
        assert result.mean == 0.0
        assert result.std == 0.0
        assert result.value == 0.0
        assert result.ewma == 0.0
        assert result.confidence == 0.0

    def test_large_values(self):
        """Test with large numerical values."""
        result = StatisticsResult(
            count=1000000,
            sum=1e12,
            min=1000.0,
            max=2000000.0,
            mean=1e6,
            std=500000.0,
            value=1500000.0,
            ewma=1200000.0,
            confidence=0.99,
        )

        assert result.count == 1000000
        assert result.sum == 1e12
        assert result.min == 1000.0
        assert result.max == 2000000.0
        assert result.mean == 1e6
        assert result.std == 500000.0
        assert result.value == 1500000.0
        assert result.ewma == 1200000.0
        assert result.confidence == 0.99

    def test_float_precision(self):
        """Test with floating point precision edge cases."""
        result = StatisticsResult(
            count=1,
            sum=0.1 + 0.2,  # Famous floating point issue
            min=0.1,
            max=0.2,
            mean=(0.1 + 0.2) / 2,
            std=0.05,
            value=0.2,
            ewma=0.15,
            confidence=0.5,
        )

        # Using math.isclose for floating point comparisons
        assert result.count == 1
        assert math.isclose(result.sum, 0.3, rel_tol=1e-10)
        assert result.min == 0.1
        assert result.max == 0.2
        assert math.isclose(result.mean, 0.15, rel_tol=1e-10)
        assert result.std == 0.05
        assert result.value == 0.2
        assert result.ewma == 0.15
        assert result.confidence == 0.5

    def test_as_dict_conversion(self):
        """Test conversion to dictionary (common dataclass feature)."""
        result = StatisticsResult(count=5, sum=25.0, mean=5.0, confidence=0.95)

        # dataclasses.asdict() would be used here, but we'll test manual conversion
        # to avoid imports
        result_dict = {
            "count": result.count,
            "sum": result.sum,
            "min": result.min,
            "max": result.max,
            "mean": result.mean,
            "std": result.std,
            "value": result.value,
            "ewma": result.ewma,
            "confidence": result.confidence,
        }

        assert result_dict["count"] == 5
        assert result_dict["sum"] == 25.0
        assert result_dict["mean"] == 5.0
        assert result_dict["confidence"] == 0.95
        assert result_dict["min"] is None
        assert result_dict["max"] is None
        assert result_dict["std"] is None
        assert result_dict["value"] is None
        assert result_dict["ewma"] is None

    def test_field_access_performance(self):
        """Test that slot-based attribute access works correctly."""
        result = StatisticsResult(count=5, sum=25.0, mean=5.0)

        # Multiple attribute accesses should work without issues
        for _ in range(1000):
            _ = result.count
            _ = result.sum
            _ = result.mean
            _ = result.min  # None value

    def test_doctest_compatibility(self):
        """Test that the class can be used in doctest examples."""
        # Example usage that would work in doctest
        stats = StatisticsResult(
            count=10,
            sum=100.0,
            min=5.0,
            max=15.0,
            mean=10.0,
            std=2.5,
            value=12.0,
            ewma=11.0,
            confidence=0.95,
        )

        assert stats.count == 10
        assert stats.mean == 10.0
        assert stats.confidence == 0.95

    @pytest.mark.parametrize(
        "field_name,test_value",
        [
            ("count", 42),
            ("sum", 123.456),
            ("min", -999.999),
            ("max", 999.999),
            ("mean", 0.0),
            ("std", 1.0),
            ("value", 3.14159),
            ("ewma", 2.71828),
            ("confidence", 0.999),
        ],
    )
    def test_individual_fields(self, field_name, test_value):
        """Parameterized test for individual field assignments."""
        # Create kwargs with only the field being tested
        kwargs = {field_name: test_value}

        # For fields that have defaults, we need to provide minimal initialization
        if field_name in ["count", "sum"]:
            result = StatisticsResult(**kwargs)
        else:
            # For optional fields, we need to provide required fields too
            kwargs["count"] = 1
            kwargs["sum"] = 1.0
            result = StatisticsResult(**kwargs)

        assert getattr(result, field_name) == test_value


# Additional edge case tests
def test_extreme_values():
    """Test with extreme float values."""
    result = StatisticsResult(
        count=1,
        sum=float("inf"),
        min=float("-inf"),
        max=float("inf"),
        mean=float("nan"),
        std=float("inf"),
        value=float("nan"),
        ewma=float("nan"),
        confidence=1.0,
    )

    assert result.count == 1
    assert result.sum == float("inf")
    assert result.min == float("-inf")
    assert result.max == float("inf")
    assert math.isnan(result.mean)
    assert result.std == float("inf")
    assert math.isnan(result.value)
    assert math.isnan(result.ewma)
    assert result.confidence == 1.0


def test_serialization_compatibility():
    """Test that the dataclass works with common serialization patterns."""
    result = StatisticsResult(count=3, sum=15.0, mean=5.0)

    # Simulate JSON serialization/deserialization
    json_compatible_dict = {
        "count": result.count,
        "sum": result.sum,
        "min": result.min,
        "max": result.max,
        "mean": result.mean,
        "std": result.std,
        "value": result.value,
        "ewma": result.ewma,
        "confidence": result.confidence,
    }

    # Simulate reconstruction
    reconstructed = StatisticsResult(**json_compatible_dict)

    assert result == reconstructed


def test_no_post_init():
    """Test that there's no __post_init__ method interfering."""
    result = StatisticsResult(count=-1, sum=-10.0)

    assert result.count == -1
    assert result.sum == -10.0
