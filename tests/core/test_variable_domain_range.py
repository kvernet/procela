"""Test suite for RangeDomain class."""

from typing import Any, Optional

import pytest

from procela.core.assessment import StatisticsResult
from procela.core.variable import RangeDomain


class TestRangeDomain:
    """Test cases for RangeDomain class."""

    def test_initialization_with_no_bounds(self):
        """Test initialization without bounds."""
        domain = RangeDomain()
        assert domain.min_value is None
        assert domain.max_value is None
        assert domain.name == ""

    def test_initialization_with_min_only(self):
        """Test initialization with only minimum bound."""
        domain = RangeDomain(min_value=0)
        assert domain.min_value == 0
        assert domain.max_value is None
        assert domain.name == ""

    def test_initialization_with_max_only(self):
        """Test initialization with only maximum bound."""
        domain = RangeDomain(max_value=100)
        assert domain.min_value is None
        assert domain.max_value == 100
        assert domain.name == ""

    def test_initialization_with_both_bounds(self):
        """Test initialization with both bounds."""
        domain = RangeDomain(min_value=0, max_value=100)
        assert domain.min_value == 0
        assert domain.max_value == 100
        assert domain.name == ""

    def test_initialization_with_name(self):
        """Test initialization with custom name."""
        domain = RangeDomain(name="temperature")
        assert domain.name == "temperature"

    def test_initialization_with_all_parameters(self):
        """Test initialization with all parameters."""
        domain = RangeDomain(min_value=-10, max_value=10, name="range")
        assert domain.min_value == -10
        assert domain.max_value == 10
        assert domain.name == "range"

    def test_initialization_with_invalid_bounds_raises_error(self):
        """Test that min > max raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            RangeDomain(min_value=10, max_value=0)
        msg = "min_value (10) cannot be greater than max_value (0)"
        assert msg in str(exc_info.value)

    def test_validate_numeric_value_within_bounds(self):
        """Test validation of numeric value within bounds."""
        domain = RangeDomain(min_value=0, max_value=100)
        assert domain.validate(50) is True
        assert domain.validate(0) is True  # Edge case inclusive
        assert domain.validate(100) is True  # Edge case inclusive

    def test_validate_numeric_value_below_min(self):
        """Test validation of numeric value below minimum."""
        domain = RangeDomain(min_value=10, max_value=100)
        assert domain.validate(5) is False
        assert domain.validate(9.9) is False

    def test_validate_numeric_value_above_max(self):
        """Test validation of numeric value above maximum."""
        domain = RangeDomain(min_value=0, max_value=50)
        assert domain.validate(51) is False
        assert domain.validate(100) is False

    def test_validate_non_numeric_value(self):
        """Test validation of non-numeric values."""
        domain = RangeDomain(min_value=0, max_value=100)
        assert domain.validate("string") is False
        assert domain.validate([1, 2, 3]) is False
        assert domain.validate({"key": "value"}) is False
        assert domain.validate(None) is False
        assert domain.validate(True) is True
        assert domain.validate(False) is True

    def test_validate_with_no_bounds(self):
        """Test validation with no bounds (any numeric)."""
        domain = RangeDomain()
        assert domain.validate(42) is True
        assert domain.validate(-999) is True
        assert domain.validate(3.14) is True
        assert domain.validate("42") is False

    def test_validate_with_only_min_bound(self):
        """Test validation with only minimum bound."""
        domain = RangeDomain(min_value=0)
        assert domain.validate(10) is True
        assert domain.validate(0) is True
        assert domain.validate(-1) is False
        assert domain.validate(1e6) is True

    def test_validate_with_only_max_bound(self):
        """Test validation with only maximum bound."""
        domain = RangeDomain(max_value=100)
        assert domain.validate(50) is True
        assert domain.validate(100) is True
        assert domain.validate(101) is False
        assert domain.validate(-1e6) is True

    def test_validate_with_float_bounds_and_int_value(self):
        """Test validation with float bounds and integer value."""
        domain = RangeDomain(min_value=0.5, max_value=10.5)
        assert domain.validate(1) is True
        assert domain.validate(0.5) is True
        assert domain.validate(10.5) is True
        assert domain.validate(0.4) is False
        assert domain.validate(10.6) is False

    def test_validate_with_context_parameter(self):
        """Test validation with context parameter (should be ignored)."""
        domain = RangeDomain(min_value=0, max_value=100)
        context = {"some": "context"}
        assert domain.validate(50, context) is True
        assert domain.validate(150, context) is False
        assert domain.validate("test", context) is False

    def test_explain_valid_value(self):
        """Test explanation for valid value."""
        domain = RangeDomain(min_value=0, max_value=100)
        explanation = domain.explain(50)
        assert "Value 50 is valid in RangeDomain" == explanation

    def test_explain_non_numeric_value(self):
        """Test explanation for non-numeric value."""
        domain = RangeDomain(min_value=0, max_value=100)
        explanation = domain.explain("fifty")
        assert "Value fifty is not numeric" == explanation

    def test_explain_value_below_min(self):
        """Test explanation for value below minimum."""
        domain = RangeDomain(min_value=10, max_value=100)
        explanation = domain.explain(5)
        assert "Value 5 is less than minimum 10" == explanation

    def test_explain_value_above_max(self):
        """Test explanation for value above maximum."""
        domain = RangeDomain(min_value=0, max_value=50)
        explanation = domain.explain(75)
        assert "Value 75 is greater than maximum 50" == explanation

    def test_explain_with_only_min_bound(self):
        """Test explanation with only minimum bound."""
        domain = RangeDomain(min_value=5)
        assert domain.explain(3) == "Value 3 is less than minimum 5"
        assert domain.explain(10) == "Value 10 is valid in RangeDomain"
        assert domain.explain("test") == "Value test is not numeric"

    def test_explain_with_only_max_bound(self):
        """Test explanation with only maximum bound."""
        domain = RangeDomain(max_value=20)
        assert domain.explain(25) == "Value 25 is greater than maximum 20"
        assert domain.explain(15) == "Value 15 is valid in RangeDomain"

    def test_explain_with_no_bounds(self):
        """Test explanation with no bounds."""
        domain = RangeDomain()
        assert domain.explain(42) == "Value 42 is valid in RangeDomain"
        assert domain.explain("test") == "Value test is not numeric"

    def test_explain_with_context_parameter(self):
        """Test explanation with context parameter (should be ignored)."""
        domain = RangeDomain(min_value=0, max_value=100)
        context = {"some": "context"}
        explanation = domain.explain(50, context)
        assert "Value 50 is valid in RangeDomain" == explanation

    def test_edge_case_float_precision(self):
        """Test edge case with float precision."""
        with pytest.raises(ValueError):
            # 0.1 + 0.2 is not exactly 0.3 due to float precision
            _ = RangeDomain(min_value=0.1 + 0.2, max_value=0.3)

    def test_edge_case_large_numbers(self):
        """Test edge case with very large numbers."""
        domain = RangeDomain(min_value=-1e100, max_value=1e100)
        assert domain.validate(1e99) is True
        assert domain.validate(-1e99) is True
        assert domain.validate(2e100) is False
        assert domain.validate(-2e100) is False

    def test_edge_case_infinity_and_nan(self):
        """Test edge case with infinity and NaN."""
        domain = RangeDomain(min_value=0, max_value=100)
        # These should return False as they are numeric but special
        assert domain.validate(float("inf")) is False
        assert domain.validate(float("-inf")) is False
        assert domain.validate(float("nan")) is False

    def test_type_annotations(self):
        """Test that type annotations are correct."""
        from typing import get_type_hints

        hints = get_type_hints(RangeDomain.__init__)
        assert hints["min_value"] == float | None
        assert hints["max_value"] == float | None
        assert hints["name"] is str

        hints = get_type_hints(RangeDomain.validate)
        assert hints["value"] == Any
        assert hints["stats"] == Optional[StatisticsResult]
        assert hints["return"] is bool

        hints = get_type_hints(RangeDomain.explain)
        assert hints["value"] == Any
        assert hints["stats"] == Optional[StatisticsResult]
        assert hints["return"] is str

    def test_string_representation(self):
        """Test string representation of domain."""
        domain = RangeDomain(min_value=0, max_value=100, name="test")
        # Just ensure no error
        repr(domain)
        str(domain)

    def test_equality_not_implemented(self):
        """Test that equality is not specially implemented."""
        domain1 = RangeDomain(min_value=0, max_value=100)
        domain2 = RangeDomain(min_value=0, max_value=100)
        # Different objects should not be equal by default
        assert domain1 != domain2
