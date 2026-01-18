"""
Variable domain definitions for Procela's active reasoning framework.

The domain module provides a comprehensive set of domain classes that
define the possible values, constraints, and behaviors for variables in
the Procela system. Each domain type implements specific validation,
sampling, and reasoning capabilities tailored to different types of
data and constraints.

Core Philosophy
---------------
In Procela, domains are not just value ranges but active contracts that:
1. Define valid value spaces for variables
2. Enforce constraints and invariants
3. Provide domain-specific reasoning capabilities
4. Enable intelligent sampling and interpolation
5. Maintain consistency across reasoning operations

Domain Types
------------
1. **ValueDomain**: Base domain for continuous numerical values
2. **BooleanDomain**: Domain for true/false logical values
3. **CategoricalDomain**: Domain for discrete categorical values
4. **RangeDomain**: Domain for bounded numerical ranges
5. **StatisticalDomain**: Domain with statistical properties and constraints
6. **CompositeDomain**: Combination of multiple domain types

Usage Examples
--------------
>>> from procela.core.variable import (
...     BooleanDomain, RangeDomain, CategoricalDomain
... )
>>>
>>> # Create different domain types
>>> bool_domain = BooleanDomain()
>>> range_domain = RangeDomain(min_value=0.0, max_value=100.0)
>>> cat_domain = CategoricalDomain(categories=["low", "medium", "high"])
>>>
>>> # Validate values against domains
>>> print(f"Valid boolean: {bool_domain.validate(True)}")
Valid boolean: True
>>> print(f"Valid range: {range_domain.validate(50.0)}")
Valid range: True
>>> print(f"Valid category: {cat_domain.validate('medium')}")
Valid category: True
>>>
>>> # Generate samples from domains
>>> bool_sample = bool_domain.sample()
>>> range_sample = range_domain.sample()
>>> cat_sample = cat_domain.sample()

Domain Integration
------------------
Domains integrate with:
1. **Variables**: Define valid value spaces and constraints
2. **Reasoning**: Provide domain-specific reasoning capabilities
3. **Sampling**: Enable intelligent value generation
4. **Validation**: Ensure constraint satisfaction
5. **Interpolation**: Support smooth transitions between values

Domain-Specific Reasoning
-------------------------
Each domain type provides specialized reasoning capabilities:
- **BooleanDomain**: Logical operations and truth maintenance
- **CategoricalDomain**: Category membership and transitions
- **RangeDomain**: Boundary enforcement and interpolation
- **StatisticalDomain**: Distribution-based reasoning
- **CompositeDomain**: Multi-domain coordination

Implementation Notes
--------------------
- Domain validation is optimized for performance
- Sampling considers domain constraints and distributions
- Domains maintain their own reasoning state when applicable
- Composite domains coordinate validation across sub-domains

Error Handling
--------------
- Invalid domain configurations raise appropriate exceptions
- Value validation returns detailed error information
- Domain operations maintain consistency guarantees

Performance Considerations
--------------------------
- Domain validation is O(1) for most operations
- Sampling efficiency varies by domain complexity
- Memory usage is minimal for simple domains
- Composite domains optimize validation across components

Extensibility
-------------
Custom domain types can be created by:
1. Subclassing the appropriate base domain class
2. Implementing required validation and sampling methods
3. Adding domain-specific reasoning capabilities

See Also
--------
procela.core.variable : Variable classes using domains
procela.core.reasoning : Reasoning engine using domain knowledge
"""

from .boolean import BooleanDomain
from .categorical import CategoricalDomain
from .composite import CompositeDomain
from .range import RangeDomain
from .statistical import StatisticalDomain
from .value import ValueDomain

__all__ = [
    "BooleanDomain",
    "CategoricalDomain",
    "CompositeDomain",
    "RangeDomain",
    "StatisticalDomain",
    "ValueDomain",
]
