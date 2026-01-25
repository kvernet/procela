"""
Validator module for the Procela framework.

This module defines the ProposalValidator abstract base class and concrete
implementations for validating ActionProposal objects. Validators are key
components of Procela's contractual mechanistic framework, ensuring that only
proposals meeting specific criteria (e.g., confidence thresholds, constraints)
proceed in the reasoning and execution pipeline.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/action/validator.html

Examples Reference
------------------
https://procela.org/docs/examples/core/action/validator.html
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .proposal import ActionProposal


class ProposalValidator(ABC):
    """
    Abstract base class defining the interface for validating action proposals.

    In the Procela framework, a validator is an active reasoning entity
    responsible for enforcing system contracts and constraints. It evaluates
    whether an `ActionProposal` is admissible for further consideration,
    selection, or execution based on domain-specific rules, resource limits,
    or state consistency guarantees.

    Subclasses must implement the `validate` method with specific validation
    logic (e.g., checking confidence thresholds, resource availability,
    pre-condition satisfaction).
    """

    @abstractmethod
    def validate(self, proposal: ActionProposal) -> bool:
        """
        Validate a single action proposal.

        This is the core method that implements the validator's logic. It
        should inspect the proposal's attributes (value, confidence, effect,
        metadata, etc.) and the current system context to determine if the
        proposal satisfies all necessary conditions for being a viable
        candidate action.

        Parameters
        ----------
        proposal : ActionProposal
            The action proposal to validate. Must be a non-None instance of
            `ActionProposal`. The validator should not modify this object.

        Returns
        -------
        bool
            `True` if the proposal is valid according to this validator's
            criteria, `False` otherwise.

        Raises
        ------
        TypeError
            If the `proposal` parameter is not an instance of `ActionProposal`.
        ValueError
            If the proposal contains invalid or inconsistent data that prevents
            validation (e.g., a confidence value outside the expected [0,1]
            range, if the validator relies on it).

        Notes
        -----
        - Validators should be designed to be stateless and idempotent when
          possible, producing the same result for the same proposal and system
          state.
        - Multiple validators can be chained together to form a comprehensive
          validation pipeline (e.g., using an `AllPassValidator`).
        """
        pass


class ConfidenceThresholdValidator(ProposalValidator):
    """
    Validator that checks if a proposal's confidence meets a minimum threshold.

    This validator implements a fundamental validation rule: only proposals
    with a confidence score at or above a predefined threshold are considered
    valid. It enforces a basic quality gate in the action selection pipeline.

    Parameters
    ----------
    threshold : float
        The minimum confidence value (inclusive) required for a proposal to
        be considered valid. Must be a number between 0.0 and 1.0.

    Attributes
    ----------
    threshold : float
        The confidence threshold used for validation (read-only after
        initialization).

    Raises
    ------
    ValueError
        If the provided `threshold` is outside the valid range [0.0, 1.0].
    """

    def __init__(self, threshold: float) -> None:
        """
        Initialize a ConfidenceThresholdValidator with a specific threshold.

        The constructor validates the threshold parameter to ensure it is a
        sensible value for confidence comparison.

        Parameters
        ----------
        threshold : float
            The minimum confidence value required for validation.

        Raises
        ------
        ValueError
            If `threshold` is not a number between 0.0 and 1.0.
        """
        if not isinstance(threshold, (int, float)):
            raise TypeError(
                f"Threshold must be int or float, got {type(threshold).__name__}"
            )
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")
        self.threshold = float(threshold)

    def validate(self, proposal: ActionProposal) -> bool:
        """
        Validate that the proposal's confidence meets or exceeds the threshold.

        This method performs a simple numeric comparison between the proposal's
        confidence attribute and the validator's threshold.

        Parameters
        ----------
        proposal : ActionProposal
            The action proposal to validate.

        Returns
        -------
        bool
            `True` if `proposal.confidence >= self.threshold`, `False` otherwise.

        Raises
        ------
        TypeError
            If `proposal` is not an instance of `ActionProposal`.
        ValueError
            If `proposal.confidence` is not a comparable numeric value or is
            outside the expected [0,1] range.
        """
        if not isinstance(proposal, ActionProposal):
            raise TypeError(
                "Proposal must be an ActionProposal, " f"got {type(proposal).__name__}"
            )

        # Access confidence and validate it's a number
        confidence = proposal.confidence
        if not isinstance(confidence, (int, float)):
            raise TypeError(
                "Proposal confidence must be numeric, "
                f"got {type(confidence).__name__}"
            )

        # Optional: Ensure confidence is in valid range
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "Proposal confidence must be between 0.0 and 1.0, " f"got {confidence}"
            )

        return confidence >= self.threshold
