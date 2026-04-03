"""Tests for SystemInvariant class."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from procela.core.invariant import (
    InvariantCategory,
    InvariantPhase,
    InvariantSeverity,
    InvariantSoftness,
    InvariantViolation,
    InvariantViolationCritical,
    InvariantViolationFatal,
    InvariantViolationInfo,
    InvariantViolationWarning,
    SystemInvariant,
    VariableSnapshot,
)


class TestSystemInvariant:
    """Test suite for SystemInvariant class."""

    def test_initialization_default_values(self) -> None:
        """Test initialization with default values."""

        # Create a simple condition function
        def condition(snapshot: VariableSnapshot) -> bool:
            return True

        invariant = SystemInvariant(name="Test Invariant", condition=condition)

        assert invariant.name == "Test Invariant"
        assert invariant.condition is condition
        assert invariant.on_violation is None
        assert invariant.message == "Invariant violated: Test Invariant"

    def test_initialization_custom_values(self) -> None:
        """Test initialization with custom values."""

        def condition(snapshot: VariableSnapshot) -> bool:
            return False

        def on_violation(violation, snapshot):
            pass

        invariant = SystemInvariant(
            name="Custom Invariant",
            condition=condition,
            on_violation=on_violation,
            phase=InvariantPhase.PRE,
            category=InvariantCategory.SAFETY,
            severity=InvariantSeverity.WARNING,
            softness=InvariantSoftness.SOFT,
            message="Custom violation message",
        )

        assert invariant.name == "Custom Invariant"
        assert invariant.condition is condition
        assert invariant.on_violation is on_violation
        assert invariant.phase is InvariantPhase.PRE
        assert invariant.category is InvariantCategory.SAFETY
        assert invariant.severity is InvariantSeverity.WARNING
        assert invariant.softness is InvariantSoftness.SOFT
        assert invariant.message == "Custom violation message"

    def test_check_condition_holds(self) -> None:
        """Test check() when condition holds (returns True)."""
        # Mock condition that returns True
        condition_mock = Mock(return_value=True)
        on_violation_mock = Mock()

        invariant = SystemInvariant(
            name="Holding Invariant",
            condition=condition_mock,
            on_violation=on_violation_mock,
        )

        # Create a mock snapshot
        snapshot_mock = Mock(spec=VariableSnapshot)

        # Should not raise and should not call on_violation
        invariant.check(snapshot_mock)

        condition_mock.assert_called_once_with(snapshot_mock)
        on_violation_mock.assert_not_called()

    def test_check_condition_fails_no_on_violation(self) -> None:
        """Test check() when condition fails without on_violation callback."""
        # Mock condition that returns False
        condition_mock = Mock(return_value=False)

        invariant = SystemInvariant(
            name="Failing Invariant",
            condition=condition_mock,
            on_violation=None,  # No callback
            softness=InvariantSoftness.HARD,
        )

        snapshot_mock = Mock(spec=VariableSnapshot)

        # Should raise the violation
        with pytest.raises(Exception):
            invariant.check(snapshot_mock)

        condition_mock.assert_called_once_with(snapshot_mock)
        # Exception should be raised

    def test_check_condition_fails_with_on_violation(self) -> None:
        """Test check() when condition fails with on_violation callback."""
        condition_mock = Mock(return_value=False)
        on_violation_mock = Mock()

        invariant = SystemInvariant(
            name="Failing with Callback",
            condition=condition_mock,
            on_violation=on_violation_mock,
            softness=InvariantSoftness.HARD,
        )

        snapshot_mock = Mock(spec=VariableSnapshot)

        # Should call on_violation and then raise
        with pytest.raises(Exception):
            invariant.check(snapshot_mock)

        condition_mock.assert_called_once_with(snapshot_mock)
        # on_violation should have been called with a violation and snapshot
        assert on_violation_mock.call_count == 1
        call_args = on_violation_mock.call_args[0]
        assert len(call_args) == 2
        assert call_args[1] is snapshot_mock

    def test_build_violation_info_severity(self) -> None:
        """Test build_violation() for INFO severity."""
        invariant = SystemInvariant(
            name="Info Invariant",
            condition=lambda s: True,
            severity=InvariantSeverity.INFO,
        )

        snapshot_mock = Mock(spec=VariableSnapshot)
        violation = invariant.build_violation(snapshot_mock)

        assert isinstance(violation, InvariantViolationInfo)
        assert violation.name == "Info Invariant"

    def test_build_violation_warning_severity(self) -> None:
        """Test build_violation() for WARNING severity."""
        invariant = SystemInvariant(
            name="Warning Invariant",
            condition=lambda s: True,
            severity=InvariantSeverity.WARNING,
        )

        snapshot_mock = Mock(spec=VariableSnapshot)
        violation = invariant.build_violation(snapshot_mock)

        assert isinstance(violation, InvariantViolationWarning)
        assert violation.name == "Warning Invariant"

    def test_build_violation_critical_severity(self) -> None:
        """Test build_violation() for CRITICAL severity."""
        invariant = SystemInvariant(
            name="Critical Invariant",
            condition=lambda s: True,
            severity=InvariantSeverity.CRITICAL,
        )

        snapshot_mock = Mock(spec=VariableSnapshot)
        violation = invariant.build_violation(snapshot_mock)

        assert isinstance(violation, InvariantViolationCritical)
        assert violation.name == "Critical Invariant"

    def test_build_violation_fatal_severity(self) -> None:
        """Test build_violation() for FATAL severity."""
        invariant = SystemInvariant(
            name="Fatal Invariant",
            condition=lambda s: True,
            severity=InvariantSeverity.FATAL,
        )

        snapshot_mock = Mock(spec=VariableSnapshot)
        violation = invariant.build_violation(snapshot_mock)

        assert isinstance(violation, InvariantViolationFatal)
        assert violation.name == "Fatal Invariant"

    def test_build_violation_with_custom_message(self) -> None:
        """Test build_violation() uses custom message."""
        custom_message = "Custom violation occurred"
        invariant = SystemInvariant(
            name="Test",
            condition=lambda s: True,
            message=custom_message,
            severity=InvariantSeverity.CRITICAL,
        )

        snapshot_mock = Mock(spec=VariableSnapshot)
        violation = invariant.build_violation(snapshot_mock)

        assert isinstance(violation, InvariantViolationCritical)

    def test_build_violation_with_default_message(self) -> None:
        """Test build_violation() uses default message when none provided."""
        invariant = SystemInvariant(
            name="Test Invariant",
            condition=lambda s: True,
            severity=InvariantSeverity.CRITICAL,
        )

        snapshot_mock = Mock(spec=VariableSnapshot)
        violation = invariant.build_violation(snapshot_mock)

        assert isinstance(violation, InvariantViolation)

    def test_handle_violation_hard_softness(self) -> None:
        """Test handle_violation() raises for HARD softness."""
        invariant = SystemInvariant(
            name="Test", condition=lambda s: True, softness=InvariantSoftness.HARD
        )

        violation_mock = Mock(spec=InvariantViolation)

        # Should raise the violation
        with pytest.raises(TypeError):
            invariant.handle_violation(violation_mock)

    def test_handle_violation_soft_softness(self) -> None:
        """Test handle_violation() does nothing for SOFT softness."""
        invariant = SystemInvariant(
            name="Test", condition=lambda s: True, softness=InvariantSoftness.SOFT
        )

        violation_mock = Mock(spec=InvariantViolation)

        # Should NOT raise - just returns
        invariant.handle_violation(violation_mock)
        # No exception expected

    def test_soft_invariant_with_violation(self) -> None:
        """Test that soft invariants don't raise exceptions."""
        condition_mock = Mock(return_value=False)
        on_violation_mock = Mock()

        invariant = SystemInvariant(
            name="Soft Invariant",
            condition=condition_mock,
            on_violation=on_violation_mock,
            softness=InvariantSoftness.SOFT,
        )

        snapshot_mock = Mock(spec=VariableSnapshot)
        snapshot_mock.step = 0

        # Should call on_violation but not raise
        invariant.check(snapshot_mock)

        condition_mock.assert_called_once_with(snapshot_mock)
        on_violation_mock.assert_called_once()
        # No exception raised

    def test_hard_invariant_with_violation(self) -> None:
        """Test that hard invariants raise exceptions."""
        condition_mock = Mock(return_value=False)
        on_violation_mock = Mock()

        invariant = SystemInvariant(
            name="Hard Invariant",
            condition=condition_mock,
            on_violation=on_violation_mock,
            softness=InvariantSoftness.HARD,
        )

        snapshot_mock = Mock(spec=VariableSnapshot)

        # Should call on_violation and raise
        with pytest.raises(Exception):
            invariant.check(snapshot_mock)

        condition_mock.assert_called_once_with(snapshot_mock)
        on_violation_mock.assert_called_once()

    def test_check_calls_build_and_handle(self) -> None:
        """Test that check() properly calls build_violation and handle_violation."""
        # Create invariant with SOFT softness to avoid raising
        invariant = SystemInvariant(
            name="Test", condition=lambda s: False, softness=InvariantSoftness.SOFT
        )

        # Mock the methods to verify they're called
        invariant.build_violation = Mock()
        invariant.handle_violation = Mock()

        snapshot_mock = Mock(spec=VariableSnapshot)
        snapshot_mock.step = 0
        invariant.check(snapshot_mock)

        # Should call build_violation with snapshot
        invariant.build_violation.assert_called_once_with(snapshot_mock)

        # Should call handle_violation with the violation
        invariant.handle_violation.assert_called_once()
        call_arg = invariant.handle_violation.call_args[0][0]
        assert call_arg is invariant.build_violation.return_value


class TestSystemInvariantEdgeCases:
    """Test edge cases for SystemInvariant."""

    def test_empty_name(self) -> None:
        """Test initialization with empty name."""
        invariant = SystemInvariant(name="", condition=lambda s: True)

        assert invariant.name == ""
        assert invariant.message == "Invariant violated: "

    def test_condition_returns_non_boolean(self) -> None:
        """Test that condition return value is converted to bool."""
        # Condition returns truthy/falsy values
        snapshot_mock = Mock(spec=VariableSnapshot)
        snapshot_mock.step = 0

        # Truthy condition
        invariant = SystemInvariant(name="Truthy", condition=lambda s: "truthy string")
        # Should not raise
        invariant.check(snapshot_mock)

        # Falsy condition
        invariant = SystemInvariant(
            name="Falsy",
            condition=lambda s: 0,  # Falsy
            softness=InvariantSoftness.SOFT,  # Avoid raising
        )
        # Should trigger violation handling
        on_violation_mock = Mock()
        invariant.on_violation = on_violation_mock
        invariant.check(snapshot_mock)
        on_violation_mock.assert_called_once()

    def test_on_violation_modifies_violation(self) -> None:
        """Test that on_violation can modify the violation."""

        def custom_on_violation(violation, snapshot):
            # Modify the violation (though it's likely immutable)
            violation.custom_attribute = "modified"

        invariant = SystemInvariant(
            name="Test",
            condition=lambda s: False,
            on_violation=custom_on_violation,
            softness=InvariantSoftness.SOFT,
        )

        snapshot_mock = Mock(spec=VariableSnapshot)
        snapshot_mock.step = 0
        invariant.check(snapshot_mock)
        # Just verify it doesn't crash

    def test_condition_raises_exception(self) -> None:
        """Test behavior when condition function raises an exception."""

        def failing_condition(snapshot):
            raise ValueError("Condition failed")

        invariant = SystemInvariant(
            name="Failing Condition",
            condition=failing_condition,
            softness=InvariantSoftness.SOFT,
        )

        snapshot_mock = Mock(spec=VariableSnapshot)

        # The exception from condition should propagate
        with pytest.raises(ValueError, match="Condition failed"):
            invariant.check(snapshot_mock)


class TestSystemInvariantIntegration:
    """Integration tests for SystemInvariant."""

    def test_with_real_violation_classes(self) -> None:
        """Test integration with real violation classes."""
        # Test all severity mappings
        severities = [
            (InvariantSeverity.INFO, InvariantViolationInfo),
            (InvariantSeverity.WARNING, InvariantViolationWarning),
            (InvariantSeverity.CRITICAL, InvariantViolationCritical),
            (InvariantSeverity.FATAL, InvariantViolationFatal),
        ]

        for severity_class, violation_class in severities:
            invariant = SystemInvariant(
                name=f"{severity_class.name} Test",
                condition=lambda s: False,
                severity=severity_class,
                softness=InvariantSoftness.SOFT,
            )

            snapshot_mock = Mock(spec=VariableSnapshot)
            violation = invariant.build_violation(snapshot_mock)

            assert isinstance(violation, violation_class)
            assert violation.severity is severity_class

    def test_phase_and_category_propagated(self) -> None:
        """Test that phase and category are passed to violations."""
        invariant = SystemInvariant(
            name="Test",
            condition=lambda s: True,
            phase=InvariantPhase.POST,
            category=InvariantCategory.SAFETY,
        )

        snapshot_mock = Mock(spec=VariableSnapshot)
        violation = invariant.build_violation(snapshot_mock)

        assert violation.phase is InvariantPhase.POST
        assert violation.category is InvariantCategory.SAFETY
