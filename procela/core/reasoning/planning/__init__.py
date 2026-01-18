"""
Planning subsystem for Procela's active reasoning engine.

The planning module provides the core infrastructure for generating
intelligent interventions in real-world systems. It implements a framework
where planners analyze system state, diagnose issues, consider predictions,
and propose actions to optimize behavior while respecting constraints and
resource limitations.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/planning/

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/planning/
"""

from .base import Planner
from .operator import PlanningOperator
from .preventive import PreventivePlanner
from .reactive import ReactivePlanner
from .registry import (
    _PLANNER_REGISTRY,
    available_planners,
    clear_planner_registry,
    get_planner,
    get_planners,
    has_planner,
    register_planner,
    unregister_planner,
)

__all__ = [
    # Core planner classes
    "Planner",
    "PlanningOperator",
    "PreventivePlanner",
    "ReactivePlanner",
    # Registry functions
    "get_planner",
    "register_planner",
    "unregister_planner",
    "get_planners",
    "available_planners",
    "clear_planner_registry",
    "has_planner",
    # Internal registry (exported for advanced use)
    "_PLANNER_REGISTRY",
]
