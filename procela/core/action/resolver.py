"""
Conflict resolution operators for the action subsystem.

This module defines the ConflictResolver class, which resolves
conflicting VariableRecords into a single authoritative record. It
performs computational selection only; the semantics of resolution
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

from ..memory.variable.history import VariableRecord
from ..reasoning.result import ReasoningResult
from ..reasoning.task import ReasoningTask
from .policy import SelectionPolicy
from .proposal import ActionProposal, ProposalStatus
from .validator import ProposalValidator


class ConflictResolver:
    """
    Resolve conflicts among competing VariableRecords.

    This class applies selection policies and optional validators to
    determine a single authoritative VariableRecord from multiple
    candidates. Semantic interpretation of the result is defined
    externally.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/action/resolver.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/action/resolver.html
    """

    def resolve(
        self,
        candidates: Sequence[VariableRecord],
        policy: SelectionPolicy,
        validators: Iterable[ProposalValidator] | None = None,
    ) -> tuple[ReasoningResult | None, VariableRecord | None]:
        """
        Resolve conflicting VariableRecords into a single authoritative record.

        Parameters
        ----------
        candidates : Sequence[VariableRecord]
            Competing VariableRecords produced by mechanisms.
        policy : SelectionPolicy
            Policy used to select among proposals.
        validators : Iterable[ProposalValidator] | None, optional
            Optional validators applied to proposals before selection.

        Returns
        -------
        tuple[ReasoningResult | None, VariableRecord | None]
            Tuple of a reasoning result and the resolved VariableRecord.
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
            )

        if not policy:
            return (
                self._create_failed_result(
                    task=ReasoningTask.CONFLICT_RESOLUTION,
                    confidence=0.0,
                    explanation="No policy.",
                ),
                None,
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

        if not isinstance(policy, SelectionPolicy):
            raise TypeError(f"`policy` should be a SelectionPolicy, got {policy!r}")

        if validators is not None and not isinstance(validators, Iterable):
            raise TypeError(
                f"`validators` should be a Iterable instance, got {validators!r}"
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
        if validators is not None:
            validated: list[ActionProposal] = []
            for proposal in proposals:
                if all(v.validate(proposal) for v in validators):
                    proposal = proposal.with_status(ProposalStatus.VALIDATED)
                    validated.append(proposal)

            proposals = validated

        if not proposals:
            return (
                self._create_failed_result(
                    task=ReasoningTask.CONFLICT_RESOLUTION,
                    confidence=0.0,
                    explanation="All proposals rejected by validators.",
                ),
                None,
            )

        # Step 3 — Policy selection
        selected = policy.select(proposals)

        if selected is None:
            return (
                self._create_failed_result(
                    task=ReasoningTask.CONFLICT_RESOLUTION,
                    confidence=0.0,
                    explanation="Selection policy returned no proposal.",
                ),
                None,
            )

        # Step 4 — Build resolved record
        resolved = VariableRecord(
            value=selected.value,
            confidence=selected.confidence,
            source=selected.source,
            metadata={
                "resolved_from": [
                    p.metadata.get("record_key")
                    for p in proposals
                    if p.metadata is not None
                ],
                "policy": policy.__class__.__name__,
            },
        )

        return None, resolved

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
        for validation and policy selection.
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
