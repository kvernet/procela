"""Simple Growth Model - Competing population growth theories."""

import matplotlib.pyplot as plt
import numpy as np

from procela import (
    Executive,
    HypothesisRecord,
    Mechanism,
    RangeDomain,
    Variable,
    VariableRecord,
    WeightedConfidencePolicy,
)

rng = np.random.default_rng(42)

# Population variable with realistic bounds (0 to 1000)
population = Variable(
    name="Population",
    domain=RangeDomain(0, 1000),
    policy=WeightedConfidencePolicy(),  # Weighted by confidence
)

# Initialize at 100 individuals
population.init(VariableRecord(value=100.0, confidence=1.0, source=None))

print(f"Initial population: {population.value}")


class LinearGrowthMechanism(Mechanism):
    """Assumes population grows exponentially without limits."""

    def __init__(self, growth_rate: float = 0.05) -> None:
        """Linear growth mechanism constructor."""
        super().__init__(reads=[population], writes=[population])
        self.growth_rate = growth_rate

    def transform(self) -> None:
        """Transform method."""
        current = self.reads()[0].value

        # Linear (exponential) growth model
        # P(t+1) = P(t) * (1 + r)
        new_population = current * (1 + self.growth_rate)

        # Add small random noise to simulate environmental variability
        noise = rng.normal(0, current * 0.02)
        new_population += noise

        # Confidence decreases as population grows (more uncertainty)
        confidence = 0.9 if current < 500 else 0.6

        self.writes()[0].add_hypothesis(
            VariableRecord(
                value=new_population,
                confidence=confidence,
                source=self.key(),
                metadata={"model": "linear", "growth_rate": self.growth_rate},
            )
        )
        print(
            f"  📈 Linear model predicts: {new_population:.1f} (conf: {confidence:.2f})"
        )


class LogisticGrowthMechanism(Mechanism):
    """Assumes growth limited by carrying capacity (environmental limits)."""

    def __init__(
        self, carrying_capacity: float = 800, growth_rate: float = 0.08
    ) -> None:
        """Logistic growth mechanism constructor."""
        super().__init__(reads=[population], writes=[population])
        self.K = carrying_capacity  # Carrying capacity
        self.r = growth_rate  # Maximum growth rate

    def transform(self) -> None:
        """Transform method."""
        current = self.reads()[0].value

        # Logistic growth model
        # P(t+1) = P(t) + r * P(t) * (1 - P(t)/K)
        if current < self.K:
            growth = self.r * current * (1 - current / self.K)
            new_population = current + growth
        else:
            # At or above carrying capacity, population declines
            new_population = current * 0.95

        # Add small random noise
        noise = rng.normal(0, current * 0.01)
        new_population += noise

        # Confidence is higher when population is near equilibrium
        distance_to_capacity = abs(new_population - self.K) / self.K
        confidence = 0.9 - distance_to_capacity * 0.5
        confidence = max(0.5, min(0.95, confidence))

        self.writes()[0].add_hypothesis(
            VariableRecord(
                value=new_population,
                confidence=confidence,
                source=self.key(),
                metadata={"model": "logistic", "K": self.K, "r": self.r},
            )
        )
        print(
            f"  📉 Logistic model predicts: {new_population:.1f} "
            f"(conf: {confidence:.2f})"
        )


# Create both mechanisms
mechanisms = [
    LinearGrowthMechanism(growth_rate=0.05),
    LogisticGrowthMechanism(carrying_capacity=800, growth_rate=0.08),
]

# Create executive
executive = Executive(mechanisms=mechanisms)
executive.set_rng(rng=rng)

# Run simulation
print("\n" + "=" * 50)
print("Starting Population Growth Simulation")
print("=" * 50 + "\n")

executive.run(steps=50)

print("\n" + "=" * 50)
print("Simulation Complete!")
print(f"Final population: {population.value:.1f}")
print("=" * 50)


def analyze_growth_simulation(population: Variable) -> None:
    """Analyze and visualize the competition between growth models."""
    print("\n📊 Growth Model Competition Analysis")
    print("-" * 40)

    # Extract memory
    memory = population.memory
    if memory is None:
        return

    # Track confidence over time
    confidences = [r.confidence for _, r, _, _ in memory.records() if r is not None]
    print("\nConfidence statistics:")
    print(f"  Mean confidence: {np.mean(confidences):.3f}")
    print(f"  Min confidence:  {np.min(confidences):.3f}")
    print(f"  Max confidence:  {np.max(confidences):.3f}")

    # Growth analysis
    values = [r.value for _, r, _, _ in memory.records() if r is not None]
    initial = values[0]
    final = values[-1]
    total_growth = final - initial
    growth_rate_per_step = total_growth / len(values)

    print("\nPopulation dynamics:")
    print(f"  Initial: {initial:.1f}")
    print(f"  Final:   {final:.1f}")
    print(f"  Total growth: {total_growth:+.1f}")
    print(f"  Avg growth per step: {growth_rate_per_step:.2f}")

    # Check if population stabilized
    if len(values) > 20:
        recent = values[-20:]
        stability = np.std(recent) / np.mean(recent)
        if stability < 0.05:
            print(f"  Population stabilized at ≈ {np.mean(recent):.0f}")


# Run analysis
analyze_growth_simulation(population)


def plot_growth_simulation(population: Variable) -> None:
    """Plot population growth and model competition."""
    memory = population.memory
    if memory is None:
        return

    records = memory.records()
    values = [r.value for _, r, _, _ in records if r is not None]
    confidences = [r.confidence for _, r, _, _ in records if r is not None]
    steps = list(range(len(values)))

    # Identify which model was closest to the resolved conclusion at each step
    def closest_model(h: tuple[HypothesisRecord, ...], r: VariableRecord | None) -> str:
        if not h or r is None:
            return "unknown"

        distances = {
            hi.record: hi.record.value - r.value for hi in h if hi.record is not None
        }
        closest = min(distances.items(), key=lambda d: d[1])
        model = (
            closest[0].metadata.get("model", "unknown")
            if closest[0] is not None
            else "unknown"
        )
        return str(model)

    models = []
    for h, r, _, _ in records:
        models.append(closest_model(h, r))

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10.0, 10.0))

    # Plot 1: Population over time
    ax1.plot(steps, values, "b-", linewidth=2, label="Population")
    ax1.fill_between(
        steps,
        [
            v - c * 100
            for v, c in zip(values, confidences)
            if v is not None and c is not None
        ],
        [
            v + c * 100
            for v, c in zip(values, confidences)
            if v is not None and c is not None
        ],
        alpha=0.3,
        label="Uncertainty (±confidence*100)",
    )
    ax1.axhline(
        y=800, color="r", linestyle="--", alpha=0.5, label="Carrying Capacity (K)"
    )
    ax1.set_xlabel("Step")
    ax1.set_ylabel("Population")
    ax1.set_title("Population Growth with Competing Models")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Confidence over time
    ax2.plot(steps, confidences, "g-", linewidth=2)
    ax2.set_xlabel("Step")
    ax2.set_ylabel("Confidence")
    ax2.set_title("Epistemic Confidence")
    ax2.set_ylim([0, 1])
    ax2.grid(True, alpha=0.3)

    # Plot 3: Model acceptance (color-coded)
    colors = {"linear": "blue", "logistic": "orange", "unknown": "gray"}
    color_values = [colors.get(m, "gray") for m in models]
    ax3.scatter(steps, [0] * len(steps), c=color_values, s=50, alpha=0.6)
    ax3.set_xlabel("Step")
    ax3.set_yticks([])
    ax3.set_title(
        "Closet Model to the Resolved Conclusion per Step "
        "(Blue=Linear, Orange=Logistic)"
    )
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("growth_simulation.png", dpi=150)
    plt.show()


# Uncomment to visualize
plot_growth_simulation(population)
