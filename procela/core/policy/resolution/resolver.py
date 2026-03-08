"""
Resolver policy in Procela.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/policy/resolution/resolver.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/policy/resolution/resolver.html
"""

from __future__ import annotations

from typing import Callable, Iterable

from ...assessment.reasoning import ReasoningResult, ReasoningTask
from ...memory.hypothesis import HypothesisRecord
from ...memory.record import VariableRecord
from ...timer import Timer
from .base import ResolutionPolicy


class ResolverPolicy:
    """
    Resolve conflicts among competing hypotheses.

    This class applies resolution policies and optional validators to
    determine a single authoritative VariableRecord from multiple
    hypotheses.
    """

    def resolve(
        self,
        hypotheses: Iterable[HypothesisRecord],
        policy: ResolutionPolicy,
        validators: Iterable[Callable[[HypothesisRecord], bool]] | None = None,
    ) -> tuple[VariableRecord | None, ReasoningResult]:
        """
        Resolve competing hypotheses into a single authoritative conclusion.

        Parameters
        ----------
        hypotheses : Iterable[HypothesisRecord]
            The iterable hypotheses to resolve conflicts from.
        policy : ResolutionPolicy
            The resolution policy to use.
        validators : Iterable[Callable[[HypothesisRecord], bool]] | None
            The optional iterable validators to filter hypotheses before
            resolution.

        Returns
        -------
        tuple[VariableRecord | None, ReasoningResult]
            The tuple with:
                - resolved conclusion or None if no suitable conclusion is found
                - reasoning result with details about the resolution logic.
        """
        with Timer() as timer:
            if not hypotheses:
                return (
                    None,
                    ReasoningResult.failed_result(
                        task=ReasoningTask.CONFLICT_RESOLUTION,
                        confidence=None,
                        explanation="No hypothesis.",
                    ),
                )

            if not isinstance(hypotheses, Iterable):
                raise TypeError(
                    "`hypotheses` should be an Iterable of `HypothesisRecord`, "
                    f"got {type(hypotheses)}"
                )

            for i, hypothesis in enumerate(hypotheses):
                if not isinstance(hypothesis, HypothesisRecord):
                    raise TypeError(
                        f"`hypothesis` {i} should be a `HypothesisRecord` instance, "
                        f"got {type(hypothesis)}"
                    )

            if validators is not None:
                if not isinstance(validators, Iterable):
                    raise TypeError(
                        f"`validators` should be an Iterable instance, "
                        f"got {validators!r}"
                    )

                for i, validator in enumerate(validators):
                    if not callable(validator):
                        raise TypeError(
                            f"`validator` {i} should be a Callable instance, "
                            f"got {validator!r}"
                        )

            hypotheses_validated = []
            if validators:
                for hypothesis in hypotheses:
                    if all(validator(hypothesis) for validator in validators):
                        hypotheses_validated.append(hypothesis)
            else:
                hypotheses_validated = list(hypotheses)

            if not hypotheses_validated:
                return (
                    None,
                    ReasoningResult.failed_result(
                        task=ReasoningTask.CONFLICT_RESOLUTION,
                        confidence=None,
                        explanation="All hypotheses rejected by validators.",
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

            resolved = policy.resolve(hypotheses=hypotheses)

            if resolved is None:
                return (
                    None,
                    ReasoningResult.failed_result(
                        task=ReasoningTask.CONFLICT_RESOLUTION,
                        confidence=None,
                        explanation="Resolution policy returned no conclusion.",
                    ),
                )

        return (
            resolved,
            ReasoningResult(
                task=ReasoningTask.CONFLICT_RESOLUTION,
                success=True,
                result=resolved.key(),
                confidence=resolved.confidence,
                explanation="Conflict resolved successfully.",
                execution_time=timer.elapsed,
            ),
        )
