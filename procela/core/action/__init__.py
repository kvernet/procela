"""
Action management subsystem for Procela's active reasoning engine.

The action module provides the complete infrastructure for creating,
validating, selecting, and executing intervention proposals generated
by the reasoning engine. It implements the "propose-validate-select"
pattern that is central to Procela's active reasoning methodology.

Core Components
---------------
1. **Proposals (ActionProposal)**: Structured representations of potential
   interventions with confidence scores, rationales, and expected effects.

2. **Effects (ActionEffect)**: Predicted outcomes and impacts of proposed
   actions, including confidence metrics and expected system changes.

3. **Policies (SelectionPolicy)**: Algorithms for selecting which proposals
   to choose from a set of validated options.

4. **Validators (ProposalValidator)**: Components that validate proposals
   against system constraints, resources, and semantic rules.

Architecture Overview
---------------------
The action subsystem follows a pipeline architecture:

Reasoning Engine → Proposals → Validation → Selection
                     ↓           ↓           ↓
               ActionProposal  Validators  Policies

Key Design Principles
---------------------
- **Resource Awareness**: Action selection respects available resources
- **Explainability**: Every action includes human-readable rationales
- **Feedback Consistency**: Action execution maintains system invariants

Usage Examples
--------------
Basic action creation and validation:
>>> from procela.core.action import (
...     ActionProposal, ActionEffect, ProposalStatus,
...     ConfidenceThresholdValidator
... )
>>>
>>> # Create an action proposal
>>> effect = ActionEffect(
...     description="Reduce system load",
...     expected_outcome="Improved responsiveness",
...     confidence=0.85
... )
>>> proposal = ActionProposal(
...     action="scale_down",
...     value=0.7,
...     confidence=0.82,
...     rationale="High system load detected",
...     effect=effect,
...     status=ProposalStatus.PROPOSED
... )
>>>
>>> # Validate the proposal
>>> validator = ConfidenceThresholdValidator(threshold=0.75)
>>> is_valid = validator.validate(proposal)
>>> print(f"Proposal valid: {is_valid}")

Advanced policy-based selection:
>>> from procela.core.action import HighestConfidencePolicy
>>>
>>> # Create multiple proposals
>>> proposals = [
...     ActionProposal(action="action1", confidence=0.9, value=10.0),
...     ActionProposal(action="action2", confidence=0.7, value=15.0),
...     ActionProposal(action="action3", confidence=0.95, value=8.0),
... ]
>>>
>>> # Select best proposal using policy
>>> policy = HighestConfidencePolicy()
>>> selected = policy.select(proposals)
>>> assert selected is None # To be selected, an action should be validated first

Module Structure
----------------
- `effect.py`: `ActionEffect` class for modeling action outcomes
- `proposal.py`: `ActionProposal` class and `ProposalStatus` enum
- `validator.py`: `ProposalValidator` base class and implementations
- `policy.py`: `SelectionPolicy` base class and implementations

Integration Points
------------------
The action subsystem integrates with:
1. **Reasoning Engine**: Receives proposals from planners
2. **Constraint System**: Validates against hard and soft constraints
3. **Resource Manager**: Checks resource availability
4. **Execution Engine**: Dispatches selected actions for execution
5. **Monitoring System**: Tracks action outcomes for learning

Error Handling
--------------
- Invalid proposals raise appropriate exceptions during validation
- Policy selection fails gracefully when no suitable proposals exist

Performance Considerations
--------------------------
- Validation is optimized for real-time operation
- Policy selection algorithms scale with proposal count
- Effect modeling supports both precise and approximate calculations

Extensibility
-------------
The system supports custom:
1. **Validators**: Implement `ProposalValidator` with custom logic
2. **Policies**: Extend `SelectionPolicy` for specialized selection algorithms
3. **Effect Models**: Create domain-specific `ActionEffect` subclasses
4. **Proposal Types**: Extend `ActionProposal` for specialized actions

Notes
-----
- All confidence values must be in the range [0.0, 1.0]
- Action proposals are immutable after creation
- Action history is maintained for auditability and learning

See Also
--------
procela.core.reasoning : Reasoning engine
"""

from .effect import ActionEffect
from .policy import HighestConfidencePolicy, SelectionPolicy
from .proposal import ActionProposal, ProposalStatus
from .proposer import ActionProposer
from .resolver import ConflictResolver
from .validator import ConfidenceThresholdValidator, ProposalValidator

__all__ = [
    # Effect modeling
    "ActionEffect",
    # Selection policies
    "SelectionPolicy",
    "HighestConfidencePolicy",
    # Proposal system
    "ProposalStatus",
    "ActionProposal",
    # Proposer
    "ActionProposer",
    # Resolver
    "ConflictResolver",
    # Validation
    "ProposalValidator",
    "ConfidenceThresholdValidator",
]
