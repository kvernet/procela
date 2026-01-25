"""
Reactive planning module for Procela's active reasoning engine.

This module provides the ReactivePlanner class, which implements a
planning strategy focused on responding to confirmed system issues
and diagnoses with immediate corrective actions.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/planning/reactive.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/planning/reactive.html
"""

from __future__ import annotations

from ...action.effect import ActionEffect
from ...action.proposal import ActionProposal, ProposalStatus
from ...assessment.planning import PlanningResult
from ...epistemic.planning import PlanningView
from .base import Planner


class ReactivePlanner(Planner):
    """
    Reactive planning based on confirmed system issues and diagnoses.

    This planner analyzes system diagnosis to generate reactive action
    proposals aimed at investigating and mitigating confirmed causes
    of issues. Unlike preventive planning, reactive planning responds
    to problems that have already been detected in the system.

    The planner converts each diagnosis cause into an investigation
    action, creating a responsive planning strategy that focuses on
    stabilizing system behavior through direct intervention.

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

    name = "reactive"

    def __init__(self, priority: int = 0, enabled: bool = True) -> None:
        """
        Initialize the ReactivePlanner.

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
        Generate reactive planning proposals based on system diagnosis.

        Analyzes the provided planning view to convert diagnosis causes
        into reactive investigation actions. Returns empty proposals
        if the view is invalid, has no diagnosis, or if the diagnosis
        contains no causes.

        Parameters
        ----------
        view : PlanningView
            The planning view containing diagnosis and current system
            state information.

        Returns
        -------
        PlanningResult
            A PlanningResult object containing reactive action proposals,
            or None if no valid planning result can be generated.

        Notes
        -----
        The method performs the following steps:
        1. Check if planner is enabled
        2. Validates the input view
        3. Checks for diagnosis availability and non-empty causes
        4. Converts each diagnosis cause into an investigation proposal
        5. Returns a PlanningResult with reactive strategy metadata

        Each generated proposal has:
        - Action type: "investigate"
        - Rationale: Includes the specific cause being addressed
        - Effect: Mitigation of detected issue
        - Status: PROPOSED
        - Confidence: Inherited from the diagnosis
        - Value: Current system value from the view
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

        diagnosis = view.diagnosis

        if diagnosis is None or not diagnosis.causes:
            return self._create_failed_result(
                metadata={"reason": "Diagnosis is None or has no causes"}
            )

        proposals: list[ActionProposal] = []

        for cause in diagnosis.causes:
            proposals.append(
                ActionProposal(
                    value=view.current_value,
                    confidence=diagnosis.confidence,
                    action="investigate",
                    rationale=f"Reactive action for cause: {cause}",
                    effect=ActionEffect(
                        description="Mitigate detected issue",
                        expected_outcome="Stabilize system behavior",
                        confidence=diagnosis.confidence,
                    ),
                    status=ProposalStatus.PROPOSED,
                )
            )

        return PlanningResult(
            proposals=proposals,
            recommended=None,
            confidence=diagnosis.confidence,
            strategy="reactive",
            metadata={"planner": self.name},
        )

    def __repr__(self) -> str:
        """
        Return official string representation of the ReactivePlanner.

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
            Human-readable description of the reactive planner.
        """
        status = "enabled" if self.enabled else "disabled"
        return f"ReactivePlanner '{self.name}' ({status}, priority: {self.priority})"
