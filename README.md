# Procela

<div align="center">

**Epistemic Governance in Mechanistic Simulations Under Structural Uncertainty**

[![PyPI version](https://img.shields.io/pypi/v/procela.svg)](https://pypi.org/project/procela/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-procela.org-green.svg)](https://docs.procela.org)
[![Tests](https://github.com/kvernet/procela/actions/workflows/ci.yaml/badge.svg)](https://github.com/kvernet/procela/actions/workflows/ci.yaml)

</div>

---

## 📖 Overview

Procela is a research-grade Python framework that treats simulation as an **epistemic process** rather than a fixed model. Traditional mechanistic simulations assume a fixed ontology—variables, causal relationships, and resolution mechanisms are specified before execution and remain static. This assumption fails when the true causal structure of a system is contested, unidentifiable, or subject to change.

**Procela solves this by enabling simulations to question their own assumptions at runtime.**

### Core abstractions

| Abstraction | Description |
|-------------|-------------|
| **Variables** | Epistemic authorities that maintain complete hypothesis memory with cryptographic source tracking. Resolve competing claims via policies (weighted voting, highest confidence, median, etc). |
| **Mechanisms** | Causal units that read variables and propose hypotheses—they never mutate state directly. Each mechanism encodes a scientific theory (ontology) and attaches confidence scores to its predictions. |
| **Governance (Invariants & Hooks)** | First-class units that observe epistemic signals (coverage, fragility, conflict, etc) and can mutate system topology at runtime. Follow the scientific method pattern: **detect → hypothesize → experiment → evaluate → conclude**. Failed experiments can be automatically reverted. |
| **Epistemic signals** | User-defined observables computed from variable memories. Standard signals: coverage (prediction accuracy), policy fragility (intervention disagreement), recent error (rolling prediction error). |
| **Executive** | Orchestrates the entire simulation: executes mechanisms, resolves variables, evaluates invariants & hooks at PRE/RUNTIME/POST phases. Maintains random state, step counter, and complete system history. |

### Why Procela?

- **Domain-agnostic**: No built-in epistemic metrics—you define what signals matter. Applicable to epidemiology, climate science, economics, robotics, and beyond.
- **Fully auditable**: Every hypothesis is permanently recorded with cryptographic source tracking. Every governance action leaves a trace. Complete reproducibility.
- **Structural mutability**: Add, remove, enable, or disable mechanisms during execution. Change resolution policies on the fly. The model is a living hypothesis.
- **Scientific method pattern**: Governance follows detect → hypothesize → experiment → evaluate → conclude. The system learns from its own interventions.

---

## 🚀 Quick start

### Installation

```bash
# From PyPI (stable)
pip install procela

# From GitHub (development)
pip install git+https://github.com/kvernet/procela.git
```

### Minimal Example

```python
import numpy as np
from procela import (
    Executive,
    Mechanism,
    Variable,
    RangeDomain,
    VariableRecord,
    WeightedVotingPolicy
)

# Create a variable
X = Variable("X", RangeDomain(0, 100), policy=WeightedVotingPolicy())
X.init(VariableRecord(50.0, confidence=1.0))

# Define a mechanism
class MyMechanism(Mechanism):
    def __init__(self):
        super().__init__(reads=[X], writes=[X])

    def transform(self):
        val = self.reads()[0].value + np.random.normal(0, 1)
        self.writes()[0].add_hypothesis(VariableRecord(val, confidence=0.8, source=self.key()))

# Run simulation
executive = Executive(mechanisms=[MyMechanism()])
executive.run(steps=10)
print(f"Final value: {X.value:.2f}")
```

### Governance Example

```python
from procela import (
    HighestConfidencePolicy,
    SystemInvariant,
    InvariantPhase,
    InvariantViolation,
    VariableSnapshot,
    KeyAuthority
)

# Define a governance invariant
class FragilityInvariant(SystemInvariant):
    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self.switched = False

        def check(snapshot: VariableSnapshot):
            confidences = [KeyAuthority.resolve(view.key).confidence for view in snapshot.views]
            if confidences and max(confidences) - min(confidences) > self.threshold:
                return False  # Violation — fragility detected
            return True

        def handle(invariant: InvariantViolation, snapshot: VariableSnapshot):
            if not self.switched:
                print("Fragility detected! Switching to highest-confidence policy")
                X.policy = HighestConfidencePolicy()
                self.switched = True

        super().__init__(
            "FragilityInvariant",
            condition=check,
            on_violation=handle,
            phase=InvariantPhase.RUNTIME,
            message="Fragility invariant violation"
        )

# Add invariant to executive
executive.add_invariant(FragilityInvariant())

executive.run(steps=10)
print(f"Final value: {X.value:.2f}")
```

---

## 📚 Case study: AMR spread in hospital networks

See the [AMR](https://github.com/kvernet/procela/tree/main/examples/amr)

---

## 🛠️ Development

### Setup development environment

```bash
git clone https://github.com/kvernet/procela.git
cd procela
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
make dev-install
```

### Available makefile targets

| Target | Description |
|--------|-------------|
| `make install` | Install package and dependencies |
| `make dev-install` | Install with development dependencies |
| `make lint` | Run linters (ruff, black) |
| `make type-check` | Run mypy type checking |
| `make test` | Run pytest with coverage |
| `make pre-commit` | Run all checks before committing |
| `make docs` | Build documentation |
| `make clean` | Clean build artifacts |

### Code style

- **Formatting**: Black (line length 88)
- **Linting**: Ruff
- **Type checking**: Mypy (strict mode)
- **Testing**: Pytest with coverage (target 100%)

```bash
make pre-commit  # Run all checks
```

---

## 📖 Documentation

- **User guide**: [https://docs.procela.org/](https://docs.procela.org/)
- **API reference**: [https://docs.procela.org/api/](https://docs.procela.org/api/)
- **Examples**: [https://docs.procela.org/examples](https://docs.procela.org/examples)

---

## 🤝 Contributing

We welcome contributions! Please see:

- [CONTRIBUTING.md](https://github.com/kvernet/procela) for detailed guidelines
- [AUTHORS.txt](https://github.com/kvernet/procela) for the list of contributors

**Areas where contributions are especially welcome:**
- Additional governance invariants (regret-based, multi-objective)
- Performance optimizations for large-scale simulations
- New domain case studies (climate, economics, robotics)
- Documentation improvements and tutorials
- Visualization tools for audit trails

---

## 📄 Citation

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

## 📋 License

Procela is licensed under the **Apache License 2.0**. See [LICENSE](https://github.com/kvernet/procela) for details.

---

## 🙏 Acknowledgments

We thank the open-source community for Pyodide, NumPy, and the Python scientific ecosystem.

---

## 📬 Contact

- **Email**: [research@procela.org](mailto:research@procela.org)
- **GitHub Issues**: [github.com/kvernet/procela/issues](https://github.com/kvernet/procela/issues)

---

<div align="center">
  <sub>Built with ❤️ for epistemic governance in simulation.</sub>
</div>

---
