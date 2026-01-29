"""
Collection of execution step traces.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/execution/trace.html

Examples Reference
------------------
https://procela.org/docs/examples/core/execution/trace.html
"""

from __future__ import annotations

from typing import Iterator

from .step import ExecutionStepTrace


class ExecutionTrace:
    """Ordered collection of execution step traces."""

    def __init__(self) -> None:
        """Initialize an instance of ExecutionTrace."""
        self._steps: list[ExecutionStepTrace] = []

    def append(self, trace: ExecutionStepTrace) -> None:
        """
        Append a completed step trace.

        Parameters
        ----------
        trace : ExecutionStepTrace
            The execution step trace to be added.
        """
        self._steps.append(trace)

    def __iter__(self) -> Iterator[ExecutionStepTrace]:
        """
        Iterate over the execution trace.

        Returns
        -------
        Iterator[ExecutionStepTrace]
            The iterator of ExecutionStepTrace.
        """
        return iter(self._steps)

    def __len__(self) -> int:
        """
        Get the length of the ExecutionTrace.

        Returns
        -------
        int
            The length of the ExecutionTrace.
        """
        return len(self._steps)

    def last(self) -> ExecutionStepTrace | None:
        """
        Return the most recent step trace.

        Returns
        -------
        ExecutionStepTrace | None
            The most recent step trace.
        """
        return self._steps[-1] if self._steps else None
