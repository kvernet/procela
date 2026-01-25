"""
Foundational epistemic interfaces for Procela.

This module defines the root epistemic abstraction used throughout the
framework to expose *knowledge about entities* without granting access
to their internal state, execution logic, or mutation capabilities.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/epistemic/base.html

Examples Reference
------------------
https://procela.org/docs/examples/core/epistemic/base.html
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ...symbols.key import Key
from ..assessment.reasoning import ReasoningResult


@runtime_checkable
class EpistemicView(Protocol):
    """
    Epistemic interface shared by all reasoning subjects.

    An ``EpistemicView`` provides a read-only interface exposing
    knowledge *about* an entity rather than access *to* the entity
    itself. It is the minimal epistemic contract implemented by all
    subjects that can be reasoned upon in Procela.

    This interface is intentionally minimal and abstract. Specialized
    epistemic views (e.g., variable, process, or executive views) extend
    this protocol to expose additional domain-specific knowledge.
    """

    @property
    def key(self) -> Key:
        """
        Unique identity of the epistemic subject.

        This key uniquely identifies the entity being observed within
        the Procela world and can be used to correlate epistemic views
        across time, processes, or reasoning layers.

        Returns
        -------
        Key
            Immutable key identifying the epistemic subject.
        """
        ...

    @property
    def reasoning(self) -> ReasoningResult | None:
        """
        Most recent reasoning outcome associated with the subject.

        This property exposes the latest reasoning result produced
        about the subject, if any. The result may originate from
        diagnostic, predictive, analytical, or evaluative reasoning
        processes.

        Returns
        -------
        ReasoningResult | None
            The most recent reasoning result, or ``None`` if no reasoning
            has been performed or recorded.
        """
        ...
