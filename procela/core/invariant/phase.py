"""
Phase of execution at which an invariant is evaluated.

Invariants may be checked at different moments of the system lifecycle
to enforce different kinds of guarantees.

Examples
--------
>>> from procela import InvariantPhase
>>>
>>> print(InvariantPhase.RUNTIME)
InvariantPhase.RUNTIME
>>> for phase in InvariantPhase:
...     print(phase.name, phase.value)
PRE 1
RUNTIME 2
POST 3

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/invariant/phase.html

Examples Reference
------------------
https://procela.org/docs/examples/core/invariant/phase.html
"""

from __future__ import annotations

from enum import Enum, auto


class InvariantPhase(Enum):
    """
    Phase of execution at which an invariant is evaluated.

    Examples
    --------
    >>> from procela import InvariantPhase
    >>>
    >>> print(InvariantPhase.RUNTIME)
    InvariantPhase.RUNTIME
    >>> for phase in InvariantPhase:
    ...     print(phase.name, phase.value)
    PRE 1
    RUNTIME 2
    POST 3
    """

    PRE = auto()
    """
    Evaluated before execution begins.

    Typical use cases:
    - Model completeness checks
    - Variable initialization consistency
    - Structural invariants
    """

    RUNTIME = auto()
    """
    Evaluated during execution, typically at each step.

    Typical use cases:
    - Safety invariants
    - Epistemic bounds
    - Dynamical constraints
    """

    POST = auto()
    """
    Evaluated after execution completes.

    Typical use cases:
    - Outcome validation
    - Convergence guarantees
    - Post-hoc scientific assertions
    """
