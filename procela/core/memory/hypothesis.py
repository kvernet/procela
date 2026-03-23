"""
Hypothesis abstraction of a Variable record in Procela.

Examples
--------
>>> from procela import HypothesisRecord, VariableRecord, HypothesisState
>>>
>>> state = HypothesisState.PROPOSED
>>>
>>> hypothesis = HypothesisRecord(
...     VariableRecord(36.87, confidence=0.45),
...     state
... )
>>>
>>> print(hypothesis.key())
<Key>
>>> print(hypothesis.record)
VariableRecord(value=36.87, time=None, source=None, confidence=0.45, ...)

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/memory/variable/hypothesis.html

Examples Reference
------------------
https://procela.org/docs/examples/core/memory/variable/hypothesis.html
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from ...symbols.key import Key
from .record import VariableRecord


class HypothesisState(Enum):
    """
    Enum representing the state of a hypothesis record.

    This enumeration defines the possible lifecycle states for hypothesis
    records within the variable resolution process.

    Attributes
    ----------
    PROPOSED : HypothesisState
        Initial state indicating the hypothesis has been proposed but not
        yet validated.
    VALIDATED : HypothesisState
        State indicating the hypothesis has passed validation checks.
    REJECTED : HypothesisState
        State indicating the hypothesis has been rejected during validation.

    Examples
    --------
    >>> from procela import HypothesisState
    >>>
    >>> state = HypothesisState.PROPOSED
    >>>
    >>> print(state)
    HypothesisState.PROPOSED
    >>> for state in HypothesisState:
        print(state.name, state.value)
    PROPOSED 1
    VALIDATED 2
    REJECTED 3

    Notes
    -----
    The state transitions typically follow the sequence:
    PROPOSED → VALIDATED or REJECTED
    """

    PROPOSED = auto()
    """Initial state indicating the hypothesis has been proposed."""

    VALIDATED = auto()
    """State indicating the hypothesis has passed validation checks."""

    REJECTED = auto()
    """State indicating the hypothesis has been rejected during validation."""


@dataclass
class HypothesisRecord:
    """
    Record representing a hypothesis with its current state.

    A hypothesis record associates a VariableRecord with a HypothesisState,
    tracking its progress through the resolution pipeline.

    Parameters
    ----------
    record : VariableRecord or None
        The associated variable record. Can be None for placeholder or
        rejected hypotheses.
    state : HypothesisState
        The current state of the hypothesis in the resolution process.

    Attributes
    ----------
    record : VariableRecord | None
        The associated variable record (read-only).
    state : HypothesisState
        The current state of the hypothesis.
    _key : Key
        Unique identifier issued by KeyAuthority (auto-generated, read-only).

    Raises
    ------
    TypeError
        If `state` is not a HypothesisState instance.
        If `record` is not a VariableRecord instance or None.

    Examples
    --------
    >>> from procela import HypothesisRecord, VariableRecord, HypothesisState
    >>>
    >>> state = HypothesisState.PROPOSED
    >>>
    >>> hypothesis = HypothesisRecord(
    ...     VariableRecord(36.87, confidence=0.45),
    ...     state
    ... )
    >>>
    >>> print(hypothesis.key())
    <Key>
    >>> print(hypothesis.record)
    VariableRecord(value=36.87, time=None, source=None, confidence=0.45, ...)
    """

    record: VariableRecord | None
    state: HypothesisState = HypothesisState.PROPOSED

    _key: Key = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validate the hypothesis record after initialization.

        Performs type checking on the `state` and `record` attributes
        and generates a unique key for the instance.

        Raises
        ------
        TypeError
            If `state` is not a HypothesisState instance.
            If `record` is not a VariableRecord instance or None.
        """
        if not isinstance(self.state, HypothesisState):
            raise TypeError(f"`state` should be a HypothesisState, got {self.state}")

        if not isinstance(self.record, VariableRecord | None):
            raise TypeError(
                f"`record` should be a VariableRecord or None, got {self.record}"
            )

        from ..key_authority import KeyAuthority

        self._key = KeyAuthority.issue(self)

    def key(self) -> Key:
        """Return the identity key of this hypothesis record."""
        return self._key
