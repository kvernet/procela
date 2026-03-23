"""Test suite for BooleanDomain class."""

from typing import Any, Optional

import pytest

from procela.core.assessment import StatisticsResult
from procela.core.variable import (
    BooleanDomain,
    CategoricalDomain,
)


class TestBooleanDomain:
    """Test cases for BooleanDomain class."""

    def test_initialization_without_name(self):
        """Test initialization without name."""
        domain = BooleanDomain()
        assert domain.categories == {True, False}
        assert domain.name == ""

    def test_initialization_with_name(self):
        """Test initialization with name."""
        domain = BooleanDomain(name="flag")
        assert domain.categories == {True, False}
        assert domain.name == "flag"

    def test_initialization_fixed_categories(self):
        """Test that categories are always {True, False}."""
        domain1 = BooleanDomain()
        domain2 = BooleanDomain(name="other")
        domain3 = BooleanDomain(name="another")

        assert domain1.categories == {True, False}
        assert domain2.categories == {True, False}
        assert domain3.categories == {True, False}

        # All should have the same categories
        assert domain1.categories == domain2.categories == domain3.categories

    def test_validate_true(self):
        """Test validation of True."""
        domain = BooleanDomain()
        assert domain.validate(True) is True

    def test_validate_false(self):
        """Test validation of False."""
        domain = BooleanDomain()
        assert domain.validate(False) is True

    def test_validate_integer_1(self):
        """Test validation of integer 1 (should be False)."""
        domain = BooleanDomain()
        assert domain.validate(1) is True

    def test_validate_integer_0(self):
        """Test validation of integer 0 (should be False)."""
        domain = BooleanDomain()
        assert domain.validate(0) is True

    def test_validate_other_values(self):
        """Test validation of other non-boolean values."""
        domain = BooleanDomain()
        assert domain.validate("True") is False
        assert domain.validate("False") is False
        assert domain.validate("true") is False
        assert domain.validate("false") is False
        assert domain.validate(None) is False
        assert domain.validate(1.0) is True
        assert domain.validate(0.0) is True

        with pytest.raises(TypeError):
            domain.validate([])

        with pytest.raises(TypeError):
            domain.validate({})

    def test_validate_with_context_parameter(self):
        """Test validation with context parameter."""
        domain = BooleanDomain()
        context = {"some": "context"}
        assert domain.validate(True, context) is True
        assert domain.validate(False, context) is True
        assert domain.validate("True", context) is False

    def test_explain_true(self):
        """Test explanation for True."""
        domain = BooleanDomain()
        explanation = domain.explain(True)
        assert "Value True is allowed in categories" in explanation
        assert "True" in explanation
        assert "False" in explanation

    def test_explain_false(self):
        """Test explanation for False."""
        domain = BooleanDomain()
        explanation = domain.explain(False)
        assert "Value False is allowed in categories" in explanation
        assert "True" in explanation
        assert "False" in explanation

    def test_explain_non_boolean(self):
        """Test explanation for non-boolean values."""
        domain = BooleanDomain()
        explanation = domain.explain(1)
        assert "Value 1 is allowed in categories {False, True}" in explanation
        assert "True" in explanation
        assert "False" in explanation

    def test_explain_with_context_parameter(self):
        """Test explanation with context parameter."""
        domain = BooleanDomain()
        context = {"some": "context"}
        explanation = domain.explain(True, context)
        assert "Value True is allowed in categories" in explanation

    def test_inheritance_from_categorical(self):
        """Test that BooleanDomain inherits from CategoricalDomain."""
        domain = BooleanDomain()
        assert isinstance(domain, CategoricalDomain)

        # Check that methods are inherited
        assert hasattr(domain, "validate")
        assert hasattr(domain, "explain")
        assert hasattr(domain, "categories")
        assert hasattr(domain, "name")

    def test_categories_immutability(self):
        """Test that categories set cannot be modified externally."""
        domain = BooleanDomain()
        original_categories = domain.categories

        # Try to modify (should not affect internal state)
        domain.categories.add("maybe")
        assert domain.categories == original_categories

    def test_boolean_identity_vs_equality(self):
        """Test boolean identity vs equality."""
        domain = BooleanDomain()

        # bool(1) is True
        assert bool(1) is True
        assert 1 == True
        assert domain.validate(bool(1)) is True
        assert domain.validate(1) is True

        # Same for False
        assert bool(0) is False
        assert 0 == False
        assert domain.validate(bool(0)) is True
        assert domain.validate(0) is True

    def test_empty_string_name(self):
        """Test that empty string name is allowed."""
        domain = BooleanDomain(name="")
        assert domain.name == ""

    def test_type_annotations(self):
        """Test that type annotations are correct."""
        from typing import get_type_hints

        hints = get_type_hints(BooleanDomain.__init__)
        assert hints["name"] is str

        # Inherited methods should have same annotations
        hints = get_type_hints(BooleanDomain.validate)
        assert hints["value"] == Any
        assert hints["stats"] == Optional[StatisticsResult]
        assert hints["return"] is bool

        hints = get_type_hints(BooleanDomain.explain)
        assert hints["value"] == Any
        assert hints["stats"] == Optional[StatisticsResult]
        assert hints["return"] is str

    def test_string_representation(self):
        """Test string representation of domain."""
        domain = BooleanDomain(name="test")
        # Just ensure no error
        repr(domain)
        str(domain)

    def test_multiple_instances_independent(self):
        """Test that multiple instances are independent."""
        domain1 = BooleanDomain(name="first")
        domain2 = BooleanDomain(name="second")

        assert domain1.name == "first"
        assert domain2.name == "second"
        assert domain1.categories == domain2.categories  # Same categories
        assert domain1 is not domain2  # Different objects
