"""
Variable domain definitions for Procela's active reasoning framework.

The domain module provides a comprehensive set of domain classes that
define the possible values, constraints, and behaviors for variables in
the Procela system. Each domain type implements specific validation,
sampling, and reasoning capabilities tailored to different types of
data and constraints.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/domain/

Examples Reference
-------------------
https://procela.org/docs/examples/core/variable/domain/
"""

from .boolean import BooleanDomain
from .categorical import CategoricalDomain
from .composite import CompositeDomain
from .range import RangeDomain
from .real import RealDomain
from .statistical import StatisticalDomain
from .value import ValueDomain

__all__ = [
    "BooleanDomain",
    "CategoricalDomain",
    "CompositeDomain",
    "RangeDomain",
    "RealDomain",
    "StatisticalDomain",
    "ValueDomain",
]
