"""Tests for InvariantPhase enum."""

from __future__ import annotations

from enum import Enum

import pytest

from procela.core.invariant import (
    InvariantCategory,
    InvariantPhase,
    InvariantSeverity,
    InvariantViolation,
)


class TestInvariantPhase:
    """Test suite for InvariantPhase enum."""

    def test_enum_is_enum(self, invariant_phase_enum) -> None:
        """Test that InvariantPhase is an Enum subclass."""
        assert issubclass(InvariantPhase, Enum)

    def test_all_members_exist(self) -> None:
        """Test that all expected enum members exist."""
        members = list(InvariantPhase)
        member_names = [member.name for member in members]

        expected_names = ["PRE", "RUNTIME", "POST"]

        assert set(member_names) == set(expected_names)
        assert len(members) == 3

    def test_member_values(self) -> None:
        """Test that members have unique auto-generated values."""
        values = [member.value for member in InvariantPhase]

        # All values should be unique
        assert len(set(values)) == len(values)

        # Values should be integers starting from 1 (auto() behavior)
        assert all(isinstance(value, int) for value in values)
        assert min(values) == 1
        assert max(values) == 3

    def test_member_access_by_name(self) -> None:
        """Test accessing enum members by name."""
        assert InvariantPhase.PRE.name == "PRE"
        assert InvariantPhase.RUNTIME.name == "RUNTIME"
        assert InvariantPhase.POST.name == "POST"

    def test_member_access_by_value(self) -> None:
        """Test accessing enum members by value."""
        # Get the value for each member
        pre_value = InvariantPhase.PRE.value
        runtime_value = InvariantPhase.RUNTIME.value
        post_value = InvariantPhase.POST.value

        # Test that we can retrieve members by value
        assert InvariantPhase(pre_value) is InvariantPhase.PRE
        assert InvariantPhase(runtime_value) is InvariantPhase.RUNTIME
        assert InvariantPhase(post_value) is InvariantPhase.POST

    def test_iteration(self) -> None:
        """Test iterating over enum members."""
        members = list(InvariantPhase)
        assert len(members) == 3

        # Check all members are present in iteration
        member_names = [m.name for m in members]
        assert "PRE" in member_names
        assert "RUNTIME" in member_names
        assert "POST" in member_names

        # Test iteration order (should be definition order)
        assert members[0] is InvariantPhase.PRE
        assert members[1] is InvariantPhase.RUNTIME
        assert members[2] is InvariantPhase.POST

    def test_docstrings(self) -> None:
        """Test docstrings."""
        assert InvariantPhase.__doc__ is not None
        assert (
            "Phase of execution at which an invariant is evaluated."
            in InvariantPhase.PRE.__doc__
        )

    def test_class_docstring(self) -> None:
        """Test that the enum class has a docstring."""
        assert InvariantPhase.__doc__ is not None
        assert "Phase of execution" in InvariantPhase.__doc__
        assert "invariant is evaluated" in InvariantPhase.__doc__

    def test_membership_testing(self) -> None:
        """Test membership testing with 'in' operator."""
        assert InvariantPhase.PRE in InvariantPhase
        assert InvariantPhase.RUNTIME in InvariantPhase
        assert InvariantPhase.POST in InvariantPhase

        # Non-members should not be in the enum
        members = list(InvariantPhase)
        member_values = [m.value for m in members]
        assert "PRE" not in member_values
        assert 1 in member_values
        assert None not in member_values

    def test_equality_and_identity(self) -> None:
        """Test equality and identity comparisons."""
        # Same object should be equal
        assert InvariantPhase.PRE == InvariantPhase.PRE
        assert InvariantPhase.PRE is InvariantPhase.PRE

        # Different members should not be equal
        assert InvariantPhase.PRE != InvariantPhase.RUNTIME
        assert InvariantPhase.PRE is not InvariantPhase.RUNTIME

        # Members should not equal their names or values
        assert InvariantPhase.PRE != "PRE"
        assert InvariantPhase.PRE != 1

    def test_hashability(self) -> None:
        """Test that enum members are hashable."""
        # Should be able to create a set of enum members
        phase_set = {
            InvariantPhase.PRE,
            InvariantPhase.RUNTIME,
            InvariantPhase.POST,
        }
        assert len(phase_set) == 3

        # Should be able to use as dictionary keys
        phase_dict = {
            InvariantPhase.PRE: "pre-execution",
            InvariantPhase.RUNTIME: "runtime",
            InvariantPhase.POST: "post-execution",
        }
        assert len(phase_dict) == 3
        assert phase_dict[InvariantPhase.PRE] == "pre-execution"

    def test_string_representation(self) -> None:
        """Test string representations of enum members."""
        # Test repr format
        assert repr(InvariantPhase.PRE).startswith("<InvariantPhase.PRE:")
        assert "InvariantPhase.PRE" in repr(InvariantPhase.PRE)

        # Test str format
        assert str(InvariantPhase.PRE) == "InvariantPhase.PRE"

        # Format should be consistent across members
        for member in InvariantPhase:
            assert f"InvariantPhase.{member.name}" in repr(member)
            assert str(member) == f"InvariantPhase.{member.name}"

    def test_name_and_value_properties(self) -> None:
        """Test name and value properties."""
        for member in InvariantPhase:
            assert isinstance(member.name, str)
            assert isinstance(member.value, int)
            assert hasattr(member, "name")
            assert hasattr(member, "value")

    def test_auto_functionality(self) -> None:
        """Test that auto() generates sequential integers."""
        values = [member.value for member in InvariantPhase]

        # auto() generates sequential integers starting from 1
        expected_values = [1, 2, 3]
        assert values == expected_values

        # Verify sequentiality
        assert values[0] == 1
        assert values[1] == 2
        assert values[2] == 3


class TestInvariantPhaseEdgeCases:
    """Test edge cases for InvariantPhase enum."""

    def test_invalid_value_access(self) -> None:
        """Test that accessing with invalid value raises ValueError."""
        with pytest.raises(ValueError):
            InvariantPhase(0)

        with pytest.raises(ValueError):
            InvariantPhase(999)

        with pytest.raises(ValueError):
            InvariantPhase("PRE")

        with pytest.raises(ValueError):
            InvariantPhase(None)

    def test_case_sensitivity(self) -> None:
        """Test that member names are case-sensitive."""
        # Access by name should match exact case
        assert hasattr(InvariantPhase, "PRE")
        assert not hasattr(InvariantPhase, "pre")
        assert not hasattr(InvariantPhase, "Pre")
        assert not hasattr(InvariantPhase, "runtime")  # lowercase

    def test_no_extra_members(self) -> None:
        """Test that no extra members exist beyond defined ones."""
        all_members = dir(InvariantPhase)

        # Filter out special methods and attributes
        regular_members = [
            name
            for name in all_members
            if not name.startswith("_") and not name.islower()
        ]

        # Only the 3 defined members should be in regular members
        assert set(regular_members) == {"PRE", "RUNTIME", "POST"}

    def test_member_immutability(self) -> None:
        """Test that enum members are immutable."""
        # Members should not allow attribute assignment
        with pytest.raises(AttributeError):
            InvariantPhase.PRE.value = 999

        # Cannot delete existing members
        with pytest.raises(AttributeError):
            del InvariantPhase.PRE


class TestInvariantPhaseFunctional:
    """Functional tests for InvariantPhase usage patterns."""

    def test_usage_in_dict(self) -> None:
        """Test typical dictionary usage pattern."""
        # Create a dictionary mapping phases to descriptions
        phase_descriptions = {
            InvariantPhase.PRE: "Pre-execution checks",
            InvariantPhase.RUNTIME: "Runtime monitoring",
            InvariantPhase.POST: "Post-execution validation",
        }

        assert len(phase_descriptions) == 3
        assert phase_descriptions[InvariantPhase.PRE] == "Pre-execution checks"

        # Test iteration over dictionary keys
        for phase in phase_descriptions:
            assert phase in InvariantPhase

    def test_usage_in_set(self) -> None:
        """Test typical set usage pattern."""
        # Create a set of active phases
        active_phases = {
            InvariantPhase.PRE,
            InvariantPhase.RUNTIME,
        }

        assert len(active_phases) == 2
        assert InvariantPhase.PRE in active_phases
        assert InvariantPhase.RUNTIME in active_phases
        assert InvariantPhase.POST not in active_phases

        # Test set operations
        all_phases = set(InvariantPhase)
        inactive_phases = all_phases - active_phases
        assert InvariantPhase.POST in inactive_phases

    def test_usage_in_control_flow(self) -> None:
        """Test usage in control flow statements."""

        # Test in if-elif chain
        def get_phase_description(phase: InvariantPhase) -> str:
            if phase is InvariantPhase.PRE:
                return "Before execution"
            elif phase is InvariantPhase.RUNTIME:
                return "During execution"
            elif phase is InvariantPhase.POST:
                return "After execution"
            else:
                return "Unknown"

        assert get_phase_description(InvariantPhase.PRE) == "Before execution"
        assert get_phase_description(InvariantPhase.RUNTIME) == "During execution"
        assert get_phase_description(InvariantPhase.POST) == "After execution"

    def test_usage_in_type_hints(self) -> None:
        """Test that enum works with type hints."""

        # Type hints should accept the enum
        def process_phase(phase: InvariantPhase) -> str:
            return phase.name

        # Should work with all members
        assert process_phase(InvariantPhase.PRE) == "PRE"
        assert process_phase(InvariantPhase.RUNTIME) == "RUNTIME"
        assert process_phase(InvariantPhase.POST) == "POST"

        # Test with Union type (common pattern)
        def handle_phase_or_none(phase: InvariantPhase | None) -> str:
            return phase.name if phase else "None"

        assert handle_phase_or_none(InvariantPhase.PRE) == "PRE"
        assert handle_phase_or_none(None) == "None"

    def test_serialization_deserialization(self) -> None:
        """Test that enum members can be serialized and deserialized."""
        # Serialize to name
        phase_name = InvariantPhase.PRE.name
        assert phase_name == "PRE"

        # Deserialize from name
        deserialized_phase = InvariantPhase[phase_name]
        assert deserialized_phase is InvariantPhase.PRE

        # Serialize to value
        phase_value = InvariantPhase.PRE.value
        assert isinstance(phase_value, int)

        # Deserialize from value
        deserialized_from_value = InvariantPhase(phase_value)
        assert deserialized_from_value is InvariantPhase.PRE

    def test_typical_use_case_scenario(self) -> None:
        """Test a realistic use case scenario."""

        # Simulate a system that evaluates invariants at different phases
        class InvariantEvaluator:
            def __init__(self):
                self.evaluations = {
                    InvariantPhase.PRE: [],
                    InvariantPhase.RUNTIME: [],
                    InvariantPhase.POST: [],
                }

            def add_invariant(self, phase: InvariantPhase, invariant_name: str):
                self.evaluations[phase].append(invariant_name)

            def evaluate_phase(self, phase: InvariantPhase):
                return len(self.evaluations[phase])

        # Create evaluator and add invariants
        evaluator = InvariantEvaluator()
        evaluator.add_invariant(InvariantPhase.PRE, "model_completeness")
        evaluator.add_invariant(InvariantPhase.PRE, "initialization_check")
        evaluator.add_invariant(InvariantPhase.RUNTIME, "safety_bounds")
        evaluator.add_invariant(InvariantPhase.POST, "outcome_validation")

        # Verify counts
        assert evaluator.evaluate_phase(InvariantPhase.PRE) == 2
        assert evaluator.evaluate_phase(InvariantPhase.RUNTIME) == 1
        assert evaluator.evaluate_phase(InvariantPhase.POST) == 1

        # Verify the actual lists
        assert "model_completeness" in evaluator.evaluations[InvariantPhase.PRE]
        assert "safety_bounds" in evaluator.evaluations[InvariantPhase.RUNTIME]


class TestInvariantPhaseIntegration:
    """Integration tests for InvariantPhase with other components."""

    def test_with_invariant_violation(self) -> None:
        """Test integration with InvariantViolation classes."""
        # Assuming InvariantViolation is imported
        # Create a violation with a specific phase
        violation = InvariantViolation(
            name="Test Violation",
            message="Test message",
            category=InvariantCategory.SAFETY,
            severity=InvariantSeverity.WARNING,
            phase=InvariantPhase.RUNTIME,
        )

        # Verify the phase is correctly set
        assert violation.phase is InvariantPhase.RUNTIME
        assert violation.phase.name == "RUNTIME"

    def test_phase_transitions(self) -> None:
        """Test conceptual phase transitions."""
        # Define expected order of phases
        phases_in_order = list(InvariantPhase)

        # Conceptually, phases should occur in this order
        assert phases_in_order[0] is InvariantPhase.PRE
        assert phases_in_order[1] is InvariantPhase.RUNTIME
        assert phases_in_order[2] is InvariantPhase.POST

        # Helper function to get next phase (conceptual)
        def get_next_phase(current: InvariantPhase) -> InvariantPhase:
            all_phases = list(InvariantPhase)
            current_index = all_phases.index(current)
            if current_index < len(all_phases) - 1:
                return all_phases[current_index + 1]
            return current  # Last phase has no next

        # Test transitions
        assert get_next_phase(InvariantPhase.PRE) is InvariantPhase.RUNTIME
        assert get_next_phase(InvariantPhase.RUNTIME) is InvariantPhase.POST
        assert get_next_phase(InvariantPhase.POST) is InvariantPhase.POST  # No next


# Optional: Fixture for dependency injection in tests
@pytest.fixture
def invariant_phase_enum():
    """Fixture to provide the InvariantPhase enum."""
    from procela.core.invariant import InvariantPhase

    return InvariantPhase
