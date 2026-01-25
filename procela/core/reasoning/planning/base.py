"""
Base planner module for Procela's active reasoning engine.

Provides abstract foundations for intelligent planning systems that propose
interventions based on diagnosis, predictions, and current system state.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/planning/base.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/planning/base.html
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from ...assessment.planning import PlanningResult
from ...epistemic.planning import PlanningView

logger = logging.getLogger(__name__)


class Planner(ABC):
    """
    Abstract base class for planning algorithms in Procela.

    Planning algorithms analyze current state (via PlanningView), diagnose
    issues, consider predictions, and propose interventions to optimize
    system behavior while respecting constraints and resource limitations.

    Subclasses must implement the `plan` method to provide specific
    planning logic while adhering to the framework's consistency guarantees.

    Parameters
    ----------
    name : str
        Name identifier for this planner instance.
    priority : int, optional
        Planning priority (higher values indicate higher priority).
        Used when multiple planners are chained. Defaults to 0.
    enabled : bool, optional
        Whether this planner is active. Defaults to True.

    Raises
    ------
    ValueError
        If `priority` is negative or if initialization parameters are invalid.
    """

    def __init__(self, name: str, priority: int = 0, enabled: bool = True) -> None:
        """
        Initialize the planner base.

        Parameters
        ----------
        name : str
            Name identifier for this planner instance.
        priority : int, optional
            Planning priority (higher values indicate higher priority).
            Used when multiple planners are chained. Defaults to 0.
        enabled : bool, optional
            Whether this planner is active. Defaults to True.

        Raises
        ------
        ValueError
            If `priority` is negative or if name is empty.
        """
        if priority < 0:
            raise ValueError("Priority must be non-negative")
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")

        self._name = name
        self._priority = priority
        self._enabled = enabled
        self._execution_count = 0

        logger.debug(
            "Initialized planner '%s' with priority %d, enabled=%s",
            name,
            priority,
            enabled,
        )

    @property
    def name(self) -> str:
        """
        Get the planner's name identifier.

        Returns
        -------
        str
            The planner's name.
        """
        return self._name

    @property
    def priority(self) -> int:
        """
        Get the planner's priority.

        Returns
        -------
        int
            The planner priority (higher values indicate higher priority).
        """
        return self._priority

    @property
    def enabled(self) -> bool:
        """
        Check if the planner is enabled.

        Returns
        -------
        bool
            True if the planner is active, False otherwise.
        """
        return self._enabled

    @property
    def execution_count(self) -> int:
        """
        Get the number of times plan() has been successfully executed.

        Returns
        -------
        int
            Count of successful planner executions.
        """
        return self._execution_count

    def enable(self) -> None:
        """
        Enable the planner for future planning cycles.

        Notes
        -----
        This method is idempotent. Calling it multiple times has no
        additional effect if the planner is already enabled.
        """
        if not self._enabled:
            self._enabled = True
            logger.info("Planner '%s' enabled", self._name)

    def disable(self) -> None:
        """
        Disable the planner from participating in planning cycles.

        Notes
        -----
        This method is idempotent. Calling it multiple times has no
        additional effect if the planner is already disabled.
        """
        if self._enabled:
            self._enabled = False
            logger.info("Planner '%s' disabled", self._name)

    @abstractmethod
    def plan(self, view: PlanningView) -> PlanningResult:
        """
        Implement and execute the planner algorithm based on the provided view.

        Subclasses must override this method to provide specific planner
        algorithms while maintaining consistency with the framework's
        guarantees.

        Parameters
        ----------
        view : PlanningView
            The validated planning view.

        Returns
        -------
        PlanningResult
            Planning result with proposed actions.

        Notes
        -----
        Implementations should:
        1. Analyze diagnosis results to understand current issues
        2. Consider predictions to anticipate future states
        3. Evaluate current value and constraints
        4. Generate appropriate ActionProposal objects
        5. Select recommendations based on optimization criteria
        """
        pass

    def __repr__(self) -> str:
        """
        Get string representation of the planner.

        Returns
        -------
        str
            String representation showing name, priority, and enabled state.
        """
        return (
            f"{self.__class__.__name__}(name={self._name!r}, "
            f"priority={self._priority}, enabled={self._enabled})"
        )

    def __str__(self) -> str:
        """
        Get human-readable description of the planner.

        Returns
        -------
        str
            Human-readable description.
        """
        status = "enabled" if self._enabled else "disabled"
        return f"Planner '{self._name}' ({status}, priority: {self._priority})"

    def _create_failed_result(self, metadata: dict[str, Any]) -> PlanningResult:
        """
        Create a planning result that contains failed details.

        Parameters
        ----------
        metadata : dict[str, Any]
            The metadata containing details about why the planning fails.

        Returns
        -------
        PlanningResult
            A failed planning result with empty proposals.
        """
        _metadata = metadata.copy()
        _metadata.update(
            {
                "priority": self.priority,
                "enabled": self.enabled,
            }
        )
        return PlanningResult(
            proposals=[],
            recommended=None,
            confidence=None,
            strategy=None,
            metadata=_metadata,
        )
