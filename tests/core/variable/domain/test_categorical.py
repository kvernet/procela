"""Test suite for CategoricalDomain class."""

from typing import Any, Iterable, Optional

import pytest

from procela.core.variable import CategoricalDomain, HistoryStatistics


class TestCategoricalDomain:
    """Test cases for CategoricalDomain class."""

    def test_initialization_with_list(self):
        """Test initialization with list of categories."""
        categories = ["cat", "dog", "bird"]
        domain = CategoricalDomain(categories)
        assert domain.categories == set(categories)
        assert domain.name == ""

    def test_initialization_with_set(self):
        """Test initialization with set of categories."""
        categories = {"red", "green", "blue"}
        domain = CategoricalDomain(categories)
        assert domain.categories == categories
        assert domain.name == ""

    def test_initialization_with_tuple(self):
        """Test initialization with tuple of categories."""
        categories = (1, 2, 3)
        domain = CategoricalDomain(categories)
        assert domain.categories == set(categories)
        assert domain.name == ""

    def test_initialization_with_name(self):
        """Test initialization with custom name."""
        domain = CategoricalDomain(["a", "b"], name="letters")
        assert domain.name == "letters"

    def test_initialization_with_empty_iterable(self):
        """Test initialization with empty categories."""
        domain = CategoricalDomain([])
        assert domain.categories == set()
        assert len(domain.categories) == 0

    def test_initialization_removes_duplicates(self):
        """Test that duplicates are removed from categories."""
        domain = CategoricalDomain(["a", "b", "a", "c", "b"])
        assert len(domain.categories) == 3
        assert domain.categories == {"a", "b", "c"}

    def test_initialization_with_unhashable_raises_error(self):
        """Test that unhashable categories raise TypeError."""
        with pytest.raises(TypeError):
            CategoricalDomain([["list", "is", "unhashable"]])
        with pytest.raises(TypeError):
            CategoricalDomain([{"dict": "is", "unhashable": True}])

    def test_validate_value_in_categories(self):
        """Test validation of value in categories."""
        domain = CategoricalDomain(["apple", "banana", "orange"])
        assert domain.validate("apple") is True
        assert domain.validate("banana") is True
        assert domain.validate("orange") is True

    def test_validate_value_not_in_categories(self):
        """Test validation of value not in categories."""
        domain = CategoricalDomain(["apple", "banana", "orange"])
        assert domain.validate("grape") is False
        assert domain.validate("") is False
        assert domain.validate(None) is False

    def test_validate_with_empty_categories(self):
        """Test validation with empty categories."""
        domain = CategoricalDomain([])
        assert domain.validate("anything") is False
        assert domain.validate(123) is False
        assert domain.validate(None) is False

    def test_validate_numeric_categories(self):
        """Test validation with numeric categories."""
        domain = CategoricalDomain([1, 2, 3])
        assert domain.validate(1) is True
        assert domain.validate(2) is True
        assert domain.validate(3) is True
        assert domain.validate(4) is False
        assert domain.validate("1") is False  # String != int

    def test_validate_mixed_type_categories(self):
        """Test validation with mixed type categories."""
        domain = CategoricalDomain([1, "1", True, False])
        assert domain.validate(1) is True
        assert domain.validate("1") is True
        assert domain.validate(True) is True
        assert domain.validate(False) is True
        assert domain.validate(0) is True

    def test_validate_with_context_parameter(self):
        """Test validation with context parameter."""
        domain = CategoricalDomain(["a", "b", "c"])
        context = {"some": "context"}
        assert domain.validate("a", context) is True
        assert domain.validate("d", context) is False

    def test_explain_value_in_categories(self):
        """Test explanation for value in categories."""
        domain = CategoricalDomain(["red", "green", "blue"])
        explanation = domain.explain("red")
        assert "Value red is allowed in categories" in explanation
        assert "red" in explanation
        assert "green" in explanation
        assert "blue" in explanation

    def test_explain_value_not_in_categories(self):
        """Test explanation for value not in categories."""
        domain = CategoricalDomain(["red", "green", "blue"])
        explanation = domain.explain("yellow")
        assert "Value yellow is not in allowed categories" in explanation
        assert "red" in explanation
        assert "green" in explanation
        assert "blue" in explanation

    def test_explain_with_empty_categories(self):
        """Test explanation with empty categories."""
        domain = CategoricalDomain([])
        explanation = domain.explain("test")
        assert explanation == "Value test is not in allowed categories set()."

    def test_explain_with_numeric_categories(self):
        """Test explanation with numeric categories."""
        domain = CategoricalDomain([1, 2, 3])
        assert "1" in domain.explain(1)
        assert "1" in domain.explain(4)  # Even for invalid values
        assert "2" in domain.explain(4)
        assert "3" in domain.explain(4)

    def test_explain_with_context_parameter(self):
        """Test explanation with context parameter."""
        domain = CategoricalDomain(["a", "b"])
        context = {"some": "context"}
        explanation = domain.explain("a", context)
        assert "Value a is allowed in categories" in explanation

    def test_set_membership_performance(self):
        """Test that categories is stored as set for O(1) lookup."""
        import time

        large_list = list(range(10000))
        domain = CategoricalDomain(large_list)

        # Time lookup for first element
        start = time.perf_counter()
        domain.validate(0)
        first_time = time.perf_counter() - start

        # Time lookup for last element
        start = time.perf_counter()
        domain.validate(9999)
        last_time = time.perf_counter() - start

        # Both should be very fast (set lookup is O(1))
        assert first_time < 0.001
        assert last_time < 0.001

    def test_case_sensitive_categories(self):
        """Test that categories are case-sensitive."""
        domain = CategoricalDomain(["Apple", "Banana"])
        assert domain.validate("Apple") is True
        assert domain.validate("apple") is False
        assert domain.validate("BANANA") is False

    def test_none_as_category(self):
        """Test None as a valid category."""
        domain = CategoricalDomain([None, "value"])
        assert domain.validate(None) is True
        assert domain.validate("value") is True
        assert domain.validate("other") is False

    def test_boolean_categories(self):
        """Test boolean values as categories."""
        domain = CategoricalDomain([True, False])
        assert domain.validate(True) is True
        assert domain.validate(False) is True
        assert domain.validate(1) is True
        assert domain.validate(0) is True

    def test_float_categories(self):
        """Test float values as categories."""
        domain = CategoricalDomain([1.0, 2.5, 3.14])
        assert domain.validate(1.0) is True
        assert domain.validate(2.5) is True
        assert domain.validate(3.14) is True
        assert domain.validate(1) is True  # 1 == 1.0
        assert domain.validate(2) is False  # 2 != 2.5

    def test_type_annotations(self):
        """Test that type annotations are correct."""
        from typing import get_type_hints

        hints = get_type_hints(CategoricalDomain.__init__)
        assert hints["categories"] == Iterable[Any]
        assert hints["name"] is str

        hints = get_type_hints(CategoricalDomain.validate)
        assert hints["value"] == Any
        assert hints["stats"] == Optional[HistoryStatistics]
        assert hints["return"] is bool

        hints = get_type_hints(CategoricalDomain.explain)
        assert hints["value"] == Any
        assert hints["stats"] == Optional[HistoryStatistics]
        assert hints["return"] is str

    def test_string_representation(self):
        """Test string representation of domain."""
        domain = CategoricalDomain(["a", "b"], name="test")
        # Just ensure no error
        repr(domain)
        str(domain)
