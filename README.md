# Procela

<div align="center">

**Epistemic Governance in Mechanistic Simulations Under Structural Uncertainty**

[![PyPI version](https://img.shields.io/pypi/v/procela.svg)](https://pypi.org/project/procela/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-procela.org-green.svg)](https://procela.org)
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

We demonstrate Procela on antimicrobial resistance (AMR) spread with three competing ontology families:

| Ontology | Equation | Intervention |
|----------|----------|--------------|
| **Contact** | $C_{t+1} = C_t + \beta_C C_t (1 - \eta_C \mathbf{1}_{I=1})$ | Isolation |
| **Environmental** | $C_{t+1} = C_t + \beta_E E_t (1 - \eta_E \mathbf{1}_{I=2})$ | Cleaning |
| **Selection** | $C_{t+1} = C_t + \beta_S A_t (1 - \eta_S \mathbf{1}_{I=3})$ | Stewardship |

### Results

| Governance strategy | Error reduction | Regret improvement |
|---------------------|-----------------|-------------------|
| Policy fragility | -1.88% | **-11.2%** |
| Coverage decay | **15.04%** | 15.0% |
| Structural probe | 9.02 | **67.0%** |
| All combined | 2.06% | 54.5% |

> **Key finding**: The case study has revealed a fundamental trade-off:

- Prediction-optimal $\neq$ decision-optimal
- Coverage improves predictions but makes worse decisions (+15.04%, C.E=-15.0%)
- Probe makes better decisions but only modestly improves predictions (+9.02%, C.E=-67.0%)

Consider hybrid — probe for information, coverage for prediction.

---

## 🛠️ Development

### Setup development environment

```bash
git clone https://github.com/kvernet/procela.git
cd procela
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
make install-dev
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

- **User guide**: [https://procela.org/docs](https://procela.org/docs)
- **API reference**: [https://procela.org/api](https://procela.dev/api)
- **Examples**: [https://procela.org/examples](https://procela.org/examples)

---

## 🤝 Contributing

We welcome contributions! Please see:

- [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines
- [AUTHORS.txt](AUTHORS.txt) for the list of contributors

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
  author = {Kinson Vernet},
  title = {Procela: A Framework for Epistemic Governance in Mechanistic Simulation},
  year = {2026},
  url = {https://procela.orh},
  doi = {10.xxxx/xxxxx}
}
```

---

## 📋 License

Procela is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Procela was developed with support from [Your Institution/Funding Source]. We thank the open-source community for Pyodide, NumPy, and the Python scientific ecosystem.

---

## 📬 Contact

- **Email**: [research@procela.org](mailto:research@procela.org)
- **GitHub Issues**: [github.com/kvernet/procela/issues](https://github.com/kvernet/procela/issues)

---

<div align="center">
  <sub>Built with ❤️ for epistemic governance in simulation.</sub>
</div>

---
