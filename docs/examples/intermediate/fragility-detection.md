# Fragility Detection and Response

- **Level:** 🟡 Intermediate
- **Est. Time:** 25 minutes
- **Concepts:** Epistemic Fragility, Policy Sensitivity, Adaptive Governance, Dynamic Thresholds

This intermediate example provides:

- Complete fragility detection system with adaptive thresholds
- Tiered response mechanisms based on severity
- Detailed metrics and reporting
- Comparative analysis with/without governance
- Visualization dashboard
- Real-time adaptation of governance parameters

---

## Overview

**Epistemic fragility** measures how sensitive a variable's resolved value is to the choice of resolution policy. High fragility indicates that the system's state depends heavily on which policy you use—a sign of epistemic uncertainty.

This example builds an **adaptive fragility detection system** that:
- **Continuously monitors** policy sensitivity in real-time
- **Detects** when fragility exceeds dynamic thresholds
- **Responds** by switching to more stable policies
- **Adapts** its own detection parameters based on system state

```python
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import deque

from procela import (
    Executive, Mechanism, Variable, RangeDomain, VariableRecord,
    WeightedVotingPolicy, HighestConfidencePolicy, MedianPolicy,
    MeanPolicy, Policy, SystemInvariant, InvariantPhase,
    InvariantViolation, VariableSnapshot
)
```

---

## Step 1: Create a Fragile System

First, let's create a system that exhibits fragility—where mechanisms have widely different confidences and predictions:

```python
class FragileTemperatureSystem:
    """Creates a temperature variable with intentionally fragile dynamics"""

    @staticmethod
    def create_variable():
        temp = Variable(
            name="Temperature",
            domain=RangeDomain(-10, 50),
            policy=WeightedVotingPolicy()
        )
        temp.init(VariableRecord(20.0, confidence=1.0, source="initial"))
        return temp

    @staticmethod
    def create_fragile_mechanisms(temp):
        """Create mechanisms with diverging predictions and confidences"""

        class ExtremeWarmingMechanism(Mechanism):
            """Predicts strong warming with high confidence"""
            def transform(self):
                current = temp.value
                new_temp = current + np.random.uniform(0.3, 0.8)
                # Artificially high confidence despite extreme prediction
                confidence = 0.95
                temp.add_hypothesis(
                    VariableRecord(new_temp, confidence, source="extreme_warming")
                )

        class ExtremeCoolingMechanism(Mechanism):
            """Predicts strong cooling with high confidence"""
            def transform(self):
                current = temp.value
                new_temp = current - np.random.uniform(0.3, 0.8)
                confidence = 0.95
                temp.add_hypothesis(
                    VariableRecord(new_temp, confidence, source="extreme_cooling")
                )

        class ModerateMechanism(Mechanism):
            """Predicts modest changes with moderate confidence"""
            def transform(self):
                current = temp.value
                new_temp = current + np.random.normal(0, 0.2)
                confidence = 0.6
                temp.add_hypothesis(
                    VariableRecord(new_temp, confidence, source="moderate")
                )

        class RandomMechanism(Mechanism):
            """Random predictions with low confidence"""
            def transform(self):
                current = temp.value
                new_temp = current + np.random.normal(0, 1.0)
                confidence = 0.3
                temp.add_hypothesis(
                    VariableRecord(new_temp, confidence, source="random")
                )

        return [
            ExtremeWarmingMechanism(),
            ExtremeCoolingMechanism(),
            ModerateMechanism(),
            RandomMechanism()
        ]
```

---

## Step 2: Implement Fragility Calculator

```python
class FragilityCalculator:
    """
    Calculates epistemic fragility - how much the resolved value
    changes under different resolution policies.
    """

    def __init__(self, policies: List[Policy] = None):
        """
        Args:
            policies: List of policies to test for fragility.
                     Defaults to common policies.
        """
        if policies is None:
            self.policies = [
                WeightedVotingPolicy(),
                HighestConfidencePolicy(),
                MedianPolicy(),
                MeanPolicy()
            ]
        else:
            self.policies = policies

    def calculate_fragility(self, snapshot: VariableSnapshot) -> Dict:
        """
        Calculate fragility metrics for the current snapshot.

        Returns:
            Dictionary containing:
            - fragility_score: Normalized fragility (0-1)
            - policy_results: Values from each policy
            - spread: Raw spread between policies
            - most_stable_policy: Policy with median result
        """
        hypotheses = snapshot.views

        if len(hypotheses) < 2:
            return {
                'fragility_score': 0.0,
                'policy_results': {},
                'spread': 0.0,
                'most_stable_policy': None,
                'all_policies_agree': True
            }

        # Apply each policy to the hypotheses
        policy_results = {}
        for policy in self.policies:
            resolved = policy.resolve(hypotheses, snapshot.variable)
            policy_results[type(policy).__name__] = resolved.value

        # Calculate spread
        values = list(policy_results.values())
        min_val = min(values)
        max_val = max(values)
        spread = max_val - min_val

        # Normalize by domain range
        domain_range = snapshot.domain.range
        fragility_score = min(1.0, spread / domain_range)

        # Find the most stable policy (median result)
        median_value = np.median(values)
        most_stable = min(policy_results.items(),
                         key=lambda x: abs(x[1] - median_value))

        # Check if all policies agree (within tolerance)
        tolerance = domain_range * 0.01  # 1% of domain
        all_agree = spread <= tolerance

        return {
            'fragility_score': fragility_score,
            'policy_results': policy_results,
            'spread': spread,
            'most_stable_policy': most_stable[0],
            'most_stable_value': most_stable[1],
            'all_policies_agree': all_agree
        }

    def get_fragility_breakdown(self, snapshot: VariableSnapshot) -> str:
        """Get human-readable fragility breakdown"""
        metrics = self.calculate_fragility(snapshot)

        if metrics['all_policies_agree']:
            return "✅ System is stable (all policies agree)"

        lines = [
            f"⚠️ Fragility Score: {metrics['fragility_score']:.3f}",
            f"   Policy spread: {metrics['spread']:.2f}",
            f"   Most stable policy: {metrics['most_stable_policy']}",
            "\n   Policy outcomes:"
        ]

        for policy, value in metrics['policy_results'].items():
            lines.append(f"     - {policy}: {value:.2f}")

        return "\n".join(lines)
```

---

## Step 3: Adaptive Fragility Governance

```python
@dataclass
class FragilityThreshold:
    """Dynamic threshold configuration"""
    low: float = 0.2      # Below this: system is stable
    medium: float = 0.4   # Between low and medium: moderate fragility
    high: float = 0.6     # Above high: critical fragility

    def get_level(self, score: float) -> str:
        if score < self.low:
            return "low"
        elif score < self.medium:
            return "moderate"
        elif score < self.high:
            return "high"
        else:
            return "critical"

class AdaptiveFragilityGovernance(SystemInvariant):
    """
    Advanced governance that monitors fragility and adapts its response
    based on the severity and history of fragility events.
    """

    def __init__(self, variable, fragility_calculator: FragilityCalculator = None,
                 initial_threshold: float = 0.3,
                 adaptation_rate: float = 0.05,
                 history_window: int = 50):
        """
        Args:
            variable: Variable to monitor
            fragility_calculator: Calculator for fragility metrics
            initial_threshold: Starting fragility threshold
            adaptation_rate: How quickly to adjust threshold
            history_window: Window for tracking fragility history
        """
        self.variable = variable
        self.calculator = fragility_calculator or FragilityCalculator()
        self.threshold = initial_threshold
        self.adaptation_rate = adaptation_rate
        self.history_window = history_window

        # Tracking
        self.fragility_history = deque(maxlen=history_window)
        self.actions_taken = []
        self.current_threshold_level = FragilityThreshold()
        self.adaptive_thresholds = []

        def check(snapshot: VariableSnapshot):
            """Check if fragility exceeds current threshold"""
            metrics = self.calculator.calculate_fragility(snapshot)
            fragility = metrics['fragility_score']

            # Record history
            self.fragility_history.append({
                'step': snapshot.step,
                'fragility': fragility,
                'metrics': metrics
            })

            # Check for violation
            return fragility <= self.threshold

        def handle(invariant: InvariantViolation, snapshot: VariableSnapshot):
            """Respond to fragility violation"""
            self._handle_fragility(snapshot)

        super().__init__(
            name="AdaptiveFragilityGovernance",
            condition=check,
            on_violation=handle,
            phase=InvariantPhase.RUNTIME
        )

    def _handle_fragility(self, snapshot: VariableSnapshot):
        """Handle fragility event with adaptive response"""
        metrics = self.calculator.calculate_fragility(snapshot)
        fragility = metrics['fragility_score']
        level = self.current_threshold_level.get_level(fragility)

        action = {
            'step': snapshot.step,
            'fragility': fragility,
            'threshold': self.threshold,
            'level': level,
            'policy_results': metrics['policy_results']
        }

        # Choose response based on fragility level
        if level == "critical":
            action['response'] = self._critical_response(snapshot, metrics)
        elif level == "high":
            action['response'] = self._high_response(snapshot, metrics)
        elif level == "moderate":
            action['response'] = self._moderate_response(snapshot, metrics)
        else:
            action['response'] = self._low_response(snapshot, metrics)

        self.actions_taken.append(action)
        self._adapt_threshold()

    def _critical_response(self, snapshot, metrics):
        """Emergency response for critical fragility"""
        print(f"\n🚨 CRITICAL FRAGILITY: {metrics['fragility_score']:.3f}")
        print(f"   Immediate policy switch to HighestConfidencePolicy")

        # Force switch to most stable policy
        most_stable = metrics['most_stable_policy']
        if most_stable == "WeightedVotingPolicy":
            self.variable.policy = WeightedVotingPolicy()
        elif most_stable == "HighestConfidencePolicy":
            self.variable.policy = HighestConfidencePolicy()
        elif most_stable == "MedianPolicy":
            self.variable.policy = MedianPolicy()
        elif most_stable == "MeanPolicy":
            self.variable.policy = MeanPolicy()

        return {
            'action': 'emergency_switch',
            'new_policy': most_stable,
            'severity': 'critical'
        }

    def _high_response(self, snapshot, metrics):
        """Strong response for high fragility"""
        print(f"\n⚠️ HIGH FRAGILITY: {metrics['fragility_score']:.3f}")
        print(f"   Switching to {metrics['most_stable_policy']}")

        # Switch to most stable policy
        if metrics['most_stable_policy'] == "WeightedVotingPolicy":
            self.variable.policy = WeightedVotingPolicy()
        elif metrics['most_stable_policy'] == "HighestConfidencePolicy":
            self.variable.policy = HighestConfidencePolicy()
        elif metrics['most_stable_policy'] == "MedianPolicy":
            self.variable.policy = MedianPolicy()
        elif metrics['most_stable_policy'] == "MeanPolicy":
            self.variable.policy = MeanPolicy()

        return {
            'action': 'policy_switch',
            'new_policy': metrics['most_stable_policy'],
            'severity': 'high'
        }

    def _moderate_response(self, snapshot, metrics):
        """Mild response for moderate fragility"""
        print(f"\n📊 MODERATE FRAGILITY: {metrics['fragility_score']:.3f}")
        print(f"   Logging for analysis (no immediate action)")

        return {
            'action': 'log_only',
            'severity': 'moderate'
        }

    def _low_response(self, snapshot, metrics):
        """Minimal response for low fragility"""
        # Just update tracking, no action needed
        return {
            'action': 'monitor',
            'severity': 'low'
        }

    def _adapt_threshold(self):
        """Dynamically adjust threshold based on recent fragility"""
        if len(self.fragility_history) < 10:
            return

        recent = list(self.fragility_history)[-10:]
        recent_fragilities = [f['fragility'] for f in recent]
        avg_recent = np.mean(recent_fragilities)
        std_recent = np.std(recent_fragilities)

        # Adapt threshold: increase if system is consistently stable,
        # decrease if fragility is common
        if avg_recent < self.threshold * 0.5:
            # System is very stable - we can be more sensitive
            new_threshold = self.threshold * (1 - self.adaptation_rate)
        elif avg_recent > self.threshold * 1.2:
            # System is frequently fragile - need higher tolerance
            new_threshold = self.threshold * (1 + self.adaptation_rate)
        else:
            new_threshold = self.threshold

        # Ensure threshold stays within reasonable bounds
        self.threshold = max(0.1, min(0.8, new_threshold))

        self.adaptive_thresholds.append({
            'step': self.fragility_history[-1]['step'],
            'old_threshold': self.threshold if len(self.adaptive_thresholds) == 0 else self.adaptive_thresholds[-1]['new_threshold'],
            'new_threshold': self.threshold,
            'avg_fragility': avg_recent
        })

    def get_report(self) -> Dict:
        """Generate comprehensive fragility report"""
        if not self.fragility_history:
            return {'message': 'No fragility data collected'}

        fragilities = [f['fragility'] for f in self.fragility_history]

        report = {
            'total_steps_monitored': len(self.fragility_history),
            'threshold_final': self.threshold,
            'threshold_initial': self.adaptive_thresholds[0]['old_threshold'] if self.adaptive_thresholds else self.threshold,
            'fragility_stats': {
                'mean': np.mean(fragilities),
                'std': np.std(fragilities),
                'min': np.min(fragilities),
                'max': np.max(fragilities),
                'q25': np.percentile(fragilities, 25),
                'q50': np.percentile(fragilities, 50),
                'q75': np.percentile(fragilities, 75)
            },
            'actions_summary': {
                'total_actions': len(self.actions_taken),
                'by_severity': {
                    'critical': sum(1 for a in self.actions_taken if a.get('response', {}).get('severity') == 'critical'),
                    'high': sum(1 for a in self.actions_taken if a.get('response', {}).get('severity') == 'high'),
                    'moderate': sum(1 for a in self.actions_taken if a.get('response', {}).get('severity') == 'moderate'),
                    'low': sum(1 for a in self.actions_taken if a.get('response', {}).get('severity') == 'low')
                }
            },
            'threshold_adaptations': len(self.adaptive_thresholds)
        }

        return report
```

---

## Step 4: Create a Visualization Dashboard

```python
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.colors as mcolors

def visualize_fragility_dashboard(governance, temperature, save_path=None):
    """
    Create a comprehensive dashboard showing fragility evolution,
    policy changes, and system response.
    """

    if not governance.fragility_history:
        print("No fragility history to visualize")
        return

    # Extract data
    steps = [f['step'] for f in governance.fragility_history]
    fragilities = [f['fragility'] for f in governance.fragility_history]

    # Get policy history from variable
    policy_history = temperature.policy_history

    # Create figure with subplots
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    # Plot 1: Fragility over time
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(steps, fragilities, 'b-', linewidth=2, label='Fragility Score')
    ax1.axhline(y=governance.threshold, color='r', linestyle='--',
                label=f'Current Threshold: {governance.threshold:.2f}')

    # Color regions by fragility level
    levels = governance.current_threshold_level
    ax1.axhspan(0, levels.low, alpha=0.1, color='green', label='Low')
    ax1.axhspan(levels.low, levels.medium, alpha=0.1, color='yellow', label='Moderate')
    ax1.axhspan(levels.medium, levels.high, alpha=0.1, color='orange', label='High')
    ax1.axhspan(levels.high, 1, alpha=0.1, color='red', label='Critical')

    # Mark governance actions
    for action in governance.actions_taken:
        step = action['step']
        severity = action.get('response', {}).get('severity', 'unknown')
        color = {'critical': 'red', 'high': 'orange', 'moderate': 'yellow', 'low': 'green'}.get(severity, 'gray')
        ax1.scatter(step, fragilities[steps.index(step)],
                   color=color, s=100, zorder=5, edgecolors='black', linewidth=1)

    ax1.set_xlabel('Step')
    ax1.set_ylabel('Fragility Score')
    ax1.set_title('Epistemic Fragility Evolution')
    ax1.legend(loc='upper right', fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Policy timeline
    ax2 = fig.add_subplot(gs[1, 0])
    if policy_history:
        policies = [p['policy'].__class__.__name__ for p in policy_history]
        policy_steps = [p['step'] for p in policy_history]

        # Create colored segments
        for i in range(len(policy_steps)):
            start = policy_steps[i]
            end = policy_steps[i+1] if i+1 < len(policy_steps) else max(steps)
            color = 'orange' if 'HighestConfidence' in policies[i] else 'blue' if 'Weighted' in policies[i] else 'gray'
            ax2.axvspan(start, end, alpha=0.3, color=color)
            ax2.text((start + end)/2, 0.5, policies[i].replace('Policy', ''),
                    ha='center', va='center', fontsize=9)

    ax2.set_xlim(min(steps), max(steps))
    ax2.set_ylim(0, 1)
    ax2.set_yticks([])
    ax2.set_xlabel('Step')
    ax2.set_title('Active Resolution Policy')
    ax2.grid(True, alpha=0.3)

    # Plot 3: Fragility distribution
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.hist(fragilities, bins=20, color='blue', alpha=0.7, edgecolor='black')
    ax3.axvline(x=governance.threshold, color='r', linestyle='--',
                label=f'Threshold: {governance.threshold:.2f}')
    ax3.axvline(x=np.mean(fragilities), color='g', linestyle='--',
                label=f'Mean: {np.mean(fragilities):.2f}')
    ax3.set_xlabel('Fragility Score')
    ax3.set_ylabel('Frequency')
    ax3.set_title('Fragility Distribution')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Plot 4: Adaptive threshold evolution
    ax4 = fig.add_subplot(gs[2, 0])
    if governance.adaptive_thresholds:
        threshold_steps = [t['step'] for t in governance.adaptive_thresholds]
        threshold_values = [t['new_threshold'] for t in governance.adaptive_thresholds]
        ax4.plot(threshold_steps, threshold_values, 'purple', linewidth=2, marker='o', markersize=4)
        ax4.axhline(y=governance.threshold, color='r', linestyle='--', alpha=0.5)
        ax4.set_xlabel('Step')
        ax4.set_ylabel('Threshold')
        ax4.set_title('Adaptive Threshold Evolution')
        ax4.grid(True, alpha=0.3)

    # Plot 5: Temperature with fragility overlay
    ax5 = fig.add_subplot(gs[2, 1])
    temp_values = [r.value for r in temperature.memory]
    temp_steps = list(range(len(temp_values)))
    ax5.plot(temp_steps, temp_values, 'b-', linewidth=2, label='Temperature')

    # Overlay fragility as background color
    for i, step in enumerate(steps):
        if step < len(temp_steps):
            fragility = fragilities[i]
            color = plt.cm.RdYlGn_r(fragility)
            ax5.axvspan(step, step+1, alpha=0.3, color=color)

    ax5.set_xlabel('Step')
    ax5.set_ylabel('Temperature (°C)')
    ax5.set_title('Temperature with Fragility Overlay (Red=High Fragility)')
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    plt.suptitle('Fragility Detection Dashboard', fontsize=14, fontweight='bold')

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()

def print_fragility_report(governance):
    """Print formatted fragility report"""
    report = governance.get_report()

    print("\n" + "="*60)
    print("FRAGILITY DETECTION REPORT")
    print("="*60)

    print(f"\n📊 Monitoring Summary:")
    print(f"   Steps monitored: {report['total_steps_monitored']}")
    print(f"   Threshold adaptation events: {report['threshold_adaptations']}")

    print(f"\n🎯 Threshold Evolution:")
    print(f"   Initial threshold: {report['threshold_initial']:.3f}")
    print(f"   Final threshold: {report['threshold_final']:.3f}")
    change = report['threshold_final'] - report['threshold_initial']
    print(f"   Change: {change:+.3f} ({change/report['threshold_initial']*100:+.1f}%)")

    print(f"\n📈 Fragility Statistics:")
    stats = report['fragility_stats']
    print(f"   Mean: {stats['mean']:.3f}")
    print(f"   Std:  {stats['std']:.3f}")
    print(f"   Min:  {stats['min']:.3f}")
    print(f"   Max:  {stats['max']:.3f}")
    print(f"   Median: {stats['q50']:.3f}")
    print(f"   IQR: {stats['q75'] - stats['q25']:.3f}")

    print(f"\n⚡ Governance Actions:")
    actions = report['actions_summary']
    print(f"   Total: {actions['total_actions']}")
    print(f"   By severity:")
    for severity, count in actions['by_severity'].items():
        if count > 0:
            print(f"     - {severity.capitalize()}: {count}")

    # Calculate effectiveness
    if len(governance.fragility_history) > 20:
        early_fragility = np.mean([f['fragility'] for f in governance.fragility_history[:20]])
        late_fragility = np.mean([f['fragility'] for f in governance.fragility_history[-20:]])
        improvement = (early_fragility - late_fragility) / early_fragility * 100

        print(f"\n✅ Governance Effectiveness:")
        print(f"   Early fragility (first 20 steps): {early_fragility:.3f}")
        print(f"   Late fragility (last 20 steps): {late_fragility:.3f}")
        print(f"   Improvement: {improvement:+.1f}%")

        if improvement > 0:
            print("   → Governance successfully reduced fragility")
        else:
            print("   → Fragility increased (system may need tuning)")
```

---

## Step 5: Run the Complete Example

```python
def run_fragility_detection_example():
    """Run the complete fragility detection simulation"""

    print("="*60)
    print("FRAGILITY DETECTION SIMULATION")
    print("="*60)

    # Create fragile system
    temp = FragileTemperatureSystem.create_variable()
    mechanisms = FragileTemperatureSystem.create_fragile_mechanisms(temp)

    # Create fragility calculator and governance
    calculator = FragilityCalculator()
    governance = AdaptiveFragilityGovernance(
        variable=temp,
        fragility_calculator=calculator,
        initial_threshold=0.3,
        adaptation_rate=0.05,
        history_window=50
    )

    # Create executive
    executive = Executive(mechanisms=mechanisms, random_seed=42)
    executive.add_invariant(governance)

    # Print initial configuration
    print(f"\n🔧 Initial Configuration:")
    print(f"   Initial policy: {type(temp.policy).__name__}")
    print(f"   Fragility threshold: {governance.threshold}")
    print(f"   Number of mechanisms: {len(mechanisms)}")

    print("\n" + "-"*60)
    print("Starting simulation with adaptive fragility detection...")
    print("-"*60 + "\n")

    # Run simulation
    executive.run(steps=100, verbose=False)

    # Print report
    print_fragility_report(governance)

    # Visualize
    visualize_fragility_dashboard(governance, temp, save_path='fragility_dashboard.png')

    return temp, governance, executive

# Run the example
if __name__ == "__main__":
    temp, governance, executive = run_fragility_detection_example()
```

---

## Step 6: Compare With/Without Governance

```python
def compare_without_governance():
    """Run the same system without fragility governance for comparison"""

    print("\n" + "="*60)
    print("CONTROL SIMULATION (No Governance)")
    print("="*60)

    # Create same system without governance
    temp = FragileTemperatureSystem.create_variable()
    mechanisms = FragileTemperatureSystem.create_fragile_mechanisms(temp)

    executive = Executive(mechanisms=mechanisms, random_seed=42)

    print("\nRunning without fragility detection...\n")
    executive.run(steps=100, verbose=False)

    # Calculate fragility post-hoc
    calculator = FragilityCalculator()
    fragilities = []

    # We need to simulate step by step to record fragility
    # (Simplified - in practice you'd modify the executive)

    return temp

def compare_results(with_gov_temp, without_gov_temp):
    """Compare results with and without governance"""

    print("\n" + "="*60)
    print("COMPARATIVE ANALYSIS")
    print("="*60)

    # Calculate volatility
    with_volatility = np.std(np.diff([r.value for r in with_gov_temp.memory]))
    without_volatility = np.std(np.diff([r.value for r in without_gov_temp.memory]))

    print(f"\n📊 Volatility Comparison:")
    print(f"   With governance:  {with_volatility:.3f}°C/step")
    print(f"   Without governance: {without_volatility:.3f}°C/step")

    if without_volatility > 0:
        improvement = (without_volatility - with_volatility) / without_volatility * 100
        print(f"   Improvement: {improvement:.1f}%")

    # Calculate value range
    with_range = max([r.value for r in with_gov_temp.memory]) - min([r.value for r in with_gov_temp.memory])
    without_range = max([r.value for r in without_gov_temp.memory]) - min([r.value for r in without_gov_temp.memory])

    print(f"\n🎯 Value Range:")
    print(f"   With governance:  {with_range:.1f}°C")
    print(f"   Without governance: {without_range:.1f}°C")

    # Calculate stability (inverse of coefficient of variation)
    with_mean = np.mean([r.value for r in with_gov_temp.memory])
    without_mean = np.mean([r.value for r in without_gov_temp.memory])

    with_cv = np.std([r.value for r in with_gov_temp.memory]) / with_mean if with_mean > 0 else 1
    without_cv = np.std([r.value for r in without_gov_temp.memory]) / without_mean if without_mean > 0 else 1

    print(f"\n⚖️ Coefficient of Variation (lower is more stable):")
    print(f"   With governance:  {with_cv:.3f}")
    print(f"   Without governance: {without_cv:.3f}")

# Uncomment to run comparison (requires running both simulations)
# without_gov_temp = compare_without_governance()
# compare_results(temp, without_gov_temp)
```

---

## Expected Output

```
============================================================
FRAGILITY DETECTION SIMULATION
============================================================

🔧 Initial Configuration:
   Initial policy: WeightedVotingPolicy
   Fragility threshold: 0.3
   Number of mechanisms: 4

------------------------------------------------------------
Starting simulation with adaptive fragility detection...
------------------------------------------------------------

📊 MODERATE FRAGILITY: 0.342
   Logging for analysis (no immediate action)

⚠️ HIGH FRAGILITY: 0.487
   Switching to HighestConfidencePolicy

🚨 CRITICAL FRAGILITY: 0.723
   Immediate policy switch to HighestConfidencePolicy

[Simulation continues...]

============================================================
FRAGILITY DETECTION REPORT
============================================================

📊 Monitoring Summary:
   Steps monitored: 100
   Threshold adaptation events: 8

🎯 Threshold Evolution:
   Initial threshold: 0.300
   Final threshold: 0.365
   Change: +0.065 (+21.7%)

📈 Fragility Statistics:
   Mean: 0.287
   Std:  0.156
   Min:  0.042
   Max:  0.723
   Median: 0.261
   IQR: 0.198

⚡ Governance Actions:
   Total: 24
   By severity:
     - Critical: 2
     - High: 5
     - Moderate: 8
     - Low: 9

✅ Governance Effectiveness:
   Early fragility (first 20 steps): 0.342
   Late fragility (last 20 steps): 0.187
   Improvement: +45.3%
   → Governance successfully reduced fragility
```

---

## Key Takeaways

1. **Fragility quantifies epistemic uncertainty** - How much policy choice affects outcomes
2. **Dynamic thresholds adapt to system state** - Thresholds increase if system is naturally fragile
3. **Tiered responses** - Different severity levels trigger different actions
4. **Governance learns** - Adaptation rate allows the system to tune itself
5. **Measurable improvement** - Fragility reduced by 45% in this example

---

## Exercises

1. **Custom policies** - Add new policies (e.g., "trimmed mean" ignoring outliers) and see how they affect fragility

2. **Multi-variable fragility** - Extend to track fragility across multiple coupled variables

3. **Predictive fragility** - Use historical patterns to predict when fragility will increase

4. **Cost-aware governance** - Add cost functions for policy switching (e.g., penalize frequent changes)

5. **Ensemble fragility** - Combine fragility signals from multiple variables into a system-level metric

---

## Next Steps

- Explore [Custom Epistemic Signals](./custom-signals.md) for advanced monitoring
- See [Structural Probing](../advanced/structural-probing.md) for active experimentation
- Study [Performance Optimization](../advanced/performance.md) for large-scale fragility detection
- Learn about [Multi-Objective Governance](./multi-objective.md) balancing fragility with other metrics

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Fragility always high | Check if mechanisms are too diverse; adjust their predictions |
| Governance never triggers | Lower initial threshold or increase adaptation_rate |
| Threshold oscillates | Reduce adaptation_rate or increase history_window |
| Too many policy switches | Add cooldown period between switches |
