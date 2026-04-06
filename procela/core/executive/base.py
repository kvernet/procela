"""
Executive execution authority for Procela.

This module defines the Executive class, which owns world execution,
coordinates processes, enforces step boundaries, and ensures that
variable conflict resolution occurs consistently across the system.

The executive represents the runtime world instance of a Procela model.

Examples
--------
>>> import random
>>>
>>> from procela import (
...     Executive,
...     Mechanism,
...     Variable,
...     RangeDomain,
...     VariableRecord,
...     WeightedVotingPolicy,
...     HighestConfidencePolicy,
...     SystemInvariant,
...     InvariantPhase,
...     VariableSnapshot,
...     InvariantViolation
... )
>>>
>>> random.seed(42)
>>>
>>> X = Variable("X", RangeDomain(-100., 100.), policy=WeightedVotingPolicy())
>>> Y = Variable("Y", RangeDomain(-100., 100.), policy=WeightedVotingPolicy())
>>> Z = Variable("Z", RangeDomain(-100., 100.), policy=WeightedVotingPolicy())
>>>
>>> def init_variables():
...     X.init(VariableRecord(1.8, confidence=1.0))
...     Y.init(VariableRecord(-0.5, confidence=1.0))
...     Z.init(VariableRecord(9.2, confidence=1.0))
>>>
>>> class AddMechanism(Mechanism):
...     def __init__(self, reads, writes):
...         super().__init__(reads, writes)
...
...     def transform(self):
...         i1, i2 = [var.value for var in self.reads()]
...         self.writes()[0].add_hypothesis(VariableRecord(
...             i1 + i2, confidence=random.uniform(0., 1.), source=self.key()
...         ))
>>>
>>> class DivideBy2Mechanism(Mechanism):
...     def __init__(self, reads, writes):
...         super().__init__(reads, writes)
...
...     def transform(self):
...         for var in self.writes():
...             var.add_hypothesis(VariableRecord(
...                 var.value*0.5,
...                 confidence=random.uniform(0., 1.),
...                 source=self.key()
...             ))
>>>
>>> class EmergencyMechanism(Mechanism):
...     def __init__(self, reads, writes):
...         super().__init__(reads, writes)
...
...     def transform(self):
...         for var in self.writes():
...             var.add_hypothesis(VariableRecord(
...                 var.value*0.3, confidence=1.0, source=self.key()
...             ))
>>>
>>> emergencyMech = EmergencyMechanism([], [X, Y, Z])
>>>
>>> executive = Executive(mechanisms=[
...     AddMechanism([X, Y], [Z]),
...     AddMechanism([X, Z], [Y]),
...     AddMechanism([Y, Z], [X]),
...     DivideBy2Mechanism([], [X, Y, Z])
... ])
>>>
>>> class SafetyInvariant(SystemInvariant):
...     def __init__(self, threshold: float = 75.0):
...         self.threshold = threshold
...         self.added = False
...
...         def check_condition(snapshot: VariableSnapshot):
...             for view in snapshot.views:
...                 if view.stats.mean > self.threshold:
...                     return False
...             return True
...
...         def handle_violation(
...             invariant: InvariantViolation, snapshot: VariableSnapshot
...         ):
...             if not self.added:
...                 executive.add_mechanism(emergencyMech)
...                 for var in [X, Y, Z]:
...                     var.policy = HighestConfidencePolicy()
...                 self.added = True
...
...         super().__init__(
...             "SafetyInvariant",
...             condition=check_condition,
...             on_violation=handle_violation,
...             phase=InvariantPhase.RUNTIME,
...             message=""
...         )
>>>
>>> executive.add_invariant(
...     SafetyInvariant(threshold=700000.0)
... )
>>>
>>> def pre_step(executive: Executive, step: int):
...     for mech in executive.mechanisms():
...         if mech == emergencyMech:
...             print(f"Step {step}: Mechanism has been added.")
...
...     if step == 80:
...         executive.remove_mechanism(emergencyMech)
>>>
# Simulation
>>> init_variables()
>>> executive.run(steps=100, pre_step=pre_step, post_step=None)
>>>
>>> for var in [X, Y, Z]:
...     _, conclusion, _ = var.memory.latest()
...     print(var.name, var.value, var.confidence)
Step 68: Mechanism has been added.
Step 69: Mechanism has been added.
Step 70: Mechanism has been added.
Step 71: Mechanism has been added.
Step 72: Mechanism has been added.
Step 73: Mechanism has been added.
Step 74: Mechanism has been added.
Step 75: Mechanism has been added.
Step 76: Mechanism has been added.
Step 77: Mechanism has been added.
Step 78: Mechanism has been added.
Step 79: Mechanism has been added.
Step 80: Mechanism has been added.
X 35.499546845738266 0.6239227647681721
Y 95.6222768274126 0.5870536688252231
Z 12.311591567968035 0.6060587403984868

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/executive/base.html

Examples Reference
------------------
https://procela.org/docs/examples/core/executive/base.html
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from typing import Any, Callable, Sequence

import numpy as np

from ...symbols.key import Key
from ..exceptions import ExecutionError
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
from ..logger import setup_logging
from ..mechanism.base import Mechanism
from ..process.base import Process
from ..variable.variable import Variable


@dataclass
class ExecutiveCheckPoint:
    """Executive checkpoint data."""

    processes: list[Process]
    mechanisms: list[Mechanism]
    mechanism_points: dict[Mechanism, Any]
    variables: set[Variable]
    variable_points: dict[Variable, Any]
    invariants: list[SystemInvariant]
    invariant_points: dict[SystemInvariant, Any]
    rng: random.Random | np.random.Generator | None
    step: int
    logger: logging.Logger
    n_steps: int


class Executive:
    """
    World execution authority.

    The executive coordinates process execution, enforces step-level
    consistency, and ensures that variable conflict resolution occurs
    exactly once per variable per step. It does not resolve conflicts
    itself but orchestrates when variables must do so.

    Examples
    --------
    >>> import random
    >>>
    >>> from procela import (
    ...     Executive,
    ...     Mechanism,
    ...     Variable,
    ...     RangeDomain,
    ...     VariableRecord,
    ...     WeightedVotingPolicy,
    ...     HighestConfidencePolicy,
    ...     SystemInvariant,
    ...     InvariantPhase,
    ...     VariableSnapshot,
    ...     InvariantViolation
    ... )
    >>>
    >>> random.seed(42)
    >>>
    >>> X = Variable("X", RangeDomain(-100., 100.), policy=WeightedVotingPolicy())
    >>> Y = Variable("Y", RangeDomain(-100., 100.), policy=WeightedVotingPolicy())
    >>> Z = Variable("Z", RangeDomain(-100., 100.), policy=WeightedVotingPolicy())
    >>>
    >>> def init_variables():
    ...     X.init(VariableRecord(1.8, confidence=1.0))
    ...     Y.init(VariableRecord(-0.5, confidence=1.0))
    ...     Z.init(VariableRecord(9.2, confidence=1.0))
    >>>
    >>> class AddMechanism(Mechanism):
    ...     def __init__(self, reads, writes):
    ...         super().__init__(reads, writes)
    ...
    ...     def transform(self):
    ...         i1, i2 = [var.value for var in self.reads()]
    ...         self.writes()[0].add_hypothesis(VariableRecord(
    ...             i1 + i2, confidence=random.uniform(0., 1.), source=self.key()
    ...         ))
    >>>
    >>> class DivideBy2Mechanism(Mechanism):
    ...     def __init__(self, reads, writes):
    ...         super().__init__(reads, writes)
    ...
    ...     def transform(self):
    ...         for var in self.writes():
    ...             var.add_hypothesis(VariableRecord(
    ...                 var.value*0.5,
    ...                 confidence=random.uniform(0., 1.),
    ...                 source=self.key()
    ...             ))
    >>>
    >>> class EmergencyMechanism(Mechanism):
    ...     def __init__(self, reads, writes):
    ...         super().__init__(reads, writes)
    ...
    ...     def transform(self):
    ...         for var in self.writes():
    ...             var.add_hypothesis(VariableRecord(
    ...                 var.value*0.3, confidence=1.0, source=self.key()
    ...             ))
    >>>
    >>> emergencyMech = EmergencyMechanism([], [X, Y, Z])
    >>>
    >>> executive = Executive(mechanisms=[
    ...     AddMechanism([X, Y], [Z]),
    ...     AddMechanism([X, Z], [Y]),
    ...     AddMechanism([Y, Z], [X]),
    ...     DivideBy2Mechanism([], [X, Y, Z])
    ... ])
    >>>
    >>> class SafetyInvariant(SystemInvariant):
    ...     def __init__(self, threshold: float = 75.0):
    ...         self.threshold = threshold
    ...         self.added = False
    ...
    ...         def check_condition(snapshot: VariableSnapshot):
    ...             for view in snapshot.views:
    ...                 if view.stats.mean > self.threshold:
    ...                     return False
    ...             return True
    ...
    ...         def handle_violation(
    ...             invariant: InvariantViolation, snapshot: VariableSnapshot
    ...         ):
    ...             if not self.added:
    ...                 executive.add_mechanism(emergencyMech)
    ...                 for var in [X, Y, Z]:
    ...                     var.policy = HighestConfidencePolicy()
    ...                 self.added = True
    ...
    ...         super().__init__(
    ...             "SafetyInvariant",
    ...             condition=check_condition,
    ...             on_violation=handle_violation,
    ...             phase=InvariantPhase.RUNTIME,
    ...             message=""
    ...         )
    >>>
    >>> executive.add_invariant(
    ...     SafetyInvariant(threshold=700000.0)
    ... )
    >>>
    >>> def pre_step(executive: Executive, step: int):
    ...     for mech in executive.mechanisms():
    ...         if mech == emergencyMech:
    ...             print(f"Step {step}: Mechanism has been added.")
    ...
    ...     if step == 80:
    ...         executive.remove_mechanism(emergencyMech)
    >>>
    # Simulation
    >>> init_variables()
    >>> executive.run(steps=100, pre_step=pre_step, post_step=None)
    >>>
    >>> for var in [X, Y, Z]:
    ...     _, conclusion, _ = var.memory.latest()
    ...     print(var.name, var.value, var.confidence)
    Step 68: Mechanism has been added.
    Step 69: Mechanism has been added.
    Step 70: Mechanism has been added.
    Step 71: Mechanism has been added.
    Step 72: Mechanism has been added.
    Step 73: Mechanism has been added.
    Step 74: Mechanism has been added.
    Step 75: Mechanism has been added.
    Step 76: Mechanism has been added.
    Step 77: Mechanism has been added.
    Step 78: Mechanism has been added.
    Step 79: Mechanism has been added.
    Step 80: Mechanism has been added.
    X 35.499546845738266 0.6239227647681721
    Y 95.6222768274126 0.5870536688252231
    Z 12.311591567968035 0.6060587403984868
    """

    def __init__(
        self,
        *,
        processes: Sequence[Process] = [],
        mechanisms: Sequence[Mechanism] = [],
        rng: random.Random | np.random.Generator | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Initialize the executive.

        Parameters
        ----------
        processes : Sequence[Process]
            Processes participating in the world.
        mechanisms : Sequence[Mechanism]
            Mechanisms participating in the world.
        rng : random.Random | np.random.Generator | None = None
            Random Number Generator to use.
        logger : logging.Logger | None
            Logger to use.

        Examples
        --------
        >>> import random
        >>>
        >>> from procela import (
        ...     Executive,
        ...     Mechanism,
        ...     Variable,
        ...     RangeDomain,
        ...     VariableRecord,
        ...     WeightedVotingPolicy,
        ...     HighestConfidencePolicy,
        ...     SystemInvariant,
        ...     InvariantPhase,
        ...     VariableSnapshot,
        ...     InvariantViolation
        ... )
        >>>
        >>> random.seed(42)
        >>>
        >>> X = Variable("X", RangeDomain(-100., 100.), policy=WeightedVotingPolicy())
        >>> Y = Variable("Y", RangeDomain(-100., 100.), policy=WeightedVotingPolicy())
        >>> Z = Variable("Z", RangeDomain(-100., 100.), policy=WeightedVotingPolicy())
        >>>
        >>> def init_variables():
        ...     X.init(VariableRecord(1.8, confidence=1.0))
        ...     Y.init(VariableRecord(-0.5, confidence=1.0))
        ...     Z.init(VariableRecord(9.2, confidence=1.0))
        >>>
        >>> class AddMechanism(Mechanism):
        ...     def __init__(self, reads, writes):
        ...         super().__init__(reads, writes)
        ...
        ...     def transform(self):
        ...         i1, i2 = [var.value for var in self.reads()]
        ...         self.writes()[0].add_hypothesis(VariableRecord(
        ...             i1 + i2, confidence=random.uniform(0., 1.), source=self.key()
        ...         ))
        >>>
        >>> class DivideBy2Mechanism(Mechanism):
        ...     def __init__(self, reads, writes):
        ...         super().__init__(reads, writes)
        ...
        ...     def transform(self):
        ...         for var in self.writes():
        ...             var.add_hypothesis(VariableRecord(
        ...                 var.value*0.5,
        ...                 confidence=random.uniform(0., 1.),
        ...                 source=self.key()
        ...             ))
        >>>
        >>> class EmergencyMechanism(Mechanism):
        ...     def __init__(self, reads, writes):
        ...         super().__init__(reads, writes)
        ...
        ...     def transform(self):
        ...         for var in self.writes():
        ...             var.add_hypothesis(VariableRecord(
        ...                 var.value*0.3, confidence=1.0, source=self.key()
        ...             ))
        >>>
        >>> emergencyMech = EmergencyMechanism([], [X, Y, Z])
        >>>
        >>> executive = Executive(mechanisms=[
        ...     AddMechanism([X, Y], [Z]),
        ...     AddMechanism([X, Z], [Y]),
        ...     AddMechanism([Y, Z], [X]),
        ...     DivideBy2Mechanism([], [X, Y, Z])
        ... ])
        >>>
        >>> class SafetyInvariant(SystemInvariant):
        ...     def __init__(self, threshold: float = 75.0):
        ...         self.threshold = threshold
        ...         self.added = False
        ...
        ...         def check_condition(snapshot: VariableSnapshot):
        ...             for view in snapshot.views:
        ...                 if view.stats.mean > self.threshold:
        ...                     return False
        ...             return True
        ...
        ...         def handle_violation(
        ...             invariant: InvariantViolation, snapshot: VariableSnapshot
        ...         ):
        ...             if not self.added:
        ...                 executive.add_mechanism(emergencyMech)
        ...                 for var in [X, Y, Z]:
        ...                     var.policy = HighestConfidencePolicy()
        ...                 self.added = True
        ...
        ...         super().__init__(
        ...             "SafetyInvariant",
        ...             condition=check_condition,
        ...             on_violation=handle_violation,
        ...             phase=InvariantPhase.RUNTIME,
        ...             message=""
        ...         )
        >>>
        >>> executive.add_invariant(
        ...     SafetyInvariant(threshold=700000.0)
        ... )
        >>>
        >>> def pre_step(executive: Executive, step: int):
        ...     for mech in executive.mechanisms():
        ...         if mech == emergencyMech:
        ...             print(f"Step {step}: Mechanism has been added.")
        ...
        ...     if step == 80:
        ...         executive.remove_mechanism(emergencyMech)
        >>>
        # Simulation
        >>> init_variables()
        >>> executive.run(steps=100, pre_step=pre_step, post_step=None)
        >>>
        >>> for var in [X, Y, Z]:
        ...     _, conclusion, _ = var.memory.latest()
        ...     print(var.name, var.value, var.confidence)
        Step 68: Mechanism has been added.
        Step 69: Mechanism has been added.
        Step 70: Mechanism has been added.
        Step 71: Mechanism has been added.
        Step 72: Mechanism has been added.
        Step 73: Mechanism has been added.
        Step 74: Mechanism has been added.
        Step 75: Mechanism has been added.
        Step 76: Mechanism has been added.
        Step 77: Mechanism has been added.
        Step 78: Mechanism has been added.
        Step 79: Mechanism has been added.
        Step 80: Mechanism has been added.
        X 35.499546845738266 0.6239227647681721
        Y 95.6222768274126 0.5870536688252231
        Z 12.311591567968035 0.6060587403984868

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
        self.rng = rng or random.Random()
        self._step_index: int = 0
        self.logger = logger or setup_logging(
            name="procela",
            log_file="logs/procela.log",
            json_file="logs/procela.jsonl",
        )
        self.n_steps: int = -1  # Updated in run() method.
        self.checkpoint: ExecutiveCheckPoint | None = None
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

    def set_rng(self, rng: random.Random | np.random.Generator) -> None:
        """
        Set the pseudo random number generator.

        Parameters
        ----------
        rng : random.Random | np.random.Generator
            The RNG to use.
        """
        self.rng = rng

    def set_logger(self, logger: logging.Logger) -> None:
        """
        Set logger.

        Parameters
        ----------
        logger : logging.Logger
            The logging logger to use.
        """
        self.logger = logger

    def prepare(self) -> None:
        """
        Prepare the executive for execution.

        Notes
        -----
        - Collects unique writable variables.
        - Collects all variables touched by the system.
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

        Execution consists of five strictly ordered phases:

        1. Call pre-phase invariants
        2. Collect competing hypotheses
        3. Call runtime-phase invariants before resolution
        4. Ask writable variables to resolve their conflicts
        5. Call post-phase invariants after resolution

        Notes
        -----
        - All processes are executed before any conflict resolution.
        - Each variable is resolved and committed at most once.
        """
        if not self._prepared:
            raise ExecutionError("Executive must be prepared before execution.")

        self._check_invariants(InvariantPhase.PRE)

        for process in self._processes:
            process.step()
        for mechanism in self._mechanisms:
            mechanism.run()

        self._check_invariants(InvariantPhase.RUNTIME)

        for variable in self.writable():
            if not isinstance(variable, Variable):
                raise TypeError(f"Expected `Variable`, got {type(variable)}")

            # Variable is resolving conflicts
            variable.resolve_conflict()

            # Commit resolved candidate
            variable.commit()

            # Clear candidates
            variable.clear_hypotheses()

        self._check_invariants(InvariantPhase.POST)

        # Increment step index
        self._step_index += 1

    def run(
        self,
        steps: int,
        pre_step: Callable[[Executive, int], None] | None = None,
        post_step: Callable[[Executive, int], None] | None = None,
    ) -> None:
        """
        Execute all the steps by calling optional callable hooks at each step.

        Execution consists of three strictly ordered phases:

        1. Call pre_step event before collecting hypotheses
        2. Process execution where invariants are checked,
           conflicts are collected, then resolution policy applied
        3. Call post_step event after simulation

        Parameters
        ----------
        steps : int
            The number of steps.
        pre_step : Callable[[Executive, int], None] | None
            The pre step hook. Default is None.
        post_step : Callable[[Executive, int], None] | None
            The post step hook. Default is None.

        Raises
        ------
        RuntimeError
            If the executive has not been prepared.
        """
        self.n_steps = steps
        if not self._prepared:
            raise ExecutionError("Executive must be prepared before execution.")

        i = 0
        while i < self.n_steps:
            if pre_step is not None:
                pre_step(self, i)
            self.step()
            if post_step is not None:
                post_step(self, i)

            i += 1

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

    def step_index(self) -> int:
        """
        Return current step index.

        Returns
        -------
        int
            The current step index.
        """
        return self._step_index

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
            self._step_index, views=[v.epistemic() for v in self.variables()]
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

    def remove_invariant(self, invariant: SystemInvariant) -> None:
        """
        Remove completely an invariant from the Execution.

        Parameters
        ----------
        invariant : SystemInvariant
            The invariant to be removed.
        """
        self._invariants = [inv for inv in self._invariants if inv != invariant]

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

    def random(self) -> float:
        """
        Get a pseudo random number between 0 and 1.

        Returns
        -------
            A pseudo random number between 0 and 1.
        """
        u = self.rng.random()
        return float(u)

    def create_checkpoint(
        self,
    ) -> ExecutiveCheckPoint:
        """
        Save checkpoint before experiment.

        Returns
        -------
        ExecutiveCheckPointType
            The executive checkpoint.
        """
        self.checkpoint = ExecutiveCheckPoint(
            processes=self._processes.copy(),
            mechanisms=self._mechanisms.copy(),
            mechanism_points={
                m: m.create_checkpoint()
                for m in self._mechanisms
                if hasattr(m, "create_checkpoint")
            },
            variables=self._variables.copy(),
            variable_points={var: var.create_checkpoint() for var in self._variables},
            invariants=self._invariants.copy(),
            invariant_points={
                inv: inv.create_checkpoint()
                for inv in self._invariants
                if hasattr(inv, "create_checkpoint")
            },
            rng=self.get_rng_state(),
            step=self._step_index,
            logger=self.logger,
            n_steps=self.n_steps,
        )

        return self.checkpoint

    def run_experiment(
        self,
        steps: int,
        pre_step: Callable[[Executive, int], None] | None = None,
        post_step: Callable[[Executive, int], None] | None = None,
    ) -> None:
        """
        Run experiment.

        Parameters
        ----------
        steps : int
            The number of steps.
        pre_step : Callable[[Executive, int], None] | None
            The pre step hook. Default is None.
        post_step : Callable[[Executive, int], None] | None
            The post step hook. Default is None.
        """
        self.run(steps=steps, pre_step=pre_step, post_step=post_step)
        self.n_steps = (
            self.checkpoint.n_steps - steps if self.checkpoint is not None else steps
        )

    def restore_checkpoint(self, checkpoint: ExecutiveCheckPoint) -> None:
        """
        Restore the executive checkpoint.

        Parameters
        ----------
        checkpoint : ExecutiveCheckPointType
            The executive checkpoint to be restored.
        """
        # Restore the processes
        self._processes = checkpoint.processes

        # Restore mechanisms
        self._mechanisms = checkpoint.mechanisms
        for mech, chpoint in checkpoint.mechanism_points.items():
            if mech in self._mechanisms and hasattr(mech, "restore_checkpoint"):
                mech.restore_checkpoint(chpoint)

        # Restore variables
        for var, chpoint in checkpoint.variable_points.items():
            if var in checkpoint.variables:
                var.restore_checkpoint(chpoint)

        # Restore invariants
        self._invariants = checkpoint.invariants
        for inv, chpoint in checkpoint.invariant_points.items():
            if inv in self._invariants and hasattr(inv, "restore_checkpoint"):
                inv.restore_checkpoint(chpoint)

        # Restore rng
        # self.rng = checkpoint[8]
        self.set_rng_state(checkpoint.rng)

        # Restore step index
        self._step_index = checkpoint.step

        # Restore logger
        self.logger = checkpoint.logger

        # Restore n_steps
        self.n_steps = checkpoint.n_steps

        self.prepare()

    def get_rng_state(self) -> Any:
        """
        Get the state of the random number generator.

        Returns
        -------
        Any
            The state of the random number generator.
        """
        if isinstance(self.rng, random.Random):
            return ("python", self.rng.getstate())
        elif isinstance(self.rng, np.random.Generator):
            return ("numpy", self.rng.bit_generator.state)

    def set_rng_state(self, state: Any) -> None:
        """
        Set the state of the random number generator.

        Parameters
        ----------
        state : Any
            The state of the random number generator to be set.
        """
        kind, value = state
        if kind == "python" and isinstance(self.rng, random.Random):
            self.rng.setstate(value)
        elif isinstance(self.rng, np.random.Generator):
            self.rng.bit_generator.state = value
