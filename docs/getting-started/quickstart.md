# Quick Start

This guide will help you get started with Procela in minutes.

## Installation

```bash
pip install procela
```

For development installation, see the [Installation Guide](installation.md).

## Your First Simulation

Let's create a simple simulation with one variable and one mechanism.

### Step 1: Import and Create a Variable

```python
from procela import (
    Variable,
    RangeDomain,
    WeightedConfidencePolicy,
    VariableRecord
)

# Create a variable with a domain
temperature = Variable("temperature", RangeDomain(-10, 40), policy=WeightedConfidencePolicy())

# Initialize it with a starting value
temperature.init(VariableRecord(20.0, confidence=1.0))
```

### Step 2: Define Mechanism

```python
import numpy as np
from procela import Mechanism
np.random.seed(1)

class TemperatureMechanism(Mechanism):
    def __init__(self, sigma=1.0):
        super().__init__(reads=[temperature], writes=[temperature])
        self.sigma = sigma

    def transform(self):
        # Read current value
        current = self.reads()[0].value

        # Propose a new hypothesis
        new_value = current + np.random.normal(0, self.sigma)

        # Add hypothesis with confidence
        self.writes()[0].add_hypothesis(
            VariableRecord(new_value, confidence=np.random.uniform(0.5, 0.95), source=self.key())
        )
```

### Step 3: Run the Simulation

```python
from procela import Executive

# Create executive with our mechanism
executive = Executive(mechanisms=[
    TemperatureMechanism(sigma=1.0),
    TemperatureMechanism(sigma=0.5),
    TemperatureMechanism(sigma=0.1)
])

# Run for 100 steps
executive.run(steps=100)
print(f"Final temperature: {temperature.value:.2f}")

# Memory
hypotheses, conclusion, reasoning = temperature.get(50)[0]
print(f"hypotheses: {len(hypotheses)}")
print(f"{conclusion.value}  {conclusion.confidence}")

hypotheses, conclusion, reasoning = temperature.get(-10, size=5, reverse=True)[3]
print(f"hypotheses: {len(hypotheses)}")
print(f"{conclusion.value}  {conclusion.confidence}")
```

## Adding Governance

Now let's add a governance invariant that monitors prediction confidence:

```python
from procela import (
    SystemInvariant,
    InvariantPhase,
    InvariantViolation,
    VariableSnapshot,
    HighestConfidencePolicy
)

class ConfidenceInvariant(SystemInvariant):
    def __init__(self, threshold=0.3):
        self.threshold = threshold
        self.policy_switched = False

        def check(snapshot: VariableSnapshot):
            # Get all hypothesis confidences for this variable
            confidences = [hy.record.confidence for hy in temperature.hypotheses]
            if confidences:
                # Check if confidence spread is too high
                return max(confidences) - min(confidences) <= self.threshold
            return True

        def handle(invariant: InvariantViolation, snapshot: VariableSnapshot):
            if not self.policy_switched:
                print(
                    f"Step {snapshot.step} - Confidence spread too high! "
                    "Switching to highest-confidence policy"
                )
                temperature.policy = HighestConfidencePolicy()
                self.policy_switched = True

        super().__init__(
            "ConfidenceInvariant",
            condition=check,
            on_violation=handle,
            phase=InvariantPhase.RUNTIME,
            message="Confidence invariant violation"
        )

# Add governance invariant to executive
executive.add_invariant(ConfidenceInvariant())

# Run with governance
executive.run(steps=100)
print(f"Final temperature (with governance): {temperature.value:.2f}")
```

## Expected Output
```text
Final temperature: 27.90
hypotheses: 3
22.800063776097407  0.6932732490133824
hypotheses: 3
26.358564888683674  0.6906402975273261
Step 104 - Confidence spread too high! Switching to highest-confidence policy
Final temperature (with governance): 23.99
```

## What's Next?

- Learn about [Core Concepts](../core-concepts/variables.md)
- Explore the [AMR Case Study](../examples/amr-case-study.md)
- Check the [API Reference](../api/reference.md)
