"""
Diagnosis result container.

This module defines the canonical result type produced by
diagnostic assessment mechanisms in Procela.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/assessment/diagnosis.html

Examples Reference
------------------
https://procela.org/docs/examples/core/assessment/diagnosis.html
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class DiagnosisResult:
    """
    Outcome of a diagnostic assessment.

    Instances of this class represent the result of a diagnostic evaluation
    procedure. A diagnosis result consists of a non-empty list of identified
    causes, an optional confidence score, and an optional metadata dictionary.
    This result type is intended to be used by reasoning mechanisms that
    produce one or more causal hypotheses that explain an observed phenomenon
    or detected anomaly.

    Parameters
    ----------
    causes : list[str]
        A list of identified causal explanations. Each element
        must be a string that names or describes a cause.
    confidence : float | None, optional
        Confidence in the diagnostic outcome expressed as
        a real number between 0.0 and 1.0 inclusive, or
        None if not applicable or unavailable.
    metadata : dict[str, Any], default_factory=dict
        Additional information associated with the diagnosis.

    Raises
    ------
    TypeError
        If `causes` is not a list of strings, or if `confidence`
        is not a float or int when provided.
    ValueError
        If `confidence` is provided but is not between 0.0
        and 1.0 inclusive.
    """

    causes: list[str]
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate structural invariants of diagnosis results.

        This post-initialization method enforces that:
        - `causes` is a list of strings.
        - `confidence`, when provided, is a number in [0.0, 1.0].

        The method is automatically invoked after object
        construction. Misuse (invalid types or out-of-range
        confidence) is signaled with an exception instead of
        deferred validation, preserving the immutability
        guarantee of the frozen dataclass.

        Raises
        ------
        TypeError
            If a type constraint is violated.
        ValueError
            If `confidence` is outside the valid range.
        """
        # Validate causes type and content
        if not isinstance(self.causes, list):
            raise TypeError(
                "Causes must be a list, " f"got {type(self.causes).__name__}"
            )
        for i, cause in enumerate(self.causes):
            if not isinstance(cause, str):
                raise TypeError(
                    "All causes must be strings, "
                    f"got {type(cause).__name__} at index {i}"
                )

        # Validate confidence range
        if self.confidence is not None:
            if not isinstance(self.confidence, int | float):
                raise TypeError(
                    "Confidence must be int or float, "
                    f"got {type(self.confidence).__name__}"
                )
            if not 0.0 <= self.confidence <= 1.0:
                raise ValueError(
                    "Confidence must be between 0.0 and 1.0, " f"got {self.confidence}"
                )
