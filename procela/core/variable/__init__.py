"""
Core variable modeling system for the Procela reasoning framework.

This module provides the complete abstraction for variables as first-class
reasoning entities, encompassing value domains, semantic roles, statistical
analysis, and the variable object model itself.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/

Examples Reference
-------------------
https://procela.org/docs/examples/core/variable/
"""

from ..memory.variable.statistics import HistoryStatistics
from .domain import (
    BooleanDomain,
    CategoricalDomain,
    CompositeDomain,
    RangeDomain,
    RealDomain,
    StatisticalDomain,
    ValueDomain,
)
from .role import VariableRole
from .variable import Variable, VariableEpistemic

__all__ = [
    # Domain
    "BooleanDomain",
    "CategoricalDomain",
    "CompositeDomain",
    "RangeDomain",
    "RealDomain",
    "StatisticalDomain",
    "ValueDomain",
    # Statistics
    "HistoryStatistics",
    # Role
    "VariableRole",
    # Variable
    "Variable",
    "VariableEpistemic",
]
