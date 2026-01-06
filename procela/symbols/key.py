"""
Key: Pure identity token for Procela.

Semantics Reference
-------------------
https://procela.org/docs/semantics/symbols/key.html
"""

from __future__ import annotations

import secrets
from typing import Any, NoReturn

from ..core.exceptions import SemanticViolation


class Key:
    """
    Immutable, opaque identity token.

    A Key is a pure identity token that denotes *that an entity is*,
    not *what it is* or *how it relates*. It carries no information
    beyond its identity function.

    Semantics Docs: https://procela.org/docs/semantics/key.html

    Attributes
    ----------
    _token : bytes
        Private 32-byte opaque token. This attribute is private and
        should not be accessed directly by users.

    Example
    -------
        >>> from procela.symbols import Key
        >>>
        >>> k1 = Key()
        >>> k2 = Key()
        >>> k1 == k2
        False
        >>> k3 = Key.from_serialized(k1.to_bytes())
        >>> k1 == k3
        True
    """

    __slots__ = ("_token",)

    def __init__(self) -> None:
        """
        Initialize a new Key.

        The Key is a pure identity token. Internally, it uses a 256-bit
        opaque value to guarantee uniqueness and immutability.

        Users could create Keys via Key(), Key.from_serialized() or generate_key().
        """
        self._token = secrets.token_bytes(32)

    # ---------------------------
    # Equality & Hashing
    # ---------------------------

    def __eq__(self, other: Any) -> bool:
        """
        Check if two Keys refer to the same entity.

        Parameters
        ----------
        other : Any
            Object to compare with.

        Returns
        -------
        bool
            True if `other` is a Key with the same token, False otherwise.
            Returns NotImplemented if `other` is not a Key.

        Notes
        -----
        This implements binary equality per §2.1 of the semantic specification.
        """
        if not isinstance(other, Key):
            return NotImplemented
        return self._token == other._token

    def __hash__(self) -> int:
        """
        Compute hash value for container use.

        Returns
        -------
        int
            Hash based on the internal token.

        Notes
        -----
        This enables Keys to be used as dictionary keys or set elements
        while maintaining consistency with equality.
        """
        return hash(self._token)

    # ---------------------------
    # Representation (fully opaque)
    # ---------------------------

    def __repr__(self) -> str:
        """
        Return opaque string representation.

        Returns
        -------
        str
            Always returns "<Key>" to maintain opaqueness.

        Notes
        -----
        This implements §3.5 (Opaqueness) of the semantic specification.
        The representation reveals no semantic information about the Key.
        """
        return "<Key>"

    # ---------------------------
    # Prohibited mutation
    # ---------------------------

    def __setattr__(self, name: str, value: object) -> None:
        """
        Prohibit mutation of a Key after initialization.

        Parameters
        ----------
        name : str
            Attribute name being assigned.
        value : object
            Value being assigned.

        Returns
        -------
        None

        Raises
        ------
        SemanticViolation
            If an attribute assignment is attempted after the identity
            token has been set.
        """
        if hasattr(self, "_token"):
            raise SemanticViolation("Key is immutable")
        super().__setattr__(name, value)

    # ---------------------------
    # Prohibited ordering
    # ---------------------------

    def __lt__(self, other: Any) -> NoReturn:
        """
        Prohibit less-than comparison.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised, as Keys cannot be ordered.

        Notes
        -----
        Implements §5.5 (No ordering) of the semantic specification.
        """
        raise SemanticViolation("Keys cannot be ordered")

    def __le__(self, other: Any) -> NoReturn:
        """
        Prohibit less-than-or-equal comparison.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised, as Keys cannot be ordered.

        Notes
        -----
        Implements §5.5 (No ordering) of the semantic specification.
        """
        raise SemanticViolation("Keys cannot be ordered")

    def __gt__(self, other: Any) -> NoReturn:
        """
        Prohibit greater-than comparison.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised, as Keys cannot be ordered.

        Notes
        -----
        Implements §5.5 (No ordering) of the semantic specification.
        """
        raise SemanticViolation("Keys cannot be ordered")

    def __ge__(self, other: Any) -> NoReturn:
        """
        Prohibit greater-than-or-equal comparison.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised, as Keys cannot be ordered.

        Notes
        -----
        Implements §5.5 (No ordering) of the semantic specification.
        """
        raise SemanticViolation("Keys cannot be ordered")

    # ---------------------------
    # Prohibited composition
    # ---------------------------

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
            Always raised, as Keys cannot be composed.

        Notes
        -----
        Implements §7.4 (No composition) of the semantic specification.
        """
        raise SemanticViolation("Keys cannot be concatenated or composed")

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
            Always raised, as Keys cannot be composed.

        Notes
        -----
        Implements §7.4 (No composition) of the semantic specification.
        """
        raise SemanticViolation("Keys cannot be concatenated or composed")

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
            Always raised, as Keys cannot be composed.

        Notes
        -----
        Implements §7.4 (No composition) of the semantic specification.
        """
        raise SemanticViolation("Keys cannot be composed")

    def __rmul__(self, other: Any) -> NoReturn:
        """
        Prohibit right multiplication/composition.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised, as Keys cannot be composed.

        Notes
        -----
        Implements §7.4 (No composition) of the semantic specification.
        """
        raise SemanticViolation("Keys cannot be composed")

    def __or__(self, other: Any) -> NoReturn:
        """
        Prohibit union/merge operation.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised, as Keys cannot be unioned.

        Notes
        -----
        Implements §7.4 (No composition) of the semantic specification.
        """
        raise SemanticViolation("Keys cannot be unioned or merged")

    def __and__(self, other: Any) -> NoReturn:
        """
        Prohibit intersection/merge operation.

        Parameters
        ----------
        other : Any
            Any object (ignored).

        Raises
        ------
        SemanticViolation
            Always raised, as Keys cannot be intersected.

        Notes
        -----
        Implements §7.4 (No composition) of the semantic specification.
        """
        raise SemanticViolation("Keys cannot be intersected or merged")

    # ---------------------------
    # Serialization
    # ---------------------------

    def to_bytes(self) -> bytes:
        """
        Serialize Key to opaque bytes for storage or transmission.

        Returns
        -------
        bytes
            32-byte opaque representation of the Key.

        Notes
        -----
        This enables persistence and cross-process communication while
        maintaining the Key's semantic properties. The bytes have no
        meaning outside of serialization/deserialization cycles.
        """
        return self._token

    @classmethod
    def from_serialized(cls, data: bytes) -> Key:
        """
        Create a Key from previously serialized bytes.

        Parameters
        ----------
        data : bytes
            Must be 32 bytes previously generated by `to_bytes()`.

        Returns
        -------
        Key
            Key instance with preserved equality semantics.

        Raises
        ------
        ValueError
            If data is not exactly 32 bytes.

        Notes
        -----
        This method is for deserialization ONLY, not for deriving Keys
        from arbitrary data. It implements §6.4 (Serialization) of the
        semantic specification.
        """
        if len(data) != 32:
            raise ValueError(f"Expected 32 bytes, got {len(data)}")

        # Create without calling __init__ to avoid generating new token
        key = cls.__new__(cls)
        key._token = data
        return key


# ---------------------------
# Helper
# ---------------------------


def generate_key() -> Key:
    """
    Generate a new canonical Key.

    Returns
    -------
    Key
        A new pure identity token with random internal token.

    Notes
    -----
    This is the recommended way to create new Keys when the
    default `Key()` constructor is not sufficient for readability.
    """
    return Key()
