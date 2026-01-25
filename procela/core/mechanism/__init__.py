"""
Mechanism module abstraction for Procela.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/mechanism/

Examples Reference
------------------
https://procela.org/docs/examples/core/mechanism/
"""

from .base import Mechanism
from .template import MechanismTemplate

__all__ = [
    "Mechanism",
    "MechanismTemplate",
]
