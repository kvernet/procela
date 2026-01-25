"""
Epistemic views for Procela variables.

This module defines the VariableView protocol, which provides a
read-only epistemic interface to Procela Variable objects. A
VariableView exposes the historical statistics, anomaly detection,
and trend analysis results of a variable without allowing mutation
or execution.

VariableViews are typically consumed by layer components to reason
about the system state without affecting it.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/epistemic/variable.html

Examples Reference
------------------
https://procela.org/docs/examples/core/epistemic/variable.html
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..assessment.anomaly import AnomalyResult
from ..assessment.statistics import StatisticsResult
from ..assessment.trend import TrendResult
from .base import EpistemicView


@runtime_checkable
class VariableView(EpistemicView, Protocol):
    """
    Epistemic view specialized for Procela variables.

    Provides read-only access to the variable's statistics, anomalies,
    and trends.

    Attributes
    ----------
    stats : StatisticsResult
        Aggregated historical statistics for the variable.
    anomaly : AnomalyResult or None
        Most recent anomaly detection result, if any.
    trend : TrendResult or None
        Most recent trend analysis result, if any.

    Notes
    -----
    - This is a Protocol and does not implement any functionality.
    - Use VariableView to inspect variable state safely without mutation.
    - Typically obtained via variable.epistemic() or similar accessor.
    """

    @property
    def stats(self) -> StatisticsResult:
        """Access the variable's statistics result."""
        ...

    @property
    def anomaly(self) -> AnomalyResult | None:
        """Access the most recent anomaly detection result."""
        ...

    @property
    def trend(self) -> TrendResult | None:
        """Access the most recent trend analysis result."""
        ...
