"""
Planning subsystem for Procela's active reasoning engine.

The planning module provides the core infrastructure for generating
intelligent interventions in real-world systems. It implements a framework
where planners analyze system state, diagnose issues, consider predictions,
and propose actions to optimize behavior while respecting constraints and
resource limitations.

Key Components
--------------
- **Planner**: Abstract base class defining the planner interface
- **PreventivePlanner**: Proactive planner focusing on early detection
- **ReactivePlanner**: Responsive planner addressing confirmed issues
- **Registry**: Dynamic system for managing and discovering planners

Architecture Overview
--------------------
The planning subsystem follows a modular design where:
1. Planners implement specific strategies for intervention generation
2. The registry allows dynamic discovery and instantiation of planners
3. All planners share a common interface defined by the base class
4. Planning results include actionable proposals with confidence metrics

Usage Example
-------------
>>> from procela.core.reasoning import (
...     get_planner, PreventivePlanner, ReactivePlanner
... )
>>>
>>> # Get a planner from the registry
>>> preventive = get_planner("preventive", priority=5)
>>> reactive = get_planner("reactive", priority=3)
>>>
>>> # Or instantiate directly
>>> custom_preventive = PreventivePlanner(priority=7)
>>> custom_reactive = ReactivePlanner(priority=4, enabled=False)
>>>
>>> # Check available planners
>>> from procela.core.reasoning import available_planners
>>> print(f"Available planners: {available_planners()}")
Available planners: {'preventive', 'reactive'}

Module Organization
-------------------
The module is organized as follows:
- `base.py`: Abstract base class and core planner infrastructure
- `preventive.py`: Preventive planning strategy implementation
- `reactive.py`: Reactive planning strategy implementation
- `registry.py`: Dynamic planner registration and discovery system
- `__init__.py`: Module exports and documentation (this file)

Typical Workflow
----------------
1. Obtain a planning view with system state, diagnosis, and predictions
2. Select appropriate planner(s) based on the situation
3. Execute planner(s) to generate action proposals
4. Validate and filter proposals based on constraints
5. Execute recommended actions in the target system

Planner Selection Guidelines
----------------------------
- Use **PreventivePlanner** for:
  - Early warning signals present in predictions
  - Proactive risk mitigation scenarios
  - Systems where prevention is cheaper than cure

- Use **ReactivePlanner** for:
  - Confirmed diagnosis with identified causes
  - Immediate intervention requirements
  - Situations requiring direct issue resolution

Notes
-----
- All planners maintain execution counts for monitoring and debugging
- Planning results include metadata about the generating planner
- The registry system supports dynamic extension with custom planners
- Multiple planners can be chained or run in parallel for complex scenarios

See Also
--------
procela.core.variable : Active reasoning entity in Procela

References
----------
[1] Procela Framework Documentation: Active Reasoning Systems
[2] Mechanistic Diagnostic Patterns for Real-World Systems
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

# Module-level documentation for Sphinx/autodoc
__docformat__ = "numpy"
