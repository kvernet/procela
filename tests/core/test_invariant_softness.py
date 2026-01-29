"""Tests for InvariantSoftness enum."""

from __future__ import annotations

from enum import Enum

import pytest

from procela.core.invariant import InvariantSoftness


class TestInvariantSoftness:
    """Test suite for InvariantSoftness enum."""

    def test_enum_is_enum(self) -> None:
        """Test that InvariantSoftness is an Enum subclass."""
        assert issubclass(InvariantSoftness, Enum)

    def test_all_members_exist(self) -> None:
        """Test that all expected enum members exist."""
        members = list(InvariantSoftness)
        member_names = [member.name for member in members]

        expected_names = ["HARD", "SOFT"]
        assert set(member_names) == set(expected_names)
        assert len(members) == 2

    def test_member_values(self) -> None:
        """Test that members have unique auto-generated values."""
        values = [member.value for member in InvariantSoftness]
        assert len(set(values)) == len(values)  # All unique
        assert all(isinstance(value, int) for value in values)
        assert sorted(values) == [1, 2]  # auto() starts at 1

    def test_member_access_by_name(self) -> None:
        """Test accessing enum members by name."""
        assert InvariantSoftness.HARD.name == "HARD"
        assert InvariantSoftness.SOFT.name == "SOFT"

    def test_member_access_by_value(self) -> None:
        """Test accessing enum members by value."""
        hard_value = InvariantSoftness.HARD.value
        soft_value = InvariantSoftness.SOFT.value

        assert InvariantSoftness(hard_value) is InvariantSoftness.HARD
        assert InvariantSoftness(soft_value) is InvariantSoftness.SOFT

    def test_iteration(self) -> None:
        """Test iterating over enum members."""
        members = list(InvariantSoftness)
        assert len(members) == 2
        assert members[0] is InvariantSoftness.HARD
        assert members[1] is InvariantSoftness.SOFT

    def test_docstrings(self) -> None:
        """Test docstrings."""
        assert InvariantSoftness.__doc__ is not None
        assert (
            "Defines whether an invariant is strict or tolerant"
            in InvariantSoftness.__doc__
        )

    def test_membership_testing(self) -> None:
        """Test membership testing with 'in' operator."""
        assert InvariantSoftness.HARD in InvariantSoftness
        assert InvariantSoftness.SOFT in InvariantSoftness
        assert "HARD" not in [
            m.value for m in InvariantSoftness
        ]  # String is not a member

    def test_equality_and_identity(self) -> None:
        """Test equality and identity comparisons."""
        assert InvariantSoftness.HARD == InvariantSoftness.HARD
        assert InvariantSoftness.HARD is InvariantSoftness.HARD
        assert InvariantSoftness.HARD != InvariantSoftness.SOFT

    def test_hashability(self) -> None:
        """Test that enum members are hashable."""
        softness_set = {InvariantSoftness.HARD, InvariantSoftness.SOFT}
        assert len(softness_set) == 2

        softness_dict = {
            InvariantSoftness.HARD: "strict",
            InvariantSoftness.SOFT: "tolerant",
        }
        assert softness_dict[InvariantSoftness.HARD] == "strict"

    def test_string_representation(self) -> None:
        """Test string representations of enum members."""
        assert repr(InvariantSoftness.HARD) == "<InvariantSoftness.HARD: 1>"
        assert str(InvariantSoftness.HARD) == "InvariantSoftness.HARD"

    def test_invalid_value_access(self) -> None:
        """Test that accessing with invalid value raises ValueError."""
        with pytest.raises(ValueError):
            InvariantSoftness(0)

        with pytest.raises(ValueError):
            InvariantSoftness("HARD")

    def test_usage_in_type_hints(self) -> None:
        """Test that enum works with type hints."""

        def get_description(softness: InvariantSoftness) -> str:
            return "strict" if softness is InvariantSoftness.HARD else "tolerant"

        assert get_description(InvariantSoftness.HARD) == "strict"
        assert get_description(InvariantSoftness.SOFT) == "tolerant"

    def test_usage_in_control_flow(self) -> None:
        """Test usage in control flow statements."""

        def should_raise_exception(softness: InvariantSoftness) -> bool:
            return softness is InvariantSoftness.HARD

        assert should_raise_exception(InvariantSoftness.HARD) is True
        assert should_raise_exception(InvariantSoftness.SOFT) is False
