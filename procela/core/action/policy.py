"""
Policy module for the Procela framework.

This module defines selection policies for action proposals within
Procela's active reasoning engine.
Policies implement strategic decision-making logic to choose the most
appropriate action from a set of competing proposals, enabling
resource-aware, constraint-respecting system optimization.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/action/policy.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/action/policy.html
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from .proposal import ActionProposal, ProposalStatus


class SelectionPolicy(ABC):
    """
    Abstract base class defining the interface for action selection policies.

    In Procela, a policy is an intelligent decision entity that analyzes
    competing `ActionProposal` objects against system constraints, resource
    availability, and strategic goals to select the optimal next action.
    Policies implement the core selection logic that drives the system's
    autonomous behavior and ensures feedback-loop consistency.

    Subclasses must implement the `select` method with specific selection
    algorithms (e.g., highest confidence, multi-criteria optimization,
    constraint satisfaction).

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/action/policy.html

    Examples Reference
    -------------------
    https://procela.org/docs/examples/core/action/policy.html
    """

    @abstractmethod
    def select(self, proposals: Iterable[ActionProposal]) -> ActionProposal | None:
        """
        Select the most appropriate action proposal from a collection.

        This method embodies the policy's decision-making intelligence.
        It evaluates proposals based on the policy's internal criteria
        (confidence, status, etc)
        and returns a single selected proposal or None if no suitable
        proposal is found.

        Parameters
        ----------
        proposals : Iterable[ActionProposal]
            An iterable of `ActionProposal` objects to evaluate and select from.
            The iterable may be empty. Policies should handle this gracefully.

        Returns
        -------
        ActionProposal | None
            The selected `ActionProposal` that best satisfies the policy's
            criteria, or `None` if the input is empty or no proposal meets
            the minimum requirements.

        Raises
        ------
        TypeError
            If any item in `proposals` is not an instance of `ActionProposal`.
        ValueError
            If the policy encounters invalid data within proposals (e.g.,
            confidence outside [0,1] if the policy relies on it).
        """
        pass


class HighestConfidencePolicy(SelectionPolicy):
    """
    Concrete policy that selects the action proposal with the highest confidence.

    This policy implements a simple but effective greedy selection strategy:
    among all valid proposals, choose the one with the numerically largest
    `confidence` value. It assumes confidence is a reliable proxy for
    expected success or utility.

    This policy is useful for:
    - Baseline comparison against more sophisticated policies
    - Systems where prediction confidence strongly correlates with outcome quality
    - Rapid prototyping and initial system deployment

    Warnings
    --------
    Using confidence alone ignores other crucial factors like resource cost,
    risk, temporal constraints, and multi-dimensional utility. It should be
    supplemented or replaced with more comprehensive policies in production
    systems with complex trade-offs.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/action/policy.html

    Examples Reference
    -------------------
    https://procela.org/docs/examples/core/action/policy.html
    """

    def select(self, proposals: Iterable[ActionProposal]) -> ActionProposal | None:
        """
        Select the proposal with the maximum confidence score.

        Parameters
        ----------
        proposals : Iterable[ActionProposal]
            An iterable of `ActionProposal` objects. All proposals must have
            a valid `confidence` attribute (float typically between 0.0 and 1.0).

        Returns
        -------
        ActionProposal | None
            The proposal with the highest confidence, or `None` if the input
            iterable is empty.

        Raises
        ------
        TypeError
            If any item in `proposals` is not an `ActionProposal` instance.
        ValueError
            If any proposal's confidence is not comparable (e.g., `None` or
            of an inappropriate type).
        """
        # Convert to list for reusability and to check emptiness
        proposals_list = list(proposals)

        if not proposals_list:
            return None

        # Type checking (optional but good for robustness)
        for proposal in proposals_list:
            if not isinstance(proposal, ActionProposal):
                raise TypeError(
                    f"All items must be ActionProposal instances, "
                    f"got {type(proposal).__name__}"
                )

        validated = [p for p in proposals_list if p.status == ProposalStatus.VALIDATED]
        if not validated:
            return None

        # Select based on maximum confidence
        try:
            return max(validated, key=lambda p: p.confidence if p.confidence else 0.0)
        except (TypeError, AttributeError) as e:
            # Convert to ValueError for consistent error handling
            raise ValueError(
                "Cannot compare proposals due to invalid confidence values"
            ) from e
