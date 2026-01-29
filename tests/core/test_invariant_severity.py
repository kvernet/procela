"""Tests for InvariantSeverity enum."""

from __future__ import annotations

from enum import Enum

import pytest

from procela.core.invariant import (
    InvariantCategory,
    InvariantPhase,
    InvariantSeverity,
    InvariantViolationCritical,
    InvariantViolationFatal,
    InvariantViolationInfo,
    InvariantViolationWarning,
)


class TestInvariantSeverity:
    """Test suite for InvariantSeverity enum."""

    def test_enum_is_enum(self) -> None:
        """Test that InvariantSeverity is an Enum subclass."""
        assert issubclass(InvariantSeverity, Enum)

    def test_all_members_exist(self) -> None:
        """Test that all expected enum members exist."""
        members = list(InvariantSeverity)
        member_names = [member.name for member in members]

        expected_names = ["INFO", "WARNING", "CRITICAL", "FATAL"]

        assert set(member_names) == set(expected_names)
        assert len(members) == 4

    def test_member_values(self) -> None:
        """Test that members have unique auto-generated values."""
        values = [member.value for member in InvariantSeverity]

        # All values should be unique
        assert len(set(values)) == len(values)

        # Values should be integers starting from 1 (auto() behavior)
        assert all(isinstance(value, int) for value in values)
        assert min(values) == 1
        assert max(values) == 4

    def test_member_access_by_name(self) -> None:
        """Test accessing enum members by name."""
        assert InvariantSeverity.INFO.name == "INFO"
        assert InvariantSeverity.WARNING.name == "WARNING"
        assert InvariantSeverity.CRITICAL.name == "CRITICAL"
        assert InvariantSeverity.FATAL.name == "FATAL"

    def test_member_access_by_value(self) -> None:
        """Test accessing enum members by value."""
        # Get the value for each member
        info_value = InvariantSeverity.INFO.value
        warning_value = InvariantSeverity.WARNING.value
        critical_value = InvariantSeverity.CRITICAL.value
        fatal_value = InvariantSeverity.FATAL.value

        # Test that we can retrieve members by value
        assert InvariantSeverity(info_value) is InvariantSeverity.INFO
        assert InvariantSeverity(warning_value) is InvariantSeverity.WARNING
        assert InvariantSeverity(critical_value) is InvariantSeverity.CRITICAL
        assert InvariantSeverity(fatal_value) is InvariantSeverity.FATAL

    def test_iteration(self) -> None:
        """Test iterating over enum members."""
        members = list(InvariantSeverity)
        assert len(members) == 4

        # Check all members are present in iteration
        member_names = [m.name for m in members]
        assert "INFO" in member_names
        assert "WARNING" in member_names
        assert "CRITICAL" in member_names
        assert "FATAL" in member_names

        # Test iteration order (should be definition order)
        assert members[0] is InvariantSeverity.INFO
        assert members[1] is InvariantSeverity.WARNING
        assert members[2] is InvariantSeverity.CRITICAL
        assert members[3] is InvariantSeverity.FATAL

    def test_docstrings(self) -> None:
        """Test docstring."""
        assert InvariantSeverity.__doc__ is not None
        assert "Severity level" in InvariantSeverity.__doc__
        assert "invariant violation" in InvariantSeverity.__doc__

    def test_membership_testing(self) -> None:
        """Test membership testing with 'in' operator."""
        assert InvariantSeverity.INFO in InvariantSeverity
        assert InvariantSeverity.WARNING in InvariantSeverity
        assert InvariantSeverity.CRITICAL in InvariantSeverity
        assert InvariantSeverity.FATAL in InvariantSeverity

        # Non-members should not be in the enum
        members = list(InvariantSeverity)
        member_values = [m.value for m in members]
        assert "INFO" not in member_values  # String is not a member
        assert 1 in member_values  # Value is a member
        assert None not in member_values

    def test_equality_and_identity(self) -> None:
        """Test equality and identity comparisons."""
        # Same object should be equal
        assert InvariantSeverity.INFO == InvariantSeverity.INFO
        assert InvariantSeverity.INFO is InvariantSeverity.INFO

        # Different members should not be equal
        assert InvariantSeverity.INFO != InvariantSeverity.WARNING
        assert InvariantSeverity.INFO is not InvariantSeverity.WARNING

        # Members should not equal their names or values
        assert InvariantSeverity.INFO != "INFO"
        assert InvariantSeverity.INFO != 1

    def test_hashability(self) -> None:
        """Test that enum members are hashable."""
        severity_set = {
            InvariantSeverity.INFO,
            InvariantSeverity.WARNING,
            InvariantSeverity.CRITICAL,
            InvariantSeverity.FATAL,
        }
        assert len(severity_set) == 4

        # Should be able to use as dictionary keys
        severity_dict = {
            InvariantSeverity.INFO: "informational",
            InvariantSeverity.WARNING: "warning",
            InvariantSeverity.CRITICAL: "critical",
            InvariantSeverity.FATAL: "fatal",
        }
        assert len(severity_dict) == 4
        assert severity_dict[InvariantSeverity.INFO] == "informational"

    def test_string_representation(self) -> None:
        """Test string representations of enum members."""
        # Test repr format
        assert repr(InvariantSeverity.INFO).startswith("<InvariantSeverity.INFO:")
        assert "InvariantSeverity.INFO" in repr(InvariantSeverity.INFO)

        # Test str format
        assert str(InvariantSeverity.INFO) == "InvariantSeverity.INFO"

        # Format should be consistent across members
        for member in InvariantSeverity:
            assert f"InvariantSeverity.{member.name}" in repr(member)
            assert str(member) == f"InvariantSeverity.{member.name}"

    def test_name_and_value_properties(self) -> None:
        """Test name and value properties."""
        for member in InvariantSeverity:
            assert isinstance(member.name, str)
            assert isinstance(member.value, int)
            assert hasattr(member, "name")
            assert hasattr(member, "value")

    def test_auto_functionality(self) -> None:
        """Test that auto() generates sequential integers."""
        values = [member.value for member in InvariantSeverity]

        # auto() generates sequential integers starting from 1
        expected_values = [1, 2, 3, 4]
        assert values == expected_values

        # Verify sequentiality
        assert values[0] == 1
        assert values[1] == 2
        assert values[2] == 3
        assert values[3] == 4


class TestInvariantSeverityEdgeCases:
    """Test edge cases for InvariantSeverity enum."""

    def test_invalid_value_access(self) -> None:
        """Test that accessing with invalid value raises ValueError."""
        with pytest.raises(ValueError):
            InvariantSeverity(0)

        with pytest.raises(ValueError):
            InvariantSeverity(999)

        with pytest.raises(ValueError):
            InvariantSeverity("INFO")

        with pytest.raises(ValueError):
            InvariantSeverity(None)

    def test_case_sensitivity(self) -> None:
        """Test that member names are case-sensitive."""
        # Access by name should match exact case
        assert hasattr(InvariantSeverity, "INFO")
        assert not hasattr(InvariantSeverity, "info")
        assert not hasattr(InvariantSeverity, "Info")
        assert not hasattr(InvariantSeverity, "warning")  # lowercase


class TestInvariantSeverityComparison:
    """Test comparison operations for InvariantSeverity."""

    def test_severity_hierarchy(self) -> None:
        """Test the conceptual severity hierarchy."""
        # Severity should increase in this order
        severities = list(InvariantSeverity)

        # INFO is least severe
        assert severities[0] is InvariantSeverity.INFO

        # WARNING is more severe than INFO
        assert severities[1] is InvariantSeverity.WARNING

        # CRITICAL is more severe than WARNING
        assert severities[2] is InvariantSeverity.CRITICAL

        # FATAL is most severe
        assert severities[3] is InvariantSeverity.FATAL


class TestInvariantSeverityFunctional:
    """Functional tests for InvariantSeverity usage patterns."""

    def test_usage_in_dict(self) -> None:
        """Test typical dictionary usage pattern."""
        # Create a dictionary mapping severities to actions
        severity_actions = {
            InvariantSeverity.INFO: "log_only",
            InvariantSeverity.WARNING: "log_and_monitor",
            InvariantSeverity.CRITICAL: "log_and_alert",
            InvariantSeverity.FATAL: "log_alert_and_halt",
        }

        assert len(severity_actions) == 4
        assert severity_actions[InvariantSeverity.INFO] == "log_only"

        # Test iteration over dictionary keys
        for severity in severity_actions:
            assert severity in InvariantSeverity

    def test_usage_in_set(self) -> None:
        """Test typical set usage pattern."""
        # Create a set of severities that should trigger alerts
        alerting_severities = {
            InvariantSeverity.CRITICAL,
            InvariantSeverity.FATAL,
        }

        assert len(alerting_severities) == 2
        assert InvariantSeverity.CRITICAL in alerting_severities
        assert InvariantSeverity.FATAL in alerting_severities
        assert InvariantSeverity.INFO not in alerting_severities
        assert InvariantSeverity.WARNING not in alerting_severities

        # Test set operations
        all_severities = set(InvariantSeverity)
        non_alerting_severities = all_severities - alerting_severities
        assert InvariantSeverity.INFO in non_alerting_severities
        assert InvariantSeverity.WARNING in non_alerting_severities

    def test_severity_threshold_check(self) -> None:
        """Test checking if a severity meets or exceeds a threshold."""

        def meets_threshold(
            severity: InvariantSeverity, threshold: InvariantSeverity
        ) -> bool:
            """Check if severity meets or exceeds threshold."""
            # Using value comparison since severities are ordered
            return severity.value >= threshold.value

        # Test various threshold checks
        assert meets_threshold(InvariantSeverity.INFO, InvariantSeverity.INFO)
        assert not meets_threshold(InvariantSeverity.INFO, InvariantSeverity.WARNING)

        assert meets_threshold(InvariantSeverity.WARNING, InvariantSeverity.INFO)
        assert meets_threshold(InvariantSeverity.WARNING, InvariantSeverity.WARNING)
        assert not meets_threshold(
            InvariantSeverity.WARNING, InvariantSeverity.CRITICAL
        )

        assert meets_threshold(InvariantSeverity.CRITICAL, InvariantSeverity.INFO)
        assert meets_threshold(InvariantSeverity.CRITICAL, InvariantSeverity.WARNING)
        assert meets_threshold(InvariantSeverity.CRITICAL, InvariantSeverity.CRITICAL)
        assert not meets_threshold(InvariantSeverity.CRITICAL, InvariantSeverity.FATAL)

        assert meets_threshold(InvariantSeverity.FATAL, InvariantSeverity.INFO)
        assert meets_threshold(InvariantSeverity.FATAL, InvariantSeverity.WARNING)
        assert meets_threshold(InvariantSeverity.FATAL, InvariantSeverity.CRITICAL)
        assert meets_threshold(InvariantSeverity.FATAL, InvariantSeverity.FATAL)

    def test_severity_based_handling(self) -> None:
        """Test handling logic based on severity levels."""

        def handle_violation(severity: InvariantSeverity) -> str:
            """Example handling logic based on severity."""
            if severity is InvariantSeverity.INFO:
                return "Log to file"
            elif severity is InvariantSeverity.WARNING:
                return "Log and send to monitoring"
            elif severity is InvariantSeverity.CRITICAL:
                return "Log, monitor, and alert on-call"
            elif severity is InvariantSeverity.FATAL:
                return "Log, alert, and halt execution"
            else:
                return "Unknown severity"

        # Test handling for all severities
        assert handle_violation(InvariantSeverity.INFO) == "Log to file"
        assert (
            handle_violation(InvariantSeverity.WARNING) == "Log and send to monitoring"
        )
        assert (
            handle_violation(InvariantSeverity.CRITICAL)
            == "Log, monitor, and alert on-call"
        )
        assert (
            handle_violation(InvariantSeverity.FATAL)
            == "Log, alert, and halt execution"
        )

    def test_severity_conversion(self) -> None:
        """Test converting severity to other representations."""

        def severity_to_color(severity: InvariantSeverity) -> str:
            """Convert severity to color for UI display."""
            return {
                InvariantSeverity.INFO: "blue",
                InvariantSeverity.WARNING: "yellow",
                InvariantSeverity.CRITICAL: "orange",
                InvariantSeverity.FATAL: "red",
            }[severity]

        def severity_to_priority(severity: InvariantSeverity) -> int:
            """Convert severity to priority number (higher = more urgent)."""
            return {
                InvariantSeverity.INFO: 1,
                InvariantSeverity.WARNING: 2,
                InvariantSeverity.CRITICAL: 3,
                InvariantSeverity.FATAL: 4,
            }[severity]

        # Test conversions
        assert severity_to_color(InvariantSeverity.INFO) == "blue"
        assert severity_to_color(InvariantSeverity.FATAL) == "red"

        assert severity_to_priority(InvariantSeverity.INFO) == 1
        assert severity_to_priority(InvariantSeverity.FATAL) == 4


class TestInvariantSeverityIntegration:
    """Integration tests for InvariantSeverity with other components."""

    def test_with_invariant_violation_classes(self) -> None:
        """Test integration with InvariantViolation classes."""
        # Test that each violation class has the correct severity
        info_violation = InvariantViolationInfo(
            name="Info Test",
            message="Info message",
            category=InvariantCategory.SAFETY,
            phase=InvariantPhase.RUNTIME,
        )
        assert info_violation.severity == InvariantSeverity.INFO

        warning_violation = InvariantViolationWarning(
            name="Warning Test",
            message="Warning message",
            category=InvariantCategory.CONSISTENCY,
            phase=InvariantPhase.RUNTIME,
        )
        assert warning_violation.severity == InvariantSeverity.WARNING

        critical_violation = InvariantViolationCritical(
            name="Critical Test",
            message="Critical message",
            category=InvariantCategory.EPISTEMIC,
            phase=InvariantPhase.RUNTIME,
        )
        assert critical_violation.severity == InvariantSeverity.CRITICAL

        fatal_violation = InvariantViolationFatal(
            name="Fatal Test",
            message="Fatal message",
            category=InvariantCategory.DYNAMICAL,
            phase=InvariantPhase.RUNTIME,
        )
        assert fatal_violation.severity == InvariantSeverity.FATAL

    def test_severity_filtering(self) -> None:
        """Test filtering violations by severity."""

        class MockViolation:
            def __init__(self, name: str, severity: InvariantSeverity):
                self.name = name
                self.severity = severity

        violations = [
            MockViolation("info1", InvariantSeverity.INFO),
            MockViolation("warning1", InvariantSeverity.WARNING),
            MockViolation("info2", InvariantSeverity.INFO),
            MockViolation("critical1", InvariantSeverity.CRITICAL),
            MockViolation("fatal1", InvariantSeverity.FATAL),
            MockViolation("warning2", InvariantSeverity.WARNING),
        ]

        # Filter by severity
        critical_or_higher = [
            v
            for v in violations
            if v.severity.value >= InvariantSeverity.CRITICAL.value
        ]
        assert len(critical_or_higher) == 2
        assert all(
            v.severity in [InvariantSeverity.CRITICAL, InvariantSeverity.FATAL]
            for v in critical_or_higher
        )

        # Filter by specific severity
        info_violations = [
            v for v in violations if v.severity is InvariantSeverity.INFO
        ]
        assert len(info_violations) == 2
        assert all(v.severity is InvariantSeverity.INFO for v in info_violations)

    def test_severity_in_configuration(self) -> None:
        """Test using severity in configuration settings."""

        class MonitoringConfig:
            def __init__(self, min_severity_to_log: InvariantSeverity):
                self.min_severity_to_log = min_severity_to_log

            def should_log(self, severity: InvariantSeverity) -> bool:
                return severity.value >= self.min_severity_to_log.value

        # Test different configurations
        log_all_config = MonitoringConfig(InvariantSeverity.INFO)
        assert log_all_config.should_log(InvariantSeverity.INFO) is True
        assert log_all_config.should_log(InvariantSeverity.FATAL) is True

        log_warning_and_above_config = MonitoringConfig(InvariantSeverity.WARNING)
        assert log_warning_and_above_config.should_log(InvariantSeverity.INFO) is False
        assert (
            log_warning_and_above_config.should_log(InvariantSeverity.WARNING) is True
        )
        assert (
            log_warning_and_above_config.should_log(InvariantSeverity.CRITICAL) is True
        )

        log_critical_only_config = MonitoringConfig(InvariantSeverity.CRITICAL)
        assert log_critical_only_config.should_log(InvariantSeverity.WARNING) is False
        assert log_critical_only_config.should_log(InvariantSeverity.CRITICAL) is True
        assert log_critical_only_config.should_log(InvariantSeverity.FATAL) is True


class TestInvariantSeverityRealWorldScenarios:
    """Test real-world usage scenarios for InvariantSeverity."""

    def test_alerting_system_integration(self) -> None:
        """Test integration with an alerting system."""

        class AlertingSystem:
            def __init__(self):
                self.alerts_sent = []

            def send_alert(self, message: str, severity: InvariantSeverity):
                self.alerts_sent.append((message, severity))

        # System that uses the alerting system
        class MonitoringSystem:
            def __init__(self, alerting_system: AlertingSystem):
                self.alerting_system = alerting_system
                self.alert_threshold = InvariantSeverity.WARNING

            def process_violation(
                self, violation_name: str, severity: InvariantSeverity
            ):
                if severity.value >= self.alert_threshold.value:
                    self.alerting_system.send_alert(
                        f"Violation: {violation_name}", severity
                    )

        # Test the integration
        alerting_system = AlertingSystem()
        monitoring_system = MonitoringSystem(alerting_system)

        # Process violations
        monitoring_system.process_violation("low_priority", InvariantSeverity.INFO)
        monitoring_system.process_violation(
            "medium_priority", InvariantSeverity.WARNING
        )
        monitoring_system.process_violation("high_priority", InvariantSeverity.CRITICAL)
        monitoring_system.process_violation("highest_priority", InvariantSeverity.FATAL)

        # INFO should not trigger alert (below threshold)
        # Others should trigger alerts
        assert len(alerting_system.alerts_sent) == 3
        assert all(
            severity != InvariantSeverity.INFO
            for _, severity in alerting_system.alerts_sent
        )

    def test_logging_system_integration(self) -> None:
        """Test integration with a logging system."""

        class LoggingSystem:
            def __init__(self):
                self.debug_logs = []
                self.info_logs = []
                self.warning_logs = []
                self.error_logs = []
                self.critical_logs = []

            def log(self, message: str, severity: InvariantSeverity):
                if severity is InvariantSeverity.INFO:
                    self.info_logs.append(message)
                elif severity is InvariantSeverity.WARNING:
                    self.warning_logs.append(message)
                elif severity is InvariantSeverity.CRITICAL:
                    self.critical_logs.append(message)
                elif severity is InvariantSeverity.FATAL:
                    self.error_logs.append(message)  # FATAL goes to error log

        # Test the logging system
        logger = LoggingSystem()

        # Log messages with different severities
        logger.log("System started", InvariantSeverity.INFO)
        logger.log("Resource usage high", InvariantSeverity.WARNING)
        logger.log("Memory threshold exceeded", InvariantSeverity.CRITICAL)
        logger.log("System in unrecoverable state", InvariantSeverity.FATAL)
        logger.log("Another info message", InvariantSeverity.INFO)

        # Verify logs went to correct destinations
        assert len(logger.info_logs) == 2
        assert "System started" in logger.info_logs

        assert len(logger.warning_logs) == 1
        assert "Resource usage high" in logger.warning_logs

        assert len(logger.critical_logs) == 1
        assert "Memory threshold exceeded" in logger.critical_logs

        assert len(logger.error_logs) == 1
        assert "System in unrecoverable state" in logger.error_logs
