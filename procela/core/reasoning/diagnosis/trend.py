"""
Trend-Based Diagnostic Reasoner for the Procela Framework.

This module implements a trend-focused diagnostic reasoner that analyzes
directional patterns and temporal changes in system variables to identify
potential root causes. It specializes in detecting issues related to
gradual degradation, improvement trends, and stability violations.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/diagnosis/trend.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/diagnosis/trend.html
"""

from __future__ import annotations

from typing import Any, ClassVar

from ...assessment.anomaly import AnomalyResult
from ...assessment.diagnosis import DiagnosisResult
from ...assessment.statistics import StatisticsResult
from ...assessment.trend import TrendResult
from ...epistemic.variable import VariableView
from .base import Diagnoser


class TrendDiagnoser(Diagnoser):
    """
    Diagnostic reasoner specialized in trend pattern analysis.

    This reasoner examines trend characteristics and temporal patterns
    in system variables to identify potential issues. It focuses on
    detecting problems related to:
    - Gradual degradation or improvement trends
    - Trend stability and consistency
    - Trend magnitude and significance
    - Trend reversals or pattern changes
    - Rate of change abnormalities

    Parameters
    ----------
    significance_threshold : float, optional
        Minimum trend magnitude considered significant for diagnosis.
        Trends with absolute value below this threshold may be
        considered stable or insignificant.
        Must be > 0. Default is 0.2.

    strong_threshold : float, optional
        Threshold for identifying strong trends that warrant more
        serious diagnostic attention.
        Must be > significance_threshold.
        Default is 0.5.

    require_confidence : bool, optional
        Whether to require confidence scores from trend results
        for more reliable diagnosis.
        Default is True.

    Attributes
    ----------
    name : ClassVar[str]
        Class attribute identifying this reasoner as "TrendDiagnoser".

    significance_threshold : float
        Threshold for significant trend detection.

    strong_threshold : float
        Threshold for strong trend detection.

    require_confidence : bool
        Flag controlling confidence requirement.

    Notes
    -----
    This reasoner assumes that trend analysis has been performed and
    that the `VariableView` contains meaningful trend results. It's
    particularly effective for:
    1. Early detection of gradual system changes
    2. Monitoring performance degradation or improvement
    3. Identifying rate-of-change abnormalities
    4. Detecting trend reversals or pattern shifts

    The trend thresholds should be tuned based on the specific
    variable characteristics and system requirements.
    """

    name: ClassVar[str] = "TrendDiagnoser"

    def __init__(
        self,
        significance_threshold: float = 0.2,
        strong_threshold: float = 0.5,
        require_confidence: bool = True,
    ) -> None:
        """
        Initialize a trend-focused diagnostic reasoner.

        Parameters
        ----------
        significance_threshold : float, optional
            Minimum trend magnitude for significance.
            Must satisfy significance_threshold > 0.
            Default is 0.2.
        strong_threshold : float, optional
            Threshold for strong trend identification.
            Must satisfy strong_threshold > significance_threshold.
            Default is 0.5.
        require_confidence : bool, optional
            Whether to require confidence from trend results.
            Default is True.

        Raises
        ------
        ValueError
            If thresholds are invalid or inconsistent.
        """
        if significance_threshold <= 0:
            raise ValueError(
                f"significance_threshold must be > 0, got {significance_threshold}"
            )
        if strong_threshold <= significance_threshold:
            raise ValueError(
                f"strong_threshold ({strong_threshold}) must be > "
                f"significance_threshold ({significance_threshold})"
            )

        self.significance_threshold = significance_threshold
        self.strong_threshold = strong_threshold
        self.require_confidence = require_confidence

    def diagnose(self, view: VariableView) -> DiagnosisResult:
        """
        Perform diagnostic reasoning focused on trend analysis.

        This method examines trend characteristics in the system view
        to identify potential issues related to directional changes,
        rates of change, and temporal patterns.

        The diagnostic process:
        1. Checks if trend data is available and valid
        2. Analyzes trend direction for diagnostic signals
        3. Evaluates trend magnitude and strength
        4. Assesses trend stability and consistency
        5. Considers statistical context if available
        6. Generates diagnostic hypotheses based on trend patterns

        Parameters
        ----------
        view : VariableView
            A view of the system containing:
            - trend: Trend analysis results (primary focus)
            - stats: Historical statistics for context (optional)
            - anomaly: Anomaly results for correlation (optional)

        Returns
        -------
        DiagnosisResult
            Structured result containing:
            - causes: List of identified potential issues
            - confidence: Estimated confidence in diagnosis (0.0 to 1.0)
            - metadata: Trend analysis details and evidence

        Raises
        ------
        TypeError
            If view is not a VariableView instance.
        ValueError
            If trend is required but not available.
        """
        # Validate input type
        if not isinstance(view, VariableView):
            raise TypeError(f"view must be VariableView, got {type(view).__name__}")

        # Check for trend data
        if view.trend is None:
            if self.require_confidence:
                raise ValueError("TrendDiagnoser requires view.trend for analysis")
            # If not required, return empty diagnosis
            return DiagnosisResult(
                causes=[],
                confidence=0.0,
                metadata={
                    "diagnoser": self.name,
                    "trend_available": False,
                    "reason": "No trend data available",
                },
            )

        # Initialize results
        causes: list[str] = []
        metadata: dict[str, Any] = {
            "diagnoser": self.name,
            "significance_threshold": self.significance_threshold,
            "strong_threshold": self.strong_threshold,
            "require_confidence": self.require_confidence,
            "trend_available": True,
            "trend_value": view.trend.value,
            "trend_direction": view.trend.direction,
            "trend_threshold": view.trend.threshold,
            "stats_available": view.stats is not None,
            "anomaly_available": view.anomaly is not None,
        }

        # Perform trend analyses
        direction_causes = self._trend_direction(view.trend)
        if direction_causes:
            causes.extend(direction_causes)
            metadata["direction_issues"] = len(direction_causes)

        magnitude_causes = self._trend_magnitude(view.trend)
        if magnitude_causes:
            causes.extend(magnitude_causes)
            metadata["magnitude_issues"] = len(magnitude_causes)

        stability_causes = self._trend_stability(view.trend)
        if stability_causes:
            causes.extend(stability_causes)
            metadata["stability_issues"] = len(stability_causes)

        # Consider statistical context if available
        if view.stats is not None:
            stat_context_causes = self._statistical_context(view.trend, view.stats)
            if stat_context_causes:
                causes.extend(stat_context_causes)
                metadata["statistical_context_issues"] = len(stat_context_causes)

        # Consider anomaly correlation if available
        if view.anomaly and view.anomaly.is_anomaly:
            anomaly_causes = self._correlate_with_anomaly(view.trend, view.anomaly)
            if anomaly_causes:
                causes.extend(anomaly_causes)
                metadata["anomaly_correlation_issues"] = len(anomaly_causes)
            metadata["anomaly_present"] = True
            metadata["anomaly_score"] = view.anomaly.score
        else:
            metadata["anomaly_present"] = False

        # Calculate confidence
        confidence = self._trend_confidence(causes, view.trend)

        # Add fallback cause if no issues detected but trend is significant
        if not causes and abs(view.trend.value) > self.significance_threshold:
            direction_desc = "stable"
            if view.trend.direction == "up":
                direction_desc = "upward"
            elif view.trend.direction == "down":
                direction_desc = "downward"

            if direction_desc != "stable":
                causes.append(f"Significant {direction_desc} trend detected")
                confidence = 0.4  # Moderate confidence for significant trend

        trend_confidence = None
        if hasattr(view.trend, "confidence") and callable(view.trend.confidence):
            trend_confidence = view.trend.confidence()
        # Update metadata with final results
        metadata.update(
            {
                "causes_identified": len(causes),
                "confidence": confidence,
                "trend_confidence": trend_confidence,
            }
        )

        return DiagnosisResult(
            causes=causes,
            confidence=confidence,
            metadata=metadata,
        )

    def _trend_direction(self, trend: TrendResult) -> list[str]:
        """
        Analyze trend direction for diagnostic signals.

        Examines the direction of the trend (up, down, stable) to
        identify potential issues related to system behavior.

        Parameters
        ----------
        trend : TrendResult
            Trend analysis results.

        Returns
        -------
        list[str]
            List of direction-related diagnostic causes.
            Empty list if no direction issues detected.
        """
        causes: list[str] = []

        # Analyze based on direction
        if trend.direction == "down":
            causes.append("Downward trend suggests potential degradation")
            if hasattr(trend, "confidence") and trend.confidence() > 0.8:
                causes.append("High-confidence degradation trend")

        elif trend.direction == "up":
            causes.append("Upward trend may indicate improvement or overshoot")
            if hasattr(trend, "confidence") and trend.confidence() > 0.8:
                causes.append("High-confidence improvement trend")

        elif trend.direction == "stable":
            # Check if stability is unexpected given context
            if abs(trend.value) > self.significance_threshold / 2:
                causes.append("Unexpected stability given trend magnitude")
            else:
                causes.append("System appears stable")

        return causes

    def _trend_magnitude(self, trend: TrendResult) -> list[str]:
        """
        Analyze trend magnitude and strength.

        Evaluates the absolute value of the trend to determine its
        significance and potential impact.

        Parameters
        ----------
        trend : TrendResult
            Trend analysis results.

        Returns
        -------
        list[str]
            List of magnitude-related diagnostic causes.
            Empty list if no magnitude issues detected.
        """
        causes: list[str] = []
        abs_value = abs(trend.value)

        # Analyze magnitude relative to thresholds
        direction_desc = "stable"
        if trend.direction == "up":
            direction_desc = "upward"
        elif trend.direction == "down":
            direction_desc = "downward"

        if abs_value > self.strong_threshold:
            if direction_desc != "stable":
                causes.append(
                    f"Strong {direction_desc} trend detected "
                    f"(magnitude={trend.value:.2f})"
                )

        elif abs_value > self.significance_threshold:
            if direction_desc != "stable":
                causes.append(f"Significant {direction_desc} trend detected")

        elif abs_value > 0:
            if direction_desc != "stable":
                causes.append(f"Minor {direction_desc} trend present")

        # Check if trend exceeds its own threshold
        if trend.threshold is not None:
            if abs_value > trend.threshold:
                causes.append(f"Trend exceeds analysis threshold ({trend.threshold})")

        return causes

    def _trend_stability(self, trend: TrendResult) -> list[str]:
        """
        Check trend stability and consistency.

        Analyzes trend characteristics that might indicate instability,
        inconsistency, or unreliable pattern detection.

        Parameters
        ----------
        trend : TrendResult
            Trend analysis results.

        Returns
        -------
        list[str]
            List of stability-related diagnostic causes.
            Empty list if no stability issues detected.
        """
        causes: list[str] = []

        # Check confidence if available
        if hasattr(trend, "confidence") and callable(trend.confidence):
            confidence = trend.confidence()
            if confidence is not None:
                if confidence < 0.3:
                    causes.append("Low confidence in trend detection")
                elif confidence > 0.7:
                    causes.append("High confidence trend pattern")
                # else: moderate confidence, no issue

        # Check for contradictory signals
        if trend.direction == "stable" and trend.value is not None:
            if abs(trend.value) > self.significance_threshold:
                causes.append(
                    "Contradiction: stable direction with significant magnitude"
                )

        # Check if trend is near threshold boundaries
        if trend.threshold is not None:
            if abs(abs(trend.value) - trend.threshold) < 0.1 * trend.threshold:
                causes.append("Trend near decision threshold - may be unstable")

        return causes

    def _statistical_context(
        self, trend: TrendResult, stats: StatisticsResult
    ) -> list[str]:
        """
        Analyze trend in statistical context.

        Examines the trend relative to historical statistics to
        provide context-aware diagnosis.

        Parameters
        ----------
        trend : TrendResult
            Trend analysis results.
        stats : StatisticsResult
            Historical statistics for context.

        Returns
        -------
        list[str]
            List of context-related diagnostic causes.
            Empty list if no context issues detected.
        """
        causes: list[str] = []
        if stats is None:
            return causes

        # Check if trend is large relative to historical variability
        std = stats.std
        if std is not None and std > 0:
            trend_z = abs(trend.value) / std
            if trend_z > 2.0:
                causes.append(
                    "Trend is large relative to historical variability "
                    f"(z={trend_z:.2f})"
                )
            elif trend_z > 1.0:
                causes.append("Trend is noticeable relative to historical variability")

        # Check if trend direction aligns with statistical extremes
        if stats.min is not None:
            if trend.direction == "down" and trend.value < 0:
                # Check if trending toward minimum
                pass  # Could add logic here

        if stats.max is not None:
            if trend.direction == "up" and trend.value > 0:
                # Check if trending toward maximum
                pass  # Could add logic here

        return causes

    def _correlate_with_anomaly(
        self, trend: TrendResult, anomaly: AnomalyResult
    ) -> list[str]:
        """
        Correlate trend with anomaly findings.

        Examines the relationship between trend patterns and
        anomaly detection results.

        Parameters
        ----------
        trend : TrendResult
            Trend analysis results.
        anomaly: AnomalyResult
            Anomaly detection results.

        Returns
        -------
        list[str]
            List of correlation-related diagnostic causes.
            Empty list if no correlation issues detected.
        """
        causes: list[str] = []

        if anomaly.is_anomaly:
            # Check if trend provides context for anomaly
            if trend.direction == "down" and anomaly.score is not None:
                if anomaly.score > 3.0:
                    causes.append("Severe anomaly with downward trend - critical")
                else:
                    causes.append("Anomaly with downward trend")

            elif trend.direction == "up" and anomaly.score is not None:
                if anomaly.score > 3.0:
                    causes.append("Severe anomaly with upward trend")
                else:
                    causes.append("Anomaly with upward trend")

        return causes

    def _trend_confidence(self, causes: list[str], trend: TrendResult) -> float:
        """
        Calculate confidence in trend-based diagnosis.

        Confidence estimation considers:
        - Number and specificity of trend-related causes
        - Trend magnitude and significance
        - Trend confidence (if available)
        - Consistency of evidence

        Parameters
        ----------
        causes : list[str]
            List of identified diagnostic causes.
        trend : TrendResult
            Trend analysis results.

        Returns
        -------
        float
            Confidence estimate between 0.0 (no confidence) and 1.0
            (high confidence).
        """
        if not causes:
            return 0.0

        # Base confidence from trend magnitude
        abs_value = abs(trend.value)
        if abs_value > self.strong_threshold:
            magnitude_factor = 0.8
        elif abs_value > self.significance_threshold:
            magnitude_factor = 0.6
        else:
            magnitude_factor = 0.3

        # Adjust based on number of causes
        cause_factor = min(len(causes) / 5.0, 1.0)

        # Adjust based on trend confidence if available
        confidence_factor = 0.5  # Default
        if hasattr(trend, "confidence") and callable(trend.confidence):
            trend_confidence = trend.confidence()
            if trend_confidence is not None:
                confidence_factor = trend_confidence

        # Weighted combination
        confidence = (
            0.4 * magnitude_factor + 0.3 * cause_factor + 0.3 * confidence_factor
        )

        return min(max(confidence, 0.0), 1.0)  # Clamp to [0, 1]

    def __repr__(self) -> str:
        """
        Return unambiguous string representation.

        Returns
        -------
        str
            Unambiguous string representation.
        """
        return (
            f"TrendDiagnoser("
            f"significance_threshold={self.significance_threshold:.2f}, "
            f"strong_threshold={self.strong_threshold:.2f}, "
            f"require_confidence={self.require_confidence}"
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
        return (
            f"Trend Diagnostic Reasoner "
            f"(significance_threshold={self.significance_threshold:.2f}, "
            f"strong_threshold={self.strong_threshold:.2f})"
        )
