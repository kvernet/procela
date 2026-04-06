# Governance: The Scientific Method in Code

**Governance** is what makes Procela unique—it enables simulations to **question their own assumptions** and **restructure themselves** at runtime. Governance units follow the **scientific method pattern**, observing epistemic signals, forming hypotheses, running experiments, and adapting the system based on results.


This comprehensive governance guide covers:

- The scientific method pattern encoded in code
- Core governance components and phases
- Practical patterns : multi-objective
- Advanced features like reversible experiments and composite governance
- Best practices and performance considerations
- Testing strategies


## The Scientific Method Pattern

Procela encodes the scientific method as executable code:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐     ┌───────────┐
│   DETECT    │────▶│  HYPOTHESIZE │────▶│  EXPERIMENT │────▶│  EVALUATE  │────▶│  CONCLUDE │
│ (Observe)   │     │  (Plan)      │     │  (Execute)  │     │ (Measure)  │     │ (Adapt)   │
└─────────────┘     └──────────────┘     └─────────────┘     └────────────┘     └───────────┘
```

Each governance unit is a **first-class citizen** that can:
- **Observe** epistemic signals (coverage, fragility, conflict)
- **Hypothesize** changes
- **Experiment** by temporarily modifying the system
- **Evaluate** the impact of changes
- **Conclude** by keeping or reverting modifications

## Core Governance Components

### SystemInvariant

The basic governance unit (second-class) that monitors conditions and triggers actions:

```python
from procela import (
    SystemInvariant,
    InvariantPhase,
    InvariantViolation,
    VariableSnapshot,
    Variable,
    HighestConfidencePolicy,
    KeyAuthority
)

class MyInvariant(SystemInvariant):
    def __init__(self, threshold=0.5):
        self.threshold = threshold

        def check(snapshot: VariableSnapshot):
            """Detect condition"""
            # snapshot contains variable state
            confidences = [view.stats.confidence for view in snapshot.views]
            if confidences:
                return max(confidences) - min(confidences) <= self.threshold
            return True

        def handle(invariant: InvariantViolation, snapshot: VariableSnapshot):
            """Respond to violation"""
            print(f"Step {snapshot.step} - Violation detected! Switching policy...")
            for view in snapshot.views:
                var = KeyAuthority.resolve(view.key)
                if isinstance(var, Variable):
                    var.policy = HighestConfidencePolicy()

        super().__init__(
            name="MyInvariant",
            condition=check,
            on_violation=handle,
            phase=InvariantPhase.RUNTIME,
            message="Confidence spread too high"
        )
```

### Invariant Phases

Governance can act at different stages of simulation:

```python
from procela import SystemInvariant, InvariantPhase

# PRE: Before mechanisms execute
class PreInvariant(SystemInvariant):
    def __init__(self):
        super().__init__(phase=InvariantPhase.PRE)

# RUNTIME: After mechanism execution and before resolution
class RuntimeInvariant(SystemInvariant):
    def __init__(self):
        super().__init__(phase=InvariantPhase.RUNTIME)

# POST: After resolution
class PostInvariant(SystemInvariant):
    def __init__(self):
        super().__init__(phase=InvariantPhase.POST)
```

| Phase | Timing | Use Cases |
|-------|--------|-----------|
| **PRE** | Before mechanisms run | Initialization, precondition checks |
| **RUNTIME** | After mechanism execution and before resolution | Dynamic adaptation, policy switching |
| **POST** | After all updates | Validation, logging, analysis |

### Hooks

The basic governance unit (first-class) that monitors conditions and triggers actions:

```python
from procela import Executive, Mechanism, WeightedVotingPolicy

executive = Executive()

class MyMechanism(Mechanism):
    pass

# Pre step hook
def pre_step(executive: Executive, step: int) -> None:
    # Disable a mechanism from some step
    if step == 10:
        for mech in executive.mechanisms():
            if mech.name == "Mechanism to disable":
                mech.disable()
                print(f"Step {step} - The mechanism has been disabled")

    # Add a new mechanism from some step
    if step == 30:
        executive.add_mechanism(MyMechanism())
        print(f"Step {step} - The mechanism has been added")


# Post step creator
def create_post_step(threshold: float = 0.1):
    def post_step(executive: Executive, step: int) -> None:
        writable = list(executive.writable())
        if writable[0].stats.ewma > threshold:
            writable[0].policy = WeightedVotingPolicy()
            print(
                f"Step {step} - The variable policy has been switched "
                f"to {writable[0].policy.name}"
            )

    return post_step
```

### Pattern 4: Multi-Objective Governance

Balances multiple competing objectives:

```python
import numpy as np

from procela import (
    SystemInvariant,
    VariableSnapshot,
    InvariantPhase,
    KeyAuthority,
    Variable
)

class MultiObjectiveGovernance(SystemInvariant):
    """Balances prediction accuracy and structural stability."""

    def __init__(self, accuracy_weight=0.7, stability_weight=0.3):
        self.accuracy_weight = accuracy_weight
        self.stability_weight = stability_weight
        self.objective_history = []

        def _policy_changes():
            # To be implemented
            return NotImplementedError()

        def _mechanism_changes():
            # To be implemented
            return NotImplementedError()

        def _rebalance(snapshot: VariableSnapshot):
            """Adjust weights based on performance"""
            if len(self.objective_history) < 20:
                return

            # Check which objective is underperforming
            recent = self.objective_history[-10:]
            accuracy_trend = recent[-1]["accuracy"] - recent[0]["accuracy"]
            stability_trend = recent[-1]["stability"] - recent[0]["stability"]

            if accuracy_trend < -0.1:
                print("Increasing accuracy weight due to declining accuracy")
                self.accuracy_weight = min(0.9, self.accuracy_weight + 0.1)
                self.stability_weight = 1 - self.accuracy_weight
            elif stability_trend < -0.1:
                print("Increasing stability weight due to instability")
                self.stability_weight = min(0.9, self.stability_weight + 0.1)
                self.accuracy_weight = 1 - self.stability_weight

        def _evaluate_objectives(snapshot: VariableSnapshot):
            """Calculate and track multi-objective performance"""

            # Objective 1: Prediction Accuracy
            if snapshot.views[0].stats.count > 10:
                var = KeyAuthority.resolve(snapshot.views[0].key)
                if not isinstance(var, Variable):
                    return

                recent = var.get(-10, 10)
                errors = [abs(recent[i+1][1].value - recent[i][1].value)
                        for i in range(len(recent)-1)]

                domain_range = var.domain.max_value, var.domain.min_value
                accuracy = 1 - (np.mean(errors) / domain_range)
            else:
                accuracy = 0.5

            # Objective 2: Structural Stability
            policy_changes = _policy_changes()
            mechanism_changes = _mechanism_changes()
            stability = 1 / (1 + policy_changes + mechanism_changes)

            # Combined score
            combined = (self.accuracy_weight * accuracy +
                    self.stability_weight * stability)

            self.objective_history.append({
                "step": snapshot.step,
                "accuracy": accuracy,
                "stability": stability,
                "combined": combined
            })

            # Log if combined score drops significantly
            if len(self.objective_history) > 20:
                recent_avg = np.mean([o["combined"]
                                    for o in self.objective_history[-10:]])
                historical_avg = np.mean([o["combined"]
                                        for o in self.objective_history[:-10]])

                if recent_avg < 0.7 * historical_avg:
                    print(f"⚠️ Multi-objective performance drop: "
                        f"{historical_avg:.3f} → {recent_avg:.3f}")

                    # Trigger rebalancing
                    _rebalance(snapshot)

        def check(snapshot: VariableSnapshot):
            # Always evaluate (never violates)
            _evaluate_objectives(snapshot)
            return True  # No violation, just monitoring

        def handle(invariant, snapshot):
            # Only called if condition returns False (never here)
            pass

        super().__init__(
            name="MultiObjectiveGovernance",
            condition=check,
            on_violation=handle,
            phase=InvariantPhase.POST
        )
```

## Advanced Governance Features

### Reversible Experiments

Procela supports automatic rollback of failed experiments:

```python
from procela import (
    Executive,
    SystemInvariant,
    VariableSnapshot,
    InvariantViolation,
    InvariantPhase
)

class ReversibleExperiment(SystemInvariant):
    """Governance that can automatically revert changes"""

    def __init__(self, executive: Executive):
        self.executive = executive

        def check(snapshot: VariableSnapshot):
            # Trigger experiment condition
            return snapshot.views[0].stats.count > 100

        def handle(invariant: InvariantViolation, snapshot: VariableSnapshot):
            # Save checkpoint before experiment
            checkpoint = self.executive.create_checkpoint()

            # Run experiment for 10 steps
            self.executive.run_experiment(steps=10)

            # After experiment, evaluate
            success = self._evaluate_experiment()

            if not success:
                print("Experiment failed! Reverting...")
                self.executive.restore_checkpoint(checkpoint)
            else:
                print("Experiment successful! Keeping changes.")

        super().__init__(
            name="ReversibleExperiment",
            condition=check,
            on_violation=handle,
            phase=InvariantPhase.PRE
        )
```

### Composite Governance

Combine multiple governance strategies:

```python
from procela import Executive, SystemInvariant

class CompositeGovernance:
    """Manages multiple governance units together"""

    def __init__(self, executive: Executive):
        self.executive = executive
        self.governors: list[SystemInvariant] = []

    def add_governor(self, governor: SystemInvariant):
        self.governors.append(governor)
        self.executive.add_invariant(governor)

    def get_governance_state(self):
        """Report on all governance units"""
        state = {}
        for gov in self.governors:
            state[gov.name] = {
                "violations": gov.violation_count,
                "actions": gov.action_count,
                "last_triggered": gov.last_triggered
            }
        return state

# Usage
governance = CompositeGovernance(executive)
governance.add_governor(FragilityGovernance(variable=X))
governance.add_governor(CoverageGovernance())
governance.add_governor(ProbeGovernance(executive))
```

## Practical Examples

### Example 1: Adaptive Ensemble Weighting

```python
from procela import (
    SystemInvariant,
    InvariantPhase,
    VariableSnapshot,
    Mechanism,
    Variable
)

class AdaptiveWeightingGovernance(SystemInvariant):
    """Adjusts mechanism weights based on performance"""

    def __init__(self, mechanisms: list[Mechanism], variable: Variable):
        self.mechanisms = mechanisms
        self.variable = variable
        self.performance = {m.key(): [] for m in mechanisms}

        def check(snapshot: VariableSnapshot) -> bool:
            # Always evaluate
            self._update_weights(snapshot)
            return True

        super().__init__(
            name="AdaptiveWeighting",
            condition=check,
            on_violation=None,
            phase=InvariantPhase.POST
        )

    def _update_weights(self, snapshot: VariableSnapshot) -> None:
        """Update mechanism weights based on prediction accuracy"""
```

### Example 2: Topology Exploration

```python
from procela import (
    Executive,
    SystemInvariant,
    InvariantPhase,
    InvariantViolation,
    VariableSnapshot
)

class TopologyExplorer(SystemInvariant):
    """Explores different mechanism combinations"""

    def __init__(self, executive: Executive):
        self.executive = executive
        self.all_mechanisms = executive.mechanisms()
        self.exploration_step = 0
        self.current_config = None

        def check(snapshot: VariableSnapshot):
            # Explore every 100 steps
            if snapshot.step % 100 == 0 and snapshot.step > 0:
                return False
            return True

        def handle(invariant: InvariantViolation, snapshot: VariableSnapshot):
            self._explore_topology(snapshot)

        super().__init__(
            name="TopologyExplorer",
            condition=check,
            on_violation=handle,
            phase=InvariantPhase.PRE
        )

    def _explore_topology(self, snapshot: VariableSnapshot):
        """Try a different combination of mechanisms"""
        import random

        # Save current state
        self.executive.create_checkpoint()

        # Try a new configuration
        num_active = random.randint(1, len(self.all_mechanisms))
        active_mechs = random.sample(self.all_mechanisms, num_active)

        # Disable all, then enable selected
        for mech in self.all_mechanisms:
            mech.disable()
        for mech in active_mechs:
            mech.enable()

        print(f"🔍 Exploring topology: {len(active_mechs)} active mechanisms")

        self.current_config = {
            "active": active_mechs,
            "step": snapshot.step
        }
```

## Best Practices

### 1. Minimal Intervention
```python
# Good: Only act when necessary
def check(snapshot):
    if fragility > threshold:
        return False  # Trigger action
    return True

# Avoid: Acting on every step
def check(snapshot):
    # Always returns False, triggers action every time
    return False
```

### 2. Checkpoint Before Changes
```python
# Always save state before making irreversible changes
def handle(invariant, snapshot):
    checkpoint = self.executive.create_checkpoint()
    # Make changes...
    if not success:
        self.executive.restore_checkpoint(checkpoint)
```

### 3. Log Governance Actions
```python
from procela import (
    Executive,
    SystemInvariant,
    InvariantPhase,
)

class LoggingGovernance(SystemInvariant):
    def __init__(self, executive: Executive):
        self.executive = executive

        def _get_details():
            pass

        def handle(invariant, snapshot):
            self.executive.logger.info({
                "step": snapshot.step,
                "action": self.name,
                "details": _get_details()
            })

        super().__init__(
            "LoggingGovernance",
            condition=lambda s: False,
            on_violation=handle,
            phase=InvariantPhase.POST,
            message=""
        )
```

### 4. Test Governance Separately
```python
from procela import (
    Variable,
    RangeDomain,
    VariableRecord,
    WeightedVotingPolicy,
    HighestConfidencePolicy
)

def test_fragility_governance():
    # Create controlled environment
    X = Variable("X", RangeDomain(0, 100))
    X.policy = WeightedVotingPolicy()

    # Force fragility
    X.add_hypothesis(VariableRecord(10, 0.9))
    X.add_hypothesis(VariableRecord(90, 0.1))

    # Check fragility governance
    #TODO

    # Assert fragility governance changes policy
    assert X.policy == HighestConfidencePolicy()
```

## Performance Considerations

```python
from procela import VariableSnapshot, SystemInvariant

class EfficientGovernance(SystemInvariant):
    """Governance with performance optimizations"""

    def __init__(self):
        self.check_interval = 10  # Only check every 10 steps
        self.last_check = 0
        self.cached_result = None

    def check(self, snapshot: VariableSnapshot):
        # Only compute expensive checks periodically
        if snapshot.step - self.last_check < self.check_interval:
            return self.cached_result

        self.last_check = snapshot.step

        # Expensive computation here
        result = self._expensive_check(snapshot)
        self.cached_result = result

        return result
```

## Next Steps

- Learn about [Epistemic Signals](epistemic-signals.md) for monitoring system health
- See governance in action in the [AMR Case Study](../examples/amr-case-study.md)
- Explore [Advanced Governance Patterns](../advanced/governance-patterns.md)
- Check the [API Reference](../api/reference.md) for complete Governance documentation
