"""
Anomaly Detection Module for the Procela Framework.

This module provides a comprehensive suite of anomaly detection algorithms
and utilities for identifying deviations from expected behavior in system
variables. As part of Procela's active reasoning engine, these detectors
enable variables to reason and identify potential issues, forming the
foundation for diagnostic reasoning and proactive system management.

The module follows a plugin architecture where new detection algorithms
can be easily registered and discovered through the central registry,
supporting Procela's goal of flexible, extensible reasoning capabilities.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/anomaly/

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/anomaly/
"""

from .base import AnomalyDetector
from .ewma import EWMADetector
from .operator import AnomalyOperator, AnomalyOperatorThreshold
from .registry import (
    _ANOMALY_DETECTORS,
    available_detectors,
    clear_detector_registry,
    get_detector,
    get_detectors,
    has_detector,
    register_detector,
    unregister_detector,
)
from .zscore import ZScoreDetector

__all__ = [
    "AnomalyDetector",
    "EWMADetector",
    "AnomalyOperator",
    "AnomalyOperatorThreshold",
    "ZScoreDetector",
    "get_detector",
    "register_detector",
    "unregister_detector",
    "get_detectors",
    "available_detectors",
    "clear_detector_registry",
    "has_detector",
    "_ANOMALY_DETECTORS",
]
