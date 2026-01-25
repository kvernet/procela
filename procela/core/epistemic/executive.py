"""
Executive-level epistemic view for Procela.

This module defines `ExecutiveView`, a read-only epistemic
representation of an Executive-managed world. The view captures a
consistent snapshot of the system state at a discrete execution
boundary, exposing the identities of all known processes
without permitting mutation, execution, or conflict resolution.

The executive epistemic view is designed for inspection, monitoring,
logging, diagnostics, reasoning, and external analysis, while remaining
strictly observational.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/epistemic/executive.html

Examples Reference
------------------
https://procela.org/docs/examples/core/epistemic/executive.html
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from ...symbols.key import Key


@dataclass(frozen=True, slots=True)
class ExecutiveView:
    """
    Epistemic snapshot of an Executive-managed world.

    An ``ExecutiveView`` represents the observable state of the entire
    Procela system at a discrete execution boundary. It provides a
    stable, immutable description of *what exists* in the world at a
    given step, without encoding *how* the world evolves or *why*
    particular states were reached.

    The executive view acts as the epistemic root of the system,
    allowing higher-level reasoning, auditing, visualization, and
    external integration without risking mutation or causal interference.

    Attributes
    ----------
    key : Key
        Unique identity of the executive instance that owns the world.

    step : int
        Discrete execution step at which the snapshot was taken.

    process_keys : tuple[Key, ...]
        Keys of all processes known to the executive at the snapshot
        boundary.

    timestamp : datetime
        Coordinated UTC timestamp indicating when the snapshot was
        created.

    Notes
    -----
    - The snapshot reflects structural knowledge, not mutable state.
    - Ordering of keys is stable but semantically irrelevant.
    - The executive view does not imply that all processes were active
    during the step.
    """

    key: Key
    step: int

    process_keys: tuple[Key, ...]

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """
        Validate ExecutiveView invariants after initialization.

        This method enforces structural and semantic constraints on the
        executive view to ensure internal consistency and downstream
        reliability. It is automatically invoked after dataclass initialization
        and may raise if invariants are violated.

        Raises
        ------
        TypeError
            If any field has an incompatible type.
        """
        if not isinstance(self.key, Key):
            raise TypeError(f"expected Key instance, got {self.key!r}")

        if not isinstance(self.step, int):
            raise TypeError(f"expected int, got {self.step!r}")

        for i, key in enumerate(self.process_keys):
            if not isinstance(key, Key):
                raise TypeError(
                    "process_keys should contain Key instance, "
                    f"got {key!r} at index {i}"
                )

        if not isinstance(self.timestamp, datetime):
            raise TypeError(f"expected datetime instance, got {self.timestamp!r}")
