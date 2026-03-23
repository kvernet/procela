"""
Resolution policy base class in Procela.

Examples
--------
>>> import random
>>>
>>> from procela import (
...     HypothesisRecord,
...     VariableRecord,
...     ResolutionPolicy
... )
>>>
>>> random.seed(42)
>>>
>>> class PriorityOrderPolicy(ResolutionPolicy):
...     def resolve(self, hypotheses):
...         hypotheses_list = list(hypotheses)
...         if not hypotheses_list:
...             return None
...
...         return hypotheses_list[0].record
>>>
>>> policy = PriorityOrderPolicy()
>>>
>>> hypotheses = [
...     HypothesisRecord(
...         VariableRecord(
...             value=random.gauss(1.3, 0.2),
...             confidence=random.uniform(0, 1)
...         ),
...     ) for _ in range(15)
... ]
>>> resolved = policy.resolve(
...     hypotheses=hypotheses
... )
>>>
>>> print(resolved.value)
1.2711819340844144
>>> print(resolved.confidence)
0.27502931836911926
>>> print(resolved.explanation)
None

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/policy/resolution/base.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/policy/resolution/base.html
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from ....symbols.key import Key
from ...key_authority import KeyAuthority
from ...memory.hypothesis import HypothesisRecord
from ...memory.record import VariableRecord


class ResolutionPolicy(ABC):
    """
    Abstract base class defining the interface for resolution policies.

    In Procela, a policy resolution is a logic that defines how to resolve
    among competing hypothesis objects into a single authoritative conclusion.

    Subclasses must implement the `resolve` method with specific resolution
    algorithms (e.g., highest confidence, multi-criteria optimization,
    constraint satisfaction).

    Examples
    --------
    >>> import random
    >>>
    >>> from procela import (
    ...     HypothesisRecord,
    ...     VariableRecord,
    ...     ResolutionPolicy
    ... )
    >>>
    >>> random.seed(42)
    >>>
    >>> class PriorityOrderPolicy(ResolutionPolicy):
    ...     def resolve(self, hypotheses):
    ...         hypotheses_list = list(hypotheses)
    ...         if not hypotheses_list:
    ...             return None
    ...
    ...         return hypotheses_list[0].record
    >>>
    >>> policy = PriorityOrderPolicy()
    >>>
    >>> hypotheses = [
    ...     HypothesisRecord(
    ...         VariableRecord(
    ...             value=random.gauss(1.3, 0.2),
    ...             confidence=random.uniform(0, 1)
    ...         ),
    ...     ) for _ in range(15)
    ... ]
    >>> resolved = policy.resolve(
    ...     hypotheses=hypotheses
    ... )
    >>>
    >>> print(resolved.value)
    1.2711819340844144
    >>> print(resolved.confidence)
    0.27502931836911926
    >>> print(resolved.explanation)
    None
    """

    def __init__(self, name: str | None = None) -> None:
        """
        Initialize a ResolutionPolicy object.

        Parematers
        ----------
        name : str | None
            The unique human-readable name of the Resolution.
            Default is the class name object.

        Examples
        --------
        >>> import random
        >>>
        >>> from procela import (
        ...     HypothesisRecord,
        ...     VariableRecord,
        ...     ResolutionPolicy
        ... )
        >>>
        >>> random.seed(42)
        >>>
        >>> class PriorityOrderPolicy(ResolutionPolicy):
        ...     def resolve(self, hypotheses):
        ...         hypotheses_list = list(hypotheses)
        ...         if not hypotheses_list:
        ...             return None
        ...
        ...         return hypotheses_list[0].record
        >>>
        >>> policy = PriorityOrderPolicy()
        >>>
        >>> hypotheses = [
        ...     HypothesisRecord(
        ...         VariableRecord(
        ...             value=random.gauss(1.3, 0.2),
        ...             confidence=random.uniform(0, 1)
        ...         ),
        ...     ) for _ in range(15)
        ... ]
        >>> resolved = policy.resolve(
        ...     hypotheses=hypotheses
        ... )
        >>>
        >>> print(resolved.value)
        1.2711819340844144
        >>> print(resolved.confidence)
        0.27502931836911926
        >>> print(resolved.explanation)
        None
        """
        super().__init__()
        self._key = KeyAuthority.issue(self)
        self.name = name or self.__class__.__name__

    def key(self) -> Key:
        """
        Return the unique identity of the ResolutionPolicy.

        Returns
        -------
        Key
            The unique identity of the ResolutionPolicy.
        """
        return self._key

    @abstractmethod
    def resolve(self, hypotheses: Iterable[HypothesisRecord]) -> VariableRecord | None:
        """
        Resolve competing hypotheses from an iterable.

        This method embodies the policy's logic resolution.
        It evaluates hypotheses based on the policy's internal criteria
        (confidence, etc) and returns a single resolved conclusion or None
        if no suitable conclusion is found.

        Parameters
        ----------
        hypotheses : Iterable[HypothesisRecord]
            An iterable of `HypothesisRecord` objects to evaluate and resolve from.
            The iterable may be empty. Policies should handle this gracefully.

        Returns
        -------
        VariableRecord | None
            The resolved `VariableRecord` that best satisfies the policy's
            criteria, or `None` if the input is empty or no hypothesis meets
            the minimum requirements.

        Raises
        ------
        TypeError
            If any item in `hypotheses` is not an instance of `HypothesisRecord`.
        ValueError
            If the policy encounters invalid data within hypotheses (e.g.,
            confidence outside [0,1] if the policy relies on it).
        """
        raise NotImplementedError
