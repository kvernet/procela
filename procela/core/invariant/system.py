"""
System-level invariant evaluated against a snapshot.

Examples
--------
>>> import random
>>>
>>> from procela import (
...     SystemInvariant,
...     InvariantPhase,
...     InvariantCategory,
...     InvariantSeverity,
...     InvariantSoftness,
...     VariableSnapshot,
...     InvariantViolation,
...     Variable,
...     RealDomain,
...     VariableRecord
... )
>>>
>>> random.seed(42)
>>>
>>> X = Variable("X", RealDomain())
>>> Y = Variable("Y", RealDomain())
>>>
>>> for _ in range(7):
...    for var in [X, Y]:
...        var.set(VariableRecord(
...            value=random.gauss(1.8, 1.3), confidence=random.uniform(0, 1)
...        ))
>>>
>>> invariant = SystemInvariant(
...     name="", condition=lambda v: v.views[0].stats.mean < 2.0,
...     on_violation=lambda v, s: None,
...     phase=InvariantPhase.PRE,
...     category=InvariantCategory.EPISTEMIC,
...     severity=InvariantSeverity.FATAL,
...     softness=InvariantSoftness.HARD,
...     message="Invariant violation - mean exceeds threshold"
... )
>>>
>>> snapshot = VariableSnapshot(step=1, views=[X.epistemic(), Y.epistemic()])
>>>
>>> try:
...     print(invariant.check(snapshot))
... except InvariantViolation as err:
...     print(f"Error: {err}")
Error: Invariant violation - mean exceeds threshold

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/invariant/system.html

Examples Reference
------------------
https://procela.org/docs/examples/core/invariant/system.html
"""

from __future__ import annotations

from typing import Callable

from .category import InvariantCategory
from .exceptions import (
    InvariantViolation,
    InvariantViolationCritical,
    InvariantViolationFatal,
    InvariantViolationInfo,
    InvariantViolationWarning,
)
from .phase import InvariantPhase
from .severity import InvariantSeverity
from .snapshot import VariableSnapshot
from .softness import InvariantSoftness


class SystemInvariant:
    """
    A system-level invariant that must hold at specific execution phases.

    Invariants define non-negotiable assumptions about the system's
    epistemic, dynamical, or safety properties.

    Examples
    --------
    >>> import random
    >>>
    >>> from procela import (
    ...     SystemInvariant,
    ...     InvariantPhase,
    ...     InvariantCategory,
    ...     InvariantSeverity,
    ...     InvariantSoftness,
    ...     VariableSnapshot,
    ...     InvariantViolation,
    ...     Variable,
    ...     RealDomain,
    ...     VariableRecord
    ... )
    >>>
    >>> random.seed(42)
    >>>
    >>> X = Variable("X", RealDomain())
    >>> Y = Variable("Y", RealDomain())
    >>>
    >>> for _ in range(7):
    ...    for var in [X, Y]:
    ...        var.set(VariableRecord(
    ...            value=random.gauss(1.8, 1.3), confidence=random.uniform(0, 1)
    ...        ))
    >>>
    >>> invariant = SystemInvariant(
    ...     name="", condition=lambda v: v.views[0].stats.mean < 2.0,
    ...     on_violation=lambda v, s: None,
    ...     phase=InvariantPhase.PRE,
    ...     category=InvariantCategory.EPISTEMIC,
    ...     severity=InvariantSeverity.FATAL,
    ...     softness=InvariantSoftness.HARD,
    ...     message="Invariant violation - mean exceeds threshold"
    ... )
    >>>
    >>> snapshot = VariableSnapshot(step=1, views=[X.epistemic(), Y.epistemic()])
    >>>
    >>> try:
    ...     print(invariant.check(snapshot))
    ... except InvariantViolation as err:
    ...     print(f"Error: {err}")
    Error: Invariant violation - mean exceeds threshold
    """

    def __init__(
        self,
        name: str,
        condition: Callable[[VariableSnapshot], bool],
        on_violation: (
            Callable[[InvariantViolation, VariableSnapshot], None] | None
        ) = None,
        *,
        phase: InvariantPhase = InvariantPhase.RUNTIME,
        category: InvariantCategory = InvariantCategory.CONSISTENCY,
        severity: InvariantSeverity = InvariantSeverity.CRITICAL,
        softness: InvariantSoftness = InvariantSoftness.HARD,
        message: str | None = None,
    ):
        """
        System-level invariant evaluated against a VariableSnapshot.

        Parameters
        ----------
        name : str
            Unique name of the invariant.
        condition : Callable[[VariableSnapshot], bool]
            Predicate evaluated against the current variable snapshot.
        on_violation : Callable[[InvariantViolation, VariableSnapshot], None] | None
            The epistemic event when invariant violation occurs. Raise error
            inside this event is not recommended because it does not take into
            account the severity, softness of any kind of InvariantViolation.
        phase : InvariantPhase
            Execution phase in which the invariant is evaluated.
            Default is runtime.
        category : InvariantCategory
            Semantic category of the invariant. Default is consistency.
        severity : InvariantSeverity
            Severity level when the invariant is violated. Default is crtical.
        softness : InvariantSoftness
            Whether the invariant is hard (fatal) or soft (tolerable).
            Default is hard.
        message : str, optional
            Custom violation message.

        Examples
        --------
        >>> import random
        >>>
        >>> from procela import (
        ...     SystemInvariant,
        ...     InvariantPhase,
        ...     InvariantCategory,
        ...     InvariantSeverity,
        ...     InvariantSoftness,
        ...     VariableSnapshot,
        ...     InvariantViolation,
        ...     Variable,
        ...     RealDomain,
        ...     VariableRecord
        ... )
        >>>
        >>> random.seed(42)
        >>>
        >>> X = Variable("X", RealDomain())
        >>> Y = Variable("Y", RealDomain())
        >>>
        >>> for _ in range(7):
        ...    for var in [X, Y]:
        ...        var.set(VariableRecord(
        ...            value=random.gauss(1.8, 1.3), confidence=random.uniform(0, 1)
        ...        ))
        >>>
        >>> invariant = SystemInvariant(
        ...     name="", condition=lambda v: v.views[0].stats.mean < 2.0,
        ...     on_violation=lambda v, s: None,
        ...     phase=InvariantPhase.PRE,
        ...     category=InvariantCategory.EPISTEMIC,
        ...     severity=InvariantSeverity.FATAL,
        ...     softness=InvariantSoftness.HARD,
        ...     message="Invariant violation - mean exceeds threshold"
        ... )
        >>>
        >>> snapshot = VariableSnapshot(step=1, views=[X.epistemic(), Y.epistemic()])
        >>>
        >>> try:
        ...     print(invariant.check(snapshot))
        ... except InvariantViolation as err:
        ...     print(f"Error: {err}")
        Error: Invariant violation - mean exceeds threshold
        """
        self.name = name
        self.condition = condition
        self.on_violation = on_violation
        self.phase = phase
        self.category = category
        self.severity = severity
        self.softness = softness
        self.message = message or f"Invariant violated: {name}"
        self.action_count = 0
        self.violation_count = 0
        self.last_triggered = 0

    def check(self, snapshot: VariableSnapshot) -> None:
        """
        Evaluate the invariant against a snapshot of the variables.

        Parameters
        ----------
        snapshot : VariableSnapshot
            The variable snapshot to check the invariant.

        Raises
        ------
        InvariantViolation
            If the invariant is violated and enforcement requires interruption.
        """
        self.action_count += 1
        holds = bool(self.condition(snapshot))

        if holds:
            return

        self.violation_count += 1

        violation = self.build_violation(snapshot)

        if self.on_violation is not None:
            self.on_violation(violation, snapshot)

        self.handle_violation(violation)
        self.last_triggered = snapshot.step

    def build_violation(self, snapshot: VariableSnapshot) -> InvariantViolation:
        """
        Build the violation according to severity and softness.

        Parameters
        ----------
        snapshot : VariableSnapshot
            The variable snapshot to build the violation on.

        Notes
        -----
        The snapshot is not used in the current version but probably later.
        """
        cls = {
            InvariantSeverity.INFO: InvariantViolationInfo,
            InvariantSeverity.WARNING: InvariantViolationWarning,
            InvariantSeverity.CRITICAL: InvariantViolationCritical,
            InvariantSeverity.FATAL: InvariantViolationFatal,
        }[self.severity]

        return cls(
            name=self.name,
            message=self.message,
            category=self.category,
            phase=self.phase,
        )

    def handle_violation(self, violation: InvariantViolation) -> None:
        """
        Handle an invariant violation according to severity and softness.

        Parameters
        ----------
        violation: InvariantViolation
            The violation to handle.
        """
        if self.softness is InvariantSoftness.SOFT:
            return

        raise violation
