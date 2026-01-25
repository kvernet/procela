"""
Mechanism abstraction for Procela.

This module defines the abstract Mechanism class, which represents a
real-world mechanism that transforms, consumes, and produces variables
under declared constraints. Mechanisms operate within processes and
are coordinated by the executive.

Mechanisms do not resolve conflicts and do not own variables. They
produce candidate values that variables later arbitrate.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/mechanism/base.html

Examples Reference
------------------
https://procela.org/docs/examples/core/mechanism/base.html
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from ...symbols.key import Key
from ..key_authority import KeyAuthority


class Mechanism(ABC):
    """
    Abstract base class for mechanisms.

    A mechanism models a real-world causal transformation that reads
    variables and produces candidate values for other variables.
    Mechanisms are execution units with a declared structural interface.

    Mechanisms may be dynamically enabled or disabled during execution.
    """

    def __init__(self, reads: Sequence[Key], writes: Sequence[Key]) -> None:
        """
        Initialize a mechanism.

        Parameters
        ----------
        reads : Sequence[Key]
            Keys of variables read by the mechanism.
        writes : Sequence[Key]
            Keys of variables written by the mechanism.

        Notes
        -----
        - Declared keys define the complete structural footprint
          of the mechanism.
        - Writing to undeclared keys is structurally invalid.
        """
        if not isinstance(reads, Sequence):
            raise TypeError(f"`reads` should be Sequence, got {reads!r}")
        for i, key in enumerate(reads):
            if not isinstance(key, Key):
                raise TypeError(
                    "`reads` should contain only Key instance, "
                    f"got {key!r} at index {i}"
                )
        if not isinstance(writes, Sequence):
            raise TypeError(f"`writes` should be Sequence, got {writes!r}")
        for i, key in enumerate(writes):
            if not isinstance(key, Key):
                raise TypeError(
                    "`writes` should contain only Key instance, "
                    f"got {key!r} at index {i}"
                )

        self._key: Key = KeyAuthority.issue(self)
        self._reads: tuple[Key, ...] = tuple(reads)
        self._writes: tuple[Key, ...] = tuple(writes)
        self._enabled: bool = True

    def key(self) -> Key:
        """
        Return the unique key of the mechanism.

        Returns
        -------
        Key
            Mechanism key.
        """
        return self._key

    def reads(self) -> Sequence[Key]:
        """
        Return the keys of variables read by the mechanism.

        Returns
        -------
        Sequence[Key]
            Read variable keys.
        """
        return self._reads

    def writes(self) -> Sequence[Key]:
        """
        Return the keys of variables written by the mechanism.

        Returns
        -------
        Sequence[Key]
            Written variable keys.
        """
        return self._writes

    def enable(self) -> None:
        """Enable the mechanism."""
        self._enabled = True

    def disable(self) -> None:
        """Disable the mechanism."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """
        Return whether the mechanism is enabled.

        Returns
        -------
        bool
            Enablement state.
        """
        return self._enabled

    def run(self) -> None:
        """
        Execute the mechanism if enabled.

        Notes
        -----
        - This method is called by the executive.
        - Disabled mechanisms are skipped.
        """
        if not self._enabled:
            return
        self.transform()

    @abstractmethod
    def transform(self) -> None:
        """
        Perform the mechanism transformation.

        Notes
        -----
        - Implementations must only read and write variables
          declared in `reads()` and `writes()`.
        - Conflict resolution is not handled here.
        """
        raise NotImplementedError
