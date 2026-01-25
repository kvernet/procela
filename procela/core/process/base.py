"""
Process abstraction for Procela.

This module defines the Process class, which groups mechanisms into
coherent execution units. A process represents a logical subsystem
of a real-world model and defines execution scope without owning state.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/process/base.html

Examples Reference
------------------
https://procela.org/docs/examples/core/process/base.html
"""

from __future__ import annotations

from typing import Sequence

from ...symbols.key import Key
from ..key_authority import KeyAuthority
from ..mechanism.base import Mechanism


class Process:
    """
    Execution container for mechanisms.

    A process groups mechanisms that participate in a common execution
    context. Processes do not store variables, resolve conflicts.
    """

    def __init__(self, mechanisms: Sequence[Mechanism]) -> None:
        """
        Initialize a process.

        Parameters
        ----------
        mechanisms : Sequence[Mechanism]
            Mechanisms composing the process.

        Notes
        -----
        - Mechanisms are executed in the order provided.
        - Processes may be dynamically enabled or disabled.
        """
        self._key = KeyAuthority.issue(self)
        self._mechanisms: tuple[Mechanism, ...] = tuple(mechanisms)
        self._enabled: bool = True

    def key(self) -> Key:
        """
        Return the unique identity of the process.

        Returns
        -------
        Key
            The unique identity of the process.
        """
        return self._key

    def mechanisms(self) -> Sequence[Mechanism]:
        """
        Return mechanisms in the process.

        Returns
        -------
        Sequence[Mechanism]
            Process mechanisms.
        """
        return self._mechanisms

    def enable(self) -> None:
        """
        Enable the process for execution.

        Notes
        -----
        Enabling a process does not enable or disable individual mechanisms.
        """
        self._enabled = True

    def disable(self) -> None:
        """
        Disable the process for execution.

        Notes
        -----
        Disabled processes are skipped entirely during execution.
        """
        self._enabled = False

    def is_enabled(self) -> bool:
        """
        Return whether the process is enabled.

        Returns
        -------
        bool
            Enablement state.
        """
        return self._enabled

    def step(self) -> None:
        """
        Execute all enabled mechanisms in the process.

        Notes
        -----
        - Disabled processes are skipped.
        - Mechanisms are executed sequentially. This method
        does not resolve conflicts or commit variable state.
        """
        if not self._enabled:
            return

        for mechanism in self._mechanisms:
            mechanism.run()

    def writable_keys(self) -> set[Key]:
        """
        Return keys of variables written by the process.

        Returns
        -------
        set[Key]
            Writable variable keys.
        """
        keys: set[Key] = set()
        for mechanism in self._mechanisms:
            keys.update(mechanism.writes())
        return keys

    def all_keys(self) -> set[Key]:
        """
        Return all variable keys touched by the process.

        Returns
        -------
        set[Key]
            Read and written variable keys.
        """
        keys: set[Key] = set()
        for mechanism in self._mechanisms:
            keys.update(mechanism.reads())
            keys.update(mechanism.writes())
        return keys
