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

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/prediction/

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/prediction/
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
