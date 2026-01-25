"""
Effect module for the Procela framework.

This module defines the ActionEffect class, a fundamental building block
for representing the outcomes of actions within Procela's active reasoning engine.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/action/effect.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/action/effect.html
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ActionEffect:
    """
    An immutable data container representing the effect or outcome of an action.

    Parameters
    ----------
    description : str
        A human-readable explanation of what the effect represents.
        This is the primary vehicle for explainability, translating
        mechanistic state changes into understandable narratives.

    expected_outcome : Any | None, optional
        The anticipated result or state change after the action is applied.
        Can be of any type (e.g., int, float, dict, custom object).
        Default is None.

    confidence : float | None, optional
        A quantitative measure (typically between 0.0 and 1.0) representing
        the certainty or reliability of this effect's prediction. Used by the
        reasoning engine for conflict resolution and probabilistic planning.
        Default is None.

    Attributes
    ----------
    description : str
        See Parameters section.

    expected_outcome : Any | None
        See Parameters section.

    confidence : float | None
        See Parameters section.

    Raises
    ------
    ValueError
        If `confidence` is provided but is outside the logical range [0.0, 1.0].
    """

    description: str
    expected_outcome: Any | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        """
        Validate the dataclass fields after initialization.

        This method is automatically called by the dataclass machinery.
        It enforces the contractual guarantees of the Procela framework,
        specifically the valid range for the confidence attribute.

        Raises
        ------
        ValueError
            If `confidence` is provided but is not a number between 0.0 and 1.0,
            inclusive.
        """
        if self.confidence is not None:
            # Validate that confidence is a numeric probability
            if not isinstance(self.confidence, (int, float)):
                raise TypeError(
                    f"Confidence must be int or float, "
                    f"got {type(self.confidence).__name__}"
                )
            if not 0.0 <= self.confidence <= 1.0:
                raise ValueError(
                    f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
                )
