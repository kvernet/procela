# Epistemic Signals: Measuring what we know

**Epistemic signals** are the measurable quantities that reveal the state of knowledge within a simulation. Unlike traditional simulation outputs (like temperature or population), epistemic signals tell us about **confidence, uncertainty, disagreement, and stability**—the meta-level properties that governance units use to make decisions.

This guide covers:

- What epistemic signals are and why they matter
- Examples of epistemic signals (coverage, fragility, conflict, confidence, entropy)
- Signal aggregation, time series, and anomaly detection
- Signal-driven governance examples
- Visualization techniques
- Best practices for signal computation and validation
- Decision matrices combining multiple signals

## What are Epistemic Signals?

Epistemic signals answer questions like:
- **Coverage**: How accurate are our predictions?
- **Fragility**: How sensitive are decisions to resolution policies?
- **Conflict**: How much do mechanisms disagree?
- **Confidence**: How certain are we about current values?
- **Entropy**: How diverse are the competing hypotheses?

```python
from procela import VariableSnapshot

class EpistemicSignal:
    def __init__(self, snapshot: VariableSnapshot):
        self.snapshot = snapshot

    # Prediction accuracy
    def coverage(self):
        pass

    # Policy sensitivity
    def fragility(self):
        pass

    # Hypothesis disagreement
    def conflict(self):
        pass

    # Current certainty
    def confidence(self):
        pass

    # Hypothesis diversity
    def entropy(self):
        pass
```

## Examples of Epistemic Signals Implementation

### Coverage: Prediction Accuracy

Coverage measures how well mechanisms have predicted actual outcomes:

```python
import numpy as np

from procela import VariableSnapshot, KeyAuthority

class CoverageSignal:
    """Measures prediction accuracy over time"""

    def __init__(self, snapshot: VariableSnapshot):
        """
        Coverage = 1 - (prediction_error / domain_range)

        Parameters
        ----------
        snapshot : VariableSnapshot
            The snapshot to compute coverage from.
        """
        self.snapshot = snapshot

    def compute(self, window: int) -> float:
        """
        Coverage = 1 - (prediction_error / domain_range)

        Parameters
        ----------
        window : int
            The window for recent errors.

        Returns
        -------
            float: Coverage score between 0 and 1
                  1 = perfect predictions
                  0 = predictions are maximally wrong
        """
        if min([view.stats.count for view in self.snapshot.views]) < window:
            return 0.5  # Not enough data

        # Compare recent predictions with actual outcomes
        actual_var, predicted_var = [
            KeyAuthority.resolve(view.key) for view in self.snapshot.views[:2]
        ]
        domain_range = predicted_var.domain.max_value - predicted_var.domain.mix_value
        errors = []
        for actuals, preds in zip(
            actual_var.get(start=-window, size=window),
            predicted_var.get(start=-window, size=window)
        ):
            predicted = preds[1].value
            actual = actuals[1].value
            error = abs(predicted - actual)
            errors.append(error)

        avg_error = np.mean(errors)

        coverage = 1 - (avg_error / domain_range)
        return max(0, min(1, coverage))  # Clamp to [0,1]

# Usage for some snapshot
coverage = CoverageSignal().compute(snapshot)
if coverage < 0.3:
    print("⚠️ Low coverage - predictions are unreliable!")
```

### Fragility: Policy Sensitivity

Fragility measures how much the resolved value changes when you change the resolution policy:

```python
from procela import (
    Variable,
    RangeDomain,
    WeightedConfidencePolicy,
    WeightedVotingPolicy,
    HighestConfidencePolicy,
    ResolutionPolicy
)

class FragilitySignal:
    """Measures sensitivity to resolution policy"""

    def compute(self, variable: Variable) -> float:
        """
        Fragility = max_deviation / domain_range

        Returns
        -------
            float: Fragility score between 0 and 1
                  0 = stable (all policies agree)
                  1 = fragile (policies give very different results)
        """
        hypotheses = variable.hypotheses
        if len(hypotheses) < 2:
            return 0.0

        # Compute what each policy would produce
        policies: list[ResolutionPolicy] = [
            WeightedConfidencePolicy(),
            WeightedVotingPolicy(),
            HighestConfidencePolicy(),
            #MedianPolicy(), # To be implemented
            #MeanPolicy() # To be implemented
        ]

        results = []
        for policy in policies:
            resolved = policy.resolve(hypotheses)
            results.append(resolved.value)

        # Calculate spread
        min_val = min(results)
        max_val = max(results)
        spread = max_val - min_val
        domain_range = self._domain_range(variable)

        fragility = spread / domain_range
        return min(1, fragility)  # Cap at 1

    def _domain_range(self, variable: Variable) -> float:
        if not isinstance(variable.domain, RangeDomain):
            return 1.0

        return variable.domain.max_value - variable.domain.min_value

# Usage for some variable
fragility = FragilitySignal().compute(variable)
if fragility > 0.5:
    print("⚠️ High fragility - policy choice matters greatly!")
```

### Conflict: Hypothesis Disagreement

Conflict measures how much mechanisms disagree with each other:

```python
import numpy

from procela import Variable, RangeDomain

class ConflictSignal:
    """Measures disagreement among competing hypotheses"""

    def compute(self, variable: Variable) -> float:
        """
        Conflict = normalized standard deviation of hypotheses

        Returns
        -------
            float: Conflict score between 0 and 1
                  0 = perfect agreement
                  1 = maximal disagreement
        """
        values = [
            hypothesis.record.value for hypothesis in variable.hypotheses
            if hypothesis.record.value is not None
        ]

        if len(values) < 2:
            return 0.0

        # Standard deviation as measure of spread
        std_dev = numpy.std(values)
        domain_range = self._domain_range(variable)

        conflict = std_dev / domain_range
        return min(1, conflict)  # Cap at 1

    def _domain_range(self, variable: Variable) -> float:
        if not isinstance(variable.domain, RangeDomain):
            return 1.0

        return variable.domain.max_value - variable.domain.min_value

# Usage for some variable with different disagreement patterns
conflict = ConflictSignal().compute(variable)

if conflict < 0.1:
    print("✅ High consensus among mechanisms")
elif conflict < 0.5:
    print("⚠️ Moderate disagreement")
else:
    print("🔥 Strong disagreement - epistemic crisis!")
```

### Confidence: Current Certainty

Confidence represents how certain we are about the current value:

```python
from procela import Variable

class ConfidenceSignal:
    """Measures current confidence in resolved value"""

    def compute(self, variable: Variable) -> float:
        """
        Confidence = weighted average of hypothesis confidences

        Returns
        -------
            float: Confidence score between 0 and 1
        """
        if not variable.hypotheses:
            return 0.0

        total_weight = sum(
            hypothesis.record.confidence for hypothesis in variable.hypotheses
            if hypothesis.record.confidence is not None
        )
        weighted_sum = sum(
            hypothesis.record.confidence**2 for hypothesis in variable.hypotheses
            if hypothesis.record.confidence is not None
        )

        if total_weight == 0:
            return 0.0

        confidence = weighted_sum / total_weight
        return min(1, confidence)

# Usage for some variable
confidence = ConfidenceSignal().compute(variable)
print(f"Current confidence: {confidence:.2%}")

if confidence < 0.5:
    print("⚠️ Low confidence - consider gathering more evidence")
```

### Entropy: Hypothesis Diversity

Entropy measures the diversity of hypotheses (information-theoretic):

```python
import numpy as np

from procela import Variable, RangeDomain

class EntropySignal:
    """Measures diversity of competing hypotheses"""

    def compute(self, variable: Variable, bins: int = 10) -> float:
        """
        Shannon entropy of hypothesis distribution

        Returns
        -------
            float: Entropy between 0 (all hypotheses identical)
                  and log(bins) (uniformly distributed)
        """
        values = [
            hypothesis.record.value for hypothesis in variable.hypotheses
            if hypothesis.record.value is not None
        ]

        if len(values) < 2:
            return 0.0

        # Bin the values to create a distribution
        domain_min, domain_max = self._domain_range(variable)
        bins_edges = np.linspace(domain_min, domain_max, bins + 1)

        hist, _ = np.histogram(values, bins=bins_edges)
        hist = hist / len(values)  # Normalize to probabilities

        # Remove zero probabilities
        hist = hist[hist > 0]

        # Compute Shannon entropy
        entropy = -np.sum(hist * np.log2(hist))

        # Normalize to [0, 1]
        max_entropy = np.log2(bins)
        normalized_entropy = entropy / max_entropy

        return normalized_entropy

    def _domain_range(self, variable: Variable) -> float:
        if not isinstance(variable.domain, RangeDomain):
            return [0.0, 1.0]

        return [variable.domain.max_value, variable.domain.min_value]

# Usage for some variable
entropy = EntropySignal().compute(variable, bins=10)
print(f"Hypothesis entropy: {entropy:.3f}")

if entropy > 0.8:
    print("🔀 High entropy - mechanisms have diverse views")
elif entropy < 0.3:
    print("🎯 Low entropy - strong consensus")
```

## Signal Aggregation and Analysis

### Multi-Signal Composite

```python
class CompositeSignal:
    """Combines multiple signals into a single score"""

    def __init__(self, weights: list[float] | None = None) -> None:
        self.weights = weights or [0.3, 0.3, -0.2, -0.2]

    def compute(self, values: list[float]) -> float:
        score = 0.0

        for value, weight in zip(values, self.weights):
                score += weight * value

        # Normalize to [0, 1]
        score = (score + 1) / 2
        return max(0, min(1, score))

# Usage for the previous signal
composite = CompositeSignal()
values = [coverage, confidence, conflict, fragility]
health_score = composite.compute(values)

if health_score > 0.7:
    print("✅ System is healthy")
elif health_score > 0.3:
    print("⚠️ System needs attention")
else:
    print("🔥 System is in crisis!")
```

### Signal Time Series

```python
import numpy as np

class SignalTimeSeries:
    """Tracks signal evolution over time"""

    def __init__(self, max_history=1000):
        self.max_history = max_history
        self.history = {}  # signal_name -> list of values

    def record(self, signals):
        """Record current signal values"""
        for signal_name in signals:
            if signal_name.endswith("_signal"):
                value = getattr(signals, signal_name)()

                if signal_name not in self.history:
                    self.history[signal_name] = []

                self.history[signal_name].append({
                    "step": signals["step"],
                    "value": value
                })

                # Maintain history size
                if len(self.history[signal_name]) > self.max_history:
                    self.history[signal_name].pop(0)

    def get_trend(self, signal_name, window=10):
        """Calculate recent trend"""
        if signal_name not in self.history:
            return 0.0

        recent = self.history[signal_name][-window:]
        if len(recent) < 2:
            return 0.0

        values = [r["value"] for r in recent]
        return values[-1] - values[0]  # Simple trend

    def detect_anomaly(self, signal_name, threshold=2.0):
        """Detect anomalous signal values"""
        if signal_name not in self.history:
            return False

        values = [r["value"] for r in self.history[signal_name]]
        if len(values) < 10:
            return False

        mean = np.mean(values)
        std = np.std(values)
        current = values[-1]

        z_score = abs(current - mean) / (std + 1e-6)
        return z_score > threshold

# Usage for some signals
tracker = SignalTimeSeries()
tracker.record(signals)

if tracker.detect_anomaly("coverage"):
    print("🚨 Coverage anomaly detected!")
```

## Signal-Based Governance

### Example: Adaptive Threshold Governance

```python
import numpy as np

from procela import (
    SystemInvariant,
    InvariantPhase,
    VariableSnapshot,
    InvariantViolation,
    HighestConfidencePolicy,
    Variable
)

class AdaptiveThresholdGovernance(SystemInvariant):
    """Governance that adapts its thresholds based on signal history"""

    def __init__(self, variable: Variable, base_threshold: float = 0.3):
        self.variable = variable
        self.base_threshold = base_threshold
        self.signal_history = []
        self.adaptive_threshold = base_threshold

        def _conflict(snapshot: VariableSnapshot):
            pass

        def _coverage(snapshot: VariableSnapshot):
            pass

        def _adapt_threshold(snapshot: VariableSnapshot):
            """Dynamically adjust threshold based on system state"""
            # Track signal history
            self.signal_history.append({
                "step": snapshot.step,
                "conflict": _conflict(snapshot),
                "coverage": _coverage(snapshot)
            })

            # Keep recent history only
            if len(self.signal_history) > 100:
                self.signal_history.pop(0)

            # If coverage is high, we can be more tolerant of conflict
            if len(self.signal_history) > 20:
                avg_coverage = np.mean([h["coverage"] for h in self.signal_history[-20:]])

                # Higher coverage → higher tolerance
                self.adaptive_threshold = self.base_threshold * (1 + avg_coverage)

        def check(snapshot: VariableSnapshot) -> bool:
            # Get current signals
            conflict = _conflict()
            coverage = _coverage()

            # Adapt threshold based on recent performance
            _adapt_threshold(snapshot)

            # Check if threshold exceeded
            return conflict <= self.adaptive_threshold

        def handle(invariant: InvariantViolation, snapshot: VariableSnapshot) -> None:
            conflict = _conflict(snapshot)
            print(f"⚠️ Conflict threshold exceeded: {conflict:.3f} > {self.adaptive_threshold:.3f}")
            print("Initiating conflict resolution...")

            # Switch to highest-confidence policy during conflict
            self.variable.policy = HighestConfidencePolicy()

        super().__init__(
            name="AdaptiveThreshold",
            condition=check,
            on_violation=handle,
            phase=InvariantPhase.RUNTIME
        )
```

### Example: Signal-Driven Mechanism Selection

```python
import numpy as np

from procela import (
    SystemInvariant,
    InvariantPhase,
    VariableSnapshot,
    Variable,
    Mechanism
)


class MechanismSelector(SystemInvariant):
    """Selects mechanisms based on their signal profiles"""

    def __init__(self, mechanisms: list[Mechanism], variable: Variable):
        self.mechanisms = mechanisms
        self.variable = variable
        self.performance_tracking = {m.key(): [] for m in mechanisms}

        def _coverage(snapshot: VariableSnapshot):
            pass

        def _conflict(snapshot: VariableSnapshot):
            pass

        def _evaluate_mechanisms(snapshot: VariableSnapshot) -> None:
            """Evaluate each mechanism's contribution to signals"""
            hypotheses, conclusion, _ = variable.memory.latest()
            if conclusion is not None and conclusion.value is not None:
                for hypothesis in hypotheses:
                    mech_key = hypothesis.record.key
                    if hypothesis.record.value is None or mech_key is None:
                        continue
                    error = abs(hypothesis.record.value - conclusion.value)

                    # Track performance
                    self.performance_tracking[mech_key].append(error)

                    # Keep window
                    if len(self.performance_tracking[mech_key]) > 50:
                        self.performance_tracking[mech_key].pop(0)

                # Periodically adjust mechanism weights based on signals
                if snapshot.step % 20 == 0:
                    _adjust_weights(snapshot)

        def _adjust_weights(snapshot: VariableSnapshot) -> None:
            """Adjust which mechanisms are active based on signals"""
            # Calculate signal health
            coverage = _coverage(snapshot)
            conflict = _conflict(snapshot)

            if coverage < 0.3:
                # Low coverage - need better mechanisms
                print("Low coverage detected, switching to high-confidence mechanisms")
                _select_by_confidence()
            elif conflict > 0.7:
                # High conflict - need consensus
                print("High conflict detected, using median mechanisms")
                _select_by_consensus() # To be implemented
            else:
                # Normal operation
                _select_by_performance() # To be implemented

        def _select_by_confidence():
            """Select mechanisms with highest average confidence"""
            confidences = {}
            for mech in self.mechanisms:
                if mech.key() in self.performance_tracking:
                    # Confidence = 1 - normalized error
                    errors = self.performance_tracking[mech.key()]
                    if errors:
                        avg_error = np.mean(errors)
                        confidence = 1 - avg_error
                        confidences[mech.key()] = confidence

            # Enable top 3 mechanisms
            top_mechs = sorted(confidences.items(), key=lambda x: x[1], reverse=True)[:3]
            for mech in self.mechanisms:
                if mech.key() in [m[0] for m in top_mechs]:
                    mech.enable()
                else:
                    mech.disable()

        def check(snapshot: VariableSnapshot) -> bool:
            # Always evaluate
            self._evaluate_mechanisms(snapshot)
            return True

        super().__init__(
            name="MechanismSelector",
            condition=check,
            on_violation=None,
            phase=InvariantPhase.POST
        )
```

## Signal Visualization

Install matplotlib if not already installed.

```bash
pip install matplotlib
```

```python
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def visualize_signals(signal_history, variable_name):
    """Create dashboard of epistemic signals"""

    steps = [s["step"] for s in signal_history]

    fig = plt.figure(figsize=(12, 10))
    gs = GridSpec(3, 2, figure=fig)

    # 1. Coverage
    ax1 = fig.add_subplot(gs[0, 0])
    coverage = [s["coverage"] for s in signal_history]
    ax1.plot(steps, coverage, 'g-', linewidth=2)
    ax1.axhline(y=0.5, color='r', linestyle='--', alpha=0.5)
    ax1.set_ylabel('Coverage')
    ax1.set_title('Prediction Accuracy')
    ax1.grid(True, alpha=0.3)

    # 2. Confidence
    ax2 = fig.add_subplot(gs[0, 1])
    confidence = [s["confidence"] for s in signal_history]
    ax2.plot(steps, confidence, 'b-', linewidth=2)
    ax2.set_ylabel('Confidence')
    ax2.set_title('Current Certainty')
    ax2.grid(True, alpha=0.3)

    # 3. Conflict
    ax3 = fig.add_subplot(gs[1, 0])
    conflict = [s["conflict"] for s in signal_history]
    ax3.fill_between(steps, 0, conflict, alpha=0.3, color='red')
    ax3.plot(steps, conflict, 'r-', linewidth=2)
    ax3.set_ylabel('Conflict')
    ax3.set_title('Mechanism Disagreement')
    ax3.grid(True, alpha=0.3)

    # 4. Fragility
    ax4 = fig.add_subplot(gs[1, 1])
    fragility = [s["fragility"] for s in signal_history]
    ax4.plot(steps, fragility, 'orange', linewidth=2)
    ax4.set_ylabel('Fragility')
    ax4.set_title('Policy Sensitivity')
    ax4.grid(True, alpha=0.3)

    # 5. Entropy
    ax5 = fig.add_subplot(gs[2, :])
    entropy = [s["entropy"] for s in signal_history]
    ax5.plot(steps, entropy, 'purple', linewidth=2)
    ax5.set_xlabel('Simulation Step')
    ax5.set_ylabel('Entropy')
    ax5.set_title('Hypothesis Diversity')
    ax5.grid(True, alpha=0.3)

    plt.suptitle(f'Epistemic Signals for {variable_name}')
    plt.tight_layout()
    plt.savefig(f'{variable_name}_signals.png', dpi=150)
    plt.show()

# Usage for some signal_history and variable_name
visualize_signals(signal_history, variable_name)
```

## Best Practices

### 1. Signal Normalization
```python
# Always normalize signals to [0, 1] for comparability
def normalize_signal(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)

# Or use domain ranges when available
def normalize_by_domain(value, domain_range):
    return value / domain_range
```

### 2. Signal Smoothing

Install scipy if not already installed.

```bash
pip install scipy
```

```python
from scipy.signal import savgol_filter

def smooth_signal(values, window=11):
    """Apply smoothing to reduce noise"""
    if len(values) < window:
        return values
    return savgol_filter(values, window, 3)
```

### 3. Signal Caching
```python
class CachedSignal(EpistemicSignal):
    """Cache expensive signal computations"""

    def __init__(self, compute_func, cache_ttl=10):
        self.compute_func = compute_func
        self.cache_ttl = cache_ttl
        self.cache = {}

    def compute(self, snapshot):
        step = snapshot.step
        key = (step // self.cache_ttl)  # Cache per TTL block

        if key not in self.cache:
            self.cache[key] = self.compute_func(snapshot)

        return self.cache[key]
```

### 4. Signal Validation
```python
def validate_signal(signal_value, signal_name):
    """Validate signal is within expected range"""
    if not 0 <= signal_value <= 1:
        print(f"⚠️ Invalid {signal_name}: {signal_value} (clamping to [0,1])")
        return max(0, min(1, signal_value))
    return signal_value
```

## Signal Combinations for Decision Making

```python
class DecisionMatrix:
    """Combines signals for governance decisions"""

    def __init__(self):
        self.rules = []

    def add_rule(self, conditions, action):
        """Add decision rule"""
        self.rules.append((conditions, action))

    def decide(self, snapshot):
        """Evaluate all rules and take highest priority action"""
        signals = {
            "coverage": self._coverage(snapshot),
            "confidence": self._confidence(snapshot),
            "conflict": self._conflict(snapshot),
            "fragility": self._fragility(snapshot)
        }

        for conditions, action in self.rules:
            if all(conditions[k](v) for k, v in signals.items() if k in conditions):
                return action

        return None  # No action needed

    def _coverage(self, snapshot):
        return NotImplementedError

    def _confidence(self, snapshot):
        return NotImplementedError

    def _conflict(self, snapshot):
        return NotImplementedError

    def _fragility(self, snapshot):
        return NotImplementedError

# Usage for some snapshot
matrix = DecisionMatrix()
matrix.add_rule(
    conditions={
        "coverage": lambda x: x < 0.3,
        "confidence": lambda x: x < 0.5
    },
    action="gather_more_data"
)
matrix.add_rule(
    conditions={
        "conflict": lambda x: x > 0.7,
        "fragility": lambda x: x > 0.5
    },
    action="switch_to_highest_confidence"
)
matrix.add_rule(
    conditions={
        "coverage": lambda x: x > 0.8,
        "conflict": lambda x: x < 0.2
    },
    action="maintain_current_policy"
)

decision = matrix.decide(snapshot)
print(f"Decision: {decision}")
```

## Next Steps

- Learn how [Governance](governance.md) uses signals to make decisions
- See signals in action in the [AMR Case Study](../examples/amr-case-study.md)
- Explore [Advanced Signal Processing](../advanced/signal-processing.md)
- Check the [API Reference](../api/reference.md) for complete Signal documentation
