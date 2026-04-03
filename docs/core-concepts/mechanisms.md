# Mechanisms: Causal Theories in Action

**Mechanisms** are the active components that propose hypotheses and encode scientific theories. Unlike traditional simulation components that directly modify state, mechanisms only **propose**—they never mutate variables directly. This separation of **proposal** from **resolution** is what enables epistemic governance.

This guide covers:

- Core philosophy of proposal-resolution separation
- Complete mechanism anatomy and lifecycle
- Multiple examples from simple to complex
- Advanced patterns (calibration, ensemble, adaptive)
- Best practices and performance considerations
- Testing strategies


## Core Philosophy

### The Proposal-Resolution Separation

Traditional simulations combine proposal and execution:

```python
# Traditional approach (state mutation)
def update_temperature(current):
    return current + 0.1  # Direct state change

temperature = update_temperature(temperature)  # Mutates state
```

Procela separates concerns:

```python
# Procela approach (hypothesis proposal)
class WarmingMechanism(Mechanism):
    def transform(self):
        # Propose a hypothesis, never mutate
        self.writes()[0].add_hypothesis(
            VariableRecord(value=current + 0.1, confidence=0.8, source=self.key())
        )

# Variable resolves competing hypotheses
temperature = variable.value  # Resolved by policy, not direct mutation
```

This separation enables:
- **Competing theories** to coexist
- **Auditability** of all proposals
- **Governance** to intervene before state changes
- **Reproducibility** through complete hypothesis tracking

## Anatomy of a Mechanism

### Basic Structure

```python
from procela import Mechanism, Variable, VariableRecord

class MyMechanism(Mechanism):
    def __init__(self):
        # Define what variables this mechanism reads and writes
        super().__init__(
            reads=[input_variable],
            writes=[output_variable]
        )

    def transform(self):
        # Read current values
        inputs = self.reads()
        current_value = inputs[0].value

        # Compute new hypothesis
        proposed_value = self.compute_prediction(current_value)

        # Propose hypothesis (never mutate directly!)
        outputs = self.writes()
        outputs[0].add_hypothesis(
            VariableRecord(
                value=proposed_value,
                confidence=self.compute_confidence(),
                source=self.key()  # Automatic source tracking
            )
        )

    def compute_prediction(self, input_value):
        # Implement your causal theory here
        return input_value + 0.1

    def compute_confidence(self):
        # Return confidence in this prediction (0-1)
        return 0.8
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `reads` | Variables this mechanism observes (read-only) |
| `writes` | Variables this mechanism proposes hypotheses for |
| `transform()` | Core logic that computes predictions |
| `key()` | Unique identifier for source tracking |
| `confidence` | How much the mechanism trusts its own prediction |

## Creating Mechanisms

### Simple Linear Mechanism

```python
import numpy as np
from procela import Mechanism, Variable, VariableRecord

class LinearGrowthMechanism(Mechanism):
    """Assumes population grows linearly"""

    def __init__(self, growth_rate=0.02):
        super().__init__(reads=[population], writes=[population])
        self.growth_rate = growth_rate

    def transform(self):
        current_pop = self.reads()[0].value

        # Linear growth prediction
        new_pop = current_pop * (1 + self.growth_rate)

        # Add noise to model uncertainty
        noise = np.random.normal(0, current_pop * 0.01)
        new_pop += noise

        self.writes()[0].add_hypothesis(
            VariableRecord(
                value=new_pop,
                confidence=0.7,  # Moderate confidence
                source=self.key()
            )
        )
```

### Logistic Growth Mechanism

```python
class LogisticGrowthMechanism(Mechanism):
    """Assumes population follows logistic growth (carrying capacity)"""

    def __init__(self, carrying_capacity=1000, growth_rate=0.1):
        super().__init__(reads=[population], writes=[population])
        self.K = carrying_capacity  # Carrying capacity
        self.r = growth_rate        # Growth rate
        self.accuracy_history = []  # Track prediction accuracy

    def transform(self):
        current_pop = self.reads()[0].value

        # Logistic growth equation
        new_pop = current_pop + self.r * current_pop * (1 - current_pop / self.K)

        # Confidence based on historical accuracy
        confidence = self._compute_confidence()

        self.writes()[0].add_hypothesis(
            VariableRecord(
                value=new_pop,
                confidence=confidence,
                source=self.key(),
                metadata={"model": "logistic", "K": self.K, "r": self.r}
            )
        )

    def _compute_confidence(self):
        """Higher confidence when population is within plausible range"""
        current_pop = self.reads()[0].value

        if 0 < current_pop < self.K:
            return 0.9  # Within capacity, high confidence
        elif current_pop <= 0:
            return 0.1  # Below zero, very uncertain
        else:
            return 0.5  # Exceeds capacity, uncertain
```

### Complex Multi-Variable Mechanism

```python
class SEIRMechanism(Mechanism):
    """SIR/SEIR epidemiological model"""

    def __init__(self, beta=0.3, gamma=0.1, sigma=0.2):
        super().__init__(
            reads=[susceptible, exposed, infectious, recovered],
            writes=[susceptible, exposed, infectious, recovered]
        )
        self.beta = beta      # Transmission rate
        self.gamma = gamma    # Recovery rate
        self.sigma = sigma    # Incubation rate (exposed -> infectious)

    def transform(self):
        # Read current state
        S = self.reads()[0].value
        E = self.reads()[1].value
        I = self.reads()[2].value
        R = self.reads()[3].value
        N = S + E + I + R

        # SEIR differential equations (discrete time)
        new_infections = self.beta * S * I / N
        new_exposed = new_infections
        new_infectious = self.sigma * E
        new_recovered = self.gamma * I

        # Propose new state
        S_new = S - new_infections
        E_new = E + new_exposed - new_infectious
        I_new = I + new_infectious - new_recovered
        R_new = R + new_recovered

        # Confidence based on population size
        confidence = min(0.95, N / 10000)

        # Write hypotheses for each variable
        self.writes()[0].add_hypothesis(
            VariableRecord(S_new, confidence=confidence, source=self.key())
        )
        self.writes()[1].add_hypothesis(
            VariableRecord(E_new, confidence=confidence, source=self.key())
        )
        self.writes()[2].add_hypothesis(
            VariableRecord(I_new, confidence=confidence, source=self.key())
        )
        self.writes()[3].add_hypothesis(
            VariableRecord(R_new, confidence=confidence, source=self.key())
        )
```

## Advanced Mechanism Patterns

### Pattern 1: Confidence Calibration

```python
import numpy as np

from procela import Mechanism, VariableRecord

class SelfCalibratingMechanism(Mechanism):
    """Adjusts confidence based on historical prediction accuracy"""

    def __init__(self, reads, writes, name="calibrated"):
        super().__init__(reads, writes)
        self.name = name

    def transform(self):
        # Make prediction
        prediction = self._predict()

        # Compute dynamic confidence
        confidence = self._compute_calibrated_confidence()

        # Propose with calibrated confidence
        self.writes()[0].add_hypothesis(
            VariableRecord(prediction, confidence, source=self.key())
        )

    def _predict(self):
        """Override with actual prediction logic"""
        raise NotImplementedError

    def _compute_calibrated_confidence(self):
        """Confidence = historical accuracy (if available)"""
        if min([var.stats.count for var in self.reads()]) < 10:
            return 0.5  # Initial uncertainty

        recent_errors = []
        truths, preds = [var.get(start=-10, size=10) for var in self.reads()]
        for (_, tc, _), (_, pc, _) in zip(truths, preds):
            recent_errors.append(abs(tc.value - pc.value))

        avg_error = np.mean(recent_errors)

        # Convert error to confidence (0-1)
        max_expected_error = self._max_expected_error() # to be implemented
        confidence = max(0, min(1, 1 - avg_error / max_expected_error))

        return confidence
```

### Pattern 2: Ensemble Mechanisms

```python
from procela import Mechanism, VariableRecord


class EnsembleMechanism(Mechanism):
    """Combines multiple sub-mechanisms as an ensemble"""

    def __init__(
        self,
        name: str,
        mechanisms: list[Mechanism],
        weights: list[float] | None = None
    ):
        # Ensemble reads from inputs, writes to outputs
        super().__init__(
            reads=[var for m in mechanisms for var in m.reads()],
            writes=[var for m in mechanisms for var in m.writes()]
        )
        self.name = name
        self.mechanisms = mechanisms
        self.weights = weights or [1.0/len(mechanisms)] * len(mechanisms)
        self.write_keys = {
            var.key():var for var in self.writes()
        }

    def transform(self):
        # Get predictions from all sub-mechanisms
        predictions = []
        for i, mechanism in enumerate(self.mechanisms):
            # Let sub-mechanism propose
            mechanism.transform()

            # Get its predictions for each variable
            for var in mechanism.writes():
                for hypothesis in var.hypotheses:
                    if hypothesis.record.source == mechanism.key():
                        predictions.append({
                            "mechanism": i,
                            "variable": var.key(),
                            "value": hypothesis.record.value,
                            "confidence": hypothesis.record.confidence
                        })

        # Ensemble aggregation
        self._aggregate_predictions(predictions)

    def _aggregate_predictions(self, predictions):
        """Weighted average of sub-mechanism predictions"""
        # Group by variable
        by_variable = {}
        for pred in predictions:
            var_key = pred["variable"]
            if var_idx not in by_variable:
                by_variable[var_key] = []
            by_variable[var_idx].append(pred)

        # Weighted average for each variable
        for var_idx, preds in by_variable.items():
            total_weight = sum(p["confidence"] * self.weights[p["mechanism"]]
                              for p in preds)
            weighted_sum = sum(p["value"] * p["confidence"] * self.weights[p["mechanism"]]
                              for p in preds)

            ensemble_value = weighted_sum / total_weight
            ensemble_confidence = total_weight / len(preds)

            self.write_keys[var_idx].add_hypothesis(
                VariableRecord(
                    value=ensemble_value,
                    confidence=ensemble_confidence,
                    source=self.key(),
                    metadata={
                        "component_predictions": [
                            {"mechanism": p["mechanism"], "value": p["value"]}
                            for p in preds
                        ]
                    }
                )
            )
```

### Pattern 3: Adaptive Mechanisms

```python
import numpy as np

from procela import Mechanism, VariableRecord

class AdaptiveMechanism(Mechanism):
    """Adapts its parameters based on governance feedback"""

    def __init__(self, reads, writes, initial_params=None):
        super().__init__(reads, writes)
        self.params = initial_params or {"rate": 0.1, "threshold": 0.5}
        self.adaptation_history = []
        self.performance_window = []

    def transform(self):
        # Use current parameters
        prediction = self._predict_with_params() # to be implemented
        confidence = self._compute_confidence()  # to be implemented

        self.writes()[0].add_hypothesis(
            VariableRecord(prediction, confidence=confidence, source=self.key())
        )

    def adapt(self, feedback):
        """Called by governance to adapt mechanism"""
        self.performance_window.append(feedback)

        # Keep window manageable
        if len(self.performance_window) > 50:
            self.performance_window.pop(0)

        # Adaptation logic
        old_params = self.params.copy()

        if len(self.performance_window) > 10:
            avg_error = np.mean(self.performance_window[-10:])

            # Adjust rate based on error
            if avg_error > 0.5:
                self.params["rate"] *= 0.95  # Slow down
            elif avg_error < 0.1:
                self.params["rate"] *= 1.05  # Speed up

        # Record adaptation
        self.adaptation_history.append({
            "old_params": old_params,
            "new_params": self.params.copy(),
            "feedback": feedback
        })
```

## Mechanism Lifecycle

### 1. Initialization

```python
# Created with read/write dependencies
mechanism = MyMechanism()

# Added to executive
executive.add_mechanism(mechanism)

# Removed from executive
executive.remove_mechanism(mechanism)

# Disabled
mechanism.disable()

# Enabled
mechanism.enable()
```

### 2. Execution

```python
# Each simulation step:
for step in range(n_steps):
    # 1. Mechanisms transform
    for mechanism in active_mechanisms:
        mechanism.transform()  # Proposes hypotheses

    # 2. Variables resolve
    for variable in all_variables:
        variable.resolve_conflict()  # Selects final value
```

### 3. Deactivation/Removal

```python
# Governance can disable mechanisms
mechanism.disable()

# Or remove them entirely
executive.remove_mechanism(mechanism)
```

## Best Practices

### 1. Single Responsibility
```python
# Good: Each mechanism encodes one theory
class LinearGrowthMechanism(Mechanism):
    pass

class LogisticGrowthMechanism(Mechanism):
    pass

# Avoid: One mechanism trying to do everything
class EverythingMechanism(Mechanism):  # Too complex
    pass
```

### 2. Meaningful Confidence
```python
# Good: Confidence reflects uncertainty
def compute_confidence(self):
    if self.has_validation_data:
        return self.historical_accuracy
    else:
        return 0.5  # Default uncertainty

# Bad: Arbitrary confidence
confidence = 0.99  # Always high, meaningless
```

### 3. Metadata for Auditability
```python
# Good: Include model details
VariableRecord(
    value=prediction,
    confidence=confidence,
    source=self.key(),
    metadata={
        "model_version": "2.1",
        "parameters": self.params,
        "training_data": "2024_dataset"
    }
)
```

### 4. Handle Edge Cases
```python
def transform(self):
    current = self.reads()[0].value

    # Guard against invalid inputs
    if current is None or current < 0:
        # Propose fallback with low confidence
        self.writes()[0].add_hypothesis(
            VariableRecord(0, confidence=0.1, source=self.key())
        )
        return

    # Normal operation
    # ...
```

## Common Use Cases

### Use Case 1: Predictive Models
```python
class NeuralNetworkMechanism(Mechanism):
    """Wrapper for ML model predictions"""

    def __init__(self, model_path, reads, writes):
        super().__init__(reads, writes)
        self.model = load_model(model_path)

    def transform(self):
        features = [var.value for var in self.reads()]
        prediction = self.model.predict(features)
        confidence = self.model.prediction_confidence()

        self.writes()[0].add_hypothesis(
            VariableRecord(prediction, confidence=confidence, source=self.key())
        )
```

### Use Case 2: Physics-Based Simulation
```python
class PhysicsMechanism(Mechanism):
    """Newtonian physics simulation"""

    def transform(self):
        position = self.reads()[0].value
        velocity = self.reads()[1].value
        dt = 0.1

        # Euler integration
        new_position = position + velocity * dt

        self.writes()[0].add_hypothesis(
            VariableRecord(new_position, confidence=0.95, source=self.key())
        )
```

### Use Case 3: Rule-Based Systems
```python
class RuleBasedMechanism(Mechanism):
    """Expert system with if-then rules"""

    def __init__(self):
        super().__init__(reads=[temperature, humidity], writes=[alert])
        self.rules = [
            (lambda t, h: t > 35 and h < 30, "heat_warning", 0.8),
            (lambda t, h: t < 0, "freeze_warning", 0.9),
            (lambda t, h: h > 80, "humidity_warning", 0.7),
        ]

    def transform(self):
        temp = self.reads()[0].value
        hum = self.reads()[1].value

        for condition, alert, confidence in self.rules:
            if condition(temp, hum):
                self.writes()[0].add_hypothesis(
                    VariableRecord(alert, confidence=confidence, source=self.key())
                )
                return

        # Default: no alert
        self.writes()[0].add_hypothesis(
            VariableRecord("normal", confidence=0.95, source=self.key())
        )
```

## Performance Considerations

### Efficient Transformations
```python
class EfficientMechanism(Mechanism):
    def __init__(self, reads, writes):
        super().__init__(reads, writes)
        self.cache = {}  # Cache expensive computations

    def transform(self):
        # Cache key based on inputs
        key = tuple(var.value for var in self.reads())

        if key in self.cache:
            prediction, confidence = self.cache[key]
        else:
            # Expensive computation
            prediction = self._expensive_computation()
            confidence = self._compute_confidence()
            self.cache[key] = (prediction, confidence)

        # Propose
        self.writes()[0].add_hypothesis(
            VariableRecord(prediction, confidence=confidence, source=self.key())
        )
```

## Testing Mechanisms

```python
import unittest

from procela import Variable, RangeDomain, VariableRecord

class TestMyMechanism(unittest.TestCase):
    def setUp(self):
        self.X = Variable("X", RangeDomain(0, 100))
        self.X.init(VariableRecord(50, confidence=1.0))
        self.mechanism = MyMechanism(reads=[self.X], writes=[self.X])

    def test_transform_adds_hypothesis(self):
        """Should add hypothesis to variable"""
        initial_count = len(self.X.hypotheses)

        self.mechanism.transform()

        self.assertEqual(len(self.X.hypotheses), initial_count + 1)

    def test_prediction_in_domain(self):
        """Predictions should respect variable domain"""
        for _ in range(100):
            self.mechanism.transform()
            hypothesis = self.X.hypotheses[-1].record
            self.assertGreaterEqual(hypothesis.value, 0)
            self.assertLessEqual(hypothesis.value, 100)

    def test_confidence_in_range(self):
        """Confidence should be between 0 and 1"""
        self.mechanism.transform()
        hypothesis = self.X.hypotheses[-1].record
        self.assertGreaterEqual(hypothesis.confidence, 0)
        self.assertLessEqual(hypothesis.confidence, 1)
```

## Next Steps

- Learn how [Governance](governance.md) observes and restructures mechanisms
- Explore [Epistemic Signals](epistemic-signals.md) for evaluating mechanism performance
- See the [AMR Case Study](../examples/amr-case-study.md) with competing mechanisms
- Check the [API Reference](../api/reference.md) for complete Mechanism documentation
