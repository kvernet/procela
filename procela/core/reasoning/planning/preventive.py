"""
Preventive planning module for Procela's active reasoning engine.

This module provides the PreventivePlanner class, which implements a
planning strategy focused on early intervention based on system predictions
and diagnoses to prevent potential issues before they occur.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/planning/preventive.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/planning/preventive.html
"""

from __future__ import annotations

from ...action.effect import ActionEffect
from ...action.proposal import ActionProposal, ProposalStatus
from ..result import PlanningResult
from ..view import PlanningView
from .base import Planner


class PreventivePlanner(Planner):
    """
    Preventive planning based on early signals and predictions.

    This planner analyzes system predictions and diagnoses to generate
    preventive action proposals aimed at monitoring and early detection
    of potential degradation or failures.

    The planner converts predictions into monitoring actions with associated
    confidence levels, creating a proactive planning strategy that focuses
    on risk reduction rather than reactive intervention.

    Parameters
    ----------
    priority : int, optional
        Planning priority (higher values indicate higher priority).
        Used when multiple planners are chained. Defaults to 0.
    enabled : bool, optional
        Whether this planner is active. Defaults to True.

    Raises
    ------
    ValueError
        If `priority` is negative.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/reasoning/planning/preventive.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/reasoning/planning/preventive.html
    """

    name = "preventive"

    def __init__(self, priority: int = 0, enabled: bool = True) -> None:
        """
        Initialize the PreventivePlanner.

        Parameters
        ----------
        priority : int, optional
            Planning priority (higher values indicate higher priority).
            Used when multiple planners are chained. Defaults to 0.
        enabled : bool, optional
            Whether this planner is active. Defaults to True.

        Raises
        ------
        ValueError
            If `priority` is negative.
        """
        super().__init__(self.name, priority, enabled)

    def plan(self, view: PlanningView) -> PlanningResult:
        """
        Generate preventive planning proposals based on system view.

        Analyzes the provided planning view to convert predictions into
        preventive monitoring actions. Returns empty proposals if the view
        is invalid, has no diagnosis, or if no proposals can be generated.

        Parameters
        ----------
        view : PlanningView
            The planning view containing diagnosis and predictions for
            the current system state.

        Returns
        -------
        PlanningResult
            A PlanningResult object containing preventive action proposals.

        Notes
        -----
        The method performs the following steps:
        1. Check if planner is enabled
        2. Validates the input view
        3. Checks for diagnosis availability
        4. Converts each prediction into a monitoring proposal
        5. Returns a PlanningResult with preventive strategy metadata

        Each generated proposal has:
        - Action type: "monitor"
        - Rationale: Preventive monitoring explanation
        - Effect: Early detection of degradation
        - Status: PROPOSED
        - Confidence: Inherited from the prediction
        """
        if not self.enabled:
            return self._create_failed_result(
                metadata={"reason": f"Planner '{self.name}' is disabled"}
            )

        if view is None:
            return self._create_failed_result(
                metadata={"reason": "Planning view is None"}
            )

        if not isinstance(view, PlanningView):
            raise ValueError(
                f"View must implement PlanningView protocol, got {type(view)}"
            )

        self._execution_count += 1

        predictions = view.predictions
        if predictions is None:
            return self._create_failed_result(
                metadata={"reason": "Predictions is None"}
            )

        proposals: list[ActionProposal] = []

        for pred in predictions:
            proposals.append(
                ActionProposal(
                    value=pred.value,
                    confidence=pred.confidence,
                    action="monitor",
                    rationale="Preventive monitoring based on prediction",
                    effect=ActionEffect(
                        description="Early detection of degradation",
                        expected_outcome="Reduced risk of failure",
                        confidence=pred.confidence,
                    ),
                    metadata=pred.metadata,
                    status=ProposalStatus.PROPOSED,
                )
            )

        return PlanningResult(
            proposals=proposals,
            strategy="preventive",
            metadata={"planner": self.name},
        )

    def __repr__(self) -> str:
        """
        Return official string representation of the PreventivePlanner.

        Returns
        -------
        str
            String representation showing the planner name and configuration.
        """
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"priority={self.priority}, enabled={self.enabled})"
        )

    def __str__(self) -> str:
        """
        Return human-readable description of the planner.

        Returns
        -------
        str
            Human-readable description of the preventive planner.
        """
        status = "enabled" if self.enabled else "disabled"
        return (
            f"PreventivePlanner '{self.name}' ({status}, " f"priority: {self.priority})"
        )
