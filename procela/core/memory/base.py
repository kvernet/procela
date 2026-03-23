"""
Memory structures for variable in Procela.

This module defines immutable, chained-only memory structures used to
understand the evolution of a variable records and reasoning results over time.
Each memory instance represents a complete epistemic knowledge derived from
its predecessor and a newly added memory.

Memories are persistent and immutable: all update operations return new
memory instances without mutating existing ones.

Examples
--------
>>> from procela import (
...     VariableMemory,
...     HypothesisRecord,
...     VariableRecord,
...     ReasoningResult,
...     ReasoningTask
... )
>>>
>>> hypotheses = [
...     HypothesisRecord(
...         VariableRecord(i + 1, confidence=i/5)
...     ) for i in range(5)
... ]
>>>
>>> memory = VariableMemory(
...     hypotheses=tuple(hypotheses),
...     conclusion=VariableRecord(3, confidence=2/5),
...     reasoning=ReasoningResult(
...         task=ReasoningTask.CONFLICT_RESOLUTION,
...         success=True,
...         result=3,
...         confidence=2/5,
...     )
... )
>>>
>>> memory = memory.new(tuple(hypotheses[:2]), None, None)
>>>
>>> for hy, c, r in memory.iter():
...    print(len(hy), c, r)
2 None None
5 VariableRecord(value=3, time=None, source=None, confidence=0.4, ...)
>>> hy, c, r = memory.latest()
>>> print(hy, c, r)
(HypothesisRecord(record=VariableRecord(value=1, time=None, ...)) None None
>>> memory.reset()
>>> print(memory)
VariableMemory(hypotheses=(), conclusion=None, reasoning=None)

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/memory/variable/base.html

Examples Reference
------------------
https://procela.org/docs/examples/core/memory/variable/base.html
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from ...symbols.key import Key
from ..assessment.reasoning import ReasoningResult, ReasoningTask
from ..key_authority import KeyAuthority
from .hypothesis import HypothesisRecord
from .record import VariableRecord


@dataclass(frozen=True)
class VariableMemory:
    """
    Represent an immutable epistemic memory node of a variable.

    Each node captures the epistemic state of a variable at a given resolution
    moment: hypotheses considered, conclusion reached, and reasoning produced.
    Nodes form a persistent chain enabling full epistemic auditability.

    Parameters
    ----------
    hypotheses : tuple[HypothesisRecord, ...]
        Hypotheses retained at commit time.
    conclusion : VariableRecord | None
        Final resolved value at commit time.
    reasoning : ReasoningResult | None
        Reasoning explaining the resolution.
    config : dict[str, Any]
        Configuration metadata associated with this commit.
    previous : Key | None
        Key of the previous memory node.

    Examples
    --------
    >>> from procela import (
    ...     VariableMemory,
    ...     HypothesisRecord,
    ...     VariableRecord,
    ...     ReasoningResult,
    ...     ReasoningTask
    ... )
    >>>
    >>> hypotheses = [
    ...     HypothesisRecord(
    ...         VariableRecord(i + 1, confidence=i/5)
    ...     ) for i in range(5)
    ... ]
    >>>
    >>> memory = VariableMemory(
    ...     hypotheses=tuple(hypotheses),
    ...     conclusion=VariableRecord(3, confidence=2/5),
    ...     reasoning=ReasoningResult(
    ...         task=ReasoningTask.CONFLICT_RESOLUTION,
    ...         success=True,
    ...         result=3,
    ...         confidence=2/5,
    ...     )
    ... )
    >>>
    >>> memory = memory.new(tuple(hypotheses[:2]), None, None)
    >>>
    >>> for hy, c, r in memory.iter():
    ...    print(len(hy), c, r)
    2 None None
    5 VariableRecord(value=3, time=None, source=None, confidence=0.4, ...)
    >>> hy, c, r = memory.latest()
    >>> print(hy, c, r)
    (HypothesisRecord(record=VariableRecord(value=1, time=None, ...)) None None
    >>> memory.reset()
    >>> print(memory)
    VariableMemory(hypotheses=(), conclusion=None, reasoning=None)

    Notes
    -----
    VariableMemory nodes are immutable and represent epistemic commitments,
    not execution artifacts.
    """

    hypotheses: tuple[HypothesisRecord, ...]
    conclusion: VariableRecord | None
    reasoning: ReasoningResult | None
    config: dict[str, Any] = field(default_factory=dict, repr=False)
    previous: Key | None = field(default=None, repr=False)

    _key: Key = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validate a variable memory after initialization.

        Performs type checking on the attributes and generates
        a unique key for the instance.

        Raises
        ------
        TypeError
            If `hypotheses` is not a tuple of HypothesisRecord.
            If `conclusion` is not a VariableRecord instance or None.
            If `reasoning` is not a ReasoningResult or None.
            If `previous` is not a Key or None.
            If `config` is not a dict.
        """
        self._validate(
            hypotheses=self.hypotheses,
            conclusion=self.conclusion,
            reasoning=self.reasoning,
        )

        if not isinstance(self.config, dict):
            raise TypeError(f"`config` should be a dict, got {type(self.config)}")

        if not isinstance(self.previous, Key | None):
            raise TypeError(
                f"`previous` should be a Key or None, got {type(self.previous)}"
            )

        from ..key_authority import KeyAuthority

        object.__setattr__(self, "_key", KeyAuthority.issue(self))

    def new(
        self,
        hypotheses: tuple[HypothesisRecord, ...],
        conclusion: VariableRecord | None,
        reasoning: ReasoningResult | None,
    ) -> VariableMemory:
        """
        Append a new node to the variable memory.

        Parameters
        ----------
        hypotheses : tuple[HypothesisRecord, ...]
            The hypotheses of the new node.
        conclusion : VariableRecord | None
            The conclusion of the new node.
        reasoning : ReasoningResult | None
            The reasoning of the new node.

        Returns
        -------
        VariableMemory
            The new memory instance representing the extended memory.
        """
        self._validate(
            hypotheses=hypotheses, conclusion=conclusion, reasoning=reasoning
        )

        return VariableMemory(
            hypotheses=hypotheses,
            conclusion=conclusion,
            reasoning=reasoning,
            previous=self._key,
            config=self.config,
        )

    def key(self) -> Key:
        """
        Return the unique identity key of this memory node.

        Returns
        -------
        Key
            A key uniquely identifying this memory node.
        """
        return self._key

    def previous_key(self) -> Key | None:
        """
        Return the identity key of the previous memory node.

        Returns
        -------
        Key | None
            The key of the previous memory node, or None if this node is the root.
        """
        return self.previous

    def iter(
        self,
        source: Key | None = None,
        task: ReasoningTask | None = None,
        success: bool | None = None,
    ) -> Iterable[
        tuple[
            tuple[HypothesisRecord, ...],
            VariableRecord | None,
            ReasoningResult | None,
        ]
    ]:
        """
        Iterate over nodes from newest to oldest matching the specified criteria.

        Parameters
        ----------
        source : Key | None
            The source of the conclusion if provided. Default is None.
        task : ReasoningTask | None
            The reasoning task if provided. Default is None.
        success : bool | None
            (Un)Successful reasoning if provided. Default is None.

        Yields
        ------
        tuple[
            tuple[HypothesisRecord, ...],
            VariableRecord | None,
            ReasoningResult | None,
        ]
            Nodes in reverse chronological order.
        """
        current: VariableMemory | None = self

        def previous(prev_key: Key | None) -> VariableMemory | None:
            prev = KeyAuthority.resolve(prev_key)
            return prev if isinstance(prev, VariableMemory) else None

        while current is not None:
            hypotheses = current.hypotheses
            conclusion = current.conclusion
            reasoning = current.reasoning

            prev_key = current.previous
            current = previous(prev_key)

            if (
                source is not None
                and conclusion is not None
                and conclusion.source != source
            ):
                continue
            if task is not None and reasoning is not None and reasoning.task != task:
                continue
            if (
                success is not None
                and reasoning is not None
                and reasoning.success != success
            ):
                continue

            yield (hypotheses, conclusion, reasoning)

            if prev_key is None:
                break

    def records(
        self,
        *,
        source: Key | None = None,
        task: ReasoningTask | None = None,
        success: bool | None = None,
    ) -> list[
        tuple[
            tuple[HypothesisRecord, ...],
            VariableRecord | None,
            ReasoningResult | None,
        ]
    ]:
        """
        Retrieve records matching the specified criteria.

        Parameters
        ----------
        source : Key | None
            The source of the conclusion if provided. Default is None.
        task : ReasoningTask | None
            The reasoning task if provided. Default is None.
        success : bool | None
            (Un)Successful reasoning if provided. Default is None.

        Returns
        -------
        list[
            tuple[
                tuple[HypothesisRecord, ...],
                VariableRecord | None,
                ReasoningResult | None,
            ]
        ]
            Nodes matching the given criteria.
        """
        nodes = list(self.iter(source=source, task=task, success=success))
        nodes.reverse()
        return nodes

    def latest(
        self,
    ) -> tuple[
        tuple[HypothesisRecord, ...],
        VariableRecord | None,
        ReasoningResult | None,
    ]:
        """
        Return the most recent node.

        Returns
        -------
        tuple[
            tuple[HypothesisRecord, ...],
            VariableRecord | None,
            ReasoningResult | None,
        ]
            The latest node in the memory.
        """
        return (self.hypotheses, self.conclusion, self.reasoning)

    def reset(self) -> None:
        """
        Reset the variable memory.

        This method clears the current node and removes the reference to any
        previous memory node. After reset, the memory contains no observation
        and no chain to earlier nodes.

        The reset operation is intended for simulation lifecycle control, such as
        restarting a world or evaluating counterfactual scenarios.

        Notes
        -----
        - Memory objects are immutable during normal execution.
        - Resetting a memory discards the current epistemic timeline.

        Warnings
        --------
        This method must not be called during a simulation step.
        Resetting memory breaks continuity and invalidates ongoing execution.
        """
        object.__setattr__(self, "hypotheses", ())
        object.__setattr__(self, "conclusion", None)
        object.__setattr__(self, "reasoning", None)
        object.__setattr__(self, "previous", None)
        object.__setattr__(self, "config", {})

    def _validate(
        self,
        hypotheses: tuple[HypothesisRecord, ...],
        conclusion: VariableRecord | None,
        reasoning: ReasoningResult | None,
    ) -> None:
        """
        Perform type checking on the attributes of a variable node.

        Parameters
        ----------
        hypotheses : tuple[HypothesisRecord, ...]
            The hypotheses to validate.
        conclusion : VariableRecord | None
            The conclusion to validate
        reasoning : ReasoningResult | None
            The reasoning to validate.

        Raises
        ------
        TypeError
            If `hypotheses` is not a tuple of HypothesisRecord.
            If `conclusion` is not a VariableRecord instance or None.
            If `reasoning` is not a ReasoningResult or None.
        """
        if not isinstance(hypotheses, tuple):
            raise TypeError(f"`hypotheses` should be a tuple, got {type(hypotheses)}")

        for i, hypothesis in enumerate(hypotheses):
            if not isinstance(hypothesis, HypothesisRecord):
                raise TypeError(
                    f"`hypothesis` at index {i} should be a HypothesisRecord, "
                    f"got {type(hypothesis)}"
                )

        if not isinstance(conclusion, VariableRecord | None):
            raise TypeError(
                "`conclusion` should be a VariableRecord or None, "
                f"got {type(conclusion)}"
            )

        if not isinstance(reasoning, ReasoningResult | None):
            raise TypeError(
                "`reasoning` should be a ReasoningResult or None, "
                f"got {type(reasoning)}"
            )
