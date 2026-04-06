# Temperature Simulation Code

```python
# 1: Import dependencies

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
np.random.seed(1)


# 2: Define the Variable

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


# 3: Create Multiple Mechanisms

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


# 4: Create the Executive

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


# 5: Create Governance (one invariant & pre/post hooks)

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


# 6: Run the Simulation

print("\n" + "="*50)
print("Starting simulation...")
print("="*50)

# Run with detailed logging
post_step = create_post_step(error_threshold = 0.2)
executive.run(steps=100, pre_step=pre_step, post_step=post_step)

print("\n" + "="*50)
print("Simulation complete!")
print("="*50)


# 7: Analyze Results

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


# 8: Visualization (Optional)

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
