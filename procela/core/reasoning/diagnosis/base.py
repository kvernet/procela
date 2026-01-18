"""
Diagnostic Reasoning Base Module for the Procela Framework.

This module defines the abstract base class for diagnostic reasoning algorithms,
which identify root causes of observed anomalies or system behaviors. Diagnostic
reasoners are core components of Procela's active reasoning engine, enabling
variables to perform causal analysis and identify underlying issues.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/diagnosis/base.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/diagnosis/base.html
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from ..result import DiagnosisResult
from ..view import DiagnosisView


class Diagnoser(ABC):
    """
    Abstract base class for all diagnostic reasoning algorithms in Procela.

    This class defines the uniform interface that all concrete diagnostic
    reasoners must implement. Diagnostic reasoning involves analyzing system
    state, historical patterns, and anomalies to identify potential root causes
    of observed issues or deviations from expected behavior.

    Subclasses must implement the `diagnose` method with specific diagnostic
    logic (e.g., fault tree analysis, Bayesian networks, rule-based inference)
    and set the `name` class attribute.

    Attributes
    ----------
    name : ClassVar[str]
        A unique identifier for this diagnostic reasoning algorithm.
        This should be a descriptive, human-readable name that
        distinguishes the diagnostic method (e.g., "FaultTreeDiagnoser",
        "BayesianDiagnoser", "RuleBasedDiagnoser").

    Notes
    -----
    As an abstract base class, `Diagnoser` cannot be instantiated
    directly. Concrete implementations must inherit from this class and
    provide implementations for all abstract methods.

    Diagnostic reasoning in Procela typically follows anomaly detection,
    using the anomaly context along with historical trends and statistics
    to hypothesize potential root causes.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/diagnosis/base.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/reasoning/diagnosis/base.html
    """

    name: ClassVar[str]
    """A unique identifier for this diagnostic reasoning algorithm."""

    @abstractmethod
    def diagnose(self, view: DiagnosisView) -> DiagnosisResult:
        """
        Perform diagnostic reasoning on the provided system view.

        This is the core method that all concrete diagnostic reasoners must
        implement. It analyzes the provided `DiagnosisView` to identify
        potential root causes of observed anomalies, trends, or system issues.

        Parameters
        ----------
        view : DiagnosisView
            A view of the system providing access to statistics, anomalies,
            and trends. This typically includes:
            - Historical statistics for context
            - Anomaly detection results (if any)
            - Trend analysis results (if any)

        Returns
        -------
        DiagnosisResult
            A structured result containing:
            - List of identified potential causes (may be empty)
            - Confidence in the diagnostic conclusions (optional)
            - Metadata with algorithm-specific details

        Raises
        ------
        ValueError
            If the `DiagnosisView` object is incomplete, invalid,
            or contains data that the reasoner cannot process.
        NotImplementedError
            If called directly on the abstract base class (must be
            implemented by concrete subclasses).

        Notes
        -----
        Implementations should:
        1. Handle edge cases gracefully (e.g., missing data,
           contradictory evidence, insufficient context)
        2. Provide meaningful confidence scores when possible
        3. Include algorithm-specific details in the `metadata` field
           for traceability and debugging
        4. Be deterministic when possible (same input → same output)
        5. Document any assumptions about the input view

        The method should not modify the input `DiagnosisView` object.
        """
        raise NotImplementedError("Subclasses must implement the diagnose method")
