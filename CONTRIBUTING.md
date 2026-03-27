# Contributing to Procela

Thank you for your interest in contributing to Procela, a framework for epistemic governance in mechanistic simulation.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy-lang.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

---

## 📜 Code of conduct

This project adheres to a **rigorous academic and scientific standard**. All contributions must:

- Maintain **mathematical and logical rigor**
- Follow **epistemic governance best practices**
- Prioritize **clarity and reproducibility** over convenience
- Document **assumptions and limitations** explicitly
- Include **complete audit trails** for all governance actions

By participating, you agree to uphold these standards.

---

## 🧠 Development philosophy

Procela follows these core principles:

| Principle | Description |
|-----------|-------------|
| **Variables as epistemic authorities** | Variables are not passive containers — they maintain hypothesis memory and arbitrate competing claims |
| **Mechanisms as scientific theories** | Each mechanism encodes a testable hypothesis with explicit confidence and source tracking |
| **Governance as first-class citizen** | Invariants & hooks observe epistemic signals and can mutate system structure at runtime |
| **Strictness over convenience** | Type safety, complete test coverage, and formal validation are mandatory |
| **Complete auditability** | Every hypothesis, resolution, and governance action is permanently recorded |
| **Scientific method pattern** | All governance follows: detect → hypothesize → experiment → evaluate → conclude |

---

## 📋 Prerequisites

- **Python 3.10+** (strict requirement — no exceptions)
- **Git** with commit signing (recommended)
- **Make** (for development workflows)
- Understanding of:
  - Epistemic uncertainty and causal inference
  - Mechanistic modeling or simulation frameworks
  - Python type hints and testing best practices

---

## 🛠️ Development setup

### 1. Fork and clone

```bash
git clone https://github.com/kvernet/procela.git
cd procela
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install development dependencies

```bash
make dev-install
```

This installs:
- Core package with dependencies
- Development tools: `black`, `ruff`, `mypy`, `pytest`

### 4. Install pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files  # Verify hooks work
```

### 5. Verify installation

```bash
make test          # Run tests
make lint          # Check code style
make type-check    # Verify type hints
```

---

## 🌿 Branch naming convention

```
feature/<short-description>     # New functionality
fix/<issue-number>-description  # Bug fixes
docs/<topic>                    # Documentation updates
refactor/<module>               # Code refactoring
test/<coverage-area>            # Test improvements
governance/<invariant>          # New governance invariants
```

**Examples:**
- `feature/coverage-decay-invariant`
- `fix/42-variable-resolution-bug`
- `docs/epistemic-signals`

---

## 🔧 Development workflow

### 1. Create feature branch

```bash
git checkout -b feature/coverage-decay-invariant
```

### 2. Make changes with quality checks

```bash
# Auto-format code
make format

# Run linters
make lint

# Type check
make type-check

# Run tests
make test

# Run all checks
make pre-commit
```

### 3. Commit changes

```bash
git commit -S -m "feat(governance): add coverage decay invariant"
```

**Commit message format:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Test additions
- `refactor`: Code refactoring
- `governance`: New governance invariant
- `mechanism`: New mechanism family

### 4. Push and create pull request

```bash
git push origin feature/coverage-decay-invariant
```

---

## ✅ Pre-commit validation

All commits must pass the following checks:

| Check | Tool | Requirement |
|-------|------|-------------|
| **Code formatting** | Black | No deviations (line length 88) |
| **Linting** | Ruff | Zero errors (E, F, W, C90) |
| **Type checking** | mypy | Strict mode, no errors |
| **Documentation** | pydocstyle | NumPy-style docstrings |
| **Test coverage** | pytest | 100% on new code (branch coverage) |
| **Audit trail** | Manual | Governance actions must be traceable |

Run `make pre-commit` locally to ensure all checks pass.

---

## 📝 Code standards

### Type annotations

All public functions must have complete type hints:

```python
from procela import Variable, HypothesisRecord, Key

def resolve_hypotheses(
    hypotheses: List[HypothesisRecord],
    policy: str = "weighted_voting",
    threshold: float | None = None
) -> tuple[float, dict[Key, float]]:
    """
    Resolve competing hypotheses using specified policy.

    Parameters
    ----------
    hypotheses : List[HypothesisRecord]
        List of hypotheses with values and confidences
    policy : str, default="weighted_voting"
        Resolution policy: "weighted_voting", "highest_confidence", "median"
    threshold : float, optional
        Confidence threshold for policy switching

    Returns
    -------
    tuple[float, dict[Key, float]]
        Resolved value and confidence contribution per source

    Raises
    ------
    ValueError
        If policy is unknown
    """
```

### Documentation

All public entities must have NumPy-style docstrings with:

- **Description**: Clear purpose and behavior
- **Parameters**: Types and descriptions
- **Returns**: Types and descriptions
- **Raises**: Exceptions that may be raised
- **Examples**: Minimal working example
- **References**: Literature citations when applicable

### Testing requirements

**Unit tests**: All public methods/functions

```python
import pytest
from procela import (
    Variable, RangeDomain, VariableRecord, WeightedConfidencePolicy, Key
)

def test_weighted_voting_resolution():
    """Test weighted voting policy resolves correctly."""
    var = Variable("test", RangeDomain(0, 100), policy=WeightedConfidencePolicy())

    # Add hypotheses
    var.add_hypothesis(VariableRecord(10.0, confidence=0.9, source=Key()))
    var.add_hypothesis(VariableRecord(20.0, confidence=0.5, source=Key()))

    # Resolve
    result = var.resolve_conflict()

    # Expected: (10*0.9 + 20*0.5) / (0.9+0.5) = (9+10)/1.4 = 13.57
    assert result.value == pytest.approx(13.57, 0.01)

```

**Property Tests**: For mathematical invariants

```python
from hypothesis import given, strategies as st

@given(st.floats(min_value=0, max_value=100))
def test_coverage_bounded(value):
    """Coverage should always be in [0,1]."""
    coverage = compute_coverage(value, predicted=50)
    assert 0 <= coverage <= 1
```

**Integration Tests**: For governance workflows

```python
def test_coverage_decay_governance():
    """Test that coverage decay invariant triggers correctly."""
    executive, families = create_test_simulation()
    invariant = CoverageDecayInvariant(threshold=0.7)
    executive.add_invariant(invariant)

    # Simulate regime shift
    for step in range(50):
        executive.step()

    # Verify invariant triggered
    assert invariant.state == "experimenting"
    assert len(invariant.experiment_log) > 0
```

---

## 🧪 Governance invariant guidelines

When adding new governance invariants:

1. **Follow the Scientific Method Pattern**:
```python
from procela import (
    SystemInvariant,
    VariableSnapshot,
    InvariantViolation,
    InvariantPhase
)

class MyInvariant(SystemInvariant):
    def __init__(self):

        def check_condition(snapshot: VariableSnapshot) -> bool:
            # Detect epistemic crisis

        def handle_violation(invariant: InvariantViolation, snapshot: VariableSnapshot) -> None:
            # Formulate hypothesis, run experiment

        super().__init__(
            name="MyInvariant",
            condition=check_condition,
            on_violation=handle_violation,
            phase=InvariantPhase.RUNTIME,
            message=""
        )

```

2. **Use epistemic signals**:
   - Read from variables (coverage, fragility, recent_error for instance)
   - Compute trends (not just instantaneous values)

3. **Make experiments reversible**:
   - Store original state before mutation
   - Evaluate evidence after experiment window
   - Revert if experiment fails

4. **Log everything**:
   - Record experiment start/end
   - Store pre/post metrics
   - Include hypothesis and conclusion

---

## 🔍 Review process

### 1. Automated checks (Must pass)

- ✅ All tests pass (100% coverage on new code)
- ✅ No type errors (strict mypy)
- ✅ No linting violations (Ruff E, F, W)
- ✅ Documentation builds without warnings
- ✅ Pre-commit hooks pass

### 2. Maintainer review

| Aspect | Reviewer |
|--------|----------|
| **Conceptual validity** | Does the contribution align with epistemic governance principles? |
| **Mathematical correctness** | Are formulas and equations correct? |
| **Auditability** | Is every governance action recorded? |
| **API consistency** | Does it follow Procela's design patterns? |
| **Test coverage** | Are edge cases covered? |

### 3. Merge requirements

- **Two maintainer approvals** minimum
- **All discussions resolved**
- **No outstanding requested changes**
- **CI/CD pipeline passes**

---

## 🎯 Areas of contribution

### High priority

| Area | Description |
|------|-------------|
| **Governance invariants** | New invariants: regret-based, multi-objective, meta-governance |
| **Epistemic signals** | Additional signals: prediction variance, causal consistency |
| **Mechanism families** | New domain examples: climate, economics, robotics |
| **Documentation** | Tutorials, API reference, case studies |
| **Performance** | Optimize for large-scale simulations |

### Domain expertise needed

- **Causal inference**: Identification algorithms, counterfactual reasoning
- **Decision theory**: Multi-objective optimization, regret bounds
- **Stochastic processes**: Regime detection, change point analysis
- **Visualization**: Audit trail network diagrams, interactive dashboards

### Experimental contributions

- Novel governance strategies
- Domain-specific adapters
- Integration with other frameworks (PyMC, JAX, PyTorch)
- Real-world validation studies

---

## 📚 Resources

- **Documentation**: [https://docs.procela.org/](https://docs.procela.org/)
- **API reference**: [https://docs.procela.org/api](https://docs.procela.org/api)
- **Examples**: [https://docs.procela.org/examples](https://docs.procela.org/examples)
- **Community**: [https://procela.org/community](https://procela.org/community)

---

## ❓ Questions?

| Topic | Contact |
|-------|---------|
| **Technical discussions** | GitHub discussions |
| **Bug reports** | GitHub issues (include minimal reproducible example) |
| **Research collaborations** | [research@procela.org](mailto:research@procela.org) |
| **Governance design** | Open a discussion with tag "governance" |

---

## 🙏 Acknowledgments

Contributors to Procela maintain a **AUTHORS.txt** file. By contributing, you agree to be listed there.

---

<div align="center">
  <sub>
    <i>Every line of code in Procela represents an epistemic claim. Write accordingly.</i>
  </sub>
</div>

---
