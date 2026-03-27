"""
Resolution policy based on hypothesis voting in Procela.

Examples
--------
>>> import random
>>>
>>> from procela import (
...     HypothesisRecord,
...     VariableRecord,
...     WeightedVotingPolicy
... )
>>>
>>> random.seed(42)
>>>
>>> policy=WeightedVotingPolicy()
>>>
>>> hypotheses = [
...     HypothesisRecord(
...         VariableRecord(
...             value=random.gauss(1.3, 0.2),
...             confidence=random.uniform(0, 1)
...         ),
...     ) for _ in range(15)
... ]
>>> resolved = policy.resolve(hypotheses=hypotheses)
>>>
>>> print(resolved.value)
1.3103318616666704
>>> print(resolved.confidence)
0.38029515762103755
>>> print(resolved.explanation)
Weighted voting resolution

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/policy/resolution/voting.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/policy/resolution/voting.html
"""

from __future__ import annotations

from typing import Iterable

from ...memory.hypothesis import HypothesisRecord
from ...memory.record import VariableRecord
from .base import ResolutionPolicy


class WeightedVotingPolicy(ResolutionPolicy):
    """
    Policy that resolves competing hypotheses with weighted voting.

    Examples
    --------
    >>> import random
    >>>
    >>> from procela import (
    ...     HypothesisRecord,
    ...     VariableRecord,
    ...     WeightedVotingPolicy
    ... )
    >>>
    >>> random.seed(42)
    >>>
    >>> policy=WeightedVotingPolicy()
    >>>
    >>> hypotheses = [
    ...     HypothesisRecord(
    ...         VariableRecord(
    ...             value=random.gauss(1.3, 0.2),
    ...             confidence=random.uniform(0, 1)
    ...         ),
    ...     ) for _ in range(15)
    ... ]
    >>> resolved = policy.resolve(hypotheses=hypotheses)
    >>>
    >>> print(resolved.value)
    1.3103318616666704
    >>> print(resolved.confidence)
    0.38029515762103755
    >>> print(resolved.explanation)
    Weighted voting resolution
    """

    def resolve(self, hypotheses: Iterable[HypothesisRecord]) -> VariableRecord | None:
        """
        Resolve competing proposals with weighted voting.

        Parameters
        ----------
        hypotheses : Iterable[HypothesisRecord]
            An iterable of `HypothesisRecord` objects. All hypotheses must have
            a valid `confidence` attribute (float typically between 0.0 and 1.0)
            and `weight` in hypothesis metadata.

        Returns
        -------
        VariableRecord | None
            The resolved conclusion with the weighted voting,
            or `None` if the input iterable is empty.

        Raises
        ------
        TypeError
            If any item in `hypotheses` is not an `HypothesisRecord` instance.
        ValueError
            If any hypothesis's confidence is not comparable (e.g., `None` or
            of an inappropriate type) or weight is negative.

        Notes
        -----
            This method use the product of metadata.get("weight", 1.0)
            and hypothesis.confidence. If hypothesis doesn't have a weight,
            1.0 is used as default. It skips null hypothesis and
            hypothesis which value or confidence is None.
        """
        # Convert to list for reusability and to check emptiness
        hypotheses_list = list(hypotheses)

        if not hypotheses_list:
            return None

        # Type checking & computation
        weight_sum = 0.0
        confidence_sum = 0.0
        value_sum = 0.0
        for hypothesis in hypotheses_list:
            if not isinstance(hypothesis, HypothesisRecord):
                raise TypeError(
                    f"All items must be HypothesisRecord instances, "
                    f"got {type(hypothesis).__name__}"
                )

            record = hypothesis.record
            if record is None or record.value is None or record.confidence is None:
                continue

            if not (0 <= record.confidence <= 1):
                raise ValueError("Confidence should be in [0, 1].")

            weight = 1.0
            if record.metadata is not None:
                weight = record.metadata.get("weight", 1.0)

            if not (0 <= weight):
                raise ValueError(f"Weight should be >= 0, got {weight}.")

            weight_sum += weight
            confidence_sum += record.confidence * weight
            value_sum += record.value * weight

        if weight_sum == 0:
            # Fallback to simple mean
            value_sum, weight_sum, confidence_sum = 0.0, 0.0, 0.0
            for hr in hypotheses_list:
                record = hr.record
                if (
                    record is not None
                    and record.value is not None
                    and record.confidence is not None
                ):
                    value_sum += record.value
                    confidence_sum += record.confidence
                    weight_sum += 1
            if weight_sum == 0:
                return None
            value = value_sum / weight_sum
            confidence = confidence_sum / weight_sum
        else:
            value = value_sum / weight_sum
            confidence = confidence_sum / weight_sum

        return VariableRecord(
            value=value,
            confidence=confidence,
            source=self.key(),
            explanation="Weighted voting resolution",
            metadata={"voting_resolution": True},
        )
