"""
Resolution policy based on hypothesis confidence in Procela.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/policy/resolution/confidence.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/policy/resolution/confidence.html
"""

from __future__ import annotations

from typing import Iterable

from ...memory.hypothesis import HypothesisRecord
from ...memory.record import VariableRecord
from .base import ResolutionPolicy


class HighestConfidencePolicy(ResolutionPolicy):
    """
    Concrete policy that resolves competing hypotheses with the highest confidence.

    This policy implements a simple but effective greedy resolution strategy:
    among all valid hypotheses, choose the one with the numerically largest
    `confidence` value. It assumes confidence is a reliable proxy for
    expected success or utility.

    This policy is useful for:
    - Baseline comparison against more sophisticated policies
    - Systems where prediction confidence strongly correlates with outcome quality
    - Rapid prototyping and initial system deployment

    Warnings
    --------
    Using confidence alone ignores other crucial factors. It should be
    supplemented or replaced with more comprehensive policies in production
    systems with complex trade-offs.
    """

    def resolve(self, hypotheses: Iterable[HypothesisRecord]) -> VariableRecord | None:
        """
        Select the proposal with the maximum confidence score.

        Parameters
        ----------
        hypotheses : Iterable[HypothesisRecord]
            An iterable of `HypothesisRecord` objects. All hypotheses must have
            a valid `confidence` attribute (float typically between 0.0 and 1.0).

        Returns
        -------
        VariableRecord | None
            The resolved conclusion with the highest confidence,
            or `None` if the input iterable is empty.

        Raises
        ------
        TypeError
            If any item in `hypotheses` is not an `HypothesisRecord` instance.
        ValueError
            If any hypothesis's confidence is not comparable (e.g., `None` or
            of an inappropriate type).
        """
        # Convert to list for reusability and to check emptiness
        hypotheses_list = list(hypotheses)

        if not hypotheses_list:
            return None

        # Type checking
        for hypothesis in hypotheses_list:
            if not isinstance(hypothesis, HypothesisRecord):
                raise TypeError(
                    f"All items must be HypothesisRecord instances, "
                    f"got {type(hypothesis).__name__}"
                )

        # Select based on maximum confidence
        try:
            hypothesis = max(
                hypotheses_list,
                key=lambda hr: (
                    hr.record.confidence if hr.record and hr.record.confidence else 0.0
                ),
            )
            record = hypothesis.record
            return VariableRecord(
                value=record.value if record is not None else None,
                confidence=record.confidence if record is not None else None,
                source=self.key(),
                explanation="Weighted confidence resolution",
                metadata={"weighted_resolution": True},
            )
        except (TypeError, AttributeError) as e:
            # Convert to ValueError for consistent error handling
            raise ValueError(
                "Cannot compare proposals due to invalid confidence values"
            ) from e


class WeightedConfidencePolicy(ResolutionPolicy):
    """Policy that resolves competing hypotheses with weighted confidence."""

    def resolve(self, hypotheses: Iterable[HypothesisRecord]) -> VariableRecord | None:
        """
        Resolve competing proposals with weighted confidence.

        Parameters
        ----------
        hypotheses : Iterable[HypothesisRecord]
            An iterable of `HypothesisRecord` objects. All hypotheses must have
            a valid `confidence` attribute (float typically between 0.0 and 1.0).

        Returns
        -------
        VariableRecord | None
            The resolved conclusion with the weighted confidence,
            or `None` if the input iterable is empty.

        Raises
        ------
        TypeError
            If any item in `hypotheses` is not an `HypothesisRecord` instance.
        ValueError
            If any hypothesis's confidence is not comparable (e.g., `None` or
            of an inappropriate type).

        Notes
        -----
            This method use the product of metadata.get("weight", 1.0)
            and hypothesis.confidence. If hypothesis doesn't have a weight,
            1.0 is used as default.
        """
        # Convert to list for reusability and to check emptiness
        hypotheses_list = list(hypotheses)

        if not hypotheses_list:
            return None

        # Type checking & computation
        weight_sum = 0.0
        value_sum = 0.0
        n = 0
        for hypothesis in hypotheses_list:
            if not isinstance(hypothesis, HypothesisRecord):
                raise TypeError(
                    f"All items must be HypothesisRecord instances, "
                    f"got {type(hypothesis).__name__}"
                )

            record = hypothesis.record
            if record is None or record.source is None or record.confidence is None:
                continue

            if not (0 <= record.confidence <= 1):
                raise ValueError("Confidence should be in [0, 1].")

            weight_sum += record.confidence
            value_sum += record.value * record.confidence
            n += 1

        if weight_sum == 0:
            # Fallback to simple mean
            value, confidence, n = 0.0, 0.0, 0
            for hr in hypotheses_list:
                record = hr.record
                if (
                    record is not None
                    and record.value is not None
                    and record.confidence is not None
                ):
                    value += record.value
                    confidence += record.confidence
                    n += 1
            if n == 0:
                return None
            value /= n
            confidence /= n
        else:
            value = value_sum / weight_sum
            confidence = weight_sum / n

        return VariableRecord(
            value=value,
            confidence=confidence,
            source=self.key(),
            explanation="Weighted confidence resolution",
            metadata={"weighted_resolution": True},
        )
