# Your First Simulation

This tutorial walks you through creating a complete simulation with Procela, from basic setup to intermediate governance. By the end, you'll have built a simulation that can adapt its own structure based on epistemic signals.

## What We'll Build

We'll create a simple **temperature regulation system** with multiple competing mechanisms that propose different temperature predictions. The system will use governance to detect when predictions are inconsistent and adapt its resolution strategy.

## Prerequisites

- Procela installed (see [Installation Guide](installation.md))
- Basic Python knowledge
- A code editor of your choice

## Step 1: Import Dependencies

Create a new Python file `temperature_simulation.py`:

```python
import numpy as np

from procela import (
    Executive,
    Mechanism,
    Variable,
    RangeDomain,
    VariableRecord,
    WeightedConfidencePolicy,
    HighestConfidencePolicy,
    SystemInvariant,
    InvariantPhase,
    InvariantViolation,
    VariableSnapshot,
    ReasoningTask,
    KeyAuthority
)
np.random.seed(1) # for reproducibility
```

## Step 2: Define the Variable

Variables are epistemic authorities that maintain hypothesis histories and resolve competing claims:

```python
# Create a variable with a valid range
temperature = Variable(
    name="Temperature",
    domain=RangeDomain(-10, 50),  # Celsius range
    policy=WeightedConfidencePolicy()  # Initial resolution policy
)

# Initialize with a starting value
temperature.init(
    VariableRecord(
        value=20.0,
        confidence=1.0,
        source=None
    )
)

print(f"Initial temperature: {temperature.value:.2f}°C")
```

**Key Concepts:**
- **Domain**: Defines valid value ranges (prevents impossible values)
- **Policy**: Determines how competing hypotheses are resolved
- **VariableRecord**: A hypothesis record with value, confidence, and source tracking

## Step 3: Create Multiple Mechanisms

Mechanisms represent competing scientific theories. Each proposes hypotheses but never directly modifies state:

```python
class OptimisticMechanism(Mechanism):
    """Assumes temperature tends to increase (global warming)"""

    def __init__(self):
        super().__init__(reads=[temperature], writes=[temperature])
        self.drift = 0.2

    def transform(self):
        current = self.reads()[0].value
        # Propose a warming trend
        proposed = current + self.drift + np.random.normal(0, 0.3)
        # Moderate confidence
        confidence = np.clip(0.6 + np.random.normal(0, 0.1), 0, 1)

        self.writes()[0].add_hypothesis(
            VariableRecord(
                value=proposed,
                confidence=float(confidence),
                source=self.key()
            )
        )

class PessimisticMechanism(Mechanism):
    """Assumes temperature tends to decrease (cooling trend)"""

    def __init__(self):
        super().__init__(reads=[temperature], writes=[temperature])
        self.drift = -0.15

    def transform(self):
        current = self.reads()[0].value
        # Propose a cooling trend
        proposed = current + self.drift + np.random.normal(0, 0.3)
        confidence = np.clip(0.6 + np.random.normal(0, 0.1), 0, 1)

        self.writes()[0].add_hypothesis(
            VariableRecord(
                value=proposed,
                confidence=float(confidence),
                source=self.key()
            )
        )

class RandomMechanism(Mechanism):
    """Assumes temperature follows random walk"""

    def __init__(self):
        super().__init__(reads=[temperature], writes=[temperature])

    def transform(self):
        current = self.reads()[0].value
        # Propose random changes
        proposed = current + np.random.normal(0, 0.5)
        # Lower confidence due to randomness
        confidence = np.clip(0.4 + np.random.normal(0, 0.1), 0, 1)

        self.writes()[0].add_hypothesis(
            VariableRecord(
                value=proposed,
                confidence=float(confidence),
                source=self.key()
            )
        )

class ConservativeMechanism(Mechanism):
    """Assumes temperature remains stable"""

    def __init__(self):
        super().__init__(reads=[temperature], writes=[temperature])

    def transform(self):
        current = self.reads()[0].value
        # Propose minimal changes
        proposed = current + np.random.normal(0, 0.1)
        # High confidence in stability
        confidence = np.clip(0.8 + np.random.normal(0, 0.1), 0, 1)

        self.writes()[0].add_hypothesis(
            VariableRecord(
                value=proposed,
                confidence=float(confidence),
                source=self.key()
            )
        )
```

## Notes

We could create a single custom mechanism (with parameters) to implement these mechanisms. For the sake of simplicity, we define them separately.

## Step 4: Create the Executive

The Executive orchestrates all simulation components:

```python
# Initialize all mechanisms
mechanisms = [
    OptimisticMechanism(),
    PessimisticMechanism(),
    RandomMechanism(),
    ConservativeMechanism()
]

# Create executive
executive = Executive(mechanisms=mechanisms)

print(f"Executive created with {len(mechanisms)} mechanisms")
```

## Step 5: Create Governance

Governance units observe epistemic signals and can restructure the simulation:

```python
class FragilityDetector(SystemInvariant):
    """Detects when hypothesis confidence spread is too high and switches policy"""

    def __init__(self, threshold=0.6):
        self.threshold = threshold
        self.policy_switched = False

        def check(snapshot: VariableSnapshot):
            # Get all hypothesis confidences for the current step
            confidences = []
            var = KeyAuthority.resolve(snapshot.views[0].key)
            for hypothesis in var.hypotheses:
                confidences.append(hypothesis.record.confidence)

            if not confidences:
                return True

            # Check if confidence spread exceeds threshold
            confidence_spread = max(confidences) - min(confidences)
            return confidence_spread <= self.threshold

        def handle(invariant: InvariantViolation, snapshot: VariableSnapshot):
            if not self.policy_switched:
                print(
                    f"\n⚠️  Step {snapshot.step} - Fragility detected! "
                    f"Confidence spread > {self.threshold} - Switching to HighestConfidencePolicy..."
                )
                temperature.policy = HighestConfidencePolicy()
                self.policy_switched = True

        super().__init__(
            name="FragilityDetector",
            condition=check,
            on_violation=handle,
            phase=InvariantPhase.RUNTIME,
            message="High confidence spread detected"
        )

def pre_step(executive: Executive, step: int):
    if step == 25:
        # Disable RandomMechanism
        for mech in executive.mechanisms():
            if mech.name == "RandomMechanism":
                mech.disable()
                executive.logger.info(
                    f"  Step {step} - Mechanism {mech.name} has been disabled."
                )

    if step == 75:
        # Enable RandomMechanism
        for mech in executive.mechanisms():
            if mech.name == "RandomMechanism":
                mech.enable()
                executive.logger.info(
                    f"  Step {step} - Mechanism {mech.name} has been enabled."
                )

def create_post_step(error_threshold: float = 0.2):
    def post_step(executive: Executive, step: int):
        if step < 2:
            return

        var = list(executive.writable())[0] # variable temperature

        actual = var.get(-2)[0][1].value
        predicted = var.value
        error = abs(actual - predicted)

        if error > error_threshold:
            executive.logger.warning(
                f"  📊 Step {step} - High prediction error: "
                f"{error:.2f}°C (threshold: {error_threshold}°C)"
            )

    return post_step

# Add governance to executive
executive.add_invariant(FragilityDetector(threshold=0.6))

print("Governance units added")
```

## Step 6: Run the Simulation

Execute the simulation and observe the dynamics:

```python
print("\n" + "="*50)
print("Starting simulation...")
print("="*50)

# Run with detailed logging
post_step = create_post_step(error_threshold = 0.2)
executive.run(steps=100, pre_step=pre_step, post_step=post_step)

print("\n" + "="*50)
print("Simulation complete!")
print("="*50)
```

## Step 7: Analyze Results

Let's add analysis code to understand what happened:

```python
# Access variable memory for analysis
def analyze_results(variable: Variable):
    """Analyze the simulation results"""
    memory = variable.memory
    #policies = variable.policy_history

    print("\n📈 Simulation Analysis")
    print("-" * 40)

    # Basic statistics
    values = [record.value for _, record, _ in memory.records()]
    confidences = [record.confidence for _, record, _ in memory.records()]
    policies = []
    for step, (_, record, _) in enumerate(memory.records(task=ReasoningTask.CONFLICT_RESOLUTION)):
        if record.source is not None:
            policy = KeyAuthority.resolve(record.source)
            if len(policies) <= 0:
                policies.append((step, policy))
                continue

            if record.source != policies[-1][1].key():
                policies.append((step, policy))


    print(f"Start value: {values[0]:.2f}°C")
    print(f"End value: {values[-1]:.2f}°C")
    print(f"Change: {values[-1] - values[0]:+.2f}°C")
    print(f"Mean confidence: {np.mean(confidences):.3f}")
    print(f"Min confidence: {np.min(confidences):.3f}")
    print(f"Max confidence: {np.max(confidences):.3f}")

    # Policy changes
    if policies:
        print(f"\n📋 Policy changes ({len(policies)}):")
        for step, policy in policies:
            print(f"  Step {step}: {policy.name}")


    # Hypothesis diversity
    all_hypotheses = []
    for step, (hypotheses, _, _) in enumerate(memory.records()):
        if record.source:
            all_hypotheses.extend(
                KeyAuthority.resolve(hy.record.source).name for hy in hypotheses
                if hy.record.source is not None
            )

    unique_sources = set(all_hypotheses)
    print(f"\n🔬 Active mechanisms: {len(unique_sources)}")
    for source in unique_sources:
        count = all_hypotheses.count(source)
        print(f"  {source}: {count} hypotheses")

# Run analysis
analyze_results(temperature)
```

## Step 8: Visualization (Optional)

Add simple visualization to see the dynamics:

```python
import matplotlib.pyplot as plt

def plot_simulation(variable: Variable):
    """Plot temperature over time with confidence intervals"""

    memory = variable.memory
    steps = range(variable.stats.count)
    values = [record.value for _, record, _ in memory.records()]
    confidences = [record.confidence for _, record, _ in memory.records()]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Temperature plot
    ax1.plot(steps, values, 'b-', linewidth=2, label='Temperature')
    ax1.fill_between(steps,
                     [v - c for v, c in zip(values, confidences)],
                     [v + c for v, c in zip(values, confidences)],
                     alpha=0.3, label='Confidence interval')
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Temperature (°C)')
    ax1.set_title('Temperature Evolution with Confidence')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Confidence plot
    ax2.plot(steps, confidences, 'r-', linewidth=2, label='Confidence')
    ax2.set_xlabel('Step')
    ax2.set_ylabel('Confidence')
    ax2.set_title('Confidence Evolution')
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    plt.savefig('simulation_results.png', dpi=150)
    plt.show()

# Uncomment to plot (requires matplotlib)
#plot_simulation(temperature)
```

## Complete Script

The complete simulation script with all components is available [here](../examples/temperature-simulation.md)



## Expected Output

When you run the simulation, you'll see output similar to:

```
Initial temperature: 20.00°C
Executive created with 4 mechanisms
Governance units added

==================================================
Starting simulation...
==================================================

⚠️  Step 5 - Fragility detected! Confidence spread > 0.6 - Switching to HighestConfidencePolicy...
2026-03-31 20:11:28 | WARNING  | procela |   📊 Step 19 - High prediction error: 0.51°C (threshold: 0.2°C)
2026-03-31 20:11:28 | INFO     | procela |   Step 25 - Mechanism RandomMechanism has been disabled.
2026-03-31 20:11:28 | WARNING  | procela |   📊 Step 25 - High prediction error: 0.32°C (threshold: 0.2°C)
2026-03-31 20:11:28 | WARNING  | procela |   📊 Step 26 - High prediction error: 0.49°C (threshold: 0.2°C)
2026-03-31 20:11:28 | WARNING  | procela |   📊 Step 33 - High prediction error: 0.28°C (threshold: 0.2°C)
2026-03-31 20:11:28 | WARNING  | procela |   📊 Step 41 - High prediction error: 0.33°C (threshold: 0.2°C)
2026-03-31 20:11:28 | WARNING  | procela |   📊 Step 42 - High prediction error: 0.23°C (threshold: 0.2°C)
2026-03-31 20:11:28 | WARNING  | procela |   📊 Step 47 - High prediction error: 0.20°C (threshold: 0.2°C)
2026-03-31 20:11:28 | WARNING  | procela |   📊 Step 52 - High prediction error: 0.22°C (threshold: 0.2°C)
2026-03-31 20:11:28 | WARNING  | procela |   📊 Step 70 - High prediction error: 0.21°C (threshold: 0.2°C)
2026-03-31 20:11:28 | INFO     | procela |   Step 75 - Mechanism RandomMechanism has been enabled.
2026-03-31 20:11:28 | WARNING  | procela |   📊 Step 83 - High prediction error: 0.29°C (threshold: 0.2°C)
2026-03-31 20:11:28 | WARNING  | procela |   📊 Step 94 - High prediction error: 0.67°C (threshold: 0.2°C)

==================================================
Simulation complete!
==================================================

📈 Simulation Analysis
----------------------------------------
Start value: 20.00°C
End value: 20.09°C
Change: +0.09°C
Mean confidence: 0.820
Min confidence: 0.481
Max confidence: 1.000

📋 Policy changes (2):
  Step 0: WeightedConfidencePolicy
  Step 5: HighestConfidencePolicy

🔬 Active mechanisms: 4
  PessimisticMechanism: 100 hypotheses
  ConservativeMechanism: 100 hypotheses
  RandomMechanism: 50 hypotheses
  OptimisticMechanism: 100 hypotheses
```

## Key Takeaways

1. **Multiple Mechanisms**: Different theories compete to explain the system
2. **Epistemic Tracking**: Every hypothesis is recorded with confidence and source
3. **Adaptive Governance**: The system detects problems and adapts its structure
4. **Auditable History**: Complete trace of all decisions and changes

## Next Steps

Now that you've built your first simulation:

- Explore [Core Concepts](../core-concepts/variables.md) to understand the architecture
- Study the [AMR Case Study](../examples/amr-case-study.md) for a real-world application
- Learn about [Custom Policies](../advanced/custom-policies.md) for advanced resolution strategies
- Check the [API Reference](../api/reference.md) for detailed class documentation

## Troubleshooting

**Common issues and solutions:**

- **ImportError**: Ensure Procela is installed correctly (`pip install procela`)
- **Mechanism not proposing**: Check that `transform()` method adds hypotheses with `add_hypothesis()`
- **Policy not switching**: Verify governance invariants are added with `add_invariant()`
- **Memory overflow**: For long simulations, consider pruning old hypotheses (advanced topic)

## Exercises

Try modifying the simulation to:

1. Add a new mechanism with a different temperature model
2. Create a governance unit that disables poorly performing mechanisms
3. Implement a voting policy that weights mechanisms by historical accuracy
4. Add logging to track which mechanism's hypotheses are accepted most often
