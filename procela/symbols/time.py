"""
TimePoint: Pure temporal identity token for Procela.

This module implements the TimePoint semantic specification:
https://procela.org/docs/semantics/time.html

TimePoint is an immutable identity-based temporal token representing
a declared position in the system's temporal space. All precedence
relationships are managed externally.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, NoReturn

from .key import Key, SemanticViolation


@dataclass(frozen=True, eq=True, repr=False)
class TimePoint:
    """
    Immutable temporal identity token in Procela.

    A TimePoint is a pure wrapper around a Key that represents a
    temporal position. All precedence relationships are managed
    externally.

    Semantic Invariants:
    1. Identity purity: Wraps a Key with no additional state.
    2. Immutability: Cannot be modified after creation.
    3. Opaqueness: No semantic information beyond identity.
    4. No relationships: Knows nothing about temporal precedence.

    Example
    -------
    >>> from procela.symbols import TimePoint
    >>> tp = TimePoint()
    >>> tp.key()
    <Key>
    >>> tp == TimePoint(_key=tp.key())
    True
    """

    _key: Key = field(default_factory=Key, compare=True, hash=True)

    def __post_init__(self) -> None:
        """
        Validate _key is a Key instance or convert from bytes.

        Raises
        ------
        TypeError
            If _key is neither a Key instance nor bytes.
        """
        if not isinstance(self._key, Key):
            if isinstance(self._key, bytes):
                object.__setattr__(self, "_key", Key.from_serialized(self._key))
            else:
                raise TypeError(f"_key must be Key or bytes, got {type(self._key)}")

    def key(self) -> Key:
        """
        Return the immutable identity Key of this TimePoint.

        Returns
        -------
        Key
            Unique identity token representing this TimePoint.
        """
        return self._key

    def __repr__(self) -> str:
        """
        Return opaque string representation for debugging.

        Returns
        -------
        str
            Representation like "TimePoint(...)".
        """
        return f"TimePoint({self._key!r})"

    # -----------------------------------------------------------------
    # Prohibited Operations
    # -----------------------------------------------------------------
    def __lt__(self, other: Any) -> NoReturn:
        """
        Prohibit ordering operation.

        Raises
        ------
        SemanticViolation
            Always raised for < operation.
        """
        raise SemanticViolation("TimePoint cannot be ordered with <")

    def __le__(self, other: Any) -> NoReturn:
        """
        Prohibit ordering operation.

        Raises
        ------
        SemanticViolation
            Always raised for <= operation.
        """
        raise SemanticViolation("TimePoint cannot be ordered with <=")

    def __gt__(self, other: Any) -> NoReturn:
        """
        Prohibit ordering operation.

        Raises
        ------
        SemanticViolation
            Always raised for > operation.
        """
        raise SemanticViolation("TimePoint cannot be ordered with >")

    def __ge__(self, other: Any) -> NoReturn:
        """
        Prohibit ordering operation.

        Raises
        ------
        SemanticViolation
            Always raised for >= operation.
        """
        raise SemanticViolation("TimePoint cannot be ordered with >=")

    def __add__(self, other: Any) -> NoReturn:
        """
        Prohibit addition/concatenation.

        Raises
        ------
        SemanticViolation
            Always raised for + operation.
        """
        raise SemanticViolation("TimePoint cannot be added or concatenated")

    def __radd__(self, other: Any) -> NoReturn:
        """
        Prohibit right addition/concatenation.

        Raises
        ------
        SemanticViolation
            Always raised for + operation.
        """
        raise SemanticViolation("TimePoint cannot be added or concatenated")

    def __sub__(self, other: Any) -> NoReturn:
        """
        Prohibit subtraction/duration calculation.

        Raises
        ------
        SemanticViolation
            Always raised for - operation.
        """
        raise SemanticViolation(
            "TimePoint cannot be subtracted; no duration calculation"
        )

    def __rsub__(self, other: Any) -> NoReturn:
        """
        Prohibit right subtraction.

        Raises
        ------
        SemanticViolation
            Always raised for - operation.
        """
        raise SemanticViolation(
            "TimePoint cannot be subtracted; no duration calculation"
        )

    def __mul__(self, other: Any) -> NoReturn:
        """
        Prohibit multiplication/composition.

        Raises
        ------
        SemanticViolation
            Always raised for * operation.
        """
        raise SemanticViolation("TimePoint cannot be multiplied or composed")

    def __rmul__(self, other: Any) -> NoReturn:
        """
        Prohibit right multiplication.

        Raises
        ------
        SemanticViolation
            Always raised for * operation.
        """
        raise SemanticViolation("TimePoint cannot be multiplied or composed")

    def __or__(self, other: Any) -> NoReturn:
        """
        Prohibit union operation.

        Raises
        ------
        SemanticViolation
            Always raised for | operation.
        """
        raise SemanticViolation("TimePoint cannot be unioned")

    def __and__(self, other: Any) -> NoReturn:
        """
        Prohibit intersection operation.

        Raises
        ------
        SemanticViolation
            Always raised for & operation.
        """
        raise SemanticViolation("TimePoint cannot be intersected")

    # -----------------------------------------------------------------
    # Serialization Support
    # -----------------------------------------------------------------
    def to_bytes(self) -> bytes:
        """
        Serialize TimePoint to bytes (identity only).

        Returns
        -------
        bytes
            Serialized representation containing only the Key.
        """
        return self._key.to_bytes()

    @classmethod
    def from_bytes(cls, data: bytes) -> TimePoint:
        """
        Create TimePoint from serialized bytes.

        Parameters
        ----------
        data : bytes
            Bytes previously generated by `to_bytes()`.

        Returns
        -------
        TimePoint
            New instance with the deserialized Key.

        Raises
        ------
        ValueError
            If data cannot be deserialized to a Key.
        """
        key = Key.from_serialized(data)
        return cls(_key=key)

    @classmethod
    def from_key(cls, key: Key) -> TimePoint:
        """
        Create TimePoint from an existing Key.

        Parameters
        ----------
        key : Key
            Existing Key to wrap as a TimePoint.

        Returns
        -------
        TimePoint
            New instance wrapping the provided Key.
        """
        return cls(_key=key)


# ---------------------------------------------------------------------
# Factory Function
# ---------------------------------------------------------------------
def create_timepoint() -> TimePoint:
    """
    Create a new TimePoint with unique identity.

    Returns
    -------
    TimePoint
        New temporal identity token.

    Example
    -------
    >>> tp = create_timepoint()
    >>> isinstance(tp, TimePoint)
    True
    >>> isinstance(tp.key(), Key)
    True
    """
    return TimePoint()
