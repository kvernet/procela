"""
Diagnosis Package for the Procela Framework.

This package provides diagnostic reasoning capabilities for the Procela framework.
It contains various diagnostic reasoners that analyze system states, detect anomalies,
identify trends, and perform statistical analysis to determine potential issues
and their root causes.

The diagnosis system follows a modular architecture where different reasoners
can be combined to provide comprehensive diagnostic insights. Each reasoner
specializes in a specific aspect of system analysis and contributes to the
overall diagnostic process.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/diagnosis/

Examples Reference
------------------
https://procela.org/docs/examples/core/reasoning/diagnosis/
"""

from .anomaly import AnomalyDiagnoser
from .base import Diagnoser
from .operator import (
    DiagnosisOperator,
    DiagnosisOperatorThreshold,
    TrendOperator,
    TrendOperatorThreshold,
)
from .registry import (
    _DIAGNOSER_REGISTRY,
    available_diagnosers,
    clear_diagnoser_registry,
    get_diagnoser,
    get_diagnosers,
    has_diagnoser,
    register_diagnoser,
    unregister_diagnoser,
)
from .statistical import StatisticalDiagnoser
from .trend import TrendDiagnoser

__all__ = [
    # Classes
    "Diagnoser",
    "AnomalyDiagnoser",
    "TrendOperator",
    "TrendOperatorThreshold",
    "DiagnosisOperator",
    "DiagnosisOperatorThreshold",
    "StatisticalDiagnoser",
    "TrendDiagnoser",
    # Registry functions
    "get_diagnoser",
    "register_diagnoser",
    "unregister_diagnoser",
    "get_diagnosers",
    "available_diagnosers",
    "clear_diagnoser_registry",
    "has_diagnoser",
    "_DIAGNOSER_REGISTRY",
]
