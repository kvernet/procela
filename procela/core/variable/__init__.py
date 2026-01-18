"""
Core variable modeling system for the Procela reasoning framework.

This module provides the complete abstraction for variables as first-class
reasoning entities, encompassing value domains, semantic roles, statistical
analysis, and the variable object model itself.

Components
----------
Variable Object Model
    The central Variable class that integrates domain constraints, historical
    tracking, role semantics, and statistical analysis into a unified entity.

Value Domains
    Type-safe domain specifications that define valid value ranges and
    constraints for variables, supporting boolean, categorical, numeric,
    statistical, and composite domains.

Semantic Roles
    Classification system that defines the semantic purpose and behavior
    patterns of variables within reasoning contexts.

Statistical Analysis
    Integration of historical statistical analysis for tracking variable
    behavior patterns and anomalies.

Key Concepts
------------
- **Domain Constraints**: Variables are strongly typed with mathematical
  domain specifications that guarantee value validity.
- **Semantic Typing**: Variables have semantic roles that define their
  purpose and expected behavior patterns.
- **Historical Awareness**: Variables maintain complete immutable histories
  of all value changes.
- **Statistical Self-Awareness**: Variables can analyze their own historical
  behavior through integrated statistics.

Core Classes
------------
Variable
    The central variable entity that combines:
    - Domain constraints for type safety
    - Immutable history tracking
    - Semantic role classification
    - Self-analysis capabilities

ValueDomain (Base)
    Abstract base for all domain specifications.

BooleanDomain
    Domain for boolean (true/false) variables with logical operations.

CategoricalDomain
    Domain for discrete categorical values with finite sets.

RangeDomain
    Domain for numeric ranges with inclusive/exclusive bounds.

StatisticalDomain
    Domain defined by statistical properties (mean, variance, etc.).

CompositeDomain
    Domain combining multiple subdomains with logical operators.

VariableRole
    Semantic classification of variable purpose.

HistoryStatistics
    Statistical analysis engine integrated into variables for reasoning
    and behavior analysis.

Architecture
------------
┌────────────────────────────────────────────────────────────┐
│                        Variable                            │
├─────────────┬──────────────┬──────────────┬────────────────┤
│   Domain    │    History   │     Role     │   Statistics   │
│ Constraints │  Tracking    │  Semantics   │    Engine      │
└─────────────┴──────────────┴──────────────┴────────────────┘

Usage Examples
--------------
>>> from procela.core.variable import (
...     Variable, RangeDomain, VariableRole, HistoryStatistics
... )
>>>
>>> # Create a temperature variable with domain constraints
>>> temp_domain = RangeDomain(min=0.0, max=100.0, inclusive_min=True)
>>> temp_var = Variable(
...     name="temperature",
...     domain=temp_domain,
...     role=VariableRole.SENSOR_READING
... )
>>>
>>> # Update variable with validation
>>> try:
>>>     updated_var = temp_var.update(value=25.5, time=..., source=...)
>>> except DomainError:
>>>     # Handle invalid value
>>>     pass
>>>
>>> # Analyze variable behavior
>>> stats = updated_var.statistics()
>>> if stats.is_anomalous():
>>>     # Handle anomaly
>>>     pass
>>>
>>> # Query domain constraints
>>> if temp_var.domain.contains(150.0):
>>>     # Value would be invalid
>>>     print("Value exceeds domain bounds")

Domain System Features
----------------------
- **Runtime Validation**: All value assignments are domain-validated
- **Mathematical Operations**: Domains support intersection, union, complement
- **Serialization**: Domains are fully serializable for persistence
- **Probabilistic Queries**: Statistical domains support probability queries

Role Semantics
--------------
Roles enable:
- **Behavior Prediction**: Expected patterns based on role
- **Constraint Inference**: Automatic domain refinement
- **Reasoning Optimization**: Role-specific reasoning strategies
- **Visualization Hints**: Role-appropriate display defaults

Statistical Integration
-----------------------
Each variable maintains:
- **Frequency Analysis**: Change rate and patterns
- **Volatility Metrics**: Value stability measures
- **Anomaly Detection**: Statistical outlier identification
- **Distribution Modeling**: Value probability distributions

Error Handling
--------------
- **Domain Violations**: Values outside domain raise DomainError
- **Type Safety**: Strict type checking at API boundaries
- **Immutable Invariants**: Variable immutability is preserved
- **Consistency Checks**: Historical consistency is validated

Integration Points
------------------
- **Memory System**: Integrated with VariableHistory for tracking
- **Reasoning Engine**: Variables are primary reasoning subjects
- **Visualization**: Role-based display configurations
- **Persistence**: Full serialization of variable state

Performance Characteristics
---------------------------
- **Update Complexity**: O(1) for valid domain values
- **Query Complexity**: O(1) for domain containment checks
- **Statistical Analysis**: O(n) for full history analysis
- **Memory**: O(n) for history, O(1) for domain/role

Semantics Reference
-------------------
For detailed domain semantics and role definitions:
https://procela.org/docs/semantics/core/variable/

See Also
--------
procela.core.memory.variable : Lower-level history and record management
procela.core.reasoning : Reasoning operations on variables
procela.symbols.value : Value representations and operations
procela.visualization.variable : Role-based visualization
"""

from ..memory.variable.statistics import HistoryStatistics
from .domain import (
    BooleanDomain,
    CategoricalDomain,
    CompositeDomain,
    RangeDomain,
    StatisticalDomain,
    ValueDomain,
)
from .role import VariableRole
from .variable import Variable

__all__ = [
    # Domain
    "BooleanDomain",
    "CategoricalDomain",
    "CompositeDomain",
    "RangeDomain",
    "StatisticalDomain",
    "ValueDomain",
    # Statistics
    "HistoryStatistics",
    # Role
    "VariableRole",
    # Variable
    "Variable",
]
