"""
Planning operators for the reasoning subsystem.

This module defines the concrete operator implementations used for
planning in the reasoning pipeline. The operator performs computations
only and do not define the semantics of plans or actions.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/planning/operator.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/planning/operator.html
"""

from __future__ import annotations

from typing import Any

from ...assessment.planning import PlanningResult
from ...epistemic.planning import PlanningView
from .registry import get_planner


class PlanningOperator:
    """
    Base class for planning operators.

    Subclasses implement specific planning strategies and computations.
    This class defines the interface for all planning operators used
    in the reasoning pipeline.
    """

    def __init__(self, name: str, **kwargs: Any) -> None:
        """
        Initialize the planning operator.

        Parameters
        ----------
        name
            Name of the planner
        **kwargs
            Configuration or strategy-specific parameters for this operator.

        Notes
        -----
        This constructor sets up computational behavior only. All semantics
        are defined in the external documentation.
        """
        self.planner = get_planner(name, **kwargs)

    def plan(self, view: PlanningView) -> PlanningResult:
        """
        Compute a plan using the operator.

        Parameters
        ----------
        view : PlanningView
            The planning view for the planning computation.

        Returns
        -------
        PlanningResult
            Result of the planning computation.

        Notes
        -----
        This method performs computational logic only. Plan interpretation
        or evaluation is defined in external semantic documentation.
        """
        return self.planner.plan(view)
