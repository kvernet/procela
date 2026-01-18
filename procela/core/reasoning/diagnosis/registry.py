"""
Diagnoser Registry Module for the Procela Framework.

This module provides a centralized registry for managing diagnostic reasoner classes.
It enables dynamic registration, instantiation, and management of diagnoser
implementations while maintaining type safety and proper error handling.
"""

from __future__ import annotations

from typing import Any, Type

from .anomaly import AnomalyDiagnoser
from .base import Diagnoser
from .statistical import StatisticalDiagnoser
from .trend import TrendDiagnoser

_DIAGNOSER_REGISTRY: dict[str, Type[Diagnoser]] = {
    "anomaly": AnomalyDiagnoser,
    "statistical": StatisticalDiagnoser,
    "trend": TrendDiagnoser,
}


def get_diagnoser(name: str, **kwargs: Any) -> Diagnoser:
    """
    Instantiate a diagnoser by name with optional constructor arguments.

    Parameters
    ----------
    name : str
        The registered name of the diagnoser to instantiate.
    **kwargs : Any
        Keyword arguments to pass to the diagnoser constructor.

    Returns
    -------
    Diagnoser
        An instance of the requested diagnoser class.

    Raises
    ------
    KeyError
        If the requested diagnoser name is not found in the registry.
    TypeError
        If the diagnoser instantiation fails due to invalid arguments.

    Examples
    --------
    >>> from procela.core.reasoning import TrendDiagnoser, get_diagnoser
    >>>
    >>> diagnoser = get_diagnoser("trend", significance_threshold=0.3)
    >>> isinstance(diagnoser, TrendDiagnoser)
    True
    """
    if name not in _DIAGNOSER_REGISTRY:
        available = ", ".join(sorted(_DIAGNOSER_REGISTRY.keys()))
        raise KeyError(
            f"Diagnoser '{name}' not found. Available diagnosers: {available}"
        )

    diagnoser_class = _DIAGNOSER_REGISTRY[name]
    try:
        return diagnoser_class(**kwargs)
    except TypeError as e:
        # Provide more informative error message
        raise TypeError(
            f"Failed to instantiate diagnoser '{name}' with arguments {kwargs}: {e}"
        ) from e


def register_diagnoser(name: str, diagnoser_class: Type[Diagnoser]) -> None:
    """
    Register a new diagnoser class in the registry.

    Parameters
    ----------
    name : str
        The name to register the diagnoser under.
    diagnoser_class : Type[Diagnoser]
        The diagnoser class to register.

    Returns
    -------
    None

    Raises
    ------
    TypeError
        If diagnoser_class is not a class or not a subclass of Diagnoser.
    ValueError
        If the name is already registered.

    Examples
    --------
    >>> from procela.core.reasoning import (
    ...     Diagnoser, register_diagnoser, available_diagnosers
    ... )
    >>>
    >>> class CustomDiagnoser(Diagnoser):
    ...     pass
    >>> register_diagnoser("custom", CustomDiagnoser)
    >>> "custom" in available_diagnosers()
    True
    """
    if not isinstance(diagnoser_class, type):
        raise TypeError(
            f"diagnoser_class must be a class, got {type(diagnoser_class).__name__}"
        )

    # Check if it's a proper Diagnoser subclass
    if not issubclass(diagnoser_class, Diagnoser):
        raise TypeError(
            f"diagnoser_class must be a subclass of Diagnoser, "
            f"got {diagnoser_class.__name__}"
        )

    # Check for name collision
    if name in _DIAGNOSER_REGISTRY:
        raise ValueError(
            f"Diagnoser name '{name}' is already registered. "
            f"Use a different name or unregister the existing diagnoser first."
        )

    _DIAGNOSER_REGISTRY[name] = diagnoser_class


def unregister_diagnoser(name: str) -> Type[Diagnoser]:
    """
    Remove a diagnoser from the registry and return its class.

    Parameters
    ----------
    name : str
        The name of the diagnoser to unregister.

    Returns
    -------
    Type[Diagnoser]
        The unregistered diagnoser class.

    Raises
    ------
    KeyError
        If the diagnoser name is not found in the registry.

    Examples
    --------
    >>> from procela.core.reasoning import unregister_diagnoser, available_diagnosers
    >>>
    >>> diagnoser_class = unregister_diagnoser("trend")
    >>> diagnoser_class
    <class 'procela.core.reasoning.diagnosis.trend.TrendDiagnoser'>
    >>> "trend" in available_diagnosers()
    False
    """
    if name not in _DIAGNOSER_REGISTRY:
        available = ", ".join(sorted(_DIAGNOSER_REGISTRY.keys()))
        raise KeyError(
            f"Cannot unregister diagnoser '{name}': not found in registry. "
            f"Available diagnosers: {available}"
        )

    return _DIAGNOSER_REGISTRY.pop(name)


def get_diagnosers() -> dict[str, Type[Diagnoser]]:
    """
    Get a copy of the current diagnoser registry.

    Returns
    -------
    dict[str, Type[Diagnoser]]
        A copy of the registry dictionary mapping names to diagnoser classes.

    Notes
    -----
    Returns a copy to prevent external modification of the internal registry.

    Examples
    --------
    >>> from procela.core.reasoning import get_diagnosers
    >>>
    >>> registry = get_diagnosers()
    >>> isinstance(registry, dict)
    True
    >>> "anomaly" in registry
    True
    """
    return _DIAGNOSER_REGISTRY.copy()


def available_diagnosers() -> set[str]:
    """
    Get the set of available diagnoser names.

    Returns
    -------
    set[str]
        A set of registered diagnoser names.

    Examples
    --------
    >>> from procela.core.reasoning import available_diagnosers
    >>>
    >>> names = available_diagnosers()
    >>> isinstance(names, set)
    True
    >>> "statistical" in names
    True
    """
    return set(_DIAGNOSER_REGISTRY.keys())


def clear_diagnoser_registry() -> None:
    """
    Clear all entries from the diagnoser registry.

    Returns
    -------
    None

    Warnings
    --------
    This operation cannot be undone. Use with caution in production code.

    Examples
    --------
    >>> from procela.core.reasoning import (
    ...     clear_diagnoser_registry, available_diagnosers
    ... )
    >>>
    >>> clear_diagnoser_registry()
    >>> len(available_diagnosers())
    0
    """
    _DIAGNOSER_REGISTRY.clear()


def has_diagnoser(name: str) -> bool:
    """
    Check if a diagnoser is registered under the given name.

    Parameters
    ----------
    name : str
        The name to check in the registry.

    Returns
    -------
    bool
        True if the diagnoser is registered, False otherwise.

    Examples
    --------
    >>> from procela.core.reasoning import has_diagnoser
    >>>
    >>> has_diagnoser("trend")
    True
    >>> has_diagnoser("unknown")
    False
    """
    return name in _DIAGNOSER_REGISTRY
