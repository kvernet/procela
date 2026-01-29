"""
Conflict resolution operators for the action subsystem.

This module defines the ConflictResolver class, which resolves
conflicting VariableRecords into a single authoritative record. It
performs computational resolution only; the semantics of resolution
and policy interpretation are defined externally.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/action/resolver.html

Examples Reference
------------------
https://procela.org/docs/examples/core/action/resolver.html
"""

from __future__ import annotations

from typing import Iterable, Sequence

from ..assessment.reasoning import ReasoningResult
from ..assessment.task import ReasoningTask
from ..memory.variable.history import VariableRecord
from .policy import ResolutionPolicy
from .proposal import ActionProposal, ProposalStatus
from .validator import ProposalValidator


class ConflictResolver:
    """
    Resolve conflicts among competing VariableRecords.

    This class applies resolution policies and optional validators to
    determine a single authoritative VariableRecord from multiple
    candidates. Semantic interpretation of the result is defined
    externally.
    """

    def resolve(
        self,
        candidates: Sequence[VariableRecord],
        policy: ResolutionPolicy,
        validators: Iterable[ProposalValidator] | None = None,
    ) -> tuple[ReasoningResult | None, VariableRecord | None, list[VariableRecord]]:
        """
        Resolve conflicting VariableRecords into a single authoritative record.

        Parameters
        ----------
        candidates : Sequence[VariableRecord]
            Competing VariableRecords produced by mechanisms.
        policy : ResolutionPolicy
            Policy used to resolve among proposals.
        validators : Iterable[ProposalValidator] | None, optional
            Optional validators applied to proposals before resolution.

        Returns
        -------
        tuple[ReasoningResult | None, VariableRecord | None, list[VariableRecord]]
            Tuple of the reasoning result, the resolved VariableRecord and the
            list of validated candidates that participate in resolution.
            If resolution fails, the ReasoningResult contains failure details
            and the VariableRecord is None. Otherwise, ReasoningResult is None
            and the resolved record is returned.

        Raises
        ------
        TypeError
            If any parameter is of the wrong type.

        Notes
        -----
        This method performs computation only. Validation rules and policy
        logic are applied mechanically, while the semantic meaning of
        resolution outcomes is defined externally.
        """
        if not candidates:
            return (
                self._create_failed_result(
                    task=ReasoningTask.CONFLICT_RESOLUTION,
                    confidence=0.0,
                    explanation="No candidates.",
                ),
                None,
                [],
            )

        if not isinstance(candidates, Sequence):
            raise TypeError(
                "`candidates` should be a Sequence of `VariableRecord`, "
                f"got {candidates!r}"
            )

        for i, candidate in enumerate(candidates):
            if not isinstance(candidate, VariableRecord):
                raise TypeError(
                    f"`candidate` {i} should be a `VariableRecord` instance, "
                    f"got {candidate!r}"
                )

        if validators is not None and not isinstance(validators, Iterable):
            raise TypeError(
                f"`validators` should be an Iterable instance, got {validators!r}"
            )

        if validators is not None:
            for i, validator in enumerate(validators):
                if not isinstance(validator, ProposalValidator):
                    raise TypeError(
                        f"`validator` {i} should be a ProposalValidator instance, "
                        f"got {validator!r}"
                    )

        # Step 1 — Convert records to proposals
        proposals = [self._record_to_proposal(r) for r in candidates]

        # Step 2 — Apply validators
        proposals_validated: list[ActionProposal] = []
        validated: list[VariableRecord] = []
        if validators is not None:
            for record, proposal in zip(candidates, proposals, strict=False):
                if all(v.validate(proposal) for v in validators):
                    proposal = proposal.with_status(ProposalStatus.VALIDATED)
                    proposals_validated.append(proposal)
                    validated.append(record)
        else:
            for proposal in proposals:
                proposal = proposal.with_status(ProposalStatus.VALIDATED)
                proposals_validated.append(proposal)
            validated = list(candidates)

        proposals = proposals_validated

        if not proposals:
            return (
                self._create_failed_result(
                    task=ReasoningTask.CONFLICT_RESOLUTION,
                    confidence=0.0,
                    explanation="All proposals rejected by validators.",
                ),
                None,
                validated,
            )

        if not policy:
            return (
                self._create_failed_result(
                    task=ReasoningTask.CONFLICT_RESOLUTION,
                    confidence=0.0,
                    explanation="No policy.",
                ),
                None,
                validated,
            )

        if not isinstance(policy, ResolutionPolicy):
            raise TypeError(f"`policy` should be a ResolutionPolicy, got {policy!r}")

        # Step 3 — Policy resolution
        resolved_proposal = policy.resolve(proposals)

        if resolved_proposal is None:
            return (
                self._create_failed_result(
                    task=ReasoningTask.CONFLICT_RESOLUTION,
                    confidence=0.0,
                    explanation="Resolution policy returned no proposal.",
                ),
                None,
                validated,
            )

        # Step 4 — Build resolved record
        resolved = VariableRecord(
            value=resolved_proposal.value,
            confidence=resolved_proposal.confidence,
            source=resolved_proposal.source,
            metadata={
                "resolved_from": [
                    p.metadata.get("record_key")
                    for p in proposals
                    if p.metadata is not None
                ],
                "policy": policy.__class__.__name__,
            },
        )

        return None, resolved, validated

    def _record_to_proposal(self, record: VariableRecord) -> ActionProposal:
        """
        Convert a VariableRecord into an ActionProposal.

        Parameters
        ----------
        record : VariableRecord
            The record to convert.

        Returns
        -------
        ActionProposal
            Proposal object corresponding to the given record.

        Notes
        -----
        This is a helper method used internally for preparing proposals
        for validation and policy resolution.
        """
        return ActionProposal(
            value=record.value,
            confidence=record.confidence or 0.0,
            source=record.source,
            metadata={
                "record_key": record.key(),
                "time": record.time,
            },
        )

    def _create_failed_result(
        self, task: ReasoningTask, confidence: float, explanation: str
    ) -> ReasoningResult:
        """
        Create a failed ReasoningResult for conflict resolution.

        Parameters
        ----------
        task : ReasoningTask
            The reasoning task associated with the failure.
        confidence : float
            Confidence value to attach to the failure.
        explanation : str
            Explanation of why the result failed.

        Returns
        -------
        ReasoningResult
            Result object representing a failed resolution attempt.

        Notes
        -----
        This is an internal helper method. Semantic interpretation of
        failure is handled externally.
        """
        return ReasoningResult(
            task=task,
            success=False,
            result=None,
            confidence=confidence,
            explanation=explanation,
        )
