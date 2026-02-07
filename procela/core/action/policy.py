"""
Policy module for the Procela framework.

This module defines resolution policies for action proposals within
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

from ...symbols.key import Key
from ..key_authority import KeyAuthority
from .proposal import ActionProposal, ProposalStatus


class ResolutionPolicy(ABC):
    """
    Abstract base class defining the interface for proposals resolution policies.

    In Procela, a policy is an intelligent decision entity that analyzes
    competing `ActionProposal` objects against system constraints, resource
    availability, and strategic goals to resolve competing proposals.
    Policies implement the core resolution logic that drives the system's
    autonomous behavior and ensures feedback-loop consistency.

    Subclasses must implement the `resolve` method with specific resolution
    algorithms (e.g., highest confidence, multi-criteria optimization,
    constraint satisfaction).
    """

    def __init__(self) -> None:
        """Initialize a ResolutionPolicy object."""
        super().__init__()
        self._key = KeyAuthority.issue(self)
        self.name = self.__class__.__name__

    def key(self) -> Key:
        """
        Return the unique identity of the ResolutionPolicy.

        Returns
        -------
        Key
            The unique identity of the ResolutionPolicy.
        """
        return self._key

    @abstractmethod
    def resolve(self, proposals: Iterable[ActionProposal]) -> ActionProposal | None:
        """
        Resolve competing proposals from a collection.

        This method embodies the policy's decision-making intelligence.
        It evaluates proposals based on the policy's internal criteria
        (confidence, status, etc)
        and returns a single resolved proposal or None if no suitable
        proposal is found.

        Parameters
        ----------
        proposals : Iterable[ActionProposal]
            An iterable of `ActionProposal` objects to evaluate and resolve from.
            The iterable may be empty. Policies should handle this gracefully.

        Returns
        -------
        ActionProposal | None
            The resolved `ActionProposal` that best satisfies the policy's
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


class MeanResolutionPolicy(ResolutionPolicy):
    """
    Policy that resolves competing proposals by computing the mean of values.

    The mean is computing over numeric values. Non-numeric are skipped.
    """

    def resolve(self, proposals: Iterable[ActionProposal]) -> ActionProposal | None:
        """
        Create a new proposal where value is the mean of all the numeric values.

        Parameters
        ----------
        proposals : Iterable[ActionProposal]
            An iterable of validated `ActionProposal` objects.
            All proposals must have a valid `confidence` attribute
            (float typically between 0.0 and 1.0).

        Returns
        -------
        ActionProposal | None
            The proposal with the mean value and mean confidence,
            or `None` if the input iterable is empty.

        Raises
        ------
        TypeError
            If any item in `proposals` is not an `ActionProposal` instance.
        ValueError
            If any proposal's confidence is not comparable (e.g., `None` or
            of an inappropriate type).

        Notes
        -----
        Only proposals with validated status are used during the resolution.
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

        value, confidence = 0.0, 0.0
        n = 0
        for p in validated:
            if p.value is not None and p.confidence is not None:
                value += float(p.value)
                confidence += float(p.confidence)
                n += 1
        if n < 1:
            return None

        return ActionProposal(
            value=value / n,
            confidence=confidence / n,
            source=self.key(),
            rationale="mean resolution policy",
            status=ProposalStatus.SELECTED,
        )


class HighestConfidencePolicy(ResolutionPolicy):
    """
    Concrete policy that resolves competing proposals with the highest confidence.

    This policy implements a simple but effective greedy resolution strategy:
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
    """

    def resolve(self, proposals: Iterable[ActionProposal]) -> ActionProposal | None:
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
