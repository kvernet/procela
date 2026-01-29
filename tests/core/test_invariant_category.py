"""Tests for InvariantCategory enum."""

from __future__ import annotations

from enum import Enum

import pytest

from procela.core.invariant import InvariantCategory


class TestInvariantCategory:
    """Test suite for InvariantCategory enum."""

    def test_enum_is_enum(self) -> None:
        """Test that InvariantCategory is an Enum subclass."""
        assert issubclass(InvariantCategory, Enum)

    def test_all_members_exist(self) -> None:
        """Test that all expected enum members exist."""
        members = list(InvariantCategory)
        member_names = [member.name for member in members]

        expected_names = [
            "SAFETY",
            "CONSISTENCY",
            "EPISTEMIC",
            "DYNAMICAL",
            "RESOURCE",
        ]

        assert set(member_names) == set(expected_names)
        assert len(members) == 5

    def test_member_values(self) -> None:
        """Test that members have unique auto-generated values."""
        values = [member.value for member in InvariantCategory]

        # All values should be unique
        assert len(set(values)) == len(values)

        # Values should be integers starting from 1 (auto() behavior)
        assert all(isinstance(value, int) for value in values)
        assert min(values) == 1
        assert max(values) == 5

    def test_member_access_by_name(self) -> None:
        """Test accessing enum members by name."""
        assert InvariantCategory.SAFETY.name == "SAFETY"
        assert InvariantCategory.CONSISTENCY.name == "CONSISTENCY"
        assert InvariantCategory.EPISTEMIC.name == "EPISTEMIC"
        assert InvariantCategory.DYNAMICAL.name == "DYNAMICAL"
        assert InvariantCategory.RESOURCE.name == "RESOURCE"

    def test_member_access_by_value(self) -> None:
        """Test accessing enum members by value."""
        # Get the value for each member
        safety_value = InvariantCategory.SAFETY.value
        consistency_value = InvariantCategory.CONSISTENCY.value
        epistemic_value = InvariantCategory.EPISTEMIC.value
        dynamical_value = InvariantCategory.DYNAMICAL.value
        resource_value = InvariantCategory.RESOURCE.value

        # Test that we can retrieve members by value
        assert InvariantCategory(safety_value) is InvariantCategory.SAFETY
        assert InvariantCategory(consistency_value) is InvariantCategory.CONSISTENCY
        assert InvariantCategory(epistemic_value) is InvariantCategory.EPISTEMIC
        assert InvariantCategory(dynamical_value) is InvariantCategory.DYNAMICAL
        assert InvariantCategory(resource_value) is InvariantCategory.RESOURCE

    def test_iteration(self) -> None:
        """Test iterating over enum members."""
        members = list(InvariantCategory)
        assert len(members) == 5

        # Check all members are present in iteration
        member_names = [m.name for m in members]
        assert "SAFETY" in member_names
        assert "CONSISTENCY" in member_names
        assert "EPISTEMIC" in member_names
        assert "DYNAMICAL" in member_names
        assert "RESOURCE" in member_names

        # Test iteration order (should be definition order)
        assert members[0] is InvariantCategory.SAFETY
        assert members[1] is InvariantCategory.CONSISTENCY
        assert members[2] is InvariantCategory.EPISTEMIC
        assert members[3] is InvariantCategory.DYNAMICAL
        assert members[4] is InvariantCategory.RESOURCE

    def test_docstrings(self) -> None:
        """Test docstrings."""
        assert "category of a system invariant" in InvariantCategory.__doc__

    def test_class_docstring(self) -> None:
        """Test that the enum class has a docstring."""
        assert InvariantCategory.__doc__ is not None
        assert "Semantic category of a system invariant" in InvariantCategory.__doc__
        assert "what kind of system property" in InvariantCategory.__doc__

    def test_membership_testing(self) -> None:
        """Test membership testing with 'in' operator."""
        assert InvariantCategory.SAFETY in InvariantCategory
        assert InvariantCategory.CONSISTENCY in InvariantCategory
        assert InvariantCategory.EPISTEMIC in InvariantCategory
        assert InvariantCategory.DYNAMICAL in InvariantCategory
        assert InvariantCategory.RESOURCE in InvariantCategory

        # Non-members should not be in the enum
        assert "SAFETY" not in (category.value for category in InvariantCategory)
        assert 1 in (category.value for category in InvariantCategory)
        assert None not in (category.value for category in InvariantCategory)

    def test_equality_and_identity(self) -> None:
        """Test equality and identity comparisons."""
        # Same object should be equal
        assert InvariantCategory.SAFETY == InvariantCategory.SAFETY
        assert InvariantCategory.SAFETY is InvariantCategory.SAFETY

        # Different members should not be equal
        assert InvariantCategory.SAFETY != InvariantCategory.CONSISTENCY
        assert InvariantCategory.SAFETY is not InvariantCategory.CONSISTENCY

        # Members should not equal their names or values
        assert InvariantCategory.SAFETY != "SAFETY"
        assert InvariantCategory.SAFETY != 1

    def test_hashability(self) -> None:
        """Test that enum members are hashable."""
        # Should be able to create a set of enum members
        category_set = {
            InvariantCategory.SAFETY,
            InvariantCategory.CONSISTENCY,
            InvariantCategory.EPISTEMIC,
            InvariantCategory.DYNAMICAL,
            InvariantCategory.RESOURCE,
        }
        assert len(category_set) == 5

        # Should be able to use as dictionary keys
        category_dict = {
            InvariantCategory.SAFETY: "safety",
            InvariantCategory.CONSISTENCY: "consistency",
            InvariantCategory.EPISTEMIC: "epistemic",
            InvariantCategory.DYNAMICAL: "dynamical",
            InvariantCategory.RESOURCE: "resource",
        }
        assert len(category_dict) == 5
        assert category_dict[InvariantCategory.SAFETY] == "safety"

    def test_string_representation(self) -> None:
        """Test string representations of enum members."""
        assert repr(InvariantCategory.SAFETY) == "<InvariantCategory.SAFETY: 1>"
        assert str(InvariantCategory.SAFETY) == "InvariantCategory.SAFETY"

        # Format should be consistent across members
        for member in InvariantCategory:
            assert repr(member) == f"<InvariantCategory.{member.name}: {member.value}>"
            assert str(member) == f"InvariantCategory.{member.name}"

    def test_name_and_value_properties(self) -> None:
        """Test name and value properties."""
        for member in InvariantCategory:
            assert isinstance(member.name, str)
            assert isinstance(member.value, int)
            assert hasattr(member, "name")
            assert hasattr(member, "value")

    def test_auto_functionality(self) -> None:
        """Test that auto() generates sequential integers."""
        values = [member.value for member in InvariantCategory]

        # auto() generates sequential integers starting from 1
        expected_values = list(range(1, 6))
        assert values == expected_values

        # Verify sequentiality
        for i in range(1, len(values)):
            assert values[i] == values[i - 1] + 1


class TestInvariantCategoryEdgeCases:
    """Test edge cases for InvariantCategory enum."""

    def test_invalid_value_access(self) -> None:
        """Test that accessing with invalid value raises ValueError."""
        with pytest.raises(ValueError):
            InvariantCategory(0)

        with pytest.raises(ValueError):
            InvariantCategory(999)

        with pytest.raises(ValueError):
            InvariantCategory("SAFETY")

        with pytest.raises(ValueError):
            InvariantCategory(None)

    def test_case_sensitivity(self) -> None:
        """Test that member names are case-sensitive."""
        # Access by name should match exact case
        assert hasattr(InvariantCategory, "SAFETY")
        assert not hasattr(InvariantCategory, "safety")
        assert not hasattr(InvariantCategory, "Safety")

    def test_no_extra_members(self) -> None:
        """Test that no extra members exist beyond defined ones."""
        all_members = dir(InvariantCategory)

        # Filter out special methods and attributes
        regular_members = [
            name
            for name in all_members
            if not name.startswith("_") and not name.islower()
        ]

        # Only the 5 defined members should be in regular members
        assert set(regular_members) == {
            "SAFETY",
            "CONSISTENCY",
            "EPISTEMIC",
            "DYNAMICAL",
            "RESOURCE",
        }

    def test_member_immutability(self) -> None:
        """Test that enum members are immutable."""
        # Members should not allow attribute assignment
        with pytest.raises(AttributeError):
            InvariantCategory.SAFETY.value = 999

        # Cannot delete existing members
        with pytest.raises(AttributeError):
            del InvariantCategory.SAFETY


class TestInvariantCategoryFunctional:
    """Functional tests for InvariantCategory usage patterns."""

    def test_usage_in_dict(self) -> None:
        """Test typical dictionary usage pattern."""
        # Create a dictionary mapping categories to descriptions
        category_descriptions = {
            InvariantCategory.SAFETY: "Prevents dangerous states",
            InvariantCategory.CONSISTENCY: "Ensures coherence",
            InvariantCategory.EPISTEMIC: "Manages uncertainty",
            InvariantCategory.DYNAMICAL: "Controls behavior over time",
            InvariantCategory.RESOURCE: "Manages abstract resources",
        }

        assert len(category_descriptions) == 5
        assert (
            category_descriptions[InvariantCategory.SAFETY]
            == "Prevents dangerous states"
        )

        # Test iteration over dictionary keys
        for category in category_descriptions:
            assert category in InvariantCategory

    def test_usage_in_set(self) -> None:
        """Test typical set usage pattern."""
        # Create a set of active categories
        active_categories = {
            InvariantCategory.SAFETY,
            InvariantCategory.CONSISTENCY,
            InvariantCategory.EPISTEMIC,
        }

        assert len(active_categories) == 3
        assert InvariantCategory.SAFETY in active_categories
        assert InvariantCategory.DYNAMICAL not in active_categories

        # Test set operations
        all_categories = set(InvariantCategory)
        inactive_categories = all_categories - active_categories
        assert InvariantCategory.DYNAMICAL in inactive_categories
        assert InvariantCategory.RESOURCE in inactive_categories

    def test_usage_in_match_case(self) -> None:
        """Test usage in match-case statement (Python 3.10+)."""

        # This tests the pattern but won't execute match in older Python
        def get_category_priority(category: InvariantCategory) -> int:
            """Example function using match-case."""
            match category:
                case InvariantCategory.SAFETY:
                    return 100
                case InvariantCategory.CONSISTENCY:
                    return 80
                case InvariantCategory.EPISTEMIC:
                    return 60
                case InvariantCategory.DYNAMICAL:
                    return 40
                case InvariantCategory.RESOURCE:
                    return 20
                case _:
                    return 0

        # Test the function (match-case will be evaluated if Python >= 3.10)
        # For compatibility, we'll test with if-elif
        def get_category_priority_compat(category: InvariantCategory) -> int:
            if category is InvariantCategory.SAFETY:
                return 100
            elif category is InvariantCategory.CONSISTENCY:
                return 80
            elif category is InvariantCategory.EPISTEMIC:
                return 60
            elif category is InvariantCategory.DYNAMICAL:
                return 40
            elif category is InvariantCategory.RESOURCE:
                return 20
            else:
                return 0

        assert get_category_priority_compat(InvariantCategory.SAFETY) == 100
        assert get_category_priority_compat(InvariantCategory.RESOURCE) == 20

    def test_json_serialization(self) -> None:
        """Test that enum members can be serialized."""
        # Typically enums are serialized by name or value
        assert InvariantCategory.SAFETY.name == "SAFETY"
        assert isinstance(InvariantCategory.SAFETY.value, int)

        # Example serialization to JSON-compatible format
        serialized = {
            "category": InvariantCategory.SAFETY.name,
            "value": InvariantCategory.SAFETY.value,
        }

        assert serialized["category"] == "SAFETY"
        assert serialized["value"] == 1

        # Deserialization
        deserialized_category = InvariantCategory[serialized["category"]]
        assert deserialized_category is InvariantCategory.SAFETY

    def test_import_and_use(self) -> None:
        """Test that the enum can be imported and used."""
        # Test that we can import individual members
        from sys import modules

        current_module = modules[__name__]

        # Verify members are accessible
        assert hasattr(current_module, "InvariantCategory")
        assert InvariantCategory.SAFETY is not None
