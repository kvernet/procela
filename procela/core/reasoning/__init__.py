"""
Core reasoning engine for Procela's active reasoning framework.

The reasoning module implements the intelligent core of the Procela system,
providing mechanisms for anomaly detection, trend analysis, diagnosis,
prediction, and planning. These components work together to transform raw
system data into actionable insights through stateful, resource-aware,
constraint-respecting reasoning processes.

Core Philosophy
---------------
Procela moves beyond correlation-based approaches to implement true
mechanistic reasoning where variables are active intelligent entities.
Each component in the reasoning engine:
- Detects anomalies and analyzes trends in system behavior
- Diagnoses root causes of identified issues
- Predicts future system states based on current conditions
- Generates intelligent intervention plans
- Maintains feedback-loop consistency across all operations

Architecture Overview
---------------------
The reasoning engine follows a pipeline architecture where data flows through:

1. **Anomaly Detection** → Identify statistical deviations from expected behavior
2. **Trend Analysis** → Detect directional patterns in system metrics
3. **Diagnosis** → Determine root causes of anomalies and trends
4. **Prediction** → Forecast future system states
5. **Planning** → Generate intervention proposals based on analysis
6. **Integration** → Combine results into coherent actionable insights

Key Concepts
------------
- **Active Variables**: Stateful entities that participate in reasoning
- **Mechanistic Models**: Causal representations of system behavior
- **Resource Awareness**: Reasoning constrained by available resources
- **Feedback Consistency**: Guaranteed consistency in closed-loop operations
- **Registry Pattern**: Dynamic discovery and extension of reasoning components

Usage Examples
--------------
Basic reasoning workflow:
>>> from procela.core.reasoning import ReasoningTask, get_detector, get_diagnoser
>>> from procela.core.reasoning import get_predictor, get_planner
>>>
>>> # Configure reasoning components
>>> detector = get_detector("ewma", threshold=3.0)
>>> diagnoser = get_diagnoser("statistical", variability_threshold=0.7)
>>> predictor = get_predictor("trend", extrapolation_factor=1.5)
>>> planner = get_planner("preventive", priority=3)

Advanced multi-component configuration:
>>> from procela.core.reasoning import (
...     EWMADetector, TrendDiagnoser, EWMAPredictor, ReactivePlanner
... )
>>>
>>> # Direct instantiation with custom parameters
>>> detector = EWMADetector(threshold=2.0)
>>> diagnoser = TrendDiagnoser(significance_threshold=0.2, strong_threshold=0.5)
>>> predictor = EWMAPredictor(alpha=0.3)
>>> planner = ReactivePlanner(priority=5, enabled=True)

Module Organization
-------------------
The module is organized into cohesive submodules:

1. **anomaly** - Statistical anomaly detection algorithms
2. **diagnosis** - Root cause analysis and issue identification
3. **prediction** - Future state forecasting methods
4. **planning** - Intervention generation and optimization
5. **result** - Structured outputs from reasoning components
6. **task** - Orchestration of complete reasoning workflows
7. **view** - Contextual epistemic views for different reasoning stages

Registry System
---------------
All major component types (detectors, diagnosers, predictors, planners)
support dynamic registration through a consistent registry pattern:

>>> from procela.core.reasoning import (
...     AnomalyDetector, register_detector, available_detectors,
...     available_diagnosers, available_predictors, available_planners
... )
>>>
>>> # Register custom components
>>> class CustomDetector(AnomalyDetector):
...     name = "custom"
...     # implementation...
>>> register_detector("custom_detector", CustomDetector)
>>>
>>> # Discover available components
>>> print(f"Available detectors: {available_detectors()}")
>>> print(f"Available diagnosers: {available_diagnosers()}")
>>> print(f"Available predictors: {available_predictors()}")
>>> print(f"Available planners: {available_planners()}")

Performance Considerations
--------------------------
- **State Management**: Components maintain internal state for consistency
- **Resource Constraints**: Reasoning respects system resource limitations
- **Computational Complexity**: Algorithms optimized for real-time operation
- **Memory Footprint**: Efficient data structures for large-scale systems

Error Handling
--------------
- All components raise appropriate exceptions for invalid inputs
- Registry functions validate component compatibility
- Result objects include confidence metrics for uncertainty representation

Extensibility
-------------
The reasoning engine is designed for extension through:
1. Custom detector/diagnoser/predictor/planner implementations
2. Dynamic registration via registry APIs
3. Subclassing of base result and view types
4. Custom task orchestration logic

Notes
-----
- All reasoning components are designed for both batch and streaming operation
- The framework supports distributed reasoning across multiple variables
- Time complexity varies by algorithm; see individual component documentation

See Also
--------
procela.core.variable : Active reasoning entity in Procela

References
----------
1. Procela Architecture Specification - https://procela.org/docs/architecture
2. Active Reasoning Methodology - https://procela.org/docs/reasoning/methodology
3. Registry Pattern Implementation - https://procela.org/docs/patterns/registry
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
from .planning import (
    _PLANNER_REGISTRY,
    Planner,
    PlanningOperator,
    PreventivePlanner,
    ReactivePlanner,
    available_planners,
    clear_planner_registry,
    get_planner,
    get_planners,
    has_planner,
    register_planner,
    unregister_planner,
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
from .result import (
    AnomalyResult,
    DiagnosisResult,
    PlanningResult,
    PredictionResult,
    ReasoningResult,
    TrendResult,
)
from .task import ReasoningTask
from .view import (
    DiagnosisView,
    EpistemicView,
    PlanningView,
    PredictionView,
    ProposalView,
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
    # Planning Components
    "PlanningOperator",
    "Planner",
    "PreventivePlanner",
    "ReactivePlanner",
    "get_planner",
    "register_planner",
    "unregister_planner",
    "get_planners",
    "available_planners",
    "clear_planner_registry",
    "has_planner",
    "_PLANNER_REGISTRY",
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
    # Result Structures
    "ReasoningResult",
    "AnomalyResult",
    "TrendResult",
    "DiagnosisResult",
    "PlanningResult",
    "PredictionResult",
    # Task Orchestration
    "ReasoningTask",
    # View Interfaces
    "EpistemicView",
    "DiagnosisView",
    "PredictionView",
    "PlanningView",
    "ProposalView",
]

# Module metadata for documentation and tooling
__docformat__ = "numpy"
