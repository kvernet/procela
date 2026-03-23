"""
Snapshot of the epistemic state of variables at a given execution moment.

Examples
--------
>>> import random
>>>
>>> from procela import (
...     VariableSnapshot,
...     Variable,
...     RealDomain,
...     VariableRecord
... )
>>>
>>> X = Variable("X", RealDomain())
>>> Y = Variable("Y", RealDomain())
>>>
>>> for _ in range(7):
...     for var in [X, Y]:
...         var.set(VariableRecord(
...             value=random.gauss(1.8, 1.3), confidence=random.uniform(0, 1)
...         ))
>>>
>>> snapshot = VariableSnapshot(step=1, views=[X.epistemic(), Y.epistemic()])
>>>
>>> print(len(snapshot.views))
2
>>> snapshot = VariableSnapshot.from_views(
...     step=0, views=[Y.epistemic(), X.epistemic()]
... )
>>>
>>> print(len(snapshot.views))
2
>>> assert snapshot.views[0].key == Y.key()

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/invariant/snapshot.html

Examples Reference
------------------
https://procela.org/docs/examples/core/invariant/snapshot.html
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..epistemic import VariableView


@dataclass(frozen=True)
class VariableSnapshot:
    """
    Snapshot of the epistemic view of variables at a given execution moment.

    Parameters
    ----------
    step : int
        The executive current step.
    views : tuple[VariableView]
        Epistemic views over variables available for invariant evaluation.

    Examples
    --------
    >>> import random
    >>>
    >>> from procela import (
    ...     VariableSnapshot,
    ...     Variable,
    ...     RealDomain,
    ...     VariableRecord
    ... )
    >>>
    >>> X = Variable("X", RealDomain())
    >>> Y = Variable("Y", RealDomain())
    >>>
    >>> for _ in range(7):
    ...     for var in [X, Y]:
    ...         var.set(VariableRecord(
    ...             value=random.gauss(1.8, 1.3), confidence=random.uniform(0, 1)
    ...         ))
    >>>
    >>> snapshot = VariableSnapshot(step=1, views=[X.epistemic(), Y.epistemic()])
    >>>
    >>> print(len(snapshot.views))
    2
    >>> snapshot = VariableSnapshot.from_views(
    ...     step=0, views=[Y.epistemic(), X.epistemic()]
    ... )
    >>>
    >>> print(len(snapshot.views))
    2
    >>> assert snapshot.views[0].key == Y.key()
    """

    step: int
    views: tuple[VariableView, ...]

    @classmethod
    def from_views(cls, step: int, views: Sequence[VariableView]) -> VariableSnapshot:
        """
        Create a VariableSnapshot instance from a sequence of variables views.

        Parameters
        ----------
        step : int
            The executive current step.
        views: Sequence[VariableView]
            The views over variables.

        Returns
        -------
        VariableSnapshot
            The VariableSnapshot instance created from views.
        """
        return cls(step, tuple(views))
