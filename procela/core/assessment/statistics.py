"""
Statistical assessment results for Procela.

This module defines immutable data structures representing aggregated
statistical summaries derived from variable histories. These results
are epistemic artifacts: they expose descriptive properties of observed
data without implying causality, execution, or decision-making.

Statistical results are typically produced by memory analysis layers
and consumed through epistemic views by reasoning, diagnosis, anomaly
detection, and monitoring components.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/assessment/statistics.html

Examples Reference
------------------
https://procela.org/docs/examples/core/assessment/statistics.html
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StatisticsResult:
    """
    Immutable statistical summary of a variable memory.

    ``StatisticsResult`` represents aggregated descriptive statistics
    computed over a variable's historical records at a specific
    evaluation boundary. It is a passive data structure intended for
    epistemic access, diagnostics, reasoning, and downstream assessment
    tasks.

    The result does not imply causality, decision-making, or execution.
    It strictly reflects observed or derived statistical properties of
    historical values.

    Attributes
    ----------
    count : int
        Number of historical observations used to compute the statistics.

    sum : float | None, Optional
        Sum of all observed values.

    min : float | None, optional
        Minimum observed value, if available.

    max : float | None, optional
        Maximum observed value, if available.

    mean : float | None, optional
        Arithmetic mean of observed values, if computable.

    std : float | None, optional
        Standard deviation of observed values, if computable.

    value : float | None, optional
        Most recent observed value.

    ewma : float | None, optional
        Exponentially weighted moving average, if computed.

    confidence : float | None, optional
        Confidence level associated with the statistical estimation, if
        applicable.

    Notes
    -----
    - This object is immutable and safe to share across subsystems.
    - Missing values indicate insufficient data or inapplicability.
    - ``StatisticsResult`` is typically exposed through epistemic views
      rather than used directly in execution logic.
    """

    count: int = 0
    sum: float | None = None
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    std: float | None = None
    value: float | None = None
    ewma: float | None = None
    confidence: float | None = None
