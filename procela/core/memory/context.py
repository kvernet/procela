"""
Resolution context capturing a single resolution attempt for a variable.

This module defines resolution context used to determine a conclusion
between hypotheses for some specific policy.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/memory/variable/context.html

Examples Reference
------------------
https://procela.org/docs/examples/core/memory/variable/context.html
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ...symbols.key import Key
from ..assessment.reasoning import ReasoningResult
from .candidate import CandidateRecord
from .record import VariableRecord


@dataclass
class ResolutionContext:
    """
    Capture a single resolution context for a variable.

    It contains the epistemic artifacts produced while resolving competing
    hypotheses into a conclusion.

    Attributes
    ----------
    hypotheses : list[CandidateRecord]
        Hypotheses proposed for resolution.
    conclusion : VariableRecord | None
        Resolved value, if resolution succeeded.
    reasoning : ReasoningResult | None
        Explanation of the resolution process.
    policy : Key | None
        Resolution policy responsible for the conclusion.

    Notes
    -----
    ResolutionContext is ephemeral and mutable. It becomes authoritative
    only when committed into variable memory.
    """

    hypotheses: list[CandidateRecord] = field(default_factory=list)
    conclusion: VariableRecord | None = None
    reasoning: ReasoningResult | None = None
    policy: Key | None = None

    _key: Key = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validate a resolution context after initialization.

        Performs type checking on the attributes and generates
        a unique key for the instance.

        Raises
        ------
        TypeError
            If `hypotheses` is not a list of CandidateRecord.
            If `conclusion` is not a VariableRecord instance or None.
            If `reasoning` is not a ReasoningResult or None
            If `policy` is not a Key or None
        """
        if not isinstance(self.hypotheses, list):
            raise TypeError(
                f"`hypotheses` should be a list, got {type(self.hypotheses)}"
            )

        for i, hypothesis in enumerate(self.hypotheses):
            if not isinstance(hypothesis, CandidateRecord):
                raise TypeError(
                    f"`hypothesis` at index {i} should be a CandidateRecord, "
                    f"got {type(hypothesis)}"
                )

        if not isinstance(self.conclusion, VariableRecord | None):
            raise TypeError(
                "`conclusion` should be a VariableRecord or None, "
                f"got {type(self.conclusion)}"
            )

        if not self.in_hypotheses(self.conclusion):
            raise TypeError("`conclusion` should be included in `hypothesis`")

        if not isinstance(self.reasoning, ReasoningResult | None):
            raise TypeError(
                "`reasoning` should be a ReasoningResult or None, "
                f"got {type(self.reasoning)}"
            )

        if not isinstance(self.policy, Key | None):
            raise TypeError(
                f"`policy` should be a Key or None, got {type(self.policy)}"
            )

        from ..key_authority import KeyAuthority

        self._key = KeyAuthority.issue(self)

    def key(self) -> Key:
        """Return the unique identity key of the resolution context."""
        return self._key

    def in_hypotheses(self, record: VariableRecord | None) -> bool:
        """
        Check if a VariableRecord is in the hypotheses.

        Parameters
        ----------
        record : VariableRecord | None
            The variable record to check if in hypotheses.

        Returns
        -------
        bool
            Whether the VariableRecord is in the hypotheses or not.

        Notes
        -----
            When the record is None, the method always returns True.
        """
        if record is None:
            return True
        for hypothesis in self.hypotheses:
            if hypothesis.record is record:
                return True
        return False

    def reset(self) -> None:
        """Reset the resolution context."""
        self.hypotheses.clear()
        self.conclusion = None
        self.reasoning = None
