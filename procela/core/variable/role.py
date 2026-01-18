"""
Variable roles semantic definitions.

Semantic classification system for variables in the Procela framework.

Defines four fundamental roles that determine how variables behave and are
processed throughout the reasoning pipeline:

ENDOGENOUS: System-determined variables (effects, dependent variables)
EXOGENOUS: Externally-determined variables (causes, independent variables)
CONTROL: Manipulable decision variables (parameters, knobs)
DERIVED: Computed or aggregated variables (outputs, metrics)

Roles influence reasoning strategies, constraint validation, visualization
selection, and error detection. Each Variable instance is assigned a role
that guides its treatment in all system components.

See: https://procela.org/docs/semantics/core/variable/roles/
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
    >>> from procela.core.variable import VariableRole
    >>>
    >>> for role in VariableRole:
    ...     print(role)
    """

    ENDOGENOUS = auto()
    EXOGENOUS = auto()
    CONTROL = auto()
    DERIVED = auto()
