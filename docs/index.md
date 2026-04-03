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
        self.writes()[0].add_hypothesis(VariableRecord(val, confidence=0.8, source=self.key()))

class Mechanism2(Mechanism):
    def __init__(self):
        super().__init__(reads=[X], writes=[X])

    def transform(self):
        val = self.reads()[0].value + np.random.normal(0, 2)
        self.writes()[0].add_hypothesis(VariableRecord(val, confidence=0.7, source=self.key()))

# Define the executive
executive = Executive(mechanisms=[Mechanism1(), Mechanism2()])

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

## Citation

If you use Procela in your research, please cite:

```bibtex
@software{procela_2026,
  author = {Kinson Vernet},
  title = {Procela: Epistemic Governance in Mechanistic Simulation Under Structural Uncertainty},
  year = {2026},
  url = {https://procela.org},
  doi = {10.xxxx/xxxxx}
}
```

---
