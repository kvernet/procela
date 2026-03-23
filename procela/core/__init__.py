"""
Procela core framework.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/

Examples Reference
------------------
https://procela.org/docs/examples/core/
"""

from .assessment import (
    AnomalyResult,
    DiagnosisResult,
    PredictionResult,
    ReasoningResult,
    ReasoningTask,
    StatisticsResult,
    TrendResult,
)
from .epistemic import (
    EpistemicView,
    ExecutiveView,
    VariableView,
)
from .exceptions import (
    ConfigurationError,
    ConstraintViolation,
    ExecutionError,
    InconsistentState,
    ProcelaException,
    SemanticViolation,
    TimeoutError,
)
from .executive import Executive
from .invariant import (
    InvariantCategory,
    InvariantPhase,
    InvariantSeverity,
    InvariantSoftness,
    InvariantViolation,
    InvariantViolationCritical,
    InvariantViolationFatal,
    InvariantViolationInfo,
    InvariantViolationWarning,
    SystemInvariant,
    VariableSnapshot,
)
from .key_authority import KeyAuthority
from .logger import (
    JsonFormatter,
    TextFormatter,
    setup_logging,
)
from .mechanism import (
    HomeostasisMechanism,
    Mechanism,
    MechanismTemplate,
)
from .memory import (
    HypothesisRecord,
    HypothesisState,
    MemoryStatistics,
    VariableMemory,
    VariableRecord,
)
from .policy import (
    HighestConfidencePolicy,
    ResolutionPolicy,
    ResolverPolicy,
    WeightedConfidencePolicy,
    WeightedVotingPolicy,
)
from .process import Compose, Process
from .reasoning import (
    _ANOMALY_DETECTORS,
    _DIAGNOSER_REGISTRY,
    _PREDICTOR_REGISTRY,
    AnomalyDetector,
    AnomalyDiagnoser,
    AnomalyOperator,
    AnomalyOperatorThreshold,
    Diagnoser,
    DiagnosisOperator,
    DiagnosisOperatorThreshold,
    EWMADetector,
    EWMAPredictor,
    LastPredictor,
    MeanPredictor,
    PredictionOperator,
    Predictor,
    StatisticalDiagnoser,
    TrendDiagnoser,
    TrendOperator,
    TrendOperatorThreshold,
    TrendPredictor,
    ZScoreDetector,
    available_detectors,
    available_diagnosers,
    available_predictors,
    clear_detector_registry,
    clear_diagnoser_registry,
    clear_predictor_registry,
    get_detector,
    get_detectors,
    get_diagnoser,
    get_diagnosers,
    get_predictor,
    get_predictors,
    has_detector,
    has_diagnoser,
    has_predictor,
    register_detector,
    register_diagnoser,
    register_predictor,
    unregister_detector,
    unregister_diagnoser,
    unregister_predictor,
)
from .timer import Timer
from .variable import (
    BooleanDomain,
    CategoricalDomain,
    CompositeDomain,
    RangeDomain,
    RealDomain,
    StatisticalDomain,
    ValueDomain,
    Variable,
    VariableEpistemic,
    VariableRole,
)

__all__ = [
    # Assessment
    "AnomalyResult",
    "DiagnosisResult",
    "PredictionResult",
    "ReasoningResult",
    "ReasoningTask",
    "StatisticsResult",
    "TrendResult",
    # Epistemic
    "EpistemicView",
    "VariableView",
    "ExecutiveView",
    # Executive
    "Executive",
    # Execptions
    "ProcelaException",
    "SemanticViolation",
    "ConstraintViolation",
    "InconsistentState",
    "ConfigurationError",
    "TimeoutError",
    "ExecutionError",
    # Invariant
    "InvariantCategory",
    "InvariantViolation",
    "InvariantViolationInfo",
    "InvariantViolationWarning",
    "InvariantViolationCritical",
    "InvariantViolationFatal",
    "InvariantPhase",
    "InvariantSeverity",
    "VariableSnapshot",
    "InvariantSoftness",
    "SystemInvariant",
    # Key authority
    "KeyAuthority",
    # Logger
    "JsonFormatter",
    "TextFormatter",
    "setup_logging",
    # Mechanism
    "Mechanism",
    "HomeostasisMechanism",
    "MechanismTemplate",
    # Memory
    "HypothesisState",
    "HypothesisRecord",
    "VariableMemory",
    "VariableRecord",
    "MemoryStatistics",
    # Policy
    "ResolutionPolicy",
    "HighestConfidencePolicy",
    "WeightedConfidencePolicy",
    "ResolverPolicy",
    "WeightedVotingPolicy",
    # Process
    "Process",
    "Compose",
    # Reasoning
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
    "Timer",
    # Variable
    "BooleanDomain",
    "CategoricalDomain",
    "CompositeDomain",
    "RangeDomain",
    "RealDomain",
    "StatisticalDomain",
    "ValueDomain",
    "VariableRole",
    "Variable",
    "VariableEpistemic",
]
