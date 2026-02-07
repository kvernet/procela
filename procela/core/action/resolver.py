"""
Conflict resolution operators in Procela.

This module defines the ConflictResolver class, which resolves
competing candidates into a single authoritative record. It
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
from ..memory.candidate import CandidateRecord
from ..memory.record import VariableRecord
from ..timer import Timer
from .policy import ResolutionPolicy
from .proposal import ActionProposal, ProposalStatus
from .validator import ProposalValidator


class ConflictResolver:
    """
    Resolve conflicts among competing candidates.

    This class applies resolution policies and optional validators to
    determine a single authoritative VariableRecord from multiple
    candidates. Semantic interpretation of the result is defined
    externally.
    """

    def resolve(
        self,
        candidates: Sequence[CandidateRecord],
        policy: ResolutionPolicy,
        validators: Iterable[ProposalValidator] | None = None,
    ) -> tuple[VariableRecord | None, ReasoningResult | None]:
        """
        Resolve conflicting candidates into a single authoritative record.

        Parameters
        ----------
        candidates : Sequence[CandidateRecord]
            Competing candidates produced by mechanisms.
        policy : ResolutionPolicy
            Policy used to resolve among candidates.
        validators : Iterable[ProposalValidator] | None, optional
            Optional validators applied to candidates before resolution.

        Returns
        -------
        tuple[VariableRecord | None, ReasoningResult | None]
            Tuple of the resolved record and the reasoning result.
            If resolution fails, the ReasoningResult contains failure details
            and the resolved is None.

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
        with Timer() as timer:
            if not candidates:
                return (
                    None,
                    ReasoningResult.failed_result(
                        task=ReasoningTask.CONFLICT_RESOLUTION,
                        confidence=None,
                        explanation="No candidates.",
                    ),
                )

            if not isinstance(candidates, Sequence):
                raise TypeError(
                    "`candidates` should be a Sequence of `CandidateRecord`, "
                    f"got {type(candidates)}"
                )

            for i, candidate in enumerate(candidates):
                if not isinstance(candidate, CandidateRecord):
                    raise TypeError(
                        f"`candidate` {i} should be a `CandidateRecord` instance, "
                        f"got {type(candidate)}"
                    )

            if validators is not None:
                if not isinstance(validators, Iterable):
                    raise TypeError(
                        f"`validators` should be a Iterable instance, "
                        f"got {validators!r}"
                    )

                for i, validator in enumerate(validators):
                    if not isinstance(validator, ProposalValidator):
                        raise TypeError(
                            f"`validator` {i} should be a ProposalValidator instance, "
                            f"got {validator!r}"
                        )

            # Step 1 — Convert records to proposals
            proposals = [
                self._record_to_proposal(r.record)
                for r in candidates
                if r is not None and r.record is not None
            ]

            # Step 2 — Apply validators
            proposals_validated: list[ActionProposal] = []
            validated: list[VariableRecord] = []
            if validators is not None:
                for candidate, proposal in zip(candidates, proposals, strict=False):
                    if all(v.validate(proposal) for v in validators):
                        proposal = proposal.with_status(ProposalStatus.VALIDATED)
                        proposals_validated.append(proposal)
                        if candidate is not None and candidate.record is not None:
                            validated.append(candidate.record)
            else:
                for candidate, proposal in zip(candidates, proposals, strict=False):
                    proposal = proposal.with_status(ProposalStatus.VALIDATED)
                    proposals_validated.append(proposal)
                    if candidate is not None and candidate.record is not None:
                        validated.append(candidate.record)

            proposals = proposals_validated

            if not proposals:
                return (
                    None,
                    ReasoningResult.failed_result(
                        task=ReasoningTask.CONFLICT_RESOLUTION,
                        confidence=None,
                        explanation="All proposals rejected by validators.",
                    ),
                )

            if not policy:
                return (
                    None,
                    ReasoningResult.failed_result(
                        task=ReasoningTask.CONFLICT_RESOLUTION,
                        confidence=None,
                        explanation="No policy.",
                    ),
                )

            if not isinstance(policy, ResolutionPolicy):
                raise TypeError(
                    f"`policy` should be a ResolutionPolicy, got {type(policy)}"
                )

            # Step 3 — Policy resolution
            resolved_proposal = policy.resolve(proposals)

            if resolved_proposal is None:
                return (
                    None,
                    ReasoningResult.failed_result(
                        task=ReasoningTask.CONFLICT_RESOLUTION,
                        confidence=None,
                        explanation="Resolution policy returned no proposal.",
                    ),
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
                    "policy": policy.name,
                },
            )

        return (
            resolved,
            ReasoningResult(
                task=ReasoningTask.CONFLICT_RESOLUTION,
                success=True,
                result=resolved.key(),
                confidence=resolved.confidence,
                explanation="Conflict resolved succesfully.",
                execution_time=timer.elapsed,
            ),
        )

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
