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
    """
    Base class for all invariant violations.

    Examples
    --------
    >>> from procela import (
    ...     InvariantViolation,
    ...     InvariantCategory,
    ...     InvariantSeverity,
    ...     InvariantPhase,
    ... )
    >>> violation = InvariantViolation(
    ...     name="",
    ...     message="Invariant violation message",
    ...     category=InvariantCategory.SAFETY,
    ...     severity=InvariantSeverity.WARNING,
    ...     phase=InvariantPhase.PRE
    ... )
    >>>
    >>> try:
    ...     raise(violation)
    ... except InvariantViolation as err:
    ...     print(err)
    Invariant violation message
    """

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


        Examples
        --------
        >>> from procela import (
        ...     InvariantViolation,
        ...     InvariantCategory,
        ...     InvariantSeverity,
        ...     InvariantPhase,
        ... )

        >>> violation = InvariantViolation(
        ...     name="",
        ...     message="Invariant violation message",
        ...     category=InvariantCategory.SAFETY,
        ...     severity=InvariantSeverity.WARNING,
        ...     phase=InvariantPhase.PRE
        ... )
        >>>
        >>> try:
        ...     raise(violation)
        ... except InvariantViolation as err:
        ...     print(err)
        Invariant violation message
        """
        super().__init__(message)
        self.name = name
        self.category = category
        self.severity = severity
        self.phase = phase


class InvariantViolationInfo(InvariantViolation):
    """
    Informational invariant violation.

    Examples
    --------
    >>> from procela import (
    ...     InvariantViolation,
    ...     InvariantViolationInfo,
    ...     InvariantCategory,
    ...     InvariantSeverity,
    ...     InvariantPhase,
    ... )
    >>>
    >>> violation = InvariantViolationInfo(
    ...     name="",
    ...     message="Invariant violation message",
    ...     category=InvariantCategory.SAFETY,
    ...     phase=InvariantPhase.PRE,
    ... )
    >>>
    >>> assert violation.severity == InvariantSeverity.INFO
    >>>
    >>> try:
    ...     raise(violation)
    ... except InvariantViolation as err:
    ...     print(err)
    Invariant violation message
    """

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

        Examples
        --------
        >>> from procela import (
        ...     InvariantViolation,
        ...     InvariantViolationInfo,
        ...     InvariantCategory,
        ...     InvariantSeverity,
        ...     InvariantPhase,
        ... )
        >>>
        >>> violation = InvariantViolationInfo(
        ...     name="",
        ...     message="Invariant violation message",
        ...     category=InvariantCategory.SAFETY,
        ...     phase=InvariantPhase.PRE,
        ... )
        >>>
        >>> assert violation.severity == InvariantSeverity.INFO
        >>>
        >>> try:
        ...     raise(violation)
        ... except InvariantViolation as err:
        ...     print(err)
        Invariant violation message
        """
        super().__init__(
            name=name,
            message=message,
            category=category,
            severity=InvariantSeverity.INFO,
            phase=phase,
        )


class InvariantViolationWarning(InvariantViolation):
    """
    Non-fatal invariant violation indicating degradation.

    Examples
    --------
    >>> from procela import (
    ...     InvariantViolation,
    ...     InvariantViolationWarning,
    ...     InvariantCategory,
    ...     InvariantSeverity,
    ...     InvariantPhase,
    ... )
    >>>
    >>> violation = InvariantViolationWarning(
    ...     name="",
    ...     message="Invariant violation message",
    ...     category=InvariantCategory.SAFETY,
    ...     phase=InvariantPhase.PRE,
    ... )
    >>>
    >>> assert violation.severity == InvariantSeverity.WARNING
    >>>
    >>> try:
    ...     raise(violation)
    ... except InvariantViolation as err:
    ...     print(err)
    Invariant violation message
    """

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

        Examples
        --------
        >>> from procela import (
        ...     InvariantViolation,
        ...     InvariantViolationWarning,
        ...     InvariantCategory,
        ...     InvariantSeverity,
        ...     InvariantPhase,
        ... )
        >>>
        >>> violation = InvariantViolationWarning(
        ...     name="",
        ...     message="Invariant violation message",
        ...     category=InvariantCategory.SAFETY,
        ...     phase=InvariantPhase.PRE,
        ... )
        >>>
        >>> assert violation.severity == InvariantSeverity.WARNING
        >>>
        >>> try:
        ...     raise(violation)
        ... except InvariantViolation as err:
        ...     print(err)
        Invariant violation message
        """
        super().__init__(
            name=name,
            message=message,
            category=category,
            severity=InvariantSeverity.WARNING,
            phase=phase,
        )


class InvariantViolationCritical(InvariantViolation):
    """
    Critical invariant violation requiring interruption.

    Examples
    --------
    >>> from procela import (
    ...     InvariantViolation,
    ...     InvariantViolationCritical,
    ...     InvariantCategory,
    ...     InvariantSeverity,
    ...     InvariantPhase,
    ... )
    >>>
    >>> violation = InvariantViolationCritical(
    ...     name="",
    ...     message="Invariant violation message",
    ...     category=InvariantCategory.SAFETY,
    ...     phase=InvariantPhase.PRE,
    ... )
    >>>
    >>> assert violation.severity == InvariantSeverity.CRITICAL
    >>>
    >>> try:
    ...     raise(violation)
    ... except InvariantViolation as err:
    ...     print(err)
    Invariant violation message
    """

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

        Examples
        --------
        >>> from procela import (
        ...     InvariantViolation,
        ...     InvariantViolationCritical,
        ...     InvariantCategory,
        ...     InvariantSeverity,
        ...     InvariantPhase,
        ... )
        >>>
        >>> violation = InvariantViolationCritical(
        ...     name="",
        ...     message="Invariant violation message",
        ...     category=InvariantCategory.SAFETY,
        ...     phase=InvariantPhase.PRE,
        ... )
        >>>
        >>> assert violation.severity == InvariantSeverity.CRITICAL
        >>>
        >>> try:
        ...     raise(violation)
        ... except InvariantViolation as err:
        ...     print(err)
        Invariant violation message
        """
        super().__init__(
            name=name,
            message=message,
            category=category,
            severity=InvariantSeverity.CRITICAL,
            phase=phase,
        )


class InvariantViolationFatal(InvariantViolation):
    """
    Fatal invariant violation invalidating the system.

    Examples
    --------
    >>> from procela import (
    ...     InvariantViolation,
    ...     InvariantViolationFatal,
    ...     InvariantCategory,
    ...     InvariantSeverity,
    ...     InvariantPhase,
    ... )
    >>>
    >>> violation = InvariantViolationFatal(
    ...     name="",
    ...     message="Invariant violation message",
    ...     category=InvariantCategory.SAFETY,
    ...     phase=InvariantPhase.PRE,
    ... )
    >>>
    >>> assert violation.severity == InvariantSeverity.FATAL
    >>>
    >>> try:
    ...     raise(violation)
    ... except InvariantViolation as err:
    ...     print(err)
    Invariant violation message
    """

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

        Examples
        --------
        >>> from procela import (
        ...     InvariantViolation,
        ...     InvariantViolationFatal,
        ...     InvariantCategory,
        ...     InvariantSeverity,
        ...     InvariantPhase,
        ... )
        >>>
        >>> violation = InvariantViolationFatal(
        ...     name="",
        ...     message="Invariant violation message",
        ...     category=InvariantCategory.SAFETY,
        ...     phase=InvariantPhase.PRE,
        ... )
        >>>
        >>> assert violation.severity == InvariantSeverity.FATAL
        >>>
        >>> try:
        ...     raise(violation)
        ... except InvariantViolation as err:
        ...     print(err)
        Invariant violation message
        """
        super().__init__(
            name=name,
            message=message,
            category=category,
            severity=InvariantSeverity.FATAL,
            phase=phase,
        )
