"""
Immutable record of a Variable value in Procela.

Captures a single observation of a Variable, including value,
temporal information, provenance, confidence, and optional explanation.
This forms the atomic unit of Variable memory - each record is a
timestamped, attributed observation that can be reasoned about.

Examples
--------
>>> from procela import VariableRecord
>>>
>>> record = VariableRecord(value=0.45, confidence=0.98, source=None)
>>>
>>> assert record.key() is not None
>>>
>>> print(record.describe())

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/memory/variable/record.html

Examples Reference
------------------
https://procela.org/docs/examples/core/memory/variable/record.html
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ...symbols.key import Key
from ...symbols.time import TimePoint


@dataclass(frozen=True, eq=True)
class VariableRecord:
    """
    Immutable record of a Variable value in Procela.

    Attributes
    ----------
        value: The value held by the Variable (type depends on domain).
        time: Optional TimePoint or temporal indicator associated with
              this record. Enables temporal reasoning and ordering.
        source: Optional Key indicating origin (e.g., producing Variable
                or mechanism). Critical for conflict resolution.
        confidence: Optional confidence score [0, 1] in the validity
                   of this record. Used in weighted decision making.
        metadata: Arbitrary key-value store for additional semantic
                 annotations. Enables extensibility without schema changes.
        explanation: Optional string explaining the rationale or provenance.
                    Supports debugging and transparency.
        _key: Private unique identity token for this record (Key).

    Examples
    --------
    >>> from procela import VariableRecord
    >>>
    >>> record = VariableRecord(value=0.45, confidence=0.98, source=None)
    >>>
    >>> assert record.key() is not None
    >>>
    >>> print(record.describe())
    """

    value: Any = field(compare=False)
    confidence: float | None = None
    source: Key | None = None
    time: TimePoint | None = field(default=None, compare=False)
    explanation: str | None = field(default=None, compare=False)
    metadata: dict[str, Any] = field(default_factory=dict, compare=False)

    _key: Key = field(
        init=False,
        repr=False,
        compare=True,
        hash=True,
    )

    def __post_init__(self) -> None:
        """
        Validate record invariants.

        Ensures confidence values are within valid bounds if provided.

        Raises
        ------
            TypeError: If any type error found
            ValueError: If confidence is provided and not in [0, 1]
        """
        # --- Time ---
        if self.time is not None and not isinstance(self.time, TimePoint):
            raise TypeError("time must be a TimePoint or None")

        # --- Source ---
        if self.source is not None and not isinstance(self.source, Key):
            raise TypeError("source must be a Key or None")

        # --- Confidence ---
        if self.confidence is not None:
            if not isinstance(self.confidence, int | float):
                raise TypeError("confidence must be a float")
            if not 0.0 <= self.confidence <= 1.0:
                raise ValueError(
                    f"Confidence must be between 0 and 1, got {self.confidence}"
                )

        # --- Metadata ---
        if not isinstance(self.metadata, Mapping):
            raise TypeError("metadata must be a mapping")

        # Defensive immutability
        object.__setattr__(self, "metadata", dict(self.metadata))

        from ..key_authority import KeyAuthority

        """Assign a unique identity key issued by KeyAuthority."""
        object.__setattr__(self, "_key", KeyAuthority.issue(self))

    def key(self) -> Key:
        """Return the identity key of this record."""
        return self._key

    def describe(self) -> str:
        """
        Return a human-readable description of this record.

        Returns
        -------
            String representation suitable for debugging and logging.
            Includes all non-None fields in a readable format.

        Note:
            This is distinct from __repr__ which is more terse and
            focuses on identity rather than content.
        """
        parts = [f"key={self._key}", f"value={self.value!r}"]
        if self.time:
            parts.append(f"time={self.time}")
        if self.source:
            parts.append(f"source={self.source}")
        if self.confidence is not None:
            parts.append(f"confidence={self.confidence}")
        if self.metadata:
            parts.append(f"metadata={self.metadata}")
        if self.explanation:
            parts.append(f"explanation={self.explanation!r}")
        return f"VariableRecord({', '.join(parts)})"

    def __repr__(self) -> str:
        """Human-readable representation."""
        return (
            f"VariableRecord("
            f"value={self.value}, "
            f"time={self.time!r}, "
            f"source={self.source}, "
            f"confidence={self.confidence!r}, "
            f"metadata keys={list(self.metadata.keys())}, "
            f"explanation={self.explanation!r})"
        )
