"""
Executive execution authority for Procela.

This module defines the Executive class, which owns world execution,
coordinates processes, enforces step boundaries, and ensures that
variable conflict resolution occurs consistently across the system.

The executive represents the runtime world instance of a Procela model.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/executive/base.html

Examples Reference
------------------
https://procela.org/docs/examples/core/executive/base.html
"""

from __future__ import annotations

from typing import Sequence

from ...symbols.key import Key
from ..epistemic.executive import ExecutiveView
from ..exceptions import ExecutionError
from ..key_authority import KeyAuthority
from ..process.base import Process
from ..variable.variable import Variable


class Executive:
    """
    World execution authority.

    The executive coordinates process execution, enforces step-level
    consistency, and ensures that variable conflict resolution occurs
    exactly once per variable per step. It does not resolve conflicts
    itself but orchestrates when variables must do so.
    """

    def __init__(self, processes: Sequence[Process]) -> None:
        """
        Initialize the executive.

        Parameters
        ----------
        processes : Sequence[Process]
            Processes participating in the world.

        Notes
        -----
        - The executive owns execution order and step boundaries.
        - Variables own conflict resolution logic.
        """
        self._key = KeyAuthority.issue(self)
        self._processes: tuple[Process, ...] = tuple(processes)
        self._writable_keys: set[Key] = set()
        self._all_keys: set[Key] = set()
        self._prepared: bool = False
        self._step_index: int = 0

    def prepare(self) -> None:
        """
        Prepare the executive for execution.

        Notes
        -----
        - Collects unique writable variable keys.
        - Collects all variable keys touched by the system.
        - Must be called once before stepping.
        """
        self._writable_keys.clear()
        self._all_keys.clear()

        for process in self._processes:
            self._writable_keys.update(process.writable_keys())
            self._all_keys.update(process.all_keys())

        self._prepared = True

    def step(self) -> None:
        """
        Execute one world step.

        Execution consists of three strictly ordered phases:

        1. Process execution where conflicts are collected
        3. Conflict resolution and commitment

        Raises
        ------
        RuntimeError
            If the executive has not been prepared.

        Notes
        -----
        - All processes are executed before any conflict resolution.
        - Each variable is resolved and committed at most once.
        - Variables without candidates are skipped.
        """
        if not self._prepared:
            raise ExecutionError("Executive must be prepared before execution.")

        # Phase 1: execute processes
        for process in self._processes:
            process.step()

        # Phase 2: resolve conflicts per writable variable
        for key in self.writable_keys():
            variable = KeyAuthority.resolve(key)
            if variable is None:
                continue
            if not isinstance(variable, Variable):
                raise TypeError(f"Expected `Variable`, got {variable!r}")

            candidates = variable.candidates()
            if not candidates:
                continue

            policy = variable.policy()
            validators = variable.validators()

            resolved = variable.resolve_conflict(
                candidates=candidates,
                policy=policy,
                validators=validators,
            )
            variable.commit(resolved)

        # Increment step index
        self._step_index += 1

    def key(self) -> Key:
        """
        Return the unique identify of the executive.

        Returns
        -------
        Key
            The unique identify of the executive.
        """
        return self._key

    def processes(self) -> Sequence[Process]:
        """
        Return the processes owned by the executive.

        Returns
        -------
        Sequence[Process]
            The processes owned by the executive.
        """
        return self._processes

    def writable_keys(self) -> set[Key]:
        """
        Return all writable variable keys in the world.

        Returns
        -------
        set[Key]
            Writable variable keys.
        """
        return self._writable_keys

    def all_keys(self) -> set[Key]:
        """
        Return all variable keys involved in the world.

        Returns
        -------
        set[Key]
            All variable keys.
        """
        return self._all_keys

    def reset(self) -> None:
        """
        Reset the world state.

        This method resets all variables involved in the world to an
        initial state by clearing their histories and pending candidates.

        Notes
        -----
        - Variable keys and configurations are preserved.
        - Processes and mechanisms are not modified.
        - This represents the creation of a new world instance
          over the same structure.
        """
        for key in self.all_keys():
            variable = KeyAuthority.resolve(key)
            if isinstance(variable, Variable):
                variable.reset()

    def snapshot(self) -> ExecutiveView:
        """
        Capture a read-only epistemic snapshot of the current Executive state.

        This method returns an `ExecutiveView` representing the state of the
        system at the current step. The snapshot includes the Executive's unique
        key, the current step index, and the keys of all processes managed by
        the Executive. It provides a safe, read-only view suitable for
        analysis, logging, or reasoning without mutating the world state.

        Returns
        -------
        ExecutiveView
            An immutable view of the Executive-managed world at the current step,
            including process keys and metadata.
        """
        return ExecutiveView(
            key=self._key,
            step=self._step_index,
            process_keys=tuple(p.key() for p in self._processes),
        )
