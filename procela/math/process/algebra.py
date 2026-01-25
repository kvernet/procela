"""
Process algebra module.

Contains mathematical operations on processes.

Semantics Reference
-------------------
https://procela.org/docs/semantics/math/process/algebra.html

Examples Reference
------------------
https://procela.org/docs/examples/math/process/algebra.html
"""

from ...core.process.base import Process
from ...core.process.compose import Compose


class ProcessAlgebra:
    """Basic operations on processes (placeholder for research)."""

    @staticmethod
    def combine(processes: list[Process]) -> Process:
        """
        Combine multiple processes using a simple summation rule.

        Future: implement full algebra, metrics, optimization.

        Parameters
        ----------
        processes : list[Process]
            The list of processes to combine.
        """
        # Placeholder: use Compose for now
        return Compose(processes)

    @staticmethod
    def scale(process: Process, factor: float) -> Process:
        """
        Scale a process by a factor.

        Future: implement real scaling on process variables.

        Parameters
        ----------
        process : Process
            The process to be multiplied by the factor.
        factor : float
            The factor to multiply the process with.
        """
        # Placeholder: returns the same process
        return process
