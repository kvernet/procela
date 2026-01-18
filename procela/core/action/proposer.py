"""
Action proposers for the action subsystem.

This module defines the ActionProposer class, which generates
ActionProposal objects based on ProposalView observations, including
anomalies, trends, and statistics. Computation is mechanical; semantic
interpretation of proposals is defined externally.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/action/proposer.html

Examples Reference
------------------
https://procela.org/docs/examples/core/action/proposer.html
"""

from __future__ import annotations

from ..reasoning.view import ProposalView
from .effect import ActionEffect
from .proposal import ActionProposal


class ActionProposer:
    """
    Generate actionable proposals from variable observations.

    This class produces ActionProposal objects using a ProposalView,
    considering anomalies, trends, and confidence levels. The semantic
    meaning of proposals is external to this module.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/action/proposer.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/action/proposer.html
    """

    def propose(self, view: ProposalView) -> list[ActionProposal]:
        """
        Generate a list of action proposals based on a ProposalView.

        Parameters
        ----------
        view : ProposalView
            Structured view containing variable statistics, anomalies, and trends.

        Returns
        -------
        list[ActionProposal]
            List of proposed actions derived from the view. The list may be empty
            if no actionable signals are present.

        Raises
        ------
        TypeError
            If `view` is not a ProposalView instance.

        Notes
        -----
        This method performs computational logic only. The semantic interpretation
        of each proposal is defined externally in the semantics documentation.
        """
        if view is None:
            return []

        if not isinstance(view, ProposalView):
            raise TypeError(f"`view` should be a ProposalView instance, got {view}")

        proposals: list[ActionProposal] = []

        stats = view.stats
        anomaly = view.anomaly
        trend = view.trend
        value_confidence = stats.confidence()
        last_value = stats.last_value

        # 1. Anomaly-driven proposals
        if anomaly is not None and anomaly.is_anomaly:
            confidence = anomaly.confidence()
            effect = ActionEffect(
                description="Investigate anomalous variable value",
                expected_outcome="Root cause identified or anomaly dismissed",
                confidence=confidence,
            )
            proposals.append(
                ActionProposal(
                    value=None,
                    confidence=confidence,
                    action="investigate_anomaly",
                    effect=effect,
                    metadata={
                        "anomaly_score": anomaly.score,
                        "threshold": anomaly.threshold,
                        "last_value": last_value,
                    },
                )
            )

        # 2. Low-confidence epistemic proposals
        if value_confidence is not None and value_confidence < 0.5:
            confidence = 1.0 - value_confidence
            proposals.append(
                ActionProposal(
                    value=None,
                    confidence=confidence,
                    action="improve_observation",
                    effect=ActionEffect(
                        description="Increase observation reliability",
                        expected_outcome="Higher confidence in future values",
                        confidence=confidence,
                    ),
                    metadata={
                        "reason": "low aggregated confidence",
                        "current_confidence": value_confidence,
                    },
                )
            )

        # 3. Trend-based proposals (only if meaningful)
        if trend is not None and trend.direction != "stable":
            confidence = trend.confidence()
            effect = ActionEffect(
                description=f"Monitor variable trend ({trend.direction})",
                expected_outcome="Early detection of instability or drift",
                confidence=confidence,
            )
            proposals.append(
                ActionProposal(
                    value=None,
                    confidence=confidence,
                    action="monitor_trend",
                    effect=effect,
                    metadata={
                        "trend_direction": trend.direction,
                        "trend_value": trend.value,
                        "threshold": trend.threshold,
                    },
                )
            )

        return proposals
