"""
Raised when a system invariant is violated.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/invariant/exceptions.html

Examples Reference
------------------
https://procela.org/docs/examples/core/invariant/exceptions.html
"""

from __future__ import annotations

from .category import InvariantCategory
from .phase import InvariantPhase
from .severity import InvariantSeverity


class InvariantViolation(RuntimeError):
    """Base class for all invariant violations."""

    def __init__(
        self,
        name: str,
        message: str,
        *,
        category: InvariantCategory,
        severity: InvariantSeverity,
        phase: InvariantPhase,
    ):
        """
        Instatiate a InvariantViolation object.

        Parameters
        ----------
        name : str
            A human-readable name for the invariant violation.
        message : str
            The violation message.
        category : InvariantCategory
            The category of the invariant violation.
        severity : InvariantSeverity
            The severity of invariant violation.
        phase : InvariantPhase
            The phase where the invariant violation occurs.
        """
        super().__init__(message)
        self.name = name
        self.category = category
        self.severity = severity
        self.phase = phase


class InvariantViolationInfo(InvariantViolation):
    """Informational invariant violation."""

    def __init__(
        self,
        name: str,
        message: str,
        *,
        category: InvariantCategory,
        phase: InvariantPhase,
    ):
        """
        Instatiate a InvariantViolation object.

        Parameters
        ----------
        name : str
            A human-readable name for the invariant violation.
        message : str
            The violation message.
        category : InvariantCategory
            The category of the invariant violation.
        phase : InvariantPhase
            The phase where the invariant violation occurs.
        """
        super().__init__(
            name=name,
            message=message,
            category=category,
            severity=InvariantSeverity.INFO,
            phase=phase,
        )


class InvariantViolationWarning(InvariantViolation):
    """Non-fatal invariant violation indicating degradation."""

    def __init__(
        self,
        name: str,
        message: str,
        *,
        category: InvariantCategory,
        phase: InvariantPhase,
    ):
        """
        Instatiate a InvariantViolation object.

        Parameters
        ----------
        name : str
            A human-readable name for the invariant violation.
        message : str
            The violation message.
        category : InvariantCategory
            The category of the invariant violation.
        phase : InvariantPhase
            The phase where the invariant violation occurs.
        """
        super().__init__(
            name=name,
            message=message,
            category=category,
            severity=InvariantSeverity.WARNING,
            phase=phase,
        )


class InvariantViolationCritical(InvariantViolation):
    """Critical invariant violation requiring interruption."""

    def __init__(
        self,
        name: str,
        message: str,
        *,
        category: InvariantCategory,
        phase: InvariantPhase,
    ):
        """
        Instatiate a InvariantViolation object.

        Parameters
        ----------
        name : str
            A human-readable name for the invariant violation.
        message : str
            The violation message.
        category : InvariantCategory
            The category of the invariant violation.
        phase : InvariantPhase
            The phase where the invariant violation occurs.
        """
        super().__init__(
            name=name,
            message=message,
            category=category,
            severity=InvariantSeverity.CRITICAL,
            phase=phase,
        )


class InvariantViolationFatal(InvariantViolation):
    """Fatal invariant violation invalidating the system."""

    def __init__(
        self,
        name: str,
        message: str,
        *,
        category: InvariantCategory,
        phase: InvariantPhase,
    ):
        """
        Instatiate a InvariantViolation object.

        Parameters
        ----------
        name : str
            A human-readable name for the invariant violation.
        message : str
            The violation message.
        category : InvariantCategory
            The category of the invariant violation.
        phase : InvariantPhase
            The phase where the invariant violation occurs.
        """
        super().__init__(
            name=name,
            message=message,
            category=category,
            severity=InvariantSeverity.FATAL,
            phase=phase,
        )
