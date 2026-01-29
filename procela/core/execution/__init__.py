"""
Execution trace abstraction within Procela's.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/execution/

Examples Reference
------------------
https://procela.org/docs/examples/core/execution/
"""

from .step import ExecutionStepTrace
from .trace import ExecutionTrace

__all__ = [
    "ExecutionStepTrace",
    "ExecutionTrace",
]
