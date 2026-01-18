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

Modules
-------
anomaly : Anomaly-based diagnostic reasoner
    Detects and analyzes anomalous behavior in system variables.

base : Base classes and interfaces
    Defines the foundational interfaces and abstract classes for all diagnosers.

registry : Diagnoser registry and factory
    Provides registration, discovery, and instantiation of diagnostic reasoners.

statistical : Statistical diagnostic reasoner
    Performs statistical analysis for diagnostic purposes.

trend : Trend-based diagnostic reasoner
    Analyzes directional patterns and temporal changes.

Classes
-------
Diagnoser : ABC
    Abstract base class for all diagnostic reasoners.

AnomalyDiagnoser
    Diagnostic reasoner specialized in anomaly detection and analysis.

StatisticalDiagnoser
    Diagnostic reasoner specialized in statistical analysis.

TrendDiagnoser
    Diagnostic reasoner specialized in trend pattern analysis.

Functions
---------
get_diagnoser(name: str, **kwargs: Any) -> Diagnoser
    Factory function to instantiate a diagnoser by name.

register_diagnoser(name: str, diagnoser_class: Type[Diagnoser]) -> None
    Register a new diagnoser class in the registry.

unregister_diagnoser(name: str) -> Type[Diagnoser]
    Remove a diagnoser from the registry.

get_diagnosers() -> Dict[str, Type[Diagnoser]]
    Get a copy of the current diagnoser registry.

available_diagnosers() -> Set[str]
    Get the set of available diagnoser names.

clear_diagnoser_registry() -> None
    Clear all entries from the diagnoser registry.

has_diagnoser(name: str) -> bool
    Check if a diagnoser is registered under the given name.

Examples
--------
>>> from procela.core.reasoning import (
...     get_diagnoser, TrendDiagnoser, DiagnosisResult
... )
>>>
>>> # Get a trend diagnoser instance
>>> diagnoser = get_diagnoser("trend", significance_threshold=0.3)
>>> isinstance(diagnoser, TrendDiagnoser)
True
>>>
>>> # Use the diagnoser on a system view
>>> result = diagnoser.diagnose(view)
>>> isinstance(result, DiagnosisResult)
True
>>> 0.0 <= result.confidence <= 1.0
True

Notes
-----
1. The diagnosis system is designed to work with the Procela framework's
   active reasoning entities and feedback-loop consistency guarantees.

2. Diagnosers can be combined or chained for more comprehensive analysis.

3. The registry system allows for dynamic addition of custom diagnosers
   without modifying the core framework.

4. All diagnosers implement the Diagnoser abstract base class, ensuring
   a consistent interface for diagnostic reasoning.

See Also
--------
procela.core.variable : Active reasoning entity in Procela

References
----------
[1] Procela Framework Documentation: Active Reasoning Systems
[2] Mechanistic Diagnostic Patterns for Real-World Systems
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
