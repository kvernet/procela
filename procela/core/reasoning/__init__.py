"""
Core reasoning engine for Procela's active reasoning framework.

The reasoning module implements the intelligent core of the Procela system,
providing mechanisms for anomaly detection, trend analysis, diagnosis,
prediction, and planning. These components work together to transform raw
system data into actionable insights through stateful, resource-aware,
constraint-respecting reasoning processes.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/reasoning/

Examples Reference
-------------------
https://procela.org/docs/examples/core/reasoning/
"""

from .anomaly import (
    _ANOMALY_DETECTORS,
    AnomalyDetector,
    AnomalyOperator,
    AnomalyOperatorThreshold,
    EWMADetector,
    ZScoreDetector,
    available_detectors,
    clear_detector_registry,
    get_detector,
    get_detectors,
    has_detector,
    register_detector,
    unregister_detector,
)
from .diagnosis import (
    _DIAGNOSER_REGISTRY,
    AnomalyDiagnoser,
    Diagnoser,
    DiagnosisOperator,
    DiagnosisOperatorThreshold,
    StatisticalDiagnoser,
    TrendDiagnoser,
    TrendOperator,
    TrendOperatorThreshold,
    available_diagnosers,
    clear_diagnoser_registry,
    get_diagnoser,
    get_diagnosers,
    has_diagnoser,
    register_diagnoser,
    unregister_diagnoser,
)
from .prediction import (
    _PREDICTOR_REGISTRY,
    EWMAPredictor,
    LastPredictor,
    MeanPredictor,
    PredictionOperator,
    Predictor,
    TrendPredictor,
    available_predictors,
    clear_predictor_registry,
    get_predictor,
    get_predictors,
    has_predictor,
    register_predictor,
    unregister_predictor,
)

__all__ = [
    # Anomaly Detection Components
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
    # Diagnosis Components
    "Diagnoser",
    "AnomalyDiagnoser",
    "TrendOperator",
    "TrendOperatorThreshold",
    "DiagnosisOperator",
    "DiagnosisOperatorThreshold",
    "StatisticalDiagnoser",
    "TrendDiagnoser",
    "get_diagnoser",
    "register_diagnoser",
    "unregister_diagnoser",
    "get_diagnosers",
    "available_diagnosers",
    "clear_diagnoser_registry",
    "has_diagnoser",
    "_DIAGNOSER_REGISTRY",
    # Prediction Components
    "Predictor",
    "EWMAPredictor",
    "LastPredictor",
    "PredictionOperator",
    "MeanPredictor",
    "TrendPredictor",
    "get_predictor",
    "register_predictor",
    "unregister_predictor",
    "get_predictors",
    "available_predictors",
    "clear_predictor_registry",
    "has_predictor",
    "_PREDICTOR_REGISTRY",
]
