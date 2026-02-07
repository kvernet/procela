"""
Candidate abstraction of a Variable record in Procela.

Captures a Variable candidate during resolution context, including
the candidate state and variable record.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/memory/variable/candidate.html

Examples Reference
------------------
https://procela.org/docs/examples/core/memory/variable/candidate.html
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from ...symbols.key import Key
from .record import VariableRecord


class CandidateState(Enum):
    """
    Enum representing the state of a candidate record.

    This enumeration defines the possible lifecycle states for candidate
    records within the variable resolution process.

    Attributes
    ----------
    PROPOSED : CandidateState
        Initial state indicating the candidate has been proposed but not
        yet validated.
    VALIDATED : CandidateState
        State indicating the candidate has passed validation checks.
    REJECTED : CandidateState
        State indicating the candidate has been rejected during validation.

    Notes
    -----
    The state transitions typically follow the sequence:
    PROPOSED → VALIDATED or REJECTED
    """

    PROPOSED = auto()
    """Initial state indicating the candidate has been proposed."""

    VALIDATED = auto()
    """State indicating the candidate has passed validation checks."""

    REJECTED = auto()
    """State indicating the candidate has been rejected during validation."""


@dataclass
class CandidateRecord:
    """
    Record representing a candidate with its current state.

    A candidate record associates a VariableRecord with a CandidateState,
    tracking its progress through the resolution pipeline.

    Parameters
    ----------
    record : VariableRecord or None
        The associated variable record. Can be None for placeholder or
        rejected candidates.
    state : CandidateState
        The current state of the candidate in the resolution process.

    Attributes
    ----------
    record : VariableRecord | None
        The associated variable record (read-only).
    state : CandidateState
        The current state of the candidate.
    _key : Key
        Unique identifier issued by KeyAuthority (auto-generated, read-only).

    Raises
    ------
    TypeError
        If `state` is not a CandidateState instance.
        If `record` is not a VariableRecord instance or None.
    """

    record: VariableRecord | None
    state: CandidateState = CandidateState.PROPOSED

    _key: Key = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validate the candidate record after initialization.

        Performs type checking on the `state` and `record` attributes
        and generates a unique key for the instance.

        Raises
        ------
        TypeError
            If `state` is not a CandidateState instance.
            If `record` is not a VariableRecord instance or None.
        """
        if not isinstance(self.state, CandidateState):
            raise TypeError(f"`state` should be a CandidateState, got {self.state}")

        if not isinstance(self.record, VariableRecord | None):
            raise TypeError(
                f"`record` should be a VariableRecord or None, got {self.record}"
            )

        from ..key_authority import KeyAuthority

        self._key = KeyAuthority.issue(self)

    def key(self) -> Key:
        """Return the identity key of this candidate record."""
        return self._key
