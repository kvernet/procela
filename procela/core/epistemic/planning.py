"""
Planning epistemic view for Procela.

This module defines the PlanningView protocol, which provides a
read-only interface for intervention planning tasks. PlanningView
exposes diagnostic and predictive insights necessary to generate
action proposals or strategies without mutating the underlying system.

PlanningView differs from raw variable views by focusing on
aggregated reasoning outputs (diagnosis, predictions) rather than
statistical or trend data.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/view.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/view.html
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ..assessment.diagnosis import DiagnosisResult
from ..assessment.prediction import PredictionResult


@runtime_checkable
class PlanningView(Protocol):
    """
    Epistemic view specialized for intervention planning.

    Provides read-only access to diagnostic conclusions, predicted
    scenarios, and the current state of a variable or system entity.
    Planning algorithms consume this information to generate action
    proposals, evaluate strategies, and assess consequences of
    interventions.

    Properties
    ----------
    diagnosis : DiagnosisResult | None
        Diagnostic conclusions about the current state or identified issues.
        Provides context for why planning decisions are necessary.

    predictions : list[PredictionResult]
        Forecasted future scenarios or outcomes under different conditions.
        Used to assess potential consequences of different intervention strategies.

    current_value : Any
        Current value or state of the variable/system entity. Serves as
        the starting point for planning actions or proposals.

    Notes
    -----
    - This is a Protocol and does not implement any functionality.
    - PlanningView emphasizes synthesized reasoning outputs rather than
      raw variable statistics or trends.
    - The `current_value` property uses type `Any` to accommodate diverse
      variable types (scalars, vectors, categorical, or complex structures).
    """

    @property
    def diagnosis(self) -> DiagnosisResult | None:
        """Access diagnostic conclusions about the current state."""
        ...

    @property
    def predictions(self) -> list[PredictionResult]:
        """Access forecasted future scenarios."""
        ...

    @property
    def current_value(self) -> Any:
        """Access the variable's current value or state."""
        ...
