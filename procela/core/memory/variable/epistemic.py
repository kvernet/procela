"""
Epistemic state representation for variables in the Procela framework.

This module defines the VariableEpistemic data class, which encapsulates
the epistemic (knowledge-related) state of a variable. This includes
statistical analysis of its history, anomaly detection results, and
trend analysis results.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/memory/variable/epistemic.html

Examples Reference
------------------
https://procela.org/docs/examples/core/memory/variable/epistemic.html
"""

from __future__ import annotations

from dataclasses import dataclass

from ...reasoning.result import AnomalyResult, TrendResult
from ...reasoning.view import DiagnosisView, PredictionView, ProposalView
from .statistics import HistoryStatistics


@dataclass(frozen=True)
class VariableEpistemic:
    """
    Container for the epistemic state of a variable.

    This immutable data class holds the knowledge-related aspects of a
    variable's state, including historical statistics, anomaly detection
    results, and trend analysis results.

    Parameters
    ----------
    stats : HistoryStatistics
        Statistical analysis of the variable's historical data.
        Contains metrics such as mean, standard deviation, and
        other statistical properties derived from the variable's history.
    anomaly : AnomalyResult | None
        Results from anomaly detection analysis. Contains information
        about whether the variable is currently in an anomalous state,
        the anomaly score, and related metadata. `None` indicates that
        no anomaly analysis has been performed or is available.
    trend : TrendResult | None
        Results from trend analysis. Contains information about
        detected trends in the variable's behavior, including trend
        direction, strength, and confidence. `None` indicates that
        no trend analysis has been performed or is available.

    Attributes
    ----------
    stats : HistoryStatistics
        Statistical analysis of the variable's historical data.
    anomaly : AnomalyResult | None
        Anomaly detection results.
    trend : TrendResult | None
        Trend analysis results.

    Notes
    -----
    - This class is a frozen dataclass, meaning instances are immutable
      after creation. This ensures epistemic states cannot be modified
      once created, maintaining consistency in reasoning processes.
    - The `anomaly` and `trend` fields are optional (`None` is allowed)
      to accommodate cases where these analyses haven't been performed
      or aren't applicable.
    - This class is designed to work within Procela's active reasoning
      framework where variables maintain self-knowledge about their state.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/memory/variable/epistemic.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/memory/variable/epistemic.html
    """

    stats: HistoryStatistics
    anomaly: AnomalyResult | None
    trend: TrendResult | None

    def get_diagnosis_view(self) -> DiagnosisView:
        """Get diagnosis view."""
        return self

    def get_prediction_view(self) -> PredictionView:
        """Get prediction view."""
        return self

    def get_proposal_view(self) -> ProposalView:
        """Get proposal view."""
        return self
