"""Minimal pytest suite for procela.core.invariant with 100% coverage."""

from procela.core.invariant import (
    InvariantCategory,
    InvariantPhase,
    InvariantSeverity,
    InvariantViolation,
    InvariantViolationCritical,
    InvariantViolationFatal,
    InvariantViolationInfo,
    InvariantViolationWarning,
)


class TestInvariantViolation:
    """Test base InvariantViolation class."""

    def test_invariant_violation_initialization(self):
        """Test that InvariantViolation initializes correctly with all parameters."""
        violation = InvariantViolation(
            name="TestViolation",
            message="Test message",
            category=InvariantCategory.CONSISTENCY,
            severity=InvariantSeverity.WARNING,
            phase=InvariantPhase.PRE,
        )

        assert violation.name == "TestViolation"
        assert str(violation) == "Test message"
        assert violation.category == InvariantCategory.CONSISTENCY
        assert violation.severity == InvariantSeverity.WARNING
        assert violation.phase == InvariantPhase.PRE
        assert isinstance(violation, RuntimeError)


class TestInvariantViolationInfo:
    """Test InvariantViolationInfo subclass."""

    def test_invariant_violation_info_initialization(self):
        """Test that InvariantViolationInfo initializes with INFO severity."""
        info = InvariantViolationInfo(
            name="TestInfo",
            message="Info message",
            category=InvariantCategory.RESOURCE,
            phase=InvariantPhase.POST,
        )

        assert info.name == "TestInfo"
        assert info.category == InvariantCategory.RESOURCE
        assert info.severity == InvariantSeverity.INFO
        assert info.phase == InvariantPhase.POST
        assert isinstance(info, InvariantViolation)


class TestInvariantViolationWarning:
    """Test InvariantViolationWarning subclass."""

    def test_invariant_violation_warning_initialization(self):
        """Test that InvariantViolationWarning initializes with WARNING severity."""
        warning = InvariantViolationWarning(
            name="TestWarning",
            message="Warning message",
            category=InvariantCategory.SAFETY,
            phase=InvariantPhase.RUNTIME,
        )

        assert warning.name == "TestWarning"
        assert warning.category == InvariantCategory.SAFETY
        assert warning.severity == InvariantSeverity.WARNING
        assert warning.phase == InvariantPhase.RUNTIME
        assert isinstance(warning, InvariantViolation)


class TestInvariantViolationCritical:
    """Test InvariantViolationCritical subclass."""

    def test_invariant_violation_critical_initialization(self):
        """Test that InvariantViolationCritical initializes with CRITICAL severity."""
        critical = InvariantViolationCritical(
            name="TestCritical",
            message="Critical message",
            category=InvariantCategory.DYNAMICAL,
            phase=InvariantPhase.RUNTIME,
        )

        assert critical.name == "TestCritical"
        assert critical.category == InvariantCategory.DYNAMICAL
        assert critical.severity == InvariantSeverity.CRITICAL
        assert critical.phase == InvariantPhase.RUNTIME
        assert isinstance(critical, InvariantViolation)


class TestInvariantViolationFatal:
    """Test InvariantViolationFatal subclass."""

    def test_invariant_violation_fatal_initialization(self):
        """Test that InvariantViolationFatal initializes with FATAL severity."""
        fatal = InvariantViolationFatal(
            name="TestFatal",
            message="Fatal message",
            category=InvariantCategory.EPISTEMIC,
            phase=InvariantPhase.POST,
        )

        assert fatal.name == "TestFatal"
        assert fatal.category == InvariantCategory.EPISTEMIC
        assert fatal.severity == InvariantSeverity.FATAL
        assert fatal.phase == InvariantPhase.POST
        assert isinstance(fatal, InvariantViolation)


# Add this test to ensure 100% coverage of error cases
def test_invariant_violation_inheritance():
    """Test the inheritance hierarchy."""
    info = InvariantViolationInfo(
        name="Test",
        message="Test",
        category=InvariantCategory.DYNAMICAL,
        phase=InvariantPhase.PRE,
    )

    # Verify inheritance chain
    assert isinstance(info, InvariantViolation)
    assert isinstance(info, RuntimeError)

    # Verify the same for other subclasses
    warning = InvariantViolationWarning(
        name="Test",
        message="Test",
        category=InvariantCategory.SAFETY,
        phase=InvariantPhase.RUNTIME,
    )
    assert isinstance(warning, InvariantViolation)

    critical = InvariantViolationCritical(
        name="Test",
        message="Test",
        category=InvariantCategory.RESOURCE,
        phase=InvariantPhase.RUNTIME,
    )
    assert isinstance(critical, InvariantViolation)

    fatal = InvariantViolationFatal(
        name="Test",
        message="Test",
        category=InvariantCategory.RESOURCE,
        phase=InvariantPhase.RUNTIME,
    )
    assert isinstance(fatal, InvariantViolation)
