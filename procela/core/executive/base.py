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

from typing import Callable, Sequence

from ...symbols.key import Key
from ..exceptions import ExecutionError
from ..execution import ExecutionStepTrace, ExecutionTrace
from ..invariant.exceptions import (
    InvariantViolation,
    InvariantViolationCritical,
    InvariantViolationFatal,
    InvariantViolationInfo,
    InvariantViolationWarning,
)
from ..invariant.phase import InvariantPhase
from ..invariant.snapshot import VariableSnapshot
from ..invariant.system import SystemInvariant
from ..key_authority import KeyAuthority
from ..mechanism.base import Mechanism
from ..memory.variable.record import VariableRecord
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

    def __init__(
        self, processes: Sequence[Process] = [], mechanisms: Sequence[Mechanism] = []
    ) -> None:
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
        self._processes: list[Process] = list(processes)
        self._mechanisms: list[Mechanism] = list(mechanisms)
        self._writable: set[Variable] = set()
        self._variables: set[Variable] = set()
        self._prepared: bool = False
        self._invariants: list[SystemInvariant] = []
        self._execution_trace = ExecutionTrace()
        self._step_index: int = 0
        self.prepare()

    def add_process(self, process: Process) -> None:
        """
        Add a process to the Execution.

        Parameters
        ----------
        process : Process
            The process to be added.
        """
        self._processes.append(process)
        self.prepare()

    def remove_process(self, process: Process) -> None:
        """
        Remove completely a process from the Execution.

        Parameters
        ----------
        process : Process
            The process to be removed.

        Notes
        -----
        Removing a process is different from disabling it.
        Remove means: doesn't exist in the list of registered processes.
        Enabling it again has no effect on the execution unless properly
        added again.
        """
        self._processes = [proc for proc in self._processes if proc != process]
        self.prepare()

    def add_mechanism(self, mechanism: Mechanism) -> None:
        """
        Add a mechanism to the Execution.

        Parameters
        ----------
        mechanism : Mechanism
            The mechanism to be added.
        """
        self._mechanisms.append(mechanism)
        self.prepare()

    def remove_mechanism(self, mechanism: Mechanism) -> None:
        """
        Remove completely a mechanism from the Execution.

        Parameters
        ----------
        mechanism : Mechanism
            The mechanism to be removed.

        Notes
        -----
        Removing a mechanism is different from disabling it.
        Remove means: doesn't exist in the list of registered mechanisms.
        Enabling it again has no effect on the execution unless properly
        added again.
        """
        self._mechanisms = [mech for mech in self._mechanisms if mech != mechanism]
        self.prepare()

    def prepare(self) -> None:
        """
        Prepare the executive for execution.

        Notes
        -----
        - Collects unique writable variables.
        - Collects all variables touched by the system.
        - Must be called once before stepping.
        """
        self._writable.clear()
        self._variables.clear()

        for process in self._processes:
            self._writable.update(process.writable())
            self._variables.update(process.variables())
        for mechanism in self._mechanisms:
            self._writable.update(mechanism.writes())
            self._variables.update(mechanism.reads())
            self._variables.update(mechanism.writes())

        self._prepared = True

    def step(self) -> None:
        """
        Execute one step.

        Execution consists of three strictly ordered phases:

        1. Process execution where conflicts are collected
        2. Conflict resolution and commitment
        3. Check runtime invariants

        Raises
        ------
        RuntimeError
            If the executive has not been prepared.

        Warnings
        --------
        - Only runtime invariants are checked.
        - To check pre/post invariants, they should be called.
        - Alternatively, use run(). It forces pre/post invariants.

        Notes
        -----
        - All processes are executed before any conflict resolution.
        - Each variable is resolved and committed at most once.
        - Variables without candidates are skipped.
        """
        if not self._prepared:
            raise ExecutionError("Executive must be prepared before execution.")

        # Increment step index
        self._step_index += 1

        proposed: dict[Key, list[VariableRecord]] = {}
        validated: dict[Key, list[VariableRecord]] = {}
        resolved: dict[Key, VariableRecord | None] = {}
        proposing_mechanisms: dict[Key, set[Key | None]] = {}

        # Phase 1: execute processes and mechanisms
        for process in self._processes:
            process.step()
        for mechanism in self._mechanisms:
            mechanism.run()

        # Phase 2: resolve conflicts per writable variable
        for variable in self.writable():
            if variable is None:
                continue
            if not isinstance(variable, Variable):
                raise TypeError(f"Expected `Variable`, got {variable!r}")

            key = variable.key()
            candidates = variable.candidates()
            if not candidates:
                continue

            # Save proposed candidates per variable
            proposed[key] = list(candidates)
            # Save proposing mechanisms
            for cand in candidates:
                proposing_mechanisms.setdefault(key, set()).add(cand.source)

            policy = variable.policy()
            validators = variable.validators()

            # Variable is resolving conflicts
            rd, vd = variable.resolve_conflict(
                candidates=candidates,
                policy=policy,
                validators=validators,
            )

            # Save validated and resolved candidates
            validated[key] = vd
            resolved[key] = rd

            # Commit resolved candidate
            variable.commit(rd)

            # Clear candidates
            variable.clear_candidates()

        # Finalize trace
        self._execution_trace.append(
            ExecutionStepTrace(
                step=self._step_index,
                proposed=proposed,
                validated=validated,
                resolved=resolved,
                proposing_mechanisms={
                    k: tuple(v) for k, v in proposing_mechanisms.items()
                },
            )
        )
        # Check invariants
        self._check_invariants(InvariantPhase.RUNTIME)

    def run(
        self, steps: int, on_step: Callable[[Executive, int], None] | None = None
    ) -> None:
        """
        Execute all the steps by allowing an optional callable at each step.

        Execution consists of two strictly ordered phases:

        1. Check pre invariants before stepping
        2. Process execution where conflicts are collected by calling
           the optionally on_step() function provided by users.
           Conflict resolution and commitment
        3. Check the post invariants

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

        self._check_invariants(InvariantPhase.PRE)

        for i in range(steps):
            self.step()
            if on_step is not None:
                on_step(self, i)

        self._check_invariants(InvariantPhase.POST)

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

    def mechanisms(self) -> Sequence[Mechanism]:
        """
        Return the mechanisms owned by the executive.

        Returns
        -------
        Sequence[Mechanism]
            The mechanisms owned by the executive.
        """
        return self._mechanisms

    def writable(self) -> set[Variable]:
        """
        Return all writable variables in the world.

        Returns
        -------
        set[Variable]
            Writable variables in the world.
        """
        return self._writable

    def variables(self) -> set[Variable]:
        """
        Return all variables involved in the world.

        Returns
        -------
        set[Variable]
            All variables involved in the world.
        """
        return self._variables

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
        for variable in self.variables():
            if isinstance(variable, Variable):
                variable.reset()

        self._step_index = 0

    def snapshot(self) -> VariableSnapshot:
        """
        Capture a read-only epistemic snapshot of the variables.

        This method returns a `VariableSnapshot` representing the
        epistemic views of the variables at the current step.
        It provides a safe, read-only views suitable for
        analysis, logging, or reasoning without mutating the execution.

        Returns
        -------
        VariableSnapshot
            An immutable snapshot of the variables at the current step.
        """
        return VariableSnapshot.from_views(
            views=[v.epistemic() for v in self.variables()]
        )

    def add_invariant(self, invariant: SystemInvariant) -> None:
        """
        Add invariant at execution level.

        Parameters
        ----------
        invariant : SystemInvariant
            The system invariant to add.
        """
        self._invariants.append(invariant)

    @property
    def execution_trace(self) -> ExecutionTrace:
        """
        Access execution trace history.

        Returns
        -------
        ExecutionTrace
            The execution trace.
        """
        return self._execution_trace

    def safe_mode(self, invariant: SystemInvariant) -> None:
        """
        Enter the safe mode.

        Parameters
        ----------
        invariant : SystemInvariant
            The invariant violation that causes execution to enter safe mode.

        Notes
        -----
        Not implemented yet.
        """
        ...

    def abort(self, invariant: SystemInvariant) -> None:
        """
        Abort the execution.

        Parameters
        ----------
        invariant : SystemInvariant
            The invariant violation that aborts the execution.
        """
        raise InvariantViolationFatal(
            invariant.name,
            invariant.message,
            category=invariant.category,
            phase=invariant.phase,
        )

    def _check_invariants(self, phase: InvariantPhase) -> None:
        """
        Check the invariants.

        Parameters
        ----------
        phase : InvariantPhase
            The phase to check the invariants.
        """
        if not self._invariants:
            return

        snapshot = self.snapshot()

        for inv in self._invariants:
            if inv.phase == phase:
                try:
                    inv.check(snapshot)
                except InvariantViolationInfo:
                    ...
                    # logger.info(...)
                except InvariantViolationWarning:
                    ...
                    # logger.warn(...)
                except InvariantViolationCritical:
                    self.safe_mode(inv)
                except InvariantViolationFatal:
                    self.abort(inv)
                except InvariantViolation:
                    raise InvariantViolation(
                        inv.name,
                        inv.message,
                        category=inv.category,
                        severity=inv.severity,
                        phase=inv.phase,
                    )
                except Exception as exec:
                    raise ExecutionError(
                        "Invariant raised an unexpected error:"
                    ) from exec
