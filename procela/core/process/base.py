"""
Process abstraction for Procela.

This module defines the Process class, which groups mechanisms into
coherent execution units. A process represents a logical subsystem
of a real-world model and defines execution scope without owning state.

Examples
--------
>>> import random
>>>
>>> from procela import (
...     Variable,
...     RangeDomain,
...     VariableRecord,
...     Mechanism,
...     Process
... )
>>>
>>> random.seed(42)
>>>
>>> X = Variable("X", RangeDomain(0., 100))
>>> Y = Variable("Y", RangeDomain(0., 100))
>>>
>>> class XplusYMechanism(Mechanism):
...     def transform(self):
...         x_val, y_val = [var.value for var in self.reads()]
...         X.add_hypothesis(VariableRecord(
...             x_val + y_val,
...             confidence=random.uniform(0., 1.),
...             source=self.key()
...         ))
...         Y.add_hypothesis(VariableRecord(
...             x_val + y_val,
...             confidence=random.uniform(0., 1.),
...             source=self.key()
...         ))
>>>
>>> class DoubleYMechanism(Mechanism):
...     def transform(self):
...         for var in self.writes():
...             var.add_hypothesis(VariableRecord(
...                 2*var.value,
...                 confidence=random.uniform(0., 1.),
...                 source=self.key()
...             ))
>>>
# Create process
>>> process = Process([
...     XplusYMechanism([X, Y], [X, Y]),
...     DoubleYMechanism([X, Y], [X, Y])
... ])
>>>
>>> print(process.key())
<Key>
>>> mechanisms = process.mechanisms()
>>> print(f"Process has {len(mechanisms)} mechanisms")
Process has 2 mechanisms
# Init variables
>>> X.set(VariableRecord(value=0.25, confidence=0.99))
>>> Y.set(VariableRecord(value=0.72, confidence=0.99))
>>>
>>>> for var in process.variables():
...     print(var.name, var.value, var.confidence, len(var.hypotheses))
X 0.25 0.99 0
Y 0.72 0.99 0
# Execute a step
>>> process.step()
>>>
>>> for var in process.variables():
...     print(var.name, var.value, var.confidence, len(var.hypotheses))
X 0.25 0.99 2
Y 0.72 0.99 2
>>> mechanisms[0].disable()
>>>
# Execute a step
>>> process.step()
>>>
>>> for var in process.variables():
...     print(var.name, var.value, var.confidence, len(var.hypotheses))
X 0.25 0.99 3
Y 0.72 0.99 3

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
from ..variable.variable import Variable


class Process:
    """
    Execution container for mechanisms.

    A process groups mechanisms that participate in a common execution
    context. Processes do not store variables, resolve conflicts.

    Examples
    --------
    >>> import random
    >>>
    >>> from procela import (
    ...     Variable,
    ...     RangeDomain,
    ...     VariableRecord,
    ...     Mechanism,
    ...     Process
    ... )
    >>>
    >>> random.seed(42)
    >>>
    >>> X = Variable("X", RangeDomain(0., 100))
    >>> Y = Variable("Y", RangeDomain(0., 100))
    >>>
    >>> class XplusYMechanism(Mechanism):
    ...     def transform(self):
    ...         x_val, y_val = [var.value for var in self.reads()]
    ...         X.add_hypothesis(VariableRecord(
    ...             x_val + y_val,
    ...             confidence=random.uniform(0., 1.),
    ...             source=self.key()
    ...         ))
    ...         Y.add_hypothesis(VariableRecord(
    ...             x_val + y_val,
    ...             confidence=random.uniform(0., 1.),
    ...             source=self.key()
    ...         ))
    >>>
    >>> class DoubleYMechanism(Mechanism):
    ...     def transform(self):
    ...         for var in self.writes():
    ...             var.add_hypothesis(VariableRecord(
    ...                 2*var.value,
    ...                 confidence=random.uniform(0., 1.),
    ...                 source=self.key()
    ...             ))
    >>>
    # Create process
    >>> process = Process([
    ...     XplusYMechanism([X, Y], [X, Y]),
    ...     DoubleYMechanism([X, Y], [X, Y])
    ... ])
    >>>
    >>> print(process.key())
    <Key>
    >>> mechanisms = process.mechanisms()
    >>> print(f"Process has {len(mechanisms)} mechanisms")
    Process has 2 mechanisms
    # Init variables
    >>> X.set(VariableRecord(value=0.25, confidence=0.99))
    >>> Y.set(VariableRecord(value=0.72, confidence=0.99))
    >>>
    >>>> for var in process.variables():
    ...     print(var.name, var.value, var.confidence, len(var.hypotheses))
    X 0.25 0.99 0
    Y 0.72 0.99 0
    # Execute a step
    >>> process.step()
    >>>
    >>> for var in process.variables():
    ...     print(var.name, var.value, var.confidence, len(var.hypotheses))
    X 0.25 0.99 2
    Y 0.72 0.99 2
    >>> mechanisms[0].disable()
    >>>
    # Execute a step
    >>> process.step()
    >>>
    >>> for var in process.variables():
    ...     print(var.name, var.value, var.confidence, len(var.hypotheses))
    X 0.25 0.99 3
    Y 0.72 0.99 3
    """

    def __init__(self, mechanisms: Sequence[Mechanism]) -> None:
        """
        Initialize a process.

        Parameters
        ----------
        mechanisms : Sequence[Mechanism]
            Mechanisms composing the process.

        Examples
        --------
        >>> import random
        >>>
        >>> from procela import (
        ...     Variable,
        ...     RangeDomain,
        ...     VariableRecord,
        ...     Mechanism,
        ...     Process
        ... )
        >>>
        >>> random.seed(42)
        >>>
        >>> X = Variable("X", RangeDomain(0., 100))
        >>> Y = Variable("Y", RangeDomain(0., 100))
        >>>
        >>> class XplusYMechanism(Mechanism):
        ...     def transform(self):
        ...         x_val, y_val = [var.value for var in self.reads()]
        ...         X.add_hypothesis(VariableRecord(
        ...             x_val + y_val,
        ...             confidence=random.uniform(0., 1.),
        ...             source=self.key()
        ...         ))
        ...         Y.add_hypothesis(VariableRecord(
        ...             x_val + y_val,
        ...             confidence=random.uniform(0., 1.),
        ...             source=self.key()
        ...         ))
        >>>
        >>> class DoubleYMechanism(Mechanism):
        ...     def transform(self):
        ...         for var in self.writes():
        ...             var.add_hypothesis(VariableRecord(
        ...                 2*var.value,
        ...                 confidence=random.uniform(0., 1.),
        ...                 source=self.key()
        ...             ))
        >>>
        # Create process
        >>> process = Process([
        ...     XplusYMechanism([X, Y], [X, Y]),
        ...     DoubleYMechanism([X, Y], [X, Y])
        ... ])
        >>>
        >>> print(process.key())
        <Key>
        >>> mechanisms = process.mechanisms()
        >>> print(f"Process has {len(mechanisms)} mechanisms")
        Process has 2 mechanisms
        # Init variables
        >>> X.set(VariableRecord(value=0.25, confidence=0.99))
        >>> Y.set(VariableRecord(value=0.72, confidence=0.99))
        >>>
        >>>> for var in process.variables():
        ...     print(var.name, var.value, var.confidence, len(var.hypotheses))
        X 0.25 0.99 0
        Y 0.72 0.99 0
        # Execute a step
        >>> process.step()
        >>>
        >>> for var in process.variables():
        ...     print(var.name, var.value, var.confidence, len(var.hypotheses))
        X 0.25 0.99 2
        Y 0.72 0.99 2
        >>> mechanisms[0].disable()
        >>>
        # Execute a step
        >>> process.step()
        >>>
        >>> for var in process.variables():
        ...     print(var.name, var.value, var.confidence, len(var.hypotheses))
        X 0.25 0.99 3
        Y 0.72 0.99 3

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

    def writable(self) -> set[Variable]:
        """
        Return unique set of variables written by the process.

        Returns
        -------
        set[Variable]
            Writable variables.
        """
        vars: set[Variable] = set()
        for mechanism in self._mechanisms:
            vars.update(mechanism.writes())
        return vars

    def variables(self) -> set[Variable]:
        """
        Return all variables touched by the process.

        Returns
        -------
        set[Variable]
            Read and written variables.
        """
        vars: set[Variable] = set()
        for mechanism in self._mechanisms:
            vars.update(mechanism.reads())
            vars.update(mechanism.writes())
        return vars
