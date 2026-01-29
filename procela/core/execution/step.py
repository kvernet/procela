"""
Trace of a single execution step.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/execution/step.html

Examples Reference
------------------
https://procela.org/docs/examples/core/execution/step.html
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from ...symbols.key import Key
from ..memory.variable.record import VariableRecord


@dataclass(frozen=True, slots=True)
class ExecutionStepTrace:
    """
    Immutable trace of a single executive step.

    Captures *what happened* during one execution step,
    without mutating variables or policies.
    """

    step: int
    """Step index."""

    proposed: Mapping[Key, Sequence[VariableRecord]]
    """Candidates proposed to each variable (before validation)."""

    validated: Mapping[Key, Sequence[VariableRecord]]
    """Candidates that passed validation."""

    resolved: Mapping[Key, VariableRecord | None]
    """Final resolved record per variable (if any)."""

    proposing_mechanisms: Mapping[Key, Sequence[Key | None]]
    """Mechanisms that proposed at least one candidate per variable."""
