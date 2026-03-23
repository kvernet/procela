"""
Variable roles semantic definitions.

Semantic classification system for variables in the Procela framework.

Defines four fundamental roles that determine how variables behave and are
processed throughout the reasoning pipeline:

Examples
--------
>>> from procela import VariableRole
>>>
>>> role = VariableRole.ENDOGENOUS
>>> assert isinstance(role, VariableRole)
>>>
>>> for role in VariableRole:
...     print(role.name)
ENDOGENOUS
EXOGENOUS
CONTROL
DERIVED

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/role.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/variable/role.html
"""

from __future__ import annotations

from enum import Enum, auto


class VariableRole(Enum):
    """
    Semantic role of a variable in a system.

    This enumeration classifies variables based on their semantic purpose
    and behavioral characteristics within reasoning contexts. Each role
    implies specific constraints, reasoning strategies, and visualization
    preferences.

    Attributes
    ----------
    ENDOGENOUS
        Variables determined within the system boundary (effects/dependent).
        These are typically the variables we aim to predict or explain.

    EXOGENOUS
        Variables determined outside the system boundary (causes/independent).
        These provide inputs or boundary conditions to the system.

    CONTROL
        Variables that can be manipulated to influence system behavior.
        These represent decision points or adjustable parameters.

    DERIVED
        Variables computed from other variables through transformations.
        These represent aggregated, derived, or synthesized information.

    Examples
    --------
    >>> from procela import VariableRole
    >>>
    >>> role = VariableRole.ENDOGENOUS
    >>> assert isinstance(role, VariableRole)
    >>>
    >>> for role in VariableRole:
    ...     print(role.name)
    ENDOGENOUS
    EXOGENOUS
    CONTROL
    DERIVED
    """

    ENDOGENOUS = auto()
    EXOGENOUS = auto()
    CONTROL = auto()
    DERIVED = auto()
