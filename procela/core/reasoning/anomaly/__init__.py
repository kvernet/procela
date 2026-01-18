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

Modules
-------
base : Abstract base class `AnomalyDetector` defining the common interface
       for all anomaly detection algorithms.
ewma : `EWMADetector` class implementing Exponentially Weighted Moving
       Average based anomaly detection.
zscore : `ZScoreDetector` class implementing Z-Score statistical anomaly
         detection.
registry : Central registry and factory functions for managing and
           instantiating anomaly detectors.

Classes
-------
AnomalyDetector : ABC defining the interface for all anomaly detectors.
EWMADetector : Detects anomalies using EWMA (Exponentially Weighted Moving
               Average) statistics precomputed by HistoryStatistics.
ZScoreDetector : Detects anomalies using Z-Score (standard score) method
                 comparing values to historical mean and standard deviation.

Functions
---------
get_detector(name, **kwargs) : Factory function to create detector instances.
register_detector(name, detector_class) : Register new detector implementations.
unregister_detector(name) : Remove a detector from the registry.
available_detectors() : Get names of all available detectors.
get_detectors() : Get copy of the detector registry.
has_detector(name) : Check if a detector is registered.
clear_registry() : Clear all registered detectors (primarily for testing).

Usage Examples
--------------
>>> from procela.core.reasoning import get_detector
>>> from procela.core.memory import HistoryStatistics
>>>
>>> # Get a Z-Score detector
>>> detector = get_detector("z-score", threshold=2.5)
>>> # Analyze statistics
>>> stats = HistoryStatistics(
...     count=10, sum=1000.0, sumsq=100250.0,
...     min=None, max=None, last_value=115.0,
...     confidence_sum=None, ewma=None,
...     sources=frozenset()
... )
>>> result = detector.detect(stats)
>>> result.is_anomaly  # abs(115-100)/5 = 3.0 > 2.5 threshold
True
>>> # List available methods
>>> from procela.core.reasoning import available_detectors
>>>
>>> methods = available_detectors()
>>> sorted(methods)
['ewma', 'z-score']

Notes
-----
All detectors operate on `HistoryStatistics` objects, leveraging the
framework's centralized statistical computation. This design ensures
consistency and efficiency across different detection methods.

The module supports runtime extension through the registry system, allowing
research experiments with new detection algorithms without modifying core
framework code.

See Also
--------
procela.core.reasoning.result : Result containers for anomaly detection.
procela.core.memory.variable.statistics : Statistical data used by detectors.
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
