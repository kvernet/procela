# Variables: Memory-bearing Epistemic Authorities

In Procela, **Variables** are not simple containers for data—they are **epistemic authorities** that actively manage knowledge about the system. They maintain complete hypothesis histories, resolve competing claims, and track the provenance of every value.


This guide covers:

- Core concepts and what makes Procela variables unique
- Creation, initialization, and configuration
- Policy resolution with built-in and custom examples
- Advanced features like source tracking and memory management
- Practical examples
- Common patterns for specialized variable types

## Core Concepts

### What Makes Variables Different?

Traditional simulation frameworks treat variables as simple state containers:

```python
# Traditional approach
temperature = 20.0  # Just a number
```

Procela variables are epistemic agents:

```python
# Procela approach
temperature = Variable("Temperature", domain=RangeDomain(-10, 50))
temperature.init(VariableRecord(20.0, confidence=1.0, source=None))

# Later, multiple mechanisms propose competing hypotheses
# The variable resolves them based on its policy
# Every value has tracked provenance
```

### Key Features

| Feature | Description |
|---------|-------------|
| **Hypothesis Memory** | Stores all proposed values with metadata |
| **Source Tracking** | Every hypothesis records its origin (mechanism, confidence) |
| **Policy Resolution** | Competing claims resolved via configurable policies |
| **Domain Constraints** | Ensures values stay within valid ranges |
| **Audit Trail** | Complete history of all changes and decisions |

## Creating a Variable

### Basic Creation

```python
from procela import Variable, RangeDomain, WeightedVotingPolicy, HighestConfidencePolicy

# Create with minimal parameters
population = Variable("Population", domain=RangeDomain(0, 1e9))

# With custom policy
temp = Variable(
    name="Temperature",
    domain=RangeDomain(-273.15, 1000),
    policy=WeightedVotingPolicy()
)

# With unit & description
cases = Variable(
    name="InfectedCases",
    domain=RangeDomain(0, 1e6),
    units="people",
    policy=HighestConfidencePolicy(),
    description="source WHO"
)
```

### Domain Types

Procela provides several domain types for constraining values:

```python
from procela import Variable, RangeDomain, CategoricalDomain, CompositeDomain, VariableRecord

# Continuous range
temperature = Variable("Temp", RangeDomain(-10, 40))

# Specific list of options
state = Variable("State", CategoricalDomain(["S", "I", "R"]))

# Custom domain with validation
class PositiveDomain(RangeDomain):
    def __init__(self):
        super().__init__(0, float('inf'))

    def validate(self, value, stats):
        return value >= 0


# Composite domain (Positive & Discrete integer range)
age = Variable("Age", CompositeDomain([
    PositiveDomain(), CategoricalDomain(list(range(0, 120)))
]))

age.set(VariableRecord(value=10, confidence=None)) # Correct

age.set(VariableRecord(value=10.9, confidence=None)) # Failed composite domain
```

## Initialization

Variables must be initialized before use:

```python
from procela import (
    Variable,
    RangeDomain,
    VariableRecord,
    HighestConfidencePolicy,
    Key
)

# Continuous range
temperature = Variable("Temp", RangeDomain(-10, 40))

# Basic initialization
X = Variable("X", domain=RangeDomain(0, 100))
X.init(VariableRecord(50.0, confidence=1.0, source=None))

# Initialize with history
hypotheses = [
    VariableRecord(10.0, confidence=0.8, source=Key()),
    VariableRecord(12.0, confidence=0.9, source=Key()),
]

# Temporary memory
for hy in hypotheses:
    X.add_hypothesis(hy)

print(X.summary())


# Permanent memory
X.policy = HighestConfidencePolicy()
X.resolve_conflict()
X.commit()

print(X.summary())
```

## Variable Anatomy

### HypothesisRecord: The Hypothesis Unit

Every hypothesis is stored as a `HypothesisRecord`:

```python
from procela import HypothesisRecord, VariableRecord, HypothesisState, Key

record = HypothesisRecord(
    VariableRecord(
        value=42.5,           # The proposed value
        confidence=0.85,      # Confidence score (0-1)
        source=Key(),  # Origin of hypothesis
        explanation="",
        metadata={            # Optional additional data
            "model_version": "2.1",
            "training_data": "2024_dataset"
        },
    ),
    state=HypothesisState.PROPOSED  # State status
)

```

### Memory Management

Variables maintain complete hypothesis histories:

```python
import random

from procela import (
    Variable,
    RangeDomain,
    VariableRecord,
    WeightedConfidencePolicy,
    Key,
    ReasoningTask
)

random.seed(42)

X = Variable("X", RangeDomain(0, 100), policy=WeightedConfidencePolicy())
X.init(VariableRecord(10.4, confidence=1.0))

for _ in range(100):
    hypotheses = [
        VariableRecord(value=random.gauss(0, 1), confidence=0.9, source=Key()),
        VariableRecord(value=random.gauss(0, 3), confidence=0.5, source=Key()),
        VariableRecord(value=random.gauss(0, 2), confidence=0.75, source=Key())
    ]
    for hypothesis in hypotheses:
        X.add_hypothesis(hypothesis)

    X.resolve_conflict()
    X.commit()
    X.clear_hypotheses()


# Access memory
all_records = X.memory.records()  # List of all VariableRecords ever RECORDED (included the init)
print(f"{len(all_records)} records")
print(X.value, X.confidence)


all_records = X.memory.records(task=ReasoningTask.CONFLICT_RESOLUTION)  # List of all VariableRecords ever proposed
print(f"{len(all_records)} records")


current_record = X.get(-1)[0]  # Current VariableRecord (with provenance)
print(len(current_record[0]), current_record[1].value, current_record[2].explanation)

current_record = all_records[-1]
print(len(current_record[0]), current_record[1].value, current_record[2].explanation)

current_record = X.memory.latest()
print(len(current_record[0]), current_record[1].value, current_record[2].explanation)


# Memory introspection
for i, (_, record, _) in enumerate(X.get(-10, 10, reverse=True)):  # Last 10 hypotheses
    print(f"Step {i}: value={record.value:.2f}, "
          f"conf={record.confidence:.2f}, "
          f"source={record.source}")
```

## Policy Resolution

Policies determine how competing hypotheses are resolved into a single value.

### Built-in and User-defined Policies

```python
from procela import (
    Variable,
    RealDomain,
    WeightedVotingPolicy,
    HighestConfidencePolicy
)

X = Variable("X", RealDomain())

# Weighted by confidence
X.policy = WeightedVotingPolicy()

# Always pick highest confidence
X.policy = HighestConfidencePolicy()


# Users can define their own policies
# Statistical aggregation
X.policy = MedianPolicy()     # Median value
X.policy = MeanPolicy()       # Arithmetic mean

# Democratic voting
X.policy = MajorityVotingPolicy()  # Most common value
```

### Custom Policies

Create custom resolution logic:

```python
from procela import (
    Variable,
    RealDomain,
    ResolutionPolicy,
    VariableRecord,
    Key
)

X = Variable("X", RealDomain())

class ConsensusWithThresholdPolicy(ResolutionPolicy):
    """Requires minimum agreement before settling on a value"""

    def __init__(self, threshold=0.7):
        super().__init__()
        self.threshold = threshold

    def resolve(self, hypotheses):
        """
        Parameters
        ----------
            hypotheses: List of HypothesisRecord objects

        Returns
        -------
            VariableRecord: The resolved hypothesis or None
        """
        if not hypotheses:
            return None

        # Check if we have strong agreement
        values = [h.record.value for h in hypotheses]
        confidences = [h.record.confidence for h in hypotheses]

        # Weighted average
        total_weight = sum(confidences)
        weighted_avg = sum(v * c for v, c in zip(values, confidences)) / total_weight

        # Calculate spread
        spread = max(values) - min(values)

        if spread < self.threshold:
            # Good consensus - return weighted average
            value = weighted_avg
            confidence = total_weight / len(hypotheses)
            explanation = "Good consensus - return weighted average"
        else:
            # Poor consensus - fall back to highest confidence
            best = max(hypotheses, key=lambda h: h.record.confidence)
            value = best.record.value
            confidence = best.record.confidence * 0.8  # Penalized
            explanation = "Poor consensus - fall back to highest confidence"

        return VariableRecord(
            value=value,
            confidence=confidence,
            source=self.key(),
            explanation=explanation
        )

# Use custom policy
X.policy = ConsensusWithThresholdPolicy(threshold=0.5)

X.add_hypothesis(VariableRecord(10, confidence=0.8, source=Key()))
X.add_hypothesis(VariableRecord(9.9, confidence=0.85, source=Key()))

resolved = X.resolve_conflict()
X.clear_hypotheses()

print(resolved.value, resolved.confidence, resolved.explanation)


X.add_hypothesis(VariableRecord(10, confidence=0.8, source=Key()))
X.add_hypothesis(VariableRecord(0.9, confidence=0.85, source=Key()))

resolved = X.resolve_conflict()
X.clear_hypotheses()

print(resolved.value, resolved.confidence, resolved.explanation)
```

## Practical Examples

### Example 1: Multi-Source Temperature Monitoring

```python
import numpy as np

from procela import (
    Variable,
    RangeDomain,
    VariableRecord,
    WeightedVotingPolicy,
    Mechanism,
    Key
)

# Create temperature variable with multiple sensor inputs
temperature = Variable(
    "Temperature",
    domain=RangeDomain(-20, 45),
    policy=WeightedVotingPolicy()
)

# Initialize with sensor calibration
sensor_configs = {
    "sensor_A": {"confidence": 0.95, "bias": 0.2, "weight": 0.3, "source": Key()},
    "sensor_B": {"confidence": 0.88, "bias": -0.1, "weight": 0.6, "source": Key()},
    "sensor_C": {"confidence": 0.92, "bias": 0.0, "weight": 0.1, "source": Key()}
}

class SensorMechanism(Mechanism):
    def __init__(self, config):
        super().__init__(reads=[], writes=[temperature])
        self.config = config

    def transform(self):
        # Simulate sensor reading with noise and bias
        true_temp = 22.5
        measurement = (true_temp +
                      self.config["bias"] +
                      np.random.normal(0, 0.3))

        temperature.add_hypothesis(
            VariableRecord(
                value=measurement,
                confidence=self.config["confidence"],
                source=self.config["source"],
                metadata={"weight": self.config["weight"]}
            )
        )

mechs = [
    SensorMechanism(config=config)
    for config in sensor_configs.values()
]

for mech in mechs:
    mech.run()


for hy in temperature.hypotheses:
    print(hy.record.value, hy.record.confidence, hy.record.source)


resolved = temperature.resolve_conflict()

print(resolved)
```

### Example 2: Decision-Making Variable

```python
from procela import (
    Variable,
    RangeDomain,
    CategoricalDomain,
    VariableRecord,
    HighestConfidencePolicy,
    Mechanism
)

# Variable for strategic decisions
market_volume = Variable(
    "market_volume",
    domain=RangeDomain(0, 1e12),
    policy=None
)
market_volatility = Variable(
    "market_volatility",
    domain=RangeDomain(0, 1),
    policy=None
)
strategy = Variable(
    "Strategy",
    domain=CategoricalDomain(["aggressive", "conservative", "adaptive"]),
    policy=HighestConfidencePolicy()
)

# Different experts propose strategies
class ExpertMechanism(Mechanism):
    def __init__(self, expert_type):
        super().__init__(reads=[market_volume, market_volatility], writes=[strategy])
        self.expert_type = expert_type

    def transform(self):
        volume, volatility = [var.value for var in self.reads()]

        if self.expert_type == "risk_taker":
            proposed = "aggressive" if volatility < 0.3 else "conservative"
            confidence = 0.7
        elif self.expert_type == "risk_averse":
            proposed = "conservative"
            confidence = 0.9
        else:  # balanced
            proposed = "adaptive"
            confidence = 0.8

        strategy.add_hypothesis(
            VariableRecord(
                value=proposed,
                confidence=confidence,
                source=self.key()
            )
        )

market_volatility.init(VariableRecord(value=0.7, confidence=0.9))

mechs = [
    ExpertMechanism(expert_type=expert_type)
    for expert_type in ("risk_taker", "risk_averse", "balanced")
]

for mech in mechs:
    mech.run()

strategy.resolve_conflict()
strategy.commit()

# Variable resolves to most confident strategy
print(f"Adopted strategy: {strategy.value}")
```

## Common Patterns

### Pattern 1: Variable with Fallback
```python
from procela import Variable

class FallbackVariable(Variable):
    def resolve_conflict(self):
        """Try policy, fallback to previous value on failure"""
        try:
            return super().resolve_conflict()
        except:
            # Return last good value if resolution fails
            return self.value
```

### Pattern 2: Anomaly Detection
```python
import numpy as np

from procela import Variable, RangeDomain, VariableRecord, WeightedConfidencePolicy

np.random.seed(42)

class AnomalyDetectingVariable(Variable):
    def add_hypothesis(self, record):
        confidence = record.confidence
        metadata = record.metadata

        # Check for anomalies before adding
        if self.memory:
            records = self.memory.records()
            mean = np.mean([r.value for _, r, _ in records[-10:]])
            std = np.std([r.value for _, r, _ in records[-10:]])

            if abs(record.value - mean) > 3 * std:
                # Anomaly detected - reduce confidence
                confidence *= 0.5
                metadata["anomaly"] = True

        super().add_hypothesis(
            VariableRecord(value=record.value, confidence=confidence*0.5, metadata=metadata)
        )

X = AnomalyDetectingVariable("X", RangeDomain(0, 100))
X.policy = WeightedConfidencePolicy()

for _ in range(5):
    X.add_hypothesis(VariableRecord(value=1, confidence=0.9))
    X.add_hypothesis(VariableRecord(value=10, confidence=0.4))
    X.add_hypothesis(VariableRecord(value=2, confidence=0.7))

    for hy in X.hypotheses:
        print(hy.record.value, hy.record.confidence, hy.record.metadata.get("anomaly", False))

    X.resolve_conflict()
    X.commit()
    X.clear_hypotheses()
```

## Next Steps

- Learn about [Mechanisms](mechanisms.md) that propose hypotheses to variables
- Understand [Governance](governance.md) that observes variable signals
- Explore [Epistemic Signals](epistemic-signals.md) for monitoring variable states
- See the [API Reference](../api/reference.md) for complete Variable documentation
