"""
Mechanism abstraction for Procela.

This module defines the abstract Mechanism class, which represents a
real-world mechanism that transforms, consumes, and produces variables
under declared constraints. Mechanisms operate within processes and
are coordinated by the executive.

Mechanisms do not resolve conflicts and do not own variables. They
produce candidate values that variables later arbitrate.

Examples
--------
>>> from procela import (
...     Mechanism,
...     Variable,
...     RangeDomain,
...     VariableRecord
... )
>>>
>>> X = Variable("X", RangeDomain(0., 50.))
>>> Y = Variable("Y", RangeDomain(-50., 50.))
>>>
>>> class DoubleValueMechanism(Mechanism):
...     def __init__(self):
...         super().__init__(reads=[X, Y], writes=[X, Y])
...
...     def transform(self):
...         for var in self.writes():
...             var.add_hypothesis(VariableRecord(
...                 var.value * 2, confidence=0.67
...             ))
>>>
>>> mech = DoubleValueMechanism()
>>> print(len(mech.reads()), len(mech.writes()))
2 2
# Init variables
>>> X.init(VariableRecord(6, confidence=1.0))
>>> Y.init(VariableRecord(2.1, confidence=1.0))
>>>
>>> mech.transform()
>>>
>>> print(X.hypotheses[0].record.value)
12.0
>>> print(Y.hypotheses[0].record.value)
4.2
>>> mech.disable()
>>> mech.run()
>>> print(len(X.hypotheses), len(Y.hypotheses))
1 1
>>> mech.disable()
>>> mech.transform()
>>> print(len(X.hypotheses), len(Y.hypotheses))
2 2

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
from ..variable.variable import Variable


class Mechanism(ABC):
    """
    Abstract base class for mechanisms.

    A mechanism models a real-world causal transformation that reads
    variables and produces candidate values for other variables.
    Mechanisms are execution units with a declared structural interface.

    Mechanisms may be dynamically enabled or disabled during execution.

    Examples
    --------
    >>> from procela import (
    ...     Mechanism,
    ...     Variable,
    ...     RangeDomain,
    ...     VariableRecord
    ... )
    >>>
    >>> X = Variable("X", RangeDomain(0., 50.))
    >>> Y = Variable("Y", RangeDomain(-50., 50.))
    >>>
    >>> class DoubleValueMechanism(Mechanism):
    ...     def __init__(self):
    ...         super().__init__(reads=[X, Y], writes=[X, Y])
    ...
    ...     def transform(self):
    ...         for var in self.writes():
    ...             var.add_hypothesis(VariableRecord(
    ...                 var.value * 2, confidence=0.67
    ...             ))
    >>>
    >>> mech = DoubleValueMechanism()
    >>> print(len(mech.reads()), len(mech.writes()))
    2 2
    # Init variables
    >>> X.init(VariableRecord(6, confidence=1.0))
    >>> Y.init(VariableRecord(2.1, confidence=1.0))
    >>>
    >>> mech.transform()
    >>>
    >>> print(X.hypotheses[0].record.value)
    12.0
    >>> print(Y.hypotheses[0].record.value)
    4.2
    >>> mech.disable()
    >>> mech.run()
    >>> print(len(X.hypotheses), len(Y.hypotheses))
    1 1
    >>> mech.disable()
    >>> mech.transform()
    >>> print(len(X.hypotheses), len(Y.hypotheses))
    2 2
    """

    def __init__(self, reads: Sequence[Variable], writes: Sequence[Variable]) -> None:
        """
        Initialize a mechanism.

        Parameters
        ----------
        reads : Sequence[Variable]
            Variables read by the mechanism.
        writes : Sequence[Variable]
            Variables written by the mechanism.

        Examples
        --------
        >>> from procela import (
        ...     Mechanism,
        ...     Variable,
        ...     RangeDomain,
        ...     VariableRecord
        ... )
        >>>
        >>> X = Variable("X", RangeDomain(0., 50.))
        >>> Y = Variable("Y", RangeDomain(-50., 50.))
        >>>
        >>> class DoubleValueMechanism(Mechanism):
        ...     def __init__(self):
        ...         super().__init__(reads=[X, Y], writes=[X, Y])
        ...
        ...     def transform(self):
        ...         for var in self.writes():
        ...             var.add_hypothesis(VariableRecord(
        ...                 var.value * 2, confidence=0.67
        ...             ))
        >>>
        >>> mech = DoubleValueMechanism()
        >>> print(len(mech.reads()), len(mech.writes()))
        2 2
        # Init variables
        >>> X.init(VariableRecord(6, confidence=1.0))
        >>> Y.init(VariableRecord(2.1, confidence=1.0))
        >>>
        >>> mech.transform()
        >>>
        >>> print(X.hypotheses[0].record.value)
        12.0
        >>> print(Y.hypotheses[0].record.value)
        4.2
        >>> mech.disable()
        >>> mech.run()
        >>> print(len(X.hypotheses), len(Y.hypotheses))
        1 1
        >>> mech.disable()
        >>> mech.transform()
        >>> print(len(X.hypotheses), len(Y.hypotheses))
        2 2

        Notes
        -----
        - Declared variables define the complete structural footprint
          of the mechanism.
        - Writing to undeclared variable is structurally invalid.
        """
        if not isinstance(reads, Sequence):
            raise TypeError(f"`reads` should be Sequence, got {reads!r}")
        for i, key in enumerate(reads):
            if not isinstance(key, Variable):
                raise TypeError(
                    "`reads` should contain only Variable instance, "
                    f"got {key!r} at index {i}"
                )
        if not isinstance(writes, Sequence):
            raise TypeError(f"`writes` should be Sequence, got {writes!r}")
        for i, key in enumerate(writes):
            if not isinstance(key, Variable):
                raise TypeError(
                    "`writes` should contain only Variable instance, "
                    f"got {key!r} at index {i}"
                )

        self._key: Key = KeyAuthority.issue(self)
        self._reads: tuple[Variable, ...] = tuple(reads)
        self._writes: tuple[Variable, ...] = tuple(writes)
        self._enabled: bool = True
        self.name = self.__class__.__name__

    def key(self) -> Key:
        """
        Return the unique key of the mechanism.

        Returns
        -------
        Key
            Mechanism key.
        """
        return self._key

    def reads(self) -> Sequence[Variable]:
        """
        Return the variables read by the mechanism.

        Returns
        -------
        Sequence[Variable]
            Variables read by the mechanism.
        """
        return self._reads

    def writes(self) -> Sequence[Variable]:
        """
        Return the variables written by the mechanism.

        Returns
        -------
        Sequence[Variable]
            Variables written by the mechanism.
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
