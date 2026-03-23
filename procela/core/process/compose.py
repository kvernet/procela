"""
Compose module for Processes.

This module defines the `Compose` class, which allows combining multiple
processes into a single higher-level process. The resulting process
aggregates the mechanisms of all constituent processes and behaves
as a single unit within an Executive-managed simulation.

Examples
--------
>>> from procela import Compose, Process
>>>
# Declare processes (see Process)
>>> proc = Compose([p1, p1, ..., pn])
>>> assert isinstance(proc, Process)
>>> proc.step()

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/process/compose.html

Examples Reference
------------------
https://procela.org/docs/examples/core/process/compose.html
"""

from __future__ import annotations

from typing import Sequence

from .base import Process


class Compose(Process):
    """
    Combine multiple processes into a single process.

    The `Compose` class enables modular design by aggregating
    mechanisms from multiple processes. Mechanisms from all
    constituent processes are included in the composed process
    in the order provided.

    Examples
    --------
    >>> from procela import Compose, Process
    >>>
    # Declare processes (see Process)
    >>> proc = Compose([p1, p1, ..., pn])
    >>> assert isinstance(proc, Process)
    >>> proc.step()

    Notes
    -----
        - The composed process behaves like any other `Process` in
            execution but internally represents multiple sub-processes.
        - Mechanism ordering follows the order of processes and their
            internal mechanisms.
    """

    def __init__(self, processes: Sequence[Process]):
        """
        Initialize the composed process with mechanisms from all sub-processes.

        Parameters
        ----------
        processes : Sequence[Process]
            List or sequence of `Process` instances to combine. All
            mechanisms from these processes will be included in the
            composed process.

        Examples
        --------
        >>> from procela import Compose, Process
        >>>
        # Declare processes (see Process)
        >>> proc = Compose([p1, p1, ..., pn])
        >>> assert isinstance(proc, Process)
        >>> proc.step()
        """
        super().__init__([mech for p in processes for mech in p.mechanisms()])
