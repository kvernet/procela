"""
Snapshot of the epistemic state of variables at a given execution moment.

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
    views : tuple[VariableView]
        Epistemic views over variables available for invariant evaluation.
    """

    views: tuple[VariableView, ...]

    @classmethod
    def from_views(cls, views: Sequence[VariableView]) -> VariableSnapshot:
        """
        Create a VariableSnapshot instance from a sequence of variables views.

        Parameters
        ----------
        views: Sequence[VariableView]
            The views over variables.

        Returns
        -------
        VariableSnapshot
            The VariableSnapshot instance created from views.
        """
        return cls(tuple(views))
