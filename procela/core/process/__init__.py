"""
Process abstraction for Procela.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/process/

Examples Reference
------------------
https://procela.org/docs/examples/core/process/
"""

from .base import Process
from .compose import Compose

__all__ = [
    "Process",
    "Compose",
]
