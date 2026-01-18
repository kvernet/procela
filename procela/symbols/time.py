"""
TimePoint: Pure temporal identity token for Procela.

TimePoint is an immutable identity-based temporal token representing
a declared position in the system's temporal space. All precedence
relationships are managed externally.

Semantics Reference
-------------------
https://procela.org/docs/semantics/symbols/time.html

Examples Reference
------------------
https://procela.org/docs/examples/symbols/time.html
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, NoReturn

from ..core.exceptions import SemanticViolation
from .key import Key


@dataclass(frozen=True, eq=True, repr=False)
class TimePoint:
    """
    Immutable temporal identity token in Procela.

    A TimePoint is a pure wrapper around a Key that represents a
    temporal position. All precedence relationships are managed
    externally.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/symbols/time.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/symbols/time.html
    """

    _key: Key = field(
        init=False,
        repr=False,
        compare=True,
        hash=True,
    )

    def __post_init__(self) -> None:
        """Assign a unique identity key issued by KeyAuthority."""
        from ..core.key_authority import KeyAuthority

        object.__setattr__(self, "_key", KeyAuthority.issue(self))

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

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised for < operation.
        """
        raise SemanticViolation("TimePoint cannot be ordered with <")

    def __le__(self, other: Any) -> NoReturn:
        """
        Prohibit ordering operation.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised for <= operation.
        """
        raise SemanticViolation("TimePoint cannot be ordered with <=")

    def __gt__(self, other: Any) -> NoReturn:
        """
        Prohibit ordering operation.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised for > operation.
        """
        raise SemanticViolation("TimePoint cannot be ordered with >")

    def __ge__(self, other: Any) -> NoReturn:
        """
        Prohibit ordering operation.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised for >= operation.
        """
        raise SemanticViolation("TimePoint cannot be ordered with >=")

    def __add__(self, other: Any) -> NoReturn:
        """
        Prohibit addition/concatenation.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised for + operation.
        """
        raise SemanticViolation("TimePoint cannot be added or concatenated")

    def __radd__(self, other: Any) -> NoReturn:
        """
        Prohibit right addition/concatenation.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised for + operation.
        """
        raise SemanticViolation("TimePoint cannot be added or concatenated")

    def __sub__(self, other: Any) -> NoReturn:
        """
        Prohibit subtraction/duration calculation.

        Parameters
        ----------
        other : Any
            Any object (ignored).

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

        Parameters
        ----------
        other : Any
            Any object (ignored).

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

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised for * operation.
        """
        raise SemanticViolation("TimePoint cannot be multiplied or composed")

    def __rmul__(self, other: Any) -> NoReturn:
        """
        Prohibit right multiplication.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised for * operation.
        """
        raise SemanticViolation("TimePoint cannot be multiplied or composed")

    def __or__(self, other: Any) -> NoReturn:
        """
        Prohibit union operation.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised for | operation.
        """
        raise SemanticViolation("TimePoint cannot be unioned")

    def __and__(self, other: Any) -> NoReturn:
        """
        Prohibit intersection operation.

        Parameters
        ----------
        other : Any
            Any object (ignored).

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
    """
    return TimePoint()
