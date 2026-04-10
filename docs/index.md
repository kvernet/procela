# Procela: Epistemic Governance in Mechanistic Simulations

**Procela** is a research-grade Python framework that treats simulation as an **epistemic process** rather than a fixed model.

## Why Procela?

Traditional mechanistic simulations assume a fixed ontology—variables, causal relationships, and resolution mechanisms are specified before execution and remain static. This assumption fails when the true causal structure of a system is contested, unidentifiable, or subject to change.

**Procela solves this by enabling simulations to question their own assumptions at runtime.**

## Key Features

<div class="grid cards" markdown>

-   **🧩 Domain-Agnostic**

    No built-in epistemic metrics—you define what signals matter. Applicable to epidemiology, climate science, economics, robotics, and beyond.

-   **🔍 Fully Auditable**

    Every hypothesis is permanently recorded with cryptographic source tracking. Every governance action leaves a trace. Complete reproducibility.

-   **🔄 Structural Mutability**

    Add, remove, enable, or disable mechanisms during execution. Change resolution policies on the fly. The model is a living hypothesis.

-   **🧪 Scientific Method Pattern**

    Governance follows detect → hypothesize → experiment → evaluate → conclude. The system learns from its own interventions.

</div>

## Core Abstractions

| Abstraction | Description |
|-------------|-------------|
| **Variables** | Epistemic authorities that maintain complete hypothesis memory with cryptographic source tracking. Resolve competing claims via policies (weighted voting, highest confidence, median, etc). |
| **Mechanisms** | Causal units that read variables and propose hypotheses—they never mutate state directly. Each mechanism encodes a scientific theory (ontology) and attaches confidence scores to its predictions. |
| **Governance** | First-class units that observe epistemic signals and can mutate system topology at runtime. Follow the scientific method pattern. |
| **Epistemic Signals** | User-defined observables computed from variable memories. |
| **Executive** | Orchestrates the entire simulation: executes mechanisms, resolves variables, evaluates governance units. |

## Quick Example

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
    ReasoningTask,
    SystemInvariant,
    VariableSnapshot,
    InvariantPhase,
    InvariantViolation,
    KeyAuthority
)
np.random.seed(42)

# Create a variable
X = Variable("X", RangeDomain(0, 100), policy=WeightedConfidencePolicy())
X.init(VariableRecord(50.0, confidence=1.0))

# Define two mechanisms
class Mechanism1(Mechanism):
    def __init__(self):
        super().__init__(reads=[X], writes=[X])

    def transform(self):
        val = self.reads()[0].value + np.random.normal(0, 1)
        confidence = np.random.uniform(0.8, 1.0)
        self.writes()[0].add_hypothesis(VariableRecord(
            val, confidence=confidence, source=self.key()
        ))

class Mechanism2(Mechanism):
    def __init__(self):
        super().__init__(reads=[X], writes=[X])

    def transform(self):
        val = self.reads()[0].value + np.random.normal(0, 2)
        confidence = np.random.uniform(0.7, 1.0)
        self.writes()[0].add_hypothesis(VariableRecord(
            val, confidence=confidence, source=self.key()
        ))

class Mechanism3(Mechanism):
    def __init__(self):
        super().__init__(reads=[X], writes=[X])

    def transform(self):
        val = self.reads()[0].value + np.random.normal(0, 0.1)
        confidence = np.random.uniform(0.9, 1.0)
        self.writes()[0].add_hypothesis(VariableRecord(
            val, confidence=confidence, source=self.key()
        ))

# Define an invariant
class EmergencyInvariant(SystemInvariant):
    def __init__(self, executive: Executive, confidence_threshold: float = 0.882):
        self.executive = executive
        self.confidence_threshold = confidence_threshold
        self.triggered = False

        def check(snapshot: VariableSnapshot) -> bool:
            var = KeyAuthority.resolve(snapshot.views[0].key)
            if isinstance(var, Variable):
                return var.confidence >= self.confidence_threshold
            return True

        def handle(violation: InvariantViolation, snapshot: VariableSnapshot) -> None:
            if not self.triggered:
                self.executive.add_mechanism(Mechanism3())
                self.executive.logger.warning(
                    f"Step {snapshot.step} - Mechanism 3 has been added."
                )
                self.triggered = True

        super().__init__(
            "EmergencyInvariant",
            condition=check,
            on_violation=handle,
            phase=InvariantPhase.PRE,
            message="Emergency invariant"
        )

# Define the executive with the first two mechanisms
executive = Executive(mechanisms=[Mechanism1(), Mechanism2()])

# Add the invariant
executive.add_invariant(EmergencyInvariant(executive, confidence_threshold=0.882))

# Governance (hook) - switch policy after step 4
def post_step(executive: Executive, step: int):
    if step == 4:
        X.policy = HighestConfidencePolicy()
        executive.logger.info(f"Step {step} - X has changed policy to {X.policy.name}")

# Run simulation
executive.run(steps=10, post_step=post_step)


for hypotheses, conclusion, reasoning in X.memory.records(task=ReasoningTask.CONFLICT_RESOLUTION):
    for hypothesis in hypotheses:
        record = hypothesis.record
        mech = KeyAuthority.resolve(record.source)
        print(f"  {record.value:.2f}  {record.confidence:.2f}  {mech.name}")
    print(f"{conclusion.value:.2f}  {conclusion.confidence:.2f}  {reasoning.explanation}")

print(f"Final value & confidence: {X.value:.2f}  {X.confidence:.2f}")
```

## Expected Output

```
2026-04-04 14:14:52 | INFO     | procela | Step 4 - X has changed policy to HighestConfidencePolicy
2026-04-04 14:14:52 | WARNING  | procela | Step 7 - Mechanism 3 has been added.
  50.50  0.95  Mechanism1
  49.72  0.88  Mechanism2
50.12  0.91  Conflict resolved successfully.
  49.89  0.81  Mechanism1
  49.66  0.96  Mechanism2
49.76  0.89  Conflict resolved successfully.
  51.34  0.80  Mechanism1
  51.30  0.99  Mechanism2
51.32  0.90  Conflict resolved successfully.
  50.85  0.84  Mechanism1
  52.40  0.76  Mechanism2
51.59  0.80  Conflict resolved successfully.
  51.83  0.89  Mechanism1
  47.76  0.79  Mechanism2
49.91  0.84  Conflict resolved successfully.
  48.90  0.86  Mechanism1
  50.54  0.81  Mechanism2
48.90  0.86  Conflict resolved successfully.
  50.37  0.84  Mechanism1
  48.45  0.85  Mechanism2
48.45  0.85  Conflict resolved successfully.
  47.91  0.92  Mechanism1
  48.67  0.75  Mechanism2
  48.39  0.97  Mechanism3
48.39  0.97  Conflict resolved successfully.
  48.10  0.89  Mechanism1
  48.36  0.71  Mechanism2
  48.28  0.99  Mechanism3
48.28  0.99  Conflict resolved successfully.
  49.11  0.86  Mechanism1
  45.84  0.86  Mechanism2
  48.15  1.00  Mechanism3
48.15  1.00  Conflict resolved successfully.
Final value & confidence: 48.15  0.91
```

## Citation

If you use Procela in your research, please cite:

```bibtex
@software{procela_2026,
    title={Procela: Epistemic Governance in Mechanistic Simulations Under Structural Uncertainty},
    author={Kinson Vernet},
    year={2026},
    eprint={2604.00675},
    archivePrefix={arXiv},
    primaryClass={physics.comp-ph},
    url={https://arxiv.org/abs/2604.00675},
}
```

---
