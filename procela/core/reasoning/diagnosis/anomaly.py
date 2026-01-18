"""
Anomaly-Based Diagnostic Reasoner for the Procela Framework.

This module implements an anomaly-focused diagnostic reasoner that specializes
in identifying root causes when anomalies are detected in system variables.
It analyzes anomaly characteristics, contextual statistics, and historical
patterns to generate diagnostic hypotheses about the underlying issues.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/diagnosis/anomaly.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/diagnosis/anomaly.html
"""

from __future__ import annotations

from typing import ClassVar, Optional

from ...memory.variable.statistics import HistoryStatistics
from ..result import (
    AnomalyResult,
    DiagnosisResult,
    TrendResult,
)
from ..view import DiagnosisView
from .base import Diagnoser


class AnomalyDiagnoser(Diagnoser):
    """
    Diagnostic reasoner specialized in analyzing detected anomalies.

    This reasoner focuses on situations where anomalies have been detected
    in system variables. It examines anomaly characteristics (score, type,
    detection method) along with historical statistics and trends to generate
    plausible explanations for why the anomaly occurred.

    The diagnoser uses a rule-based approach to map anomaly patterns to
    potential root causes, considering factors such as:
    - Anomaly severity (score relative to threshold)
    - Temporal patterns (sudden spike vs gradual drift)
    - Statistical context (relationship to historical norms)
    - Concomitant trends or patterns

    Parameters
    ----------
    severity_threshold : float, optional
        Minimum anomaly score required to trigger detailed diagnostic analysis.
        Anomalies with scores below this threshold may receive generic or
        lower-confidence diagnoses. Must be > 0.
        Default is 2.0.

    include_generic_causes : bool, optional
        Whether to include generic diagnostic causes when specific patterns
        are not identified. Generic causes provide fallback explanations
        when the anomaly doesn't match any specific diagnostic rule.
        Default is True.

    Attributes
    ----------
    name : ClassVar[str]
        Class attribute identifying this reasoner as "AnomalyDiagnoser".

    severity_threshold : float
        Minimum anomaly score for detailed analysis.

    include_generic_causes : bool
        Flag controlling inclusion of generic diagnostic causes.

    Methods
    -------
    diagnose(view: DiagnosisView) -> DiagnosisResult
        Perform anomaly-focused diagnostic reasoning.

    _analyze_pattern(anomaly, stats, trend) -> List[str]
        Analyze specific anomaly patterns to identify causes.

    _calculate_confidence(causes: List[str], anomaly_score: float) -> float
        Calculate confidence in diagnostic conclusions.

    Notes
    -----
    This reasoner assumes that anomaly detection has already been performed
    and that the `DiagnosisView` contains meaningful anomaly results. If no
    anomaly is present or the anomaly score is very low, the diagnosis will
    be minimal or generic.

    The diagnostic rules are heuristic and should be tuned for specific
    application domains. Consider subclassing and overriding the pattern
    analysis methods for domain-specific diagnostic logic.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/diagnosis/anomaly.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/reasoning/diagnosis/anomaly.html
    """

    name: ClassVar[str] = "AnomalyDiagnoser"

    def __init__(
        self,
        severity_threshold: float = 2.0,
        include_generic_causes: bool = True,
    ) -> None:
        """
        Initialize an anomaly-focused diagnostic reasoner.

        Parameters
        ----------
        severity_threshold : float, optional
            Minimum anomaly score for detailed diagnostic analysis.
            Must satisfy severity_threshold > 0.
            Default is 2.0.
        include_generic_causes : bool, optional
            Whether to include generic causes when specific patterns
            are not identified.
            Default is True.

        Raises
        ------
        ValueError
            If severity_threshold is not positive.
        """
        if severity_threshold <= 0:
            raise ValueError(
                f"severity_threshold must be > 0, got {severity_threshold}"
            )
        self.severity_threshold = severity_threshold
        self.include_generic_causes = include_generic_causes

    def diagnose(self, view: DiagnosisView) -> DiagnosisResult:
        """
        Perform diagnostic reasoning focused on anomaly analysis.

        This method examines the anomaly present in the view (if any) and
        analyzes it in the context of historical statistics and trends to
        generate diagnostic hypotheses about potential root causes.

        Parameters
        ----------
        view : DiagnosisView
            A view of the system containing:
            - anomaly: Anomaly detection results (if any)
            - stats: Historical statistics for context
            - trend: Trend analysis results (if any)

        Returns
        -------
        DiagnosisResult
            Structured result containing:
            - causes: List of identified potential root causes
            - confidence: Estimated confidence in diagnosis (0.0 to 1.0)
            - metadata: Diagnostic process details and evidence

        Raises
        ------
        TypeError
            If view is not a DiagnosisView instance.
        """
        # Validate input type
        if not isinstance(view, DiagnosisView):
            raise TypeError(f"view must be DiagnosisView, got {type(view).__name__}")

        # Initialize results
        causes: list[str] = []
        confidence: Optional[float] = None
        metadata = {
            "diagnoser": self.name,
            "severity_threshold": self.severity_threshold,
            "anomaly_present": False,
            "anomaly_score": None,
            "met_severity_threshold": False,
        }

        # Check if anomaly exists and is significant
        if view.anomaly and view.anomaly.is_anomaly:
            metadata["anomaly_present"] = True
            metadata["anomaly_score"] = view.anomaly.score
            metadata["anomaly_method"] = view.anomaly.method

            if view.anomaly.score is not None:
                met_severity_threshold = bool(
                    view.anomaly.score >= self.severity_threshold
                )
                metadata["met_severity_threshold"] = met_severity_threshold

                # Only perform detailed analysis for significant anomalies
                if met_severity_threshold:
                    causes = self._analyze_pattern(view.anomaly, view.stats, view.trend)
                    confidence = self._calculate_confidence(causes, view.anomaly.score)

        # Add generic causes if requested and no specific causes found
        if not causes and self.include_generic_causes:
            causes = self._generic_causes(view)
            confidence = 0.3  # Low confidence for generic causes

        # Ensure confidence is set (even if no anomaly)
        if confidence is None:
            confidence = 0.0

        # Add diagnostic details to metadata
        metadata.update(
            {
                "causes_identified": len(causes),
                "confidence": confidence,
                "generic_causes_used": (not causes and self.include_generic_causes),
            }
        )

        return DiagnosisResult(
            causes=causes,
            confidence=confidence,
            metadata=metadata,
        )

    def _analyze_pattern(
        self,
        anomaly: AnomalyResult,
        stats: HistoryStatistics,
        trend: TrendResult | None,
    ) -> list[str]:
        """
        Analyze anomaly patterns to identify specific root causes.

        This internal method implements the core pattern matching logic,
        examining anomaly characteristics in the context of statistics
        and trends to generate specific diagnostic hypotheses.

        Parameters
        ----------
        anomaly : AnomalyResult
            The anomaly result object containing detection details.
        stats : HistoryStatistics
            Historical statistics providing context for the anomaly.
        trend : TrendResult
            Trend analysis results (if available).

        Returns
        -------
        list[str]
            List of specific potential causes identified through pattern
            analysis. May be empty if no specific patterns are recognized.

        Notes
        -----
        This implementation provides basic pattern matching. Subclasses
        should override this method to implement domain-specific or more
        sophisticated diagnostic logic.
        """
        causes: list[str] = []

        # Check anomaly severity
        if anomaly.score is not None:
            if anomaly.score > 5.0:
                causes.append("Extreme anomaly suggests critical failure")
            elif anomaly.score > 3.0:
                causes.append("Significant anomaly indicates system issue")
            else:
                causes.append("Minor anomaly may indicate early warning")

        # Check detection method for clues
        if anomaly.method:
            if "z-score" in anomaly.method.lower():
                causes.append("Statistical deviation from historical norms")
            elif "ewma" in anomaly.method.lower():
                causes.append("Recent deviation from smoothed trend")

        # Analyze in context of trends
        if trend:
            if trend.direction == "up":
                causes.append("Anomaly coincides with upward trend")
            elif trend.direction == "down":
                causes.append("Anomaly coincides with downward trend")
            elif trend.direction == "stable":
                causes.append("Anomaly breaks stable pattern")

        # Check statistical context
        if stats and hasattr(stats, "mean") and hasattr(stats, "std"):
            # High variance might indicate measurement noise
            mean, std = stats.mean(), stats.std()
            if mean is not None and std is not None:
                if std / max(mean, 1e-9) > 0.1:  # 10%
                    causes.append("High variability suggests measurement issues")

        return causes

    def _calculate_confidence(
        self,
        causes: list[str],
        anomaly_score: float,
    ) -> float:
        """
        Calculate confidence in diagnostic conclusions.

        Confidence is estimated based on:
        - Number and specificity of identified causes
        - Anomaly severity (higher scores → more confidence)
        - Whether causes are specific or generic

        Parameters
        ----------
        causes : list[str]
            List of identified potential causes.
        anomaly_score : float
            The anomaly score that triggered diagnosis.

        Returns
        -------
        float
            Confidence estimate between 0.0 (no confidence) and 1.0
            (high confidence).

        Notes
        -----
        This is a heuristic confidence calculation. Real-world applications
        might use more sophisticated methods like Bayesian inference or
        evidence weighting.
        """
        if not causes:
            return 0.0

        # Base confidence from anomaly severity (capped)
        severity_factor = min(anomaly_score / 10.0, 1.0)

        # Adjust based on number of specific causes
        cause_factor = min(len(causes) / 5.0, 1.0)

        # Specificity factor (specific causes get higher weight)
        specificity = 0.7  # Default for mixed causes
        if any("suggests" in cause or "indicates" in cause for cause in causes):
            specificity = 0.9  # More specific language
        elif any("may indicate" in cause for cause in causes):
            specificity = 0.5  # Tentative language

        # Weighted combination
        confidence = 0.5 * severity_factor + 0.3 * cause_factor + 0.2 * specificity

        return min(max(confidence, 0.0), 1.0)  # Clamp to [0, 1]

    def _generic_causes(self, view: DiagnosisView) -> list[str]:
        """
        Provide generic diagnostic causes when specific patterns aren't found.

        Parameters
        ----------
        view : DiagnosisView
            The system view being diagnosed.

        Returns
        -------
        list[str]
            List of generic potential causes.
        """
        causes = ["Unidentified system anomaly detected"]

        if view.anomaly and view.anomaly.is_anomaly:
            if view.anomaly.score and view.anomaly.score > 3.0:
                causes.append("Requires manual investigation")
            else:
                causes.append("Monitor for recurrence")

        return causes

    def __repr__(self) -> str:
        """
        Return unambiguous string representation.

        Returns
        -------
        str
            Unambiguous string representation.
        """
        return (
            f"AnomalyDiagnoser("
            f"severity_threshold={self.severity_threshold}, "
            f"include_generic_causes={self.include_generic_causes}"
            f")"
        )

    def __str__(self) -> str:
        """
        Return human-readable description.

        Returns
        -------
        str
            Human-readable description.
        """
        return f"Anomaly Diagnostic Reasoner " f"(threshold={self.severity_threshold})"
