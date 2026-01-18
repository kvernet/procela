"""
Anomaly Detector Registry for the Procela Framework.

This module provides a centralized registry for all available anomaly detection
algorithms within the Procela framework. The registry enables dynamic discovery,
instantiation, and management of anomaly detectors through a uniform interface,
supporting the framework's goal of flexible, pluggable reasoning components.

The registry implements the Factory and Registry design patterns, allowing
the system to decouple detector implementation from usage and enabling
runtime configuration of detection strategies.
"""

from __future__ import annotations

from typing import Any, Callable, Type

from .base import AnomalyDetector
from .ewma import EWMADetector
from .zscore import ZScoreDetector

# Type alias for cleaner type hints
AnomalyDetectorConstructor = Callable[..., AnomalyDetector]


# Global registry of available anomaly detectors
_ANOMALY_DETECTORS: dict[str, Type[AnomalyDetector]] = {
    "ewma": EWMADetector,
    "z-score": ZScoreDetector,
}


def get_detector(name: str, **kwargs: Any) -> AnomalyDetector:
    """
    Create an instance of a registered anomaly detector.

    This function provides the primary interface for dynamically instantiating
    anomaly detectors. It looks up the detector class by name in the registry
    and instantiates it with the provided keyword arguments.

    Parameters
    ----------
    name : str
        The name of the anomaly detector to instantiate. Must be a key
        in the `_ANOMALY_DETECTORS` registry.
    **kwargs : Any
        Keyword arguments to pass to the detector's constructor. These are
        detector-specific parameters (e.g., `threshold` for ZScoreDetector).

    Returns
    -------
    AnomalyDetector
        An instance of the requested anomaly detector, initialized with
        the provided arguments.

    Raises
    ------
    KeyError
        If the requested detector name is not found in the registry.
    TypeError
        If the provided keyword arguments are incompatible with the
        detector's constructor.

    Examples
    --------
    >>> from procela.core.reasoning import get_detector
    >>>
    >>> # Create a Z-Score detector with custom threshold
    >>> detector = get_detector("z-score", threshold=2.5)
    >>> detector.name
    'ZScoreDetector'
    >>> detector.threshold
    2.5
    >>> # Create an EWMA detector with default parameters
    >>> ewma_detector = get_detector("ewma")
    >>> ewma_detector.name
    'EWMADetector'

    See Also
    --------
    register_detector : Register a new anomaly detector.
    detectors_available : Get all available detector names.
    """
    if name not in _ANOMALY_DETECTORS:
        available = ", ".join(sorted(_ANOMALY_DETECTORS.keys()))
        raise KeyError(
            f"Anomaly detector '{name}' not found. " f"Available detectors: {available}"
        )

    detector_class = _ANOMALY_DETECTORS[name]
    try:
        return detector_class(**kwargs)
    except TypeError as e:
        # Provide more informative error message
        raise TypeError(
            f"Failed to instantiate detector '{name}' with arguments {kwargs}: {e}"
        ) from e


def register_detector(name: str, detector_class: Type[AnomalyDetector]) -> None:
    """
    Register a new anomaly detector class in the global registry.

    This function enables runtime extension of the Procela framework by
    allowing new anomaly detection algorithms to be dynamically added.
    Registered detectors become immediately available through `get_detector`.

    Parameters
    ----------
    name : str
        A unique identifier for the detector. This will be used as the key
        to retrieve the detector from the registry. Should be descriptive
        and follow the naming convention of existing detectors (lowercase
        with hyphens for multi-word names, e.g., "isolation-forest").
    detector_class : Type[AnomalyDetector]
        The detector class to register. Must be a subclass of `AnomalyDetector`
        and implement the required interface.

    Raises
    ------
    TypeError
        If `detector_class` is not a subclass of `AnomalyDetector`.
    ValueError
        If `name` is already registered.

    Examples
    --------
    >>> from procela.core.reasoning import (
    ...     AnomalyDetector, register_detector, get_detector
    ... )
    >>>
    >>> # Define a custom detector
    >>> class MyCustomDetector(AnomalyDetector):
    ...     name = "MyCustomDetector"
    ...     def __init__(self, sensitivity=1.0):
    ...         self.sensitivity = sensitivity
    ...     def detect(self, stats):
    ...         # Implementation omitted
    ...         pass
    >>> # Register the custom detector
    >>> register_detector("custom", MyCustomDetector)
    >>> # Now it can be instantiated through the registry
    >>> detector = get_detector("custom", sensitivity=0.8)
    >>> detector.name
    'MyCustomDetector'

    Notes
    -----
    For production systems, consider adding validation to ensure the
    detector class properly implements the `AnomalyDetector` interface
    (has `name` class attribute and `detect` method).
    """
    if not isinstance(detector_class, type):
        raise TypeError(
            f"detector_class must be a class, got {type(detector_class).__name__}"
        )

    # Check if it's a proper AnomalyDetector subclass
    if not issubclass(detector_class, AnomalyDetector):
        raise TypeError(
            f"detector_class must be a subclass of AnomalyDetector, "
            f"got {detector_class.__name__}"
        )

    # Check for name collision
    if name in _ANOMALY_DETECTORS:
        raise ValueError(
            f"Detector name '{name}' is already registered. "
            f"Use a different name or unregister the existing detector first."
        )

    _ANOMALY_DETECTORS[name] = detector_class


def unregister_detector(name: str) -> Type[AnomalyDetector]:
    """
    Remove an anomaly detector from the registry.

    This function allows dynamic removal of detectors from the registry,
    which can be useful for testing, hot-reloading, or runtime reconfiguration.

    Parameters
    ----------
    name : str
        The name of the detector to remove from the registry.

    Returns
    -------
    Type[AnomalyDetector]
        The detector class that was removed from the registry.

    Raises
    ------
    KeyError
        If the detector name is not found in the registry.

    Examples
    --------
    >>> from procela.core.reasoning import unregister_detector, get_detector
    >>>
    >>> # Remove a detector (e.g., for testing or reconfiguration)
    >>> detector_class = unregister_detector("z-score")
    >>> detector_class.__name__
    'ZScoreDetector'
    >>> # Attempting to get it now will raise KeyError
    >>> try:
    ...     get_detector("z-score")
    ... except KeyError as e:
    ...     print(f"Detector not found: {e}")
    Detector not found: "Anomaly detector 'z-score' not found. Available ...
    """
    if name not in _ANOMALY_DETECTORS:
        available = ", ".join(sorted(_ANOMALY_DETECTORS.keys()))
        raise KeyError(
            f"Cannot unregister detector '{name}': not found in registry. "
            f"Available detectors: {available}"
        )

    return _ANOMALY_DETECTORS.pop(name)


def get_detectors() -> dict[str, Type[AnomalyDetector]]:
    """
    Get a copy of the current detector registry.

    Returns a dictionary containing all currently registered anomaly detectors.
    The returned dictionary is a copy to prevent accidental modification of
    the internal registry state.

    Returns
    -------
    dict[str, Type[AnomalyDetector]]
        A dictionary mapping detector names to their class objects.

    Examples
    --------
    >>> from procela.core.reasoning import get_detectors
    >>>
    >>> detectors = get_detectors()
    >>> sorted(detectors.keys())
    ['ewma', 'z-score']
    >>> detectors['z-score'].__name__
    'ZScoreDetector'
    """
    return _ANOMALY_DETECTORS.copy()


def available_detectors() -> set[str]:
    """
    Get the names of all available anomaly detection methods.

    This function provides a convenient way to discover what anomaly
    detectors are available in the system. It returns a set of detector
    names that can be used with `get_detector`.

    Returns
    -------
    set[str]
        A set containing the names of all registered anomaly detectors.

    Examples
    --------
    >>> from procela.core.reasoning import available_detectors
    >>>
    >>> methods = available_detectors()
    >>> isinstance(methods, set)
    True
    >>> "z-score" in methods
    True
    >>> "ewma" in methods
    True
    """
    return set(_ANOMALY_DETECTORS.keys())


def clear_detector_registry() -> None:
    """
    Clear all registered detectors from the registry.

    This function is primarily useful for testing, allowing test suites
    to start with a clean registry state. Use with caution in production
    as it will remove all registered detectors.

    Examples
    --------
    >>> from procela.core.reasoning import clear_detector_registry, available_detectors
    >>>
    >>> # Clear all detectors (e.g., before loading new configuration)
    >>> clear_detector_registry()
    >>> available_detectors()
    set()
    """
    _ANOMALY_DETECTORS.clear()


def has_detector(name: str) -> bool:
    """
    Check if a detector with the given name is registered.

    Parameters
    ----------
    name : str
        The name of the detector to check.

    Returns
    -------
    bool
        True if a detector with the given name is registered, False otherwise.

    Examples
    --------
    >>> from procela.core.reasoning import has_detector
    >>>
    >>> has_detector("z-score")
    True
    >>> has_detector("nonexistent")
    False
    """
    return name in _ANOMALY_DETECTORS
