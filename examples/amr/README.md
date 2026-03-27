# AMR Case Study: Epistemic Governance with Competing Ontologies

This directory contains the complete Antimicrobial Resistance (AMR) case study used in the Procela paper.

## Overview

The simulation models the spread of resistant organisms in a hospital network with three competing transmission ontologies:

| Ontology | Equation | Intervention |
|----------|----------|--------------|
| Contact | C(t+1) = C(t) + β·C(t)·(1 - η·1_{I=1}) | Isolation |
| Environmental | C(t+1) = C(t) + β·E(t)·(1 - η·1_{I=2}) | Cleaning |
| Selection | C(t+1) = C(t) + β·A(t)·(1 - η·1_{I=3}) | Stewardship |

Regime shifts occur at steps 60 and 110, changing which ontology dominates.

## Requirements

- Python 3.10+
- Procela (installed from parent directory or PyPI)
- NumPy

## Installation

```bash
# From the repository root
pip install -e .

# Or directly
pip install procela
```

## Running the Simulation

### Help
```bash
python main.py --help
```

### Reproduce paper results
```bash
python main.py -r 50 -s 160 -o outputs/
```

### Governance
- `none` — baseline, no governance
- `fragility` — PolicyFragility
- `coverage` — CoverageDecay
- `probe` — StructuralProbe
- `all` — all governances active

## Directory Structure

```
├── amr
│   ├── governance                  # Governance module
│   │   ├── hooks.py                # Hook events (pre_step, post_step)
│   │   ├── __init__.py
│   │   └── invariants
│   │       ├── coverage.py         # Coverage decay
│   │       ├── emergency.py        # Emergency governance when no mechanism is active
│   │       ├── fragility.py        # Policy fragility governance
│   │       ├── __init__.py
│   │       ├── status.py           # Experiment status
│   │       └── structural.py       # Structural probe governance
│   ├── __init__.py
│   ├── mechanisms                  # Mechanism module
│   │   ├── contact.py              # Contact ontology mechanisms
│   │   ├── environment.py          # Environmental ontology mechanisms
│   │   ├── family.py               # Group of mechanisms sharing an ontology
│   │   ├── __init__.py
│   │   ├── registry.py             # Family registry for governance convenience
│   │   └── selection.py            # Selection ontology mechanisms
│   ├── memory.py                   # Read variables memories
│   ├── setup.py                    # Simulation setup
│   ├── variables.py                # Procela variable definitions
│   ├── viz                         # Visualization module
│   │   ├── cumulative.py           # Cumulative difference computation
│   │   ├── __init__.py
│   │   └── plot.py                 # Figures
│   └── world.py                    # Hidden regime generator
├── main.py                         # Main simulation runner
├── README.md                       # This file
├── requirement.txt                 # Requirements for the AMR case study
└── share
    └── style.mplstyle              # Matplot style for the figures
```

## Paper Results

Expected output (approximately):

| Governance | Mean Error | Std Dev | Regret Improvement |
|------------|------------|---------|-------------------|
| none | 0.535 | 0.383 | — |
| fragility | 0.544 | 0.386 | -9.8% |
| coverage | 0.426 | 0.327 | 35.5% |
| probe | 0.485 | 0.364 | 69.0% |
| all | 0.491 | 0.378 | 61.6% |

## License

Same as Procela.

---
