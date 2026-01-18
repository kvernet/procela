"""
Predictor Registry Module for the Procela Framework.

This module provides a centralized registry for managing predictor classes within
the Procela prediction system. It enables dynamic registration, instantiation,
and management of predictor implementations while maintaining type safety and
proper error handling. The registry follows the factory pattern to decouple
predictor creation from usage.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/prediction/registry.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/reasoning/prediction/registry.html
"""

from __future__ import annotations

from typing import Any, Type

from .base import Predictor
from .ewma import EWMAPredictor
from .last import LastPredictor
from .mean import MeanPredictor
from .trend import TrendPredictor

_PREDICTOR_REGISTRY: dict[str, Type[Predictor]] = {
    "ewma": EWMAPredictor,
    "last": LastPredictor,
    "mean": MeanPredictor,
    "trend": TrendPredictor,
}


def get_predictor(name: str, **kwargs: Any) -> Predictor:
    """
    Instantiate a predictor by name with optional constructor arguments.

    Parameters
    ----------
    name : str
        The registered name of the predictor to instantiate (e.g., "ewma", "last").
    **kwargs : Any
        Keyword arguments to pass to the predictor constructor.

    Returns
    -------
    Predictor
        An instance of the requested predictor class.

    Raises
    ------
    KeyError
        If the requested predictor name is not found in the registry.
    TypeError
        If the predictor instantiation fails due to invalid arguments.
    """
    if name not in _PREDICTOR_REGISTRY:
        available = ", ".join(sorted(_PREDICTOR_REGISTRY.keys()))
        raise KeyError(
            f"Predictor '{name}' not found. Available predictors: {available}"
        )

    predictor_class = _PREDICTOR_REGISTRY[name]
    try:
        return predictor_class(**kwargs)
    except TypeError as e:
        # Provide more informative error message
        raise TypeError(
            f"Failed to instantiate predictor '{name}' with arguments {kwargs}: {e}"
        ) from e


def register_predictor(name: str, predictor_class: Type[Predictor]) -> None:
    """
    Register a new predictor class in the registry.

    Parameters
    ----------
    name : str
        The name to register the predictor under.
    predictor_class : Type[Predictor]
        The predictor class to register.

    Returns
    -------
    None

    Raises
    ------
    TypeError
        If predictor_class is not a class or not a subclass of Predictor.
    ValueError
        If the name is already registered.
    """
    if not isinstance(predictor_class, type):
        raise TypeError(
            "predictor_class must be a class, " f"got {type(predictor_class).__name__}"
        )

    # Check if it's a proper Predictor subclass
    if not issubclass(predictor_class, Predictor):
        raise TypeError(
            f"predictor_class must be a subclass of Predictor, "
            f"got {predictor_class.__name__}"
        )

    # Check for name collision
    if name in _PREDICTOR_REGISTRY:
        raise ValueError(
            f"Predictor name '{name}' is already registered. "
            f"Use a different name or unregister the existing predictor first."
        )

    _PREDICTOR_REGISTRY[name] = predictor_class


def unregister_predictor(name: str) -> Type[Predictor]:
    """
    Remove a predictor from the registry and return its class.

    Parameters
    ----------
    name : str
        The name of the predictor to unregister.

    Returns
    -------
    Type[Predictor]
        The unregistered predictor class.

    Raises
    ------
    KeyError
        If the predictor name is not found in the registry.
    """
    if name not in _PREDICTOR_REGISTRY:
        available = ", ".join(sorted(_PREDICTOR_REGISTRY.keys()))
        raise KeyError(
            f"Cannot unregister predictor '{name}': not found in registry. "
            f"Available predictors: {available}"
        )

    return _PREDICTOR_REGISTRY.pop(name)


def get_predictors() -> dict[str, Type[Predictor]]:
    """
    Get a copy of the current predictor registry.

    Returns
    -------
    dict[str, Type[Predictor]]
        A copy of the registry dictionary mapping names to predictor classes.

    Notes
    -----
    Returns a copy to prevent external modification of the internal registry.
    """
    return _PREDICTOR_REGISTRY.copy()


def available_predictors() -> set[str]:
    """
    Get the set of available predictor names.

    Returns
    -------
    set[str]
        A set of registered predictor names.
    """
    return set(_PREDICTOR_REGISTRY.keys())


def clear_predictor_registry() -> None:
    """
    Clear all entries from the predictor registry.

    Returns
    -------
    None

    Warnings
    --------
    This operation cannot be undone. Use with caution in production code.
    """
    _PREDICTOR_REGISTRY.clear()


def has_predictor(name: str) -> bool:
    """
    Check if a predictor is registered under the given name.

    Parameters
    ----------
    name : str
        The name to check in the registry.

    Returns
    -------
    bool
        True if the predictor is registered, False otherwise.
    """
    return name in _PREDICTOR_REGISTRY
