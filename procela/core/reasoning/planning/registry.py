"""
Planner registry module for Procela's active reasoning engine.

This module provides a registry system for managing different planner types
in the Procela framework. It allows dynamic registration, instantiation,
and management of planner classes with proper validation and error handling.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/planning/registry.html

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/planning/registry.html
"""

from __future__ import annotations

from typing import Any, Type

from .base import Planner
from .preventive import PreventivePlanner
from .reactive import ReactivePlanner

_PLANNER_REGISTRY: dict[str, Type[Planner]] = {
    "preventive": PreventivePlanner,
    "reactive": ReactivePlanner,
}


def get_planner(name: str, **kwargs: Any) -> Planner:
    """
    Instantiate a planner by name with the given keyword arguments.

    This function looks up a planner class by its registered name and
    creates an instance with the provided keyword arguments.

    Parameters
    ----------
    name : str
        The registered name of the planner to instantiate.
    **kwargs : Any
        Keyword arguments to pass to the planner constructor.

    Returns
    -------
    Planner
        An instance of the requested planner class.

    Raises
    ------
    KeyError
        If the planner name is not found in the registry.
    TypeError
        If the planner cannot be instantiated with the provided arguments.
    """
    if name not in _PLANNER_REGISTRY:
        available = ", ".join(sorted(_PLANNER_REGISTRY.keys()))
        raise KeyError(f"Planner '{name}' not found. Available planners: {available}")

    planner_class = _PLANNER_REGISTRY[name]
    try:
        return planner_class(**kwargs)
    except TypeError as e:
        # Provide more informative error message
        raise TypeError(
            f"Failed to instantiate planner '{name}' with arguments {kwargs}: {e}"
        ) from e


def register_planner(name: str, planner_class: Type[Planner]) -> None:
    """
    Register a new planner class in the registry.

    This function adds a planner class to the registry under the specified
    name. The class is validated to ensure it is a proper subclass of Planner.

    Parameters
    ----------
    name : str
        The name to register the planner under.
    planner_class : Type[Planner]
        The planner class to register.

    Raises
    ------
    TypeError
        If planner_class is not a class or not a subclass of Planner.
    ValueError
        If the name is already registered in the registry.
    """
    if not isinstance(planner_class, type):
        raise TypeError(
            f"planner_class must be a class, got {type(planner_class).__name__}"
        )

    # Check if it's a proper planner subclass
    if not issubclass(planner_class, Planner):
        raise TypeError(
            f"planner_class must be a subclass of planner, "
            f"got {planner_class.__name__}"
        )

    # Check for name collision
    if name in _PLANNER_REGISTRY:
        raise ValueError(
            f"planner name '{name}' is already registered. "
            f"Use a different name or unregister the existing planner first."
        )

    _PLANNER_REGISTRY[name] = planner_class


def unregister_planner(name: str) -> Type[Planner]:
    """
    Remove a planner from the registry and return its class.

    This function removes a planner class from the registry by name and
    returns the removed class.

    Parameters
    ----------
    name : str
        The name of the planner to unregister.

    Returns
    -------
    Type[Planner]
        The planner class that was removed from the registry.

    Raises
    ------
    KeyError
        If the planner name is not found in the registry.
    """
    if name not in _PLANNER_REGISTRY:
        available = ", ".join(sorted(_PLANNER_REGISTRY.keys()))
        raise KeyError(
            f"Cannot unregister planner '{name}': not found in registry. "
            f"Available planners: {available}"
        )

    return _PLANNER_REGISTRY.pop(name)


def get_planners() -> dict[str, Type[Planner]]:
    """
    Get a copy of the entire planner registry.

    Returns a shallow copy of the registry dictionary, preventing
    modifications to the internal registry while allowing inspection.

    Returns
    -------
    dict[str, Type[Planner]]
        A copy of the planner registry dictionary.
    """
    return _PLANNER_REGISTRY.copy()


def available_planners() -> set[str]:
    """
    Get the set of all registered planner names.

    Returns
    -------
    set[str]
        A set containing all registered planner names.
    """
    return set(_PLANNER_REGISTRY.keys())


def clear_planner_registry() -> None:
    """
    Clear all planners from the registry.

    This function removes all registered planners from the registry,
    returning it to an empty state.

    Warning
    -------
    This action cannot be undone. Use with caution, especially in
    production environments or shared contexts.
    """
    _PLANNER_REGISTRY.clear()


def has_planner(name: str) -> bool:
    """
    Check if a planner is registered under the given name.

    Parameters
    ----------
    name : str
        The name to check in the registry.

    Returns
    -------
    bool
        True if the planner is registered, False otherwise.
    """
    return name in _PLANNER_REGISTRY
