# Procela

**Procela** — Contractual mechanistic core with active causal reasoning

---

## Overview

Procela is a research-oriented Python framework designed for:

- Mechanistic modeling and reasoning
- Contractual and causal inference
- Domain-adaptable core logic for diverse applications

This is the initial version of the framework; the API and functionality are under development.

---

## Installation

Clone the repository and install dependencies in development mode:

```bash
git clone https://github.com/kvernet/procela.git
cd procela
make requirements
make dev-install
```

---

## Usage

Currently, Procela provides the package structure and development environment.
Future versions will include a CLI and programmatic API for causal reasoning.

---

## Development Guidelines

* Follow the [CONTRIBUTING.md](CONTRIBUTING.md) instructions
* All code must pass formatting, linting, and type checks:

```bash
make lint
make type-check
make test
pre-commit run --all-files
```

* Use the Makefile targets to maintain reproducibility and strict hygiene.

---

## License

Procela is licensed under the **Apache License 2.0** — see [LICENSE](LICENSE).

---

## Authors

See [AUTHORS.txt](AUTHORS.txt) for the full list of contributors and contact information.

---

## Status

* Alpha / Skeleton stage
* CI, linters, and pre-commit hooks fully configured
* API under design

---
