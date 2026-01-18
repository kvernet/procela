"""
Effect module for the Procela framework.

This module defines the ActionEffect class, a fundamental building block
for representing the outcomes of actions within Procela's active reasoning engine.
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
        Example: "Increased system pressure by 5.2 kPa."

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

    Examples
    --------
    >>> from procela.core.action import ActionEffect
    >>>
    >>> # Creating a simple descriptive effect
    >>> effect_1 = ActionEffect(description="Temperature delta applied")
    >>> effect_1.description
    'Temperature delta applied'
    >>> # Creating a predictive effect with confidence
    >>> predicted_state: dict[str, float] = {"velocity": 12.5, "error_margin": 0.3}
    >>> effect_2 = ActionEffect(
    ...     description="Updated kinematic model",
    ...     expected_outcome=predicted_state,
    ...     confidence=0.87
    ... )
    >>> effect_2.confidence
    0.87
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
