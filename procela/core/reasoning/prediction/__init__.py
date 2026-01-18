"""
Prediction Module for the Procela Framework.

This module provides a comprehensive suite of predictors for forecasting
future variable values based on epistemic data within the Procela framework.
It implements various prediction strategies ranging from simple persistence
models to sophisticated trend-based approaches, all following the active
reasoning paradigm of the Procela system.

The module is organized around a registry-based factory pattern that allows
for dynamic discovery, instantiation, and management of predictor implementations.
This architecture supports extensibility while maintaining type safety and
consistent interfaces across all predictors.

Modules
-------
base : Abstract base classes and interfaces
    Defines the `Predictor` abstract base class that all concrete predictors
    must implement.
ewma : Exponentially Weighted Moving Average predictor
    Implements forecasting using pre-computed EWMA statistics.
last : Last value predictor
    Implements a persistence model using the most recent observed value.
mean : Mean value predictor
    Implements forecasting using the historical arithmetic mean.
trend : Trend-based predictor
    Implements forecasting using pre-computed trend analysis.
registry : Predictor registry and factory
    Provides centralized management, registration, and instantiation of predictors.

Classes
-------
Predictor : ABC
    Abstract base class defining the interface for all predictors.
EWMAPredictor : Predictor
    Predictor using Exponentially Weighted Moving Average statistics.
LastPredictor : Predictor
    Predictor using the last observed value (persistence model).
MeanPredictor : Predictor
    Predictor using the historical arithmetic mean.
TrendPredictor : Predictor
    Predictor using trend direction and magnitude analysis.

Functions
---------
get_predictor(name: str, **kwargs: Any) -> Predictor
    Factory function to instantiate a predictor by its registered name.
register_predictor(name: str, predictor_class: Type[Predictor]) -> None
    Register a new predictor class in the registry.
unregister_predictor(name: str) -> Type[Predictor]
    Remove a predictor from the registry and return its class.
get_predictors() -> dict[str, Type[Predictor]]
    Get a copy of the current predictor registry.
available_predictors() -> set[str]
    Get the set of available predictor names.
clear_predictor_registry() -> None
    Clear all entries from the predictor registry.
has_predictor(name: str) -> bool
    Check if a predictor is registered under the given name.

Variables
---------
_PREDICTOR_REGISTRY : dict[str, Type[Predictor]]
    Internal registry mapping predictor names to their class implementations.
    This is exposed for advanced use cases but typically accessed through
    the public API functions.

Examples
--------
>>> from procela.core.reasoning import (
...     get_predictor, available_predictors, EWMAPredictor, Predictor
... )
>>>
>>> # Get a predictor instance from the registry
>>> ewma_predictor = get_predictor("ewma", alpha=0.3)
>>> isinstance(ewma_predictor, EWMAPredictor)
True
>>> isinstance(ewma_predictor, Predictor)
True
>>>
>>> # Check available predictors
>>> available = available_predictors()
>>> isinstance(available, set)
True
>>> "ewma" in available
True
>>> "last" in available
True
>>>
>>> # Use the predictor
>>> # Assuming we have a PredictionView with data
>>> # predictions = ewma_predictor.predict(view, horizon=5)

Notes
-----
1. All predictors follow the active reasoning paradigm of Procela, where
   variables are intelligent entities that can analyze trends, detect anomalies,
   and explain their state in human-readable terms.

2. The prediction system leverages pre-computed statistics from the epistemic
   data layer for efficient, real-time forecasting without redundant computation.

3. The registry system allows for dynamic addition of custom predictors
   without modifying the core framework, supporting the extensible nature
   of Procela.

4. Predictors are designed to work within the guaranteed feedback-loop
   consistency model of Procela, ensuring predictions respect system
   constraints and resource awareness.

5. When implementing custom predictors, ensure they inherit from `Predictor`
   and implement the `predict()` method with the correct signature.

See Also
--------
procela.core.variable : Active reasoning entity in Procela

References
----------
[1] Procela Framework Documentation: Active Reasoning Systems
[2] Mechanistic Predictive Patterns for Real-World Systems
[3] Time Series Forecasting Principles and Practices
"""

from .base import Predictor
from .ewma import EWMAPredictor
from .last import LastPredictor
from .mean import MeanPredictor
from .operator import PredictionOperator
from .registry import (
    _PREDICTOR_REGISTRY,
    available_predictors,
    clear_predictor_registry,
    get_predictor,
    get_predictors,
    has_predictor,
    register_predictor,
    unregister_predictor,
)
from .trend import TrendPredictor

__all__ = [
    "Predictor",
    "EWMAPredictor",
    "LastPredictor",
    "MeanPredictor",
    "PredictionOperator",
    "get_predictor",
    "register_predictor",
    "unregister_predictor",
    "get_predictors",
    "available_predictors",
    "clear_predictor_registry",
    "has_predictor",
    "_PREDICTOR_REGISTRY",
    "TrendPredictor",
]
