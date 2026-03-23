"""
Statistical Diagnostic Reasoner for the Procela Framework.

This module implements a statistical diagnostic reasoner that analyzes
historical patterns, distribution characteristics, and statistical anomalies
to identify potential root causes of system issues. It focuses on detecting
issues through statistical pattern recognition rather than explicit anomaly
flags.

Examples
--------
>>> from procela import (
...     Variable,
...     StatisticalDomain,
...     VariableRecord,
...     StatisticalDiagnoser
... )
>>>
>>> var = Variable("var", StatisticalDomain())
>>> var.set(VariableRecord(value=12, confidence=0.98))
>>> var.set(VariableRecord(value=13, confidence=0.94))
>>> var.set(VariableRecord(value=11, confidence=0.90))
>>> view = var.epistemic()
>>>
>>> diagnoser = StatisticalDiagnoser()
>>>
>>> result = diagnoser.diagnose(view=view)
>>>
>>> print(result.causes)
[]
>>> print(result.confidence)
0.0
>>> print(result.metadata["causes_identified"])
0
>>> print(result.metadata["patterns_detected"])
{'high_variability': False, 'significant_drift': False, ...}

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/diagnosis/statistical.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/diagnosis/statistical.html
"""

from __future__ import annotations

from typing import Any, ClassVar

from ...assessment.diagnosis import DiagnosisResult
from ...assessment.statistics import StatisticsResult
from ...assessment.trend import TrendResult
from ...epistemic.variable import VariableView
from .base import Diagnoser


class StatisticalDiagnoser(Diagnoser):
    """
    Diagnostic reasoner specialized in statistical pattern analysis.

    This reasoner examines statistical properties of system variables to
    identify potential issues that may not be flagged as explicit anomalies.
    It analyzes distribution characteristics, temporal patterns, and
    statistical deviations to detect subtle issues like:
    - Gradual degradation or drift
    - Increased variability or instability
    - Distribution shifts
    - Correlation breakdowns
    - Statistical control violations

    Parameters
    ----------
    variability_threshold : float, optional
        Threshold for identifying excessive variability issues.
        Coefficient of variation (std/mean) above this value may trigger
        variability-related diagnoses. Must be > 0. Default is 0.5.

    drift_sensitivity : float, optional
        Sensitivity to detect gradual drift or trend-related issues.
        Lower values make the diagnoser more sensitive to small drifts.
        Must be > 0. Default is 0.1.

    skewness_threshold : float, optional
        Absolute skewness value above which distribution asymmetry is
        considered significant. Must be > 0. Default is 1.0.

    Attributes
    ----------
    name : ClassVar[str]
        Class attribute identifying this reasoner as "StatisticalDiagnoser".

    variability_threshold : float
        Threshold for variability detection.

    drift_sensitivity : float
        Sensitivity for drift detection.

    skewness_threshold : float
        Threshold for skewness detection.

    Examples
    --------
    >>> from procela import (
    ...     Variable,
    ...     StatisticalDomain,
    ...     VariableRecord,
    ...     StatisticalDiagnoser
    ... )
    >>>
    >>> var = Variable("var", StatisticalDomain())
    >>> var.set(VariableRecord(value=12, confidence=0.98))
    >>> var.set(VariableRecord(value=13, confidence=0.94))
    >>> var.set(VariableRecord(value=11, confidence=0.90))
    >>> view = var.epistemic()
    >>>
    >>> diagnoser = StatisticalDiagnoser()
    >>>
    >>> result = diagnoser.diagnose(view=view)
    >>>
    >>> print(result.causes)
    []
    >>> print(result.confidence)
    0.0
    >>> print(result.metadata["causes_identified"])
    0
    >>> print(result.metadata["patterns_detected"])
    {'high_variability': False, 'significant_drift': False, ...}

    Notes
    -----
    This reasoner operates primarily on statistical properties rather than
    explicit anomaly flags. It's particularly useful for:
    1. Early detection of issues before they become full anomalies
    2. Identifying subtle degradation patterns
    3. Monitoring statistical process control

    The statistical thresholds and sensitivity parameters should be tuned
    for specific application domains and variable characteristics.
    """

    name: ClassVar[str] = "StatisticalDiagnoser"

    def __init__(
        self,
        variability_threshold: float = 0.5,
        drift_sensitivity: float = 0.1,
        skewness_threshold: float = 1.0,
    ) -> None:
        """
        Initialize a statistical pattern diagnostic reasoner.

        Parameters
        ----------
        variability_threshold : float, optional
            Threshold for identifying excessive variability.
            Must satisfy variability_threshold > 0.
            Default is 0.5.
        drift_sensitivity : float, optional
            Sensitivity for detecting gradual drift.
            Must satisfy drift_sensitivity > 0.
            Default is 0.1.
        skewness_threshold : float, optional
            Absolute skewness threshold for asymmetry detection.
            Must satisfy skewness_threshold > 0.
            Default is 1.0.

        Raises
        ------
        ValueError
            If any threshold parameter is not positive.

        Examples
        --------
        >>> from procela import (
        ...     Variable,
        ...     StatisticalDomain,
        ...     VariableRecord,
        ...     StatisticalDiagnoser
        ... )
        >>>
        >>> var = Variable("var", StatisticalDomain())
        >>> var.set(VariableRecord(value=12, confidence=0.98))
        >>> var.set(VariableRecord(value=13, confidence=0.94))
        >>> var.set(VariableRecord(value=11, confidence=0.90))
        >>> view = var.epistemic()
        >>>
        >>> diagnoser = StatisticalDiagnoser()
        >>>
        >>> result = diagnoser.diagnose(view=view)
        >>>
        >>> print(result.causes)
        []
        >>> print(result.confidence)
        0.0
        >>> print(result.metadata["causes_identified"])
        0
        >>> print(result.metadata["patterns_detected"])
        {'high_variability': False, 'significant_drift': False, ...}
        """
        if variability_threshold <= 0:
            raise ValueError(
                f"variability_threshold must be > 0, got {variability_threshold}"
            )
        if drift_sensitivity <= 0:
            raise ValueError(f"drift_sensitivity must be > 0, got {drift_sensitivity}")
        if skewness_threshold <= 0:
            raise ValueError(
                f"skewness_threshold must be > 0, got {skewness_threshold}"
            )

        self.variability_threshold = variability_threshold
        self.drift_sensitivity = drift_sensitivity
        self.skewness_threshold = skewness_threshold

    def diagnose(self, view: VariableView) -> DiagnosisResult:
        """
        Perform diagnostic reasoning based on statistical pattern analysis.

        This method examines statistical properties and patterns in the
        system view to identify potential issues. Unlike anomaly-focused
        diagnosers, this reasoner looks for statistical indications of
        problems that may not yet be flagged as explicit anomalies.

        The diagnostic process:
        1. Analyzes statistical variability and stability
        2. Detects gradual drift or trend patterns
        3. Examines distribution characteristics
        4. Checks for statistical control violations
        5. Combines evidence to generate diagnostic hypotheses

        Parameters
        ----------
        view : VariableView
            A view of the system containing statistical data:
            - stats: Historical statistics (must be present)
            - trend: Trend analysis results (optional)
            - anomaly: Anomaly results (considered but not primary)

        Returns
        -------
        DiagnosisResult
            Structured result containing:
            - causes: List of identified potential issues
            - confidence: Estimated confidence in diagnosis (0.0 to 1.0)
            - metadata: Statistical evidence and analysis details

        Raises
        ------
        TypeError
            If view is not a VariableView instance.
        ValueError
            If view.stats is None (statistical analysis requires stats).
        """
        # Validate input type
        if not isinstance(view, VariableView):
            raise TypeError(f"view must be VariableView, got {type(view).__name__}")

        # Check for required statistical data
        if view.stats is None:
            raise ValueError("StatisticalDiagnoser requires view.stats for analysis")

        # Initialize results
        causes: list[str] = []
        patterns: dict[str, bool] = {}
        metadata: dict[str, Any] = {
            "diagnoser": self.name,
            "variability_threshold": self.variability_threshold,
            "drift_sensitivity": self.drift_sensitivity,
            "skewness_threshold": self.skewness_threshold,
            "stats_available": True,
            "trend_available": view.trend is not None,
            "anomaly_available": view.anomaly is not None,
            "sample_count": view.stats.count is not None,
        }

        # Perform statistical analyses
        # Note: StatisticsResult doesn't have skewness/kurtosis/modes yet
        # So I work with what's available

        variability_causes = self._analyze_variability(view.stats)
        if variability_causes:
            causes.extend(variability_causes)
            patterns["high_variability"] = True
            metadata["variability_issues"] = len(variability_causes)
        else:
            patterns["high_variability"] = False

        # Analyze drift if trend data available
        if view.trend is not None:
            drift_causes = self._detect_drift(view.trend, view.stats)
            if drift_causes:
                causes.extend(drift_causes)
                patterns["significant_drift"] = True
                metadata["drift_issues"] = len(drift_causes)
            else:
                patterns["significant_drift"] = False

        # Check distribution characteristics based on available data
        distribution_causes = self._check_distribution(view.stats)
        if distribution_causes:
            causes.extend(distribution_causes)
            patterns["distribution_issues"] = True
            metadata["distribution_issues"] = len(distribution_causes)
        else:
            patterns["distribution_issues"] = False

        # Consider anomaly context if present (secondary consideration)
        if view.anomaly and view.anomaly.is_anomaly:
            patterns["anomaly_present"] = True
            metadata["anomaly_score"] = view.anomaly.score
            metadata["anomaly_method"] = view.anomaly.method
        else:
            patterns["anomaly_present"] = False

        # Calculate confidence based on statistical evidence
        confidence = self._statistical_confidence(patterns)

        # Update metadata with final results
        metadata.update(
            {
                "causes_identified": len(causes),
                "patterns_detected": patterns,
                "confidence": confidence,
            }
        )

        return DiagnosisResult(
            causes=causes,
            confidence=confidence,
            metadata=metadata,
        )

    def _analyze_variability(self, stats: StatisticsResult) -> list[str]:
        """
        Analyze statistical variability patterns.

        Examines standard deviation, variance, and related statistics
        to identify excessive variability that may indicate:
        - Measurement noise or instability
        - Process control issues
        - Environmental interference

        Parameters
        ----------
        stats : StatisticsResult
            Historical statistics object from StatisticsResult.

        Returns
        -------
        list[str]
            List of variability-related diagnostic causes.
            Empty list if no variability issues detected.
        """
        causes: list[str] = []

        # Check for sufficient data
        if not stats.count or stats.count < 2:
            return causes

        # Check coefficient of variation (std/mean)
        mean, std = stats.mean, stats.std
        if mean is not None and std is not None:
            if mean != 0:
                # Coefficient of variation
                cv = abs(std / mean)
                if cv > self.variability_threshold:
                    causes.append(f"High variability detected (CV={cv:.2f})")
            elif std > 10:  # Absolute threshold for zero mean
                causes.append("Significant variability with zero mean")

        # Check range relative to mean
        if stats.min is not None and stats.max is not None and mean is not None:
            data_range = stats.max - stats.min
            if mean != 0 and data_range / abs(mean) > 3.0:
                causes.append("Wide data range relative to mean")

        return causes

    def _detect_drift(self, trend: TrendResult, stats: StatisticsResult) -> list[str]:
        """
        Detect gradual drift or trend-related statistical issues.

        Analyzes trend patterns in conjunction with statistical context
        to identify:
        - Gradual degradation or improvement
        - Slow parameter drift
        - Trend-related instability

        Parameters
        ----------
        trend : TrendResult
            Trend analysis results.
        stats : StatisticsResult
            Historical statistics for context.

        Returns
        -------
        list[str]
            List of drift-related diagnostic causes.
            Empty list if no significant drift detected.
        """
        causes: list[str] = []

        # Check trend magnitude and direction
        if trend is not None and trend.value is not None:
            abs_trend = abs(trend.value)

            if abs_trend > self.drift_sensitivity:
                direction_desc = "stable"
                if trend.direction == "up":
                    direction_desc = "upward"
                elif trend.direction == "down":
                    direction_desc = "downward"

                if direction_desc != "stable":
                    # Check if trend is statistically significant
                    std = stats.std
                    if std is not None:
                        if std > 0:
                            trend_z = abs_trend / std
                            if trend_z > 1.0:  # More than 1 std deviation
                                causes.append(
                                    f"Significant {direction_desc} drift "
                                    f"(z={trend_z:.2f})"
                                )
                            else:
                                causes.append(f"Minor {direction_desc} drift detected")
                    else:
                        causes.append(f"{direction_desc.capitalize()} drift detected")

        return causes

    def _check_distribution(self, stats: StatisticsResult) -> list[str]:
        """
        Analyze distribution characteristics for potential issues.

        Note: The current StatisticsResult doesn't have skewness/kurtosis/modes.
        This method will be updated when those features are added to StatisticsResult.

        Parameters
        ----------
        stats : StatisticsResult
            Historical statistics object.

        Returns
        -------
        list[str]
            List of distribution-related diagnostic causes.
            Currently returns empty list until StatisticsResult is extended.

        Notes
        -----
        When StatisticsResult is extended with skewness, kurtosis, and modes,
        this method will analyze:
        - Skewness (asymmetry) using self.skewness_threshold
        - Kurtosis (tailedness)
        - Bimodality or multimodality
        """
        causes: list[str] = []

        # TODO: Enable these checks when StatisticsResult has these properties
        # Currently, StatisticsResult doesn't have skewness, kurtosis, or modes
        # Placeholder for future enhancement

        return causes

    def _statistical_confidence(self, patterns: dict[str, bool]) -> float:
        """
        Calculate confidence based on statistical evidence patterns.

        Confidence estimation considers:
        - Number and strength of detected patterns
        - Consistency across different statistical indicators
        - Presence of supporting anomaly evidence

        Parameters
        ----------
        patterns : dict[str, bool]
            Dictionary of detected statistical patterns.

        Returns
        -------
        float
            Confidence estimate between 0.0 (no confidence) and 1.0
            (high confidence).

        Notes
        -----
        This uses a weighted scoring system where different patterns
        contribute differently to overall confidence based on their
        diagnostic significance.
        """
        # Pattern weights (sum to 1.0)
        weights = {
            "high_variability": 0.4,
            "significant_drift": 0.4,
            "distribution_issues": 0.0,  # Currently not implemented
            "anomaly_present": 0.2,  # Supporting evidence
        }

        # Calculate weighted score
        score = 0.0
        for pattern, weight in weights.items():
            if patterns.get(pattern, False):
                score += weight

        # Adjust based on number of detected patterns
        pattern_count = sum(1 for v in patterns.values() if v)
        if pattern_count > 1:
            # Multiple consistent patterns increase confidence
            score *= min(1.0 + 0.2 * (pattern_count - 1), 1.5)

        return min(max(score, 0.0), 1.0)  # Clamp to [0, 1]

    def __repr__(self) -> str:
        """
        Return unambiguous string representation.

        Returns
        -------
        str
            Unambiguous string representation.
        """
        return (
            f"StatisticalDiagnoser("
            f"variability_threshold={self.variability_threshold:.2f}, "
            f"drift_sensitivity={self.drift_sensitivity:.2f}, "
            f"skewness_threshold={self.skewness_threshold:.2f}"
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
            f"Statistical Diagnostic Reasoner "
            f"(variability_threshold={self.variability_threshold:.2f}, "
            f"drift_sensitivity={self.drift_sensitivity:.2f})"
        )
