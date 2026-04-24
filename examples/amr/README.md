# AMR Case Study: Epistemic Governance with Competing Ontologies

This directory contains the complete Antimicrobial Resistance (AMR) case study used in the Procela paper.

## Overview

The simulation models the spread of resistant organisms in a hospital network with three competing transmission ontologies:

| Ontology | Equation | Intervention |
|----------|----------|--------------|
| Contact | $C(t+1) = C(t) + \beta \cdot C(t) \cdot (1 - \eta \cdot 1_{I=1})$ | Isolation |
| Environmental | $C(t+1) = C(t) + \beta \cdot E(t) \cdot (1 - \eta \cdot 1_{I=2})$ | Cleaning |
| Selection | $C(t+1) = C(t) + \beta \cdot A(t) \cdot (1 - \eta \cdot 1_{I=3})$ | Stewardship |

Regime shifts occur at steps 60 and 110, changing which ontology dominates.

## Requirements

- Python 3.10+
- Procela framework (`pip install procela`)
- NumPy

## Installation

```bash
# From the AMR example root
python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

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
- `all` — all governances combined


## Paper Results

Expected output (approximately):

| Governance | Mean Error | Std Dev | Regret Improvement |
|------------|------------|---------|-------------------|
| none | 0.535 | 0.383 | — |
| fragility | 0.544 | 0.386 | -9.6% |
| coverage | 0.426 | 0.327 | 37.4% |
| probe | 0.485 | 0.364 | 69.0% |
| all | 0.491 | 0.378 | 63.2% |

> **Key finding**: The case study has revealed a fundamental trade-off:

- Prediction-optimal $\neq$ decision-optimal
- Coverage decay makes better predictions but modest decisions (+20.42%, C.E=37.4%)
- Probe makes better decisions but only modestly improves predictions (+9.31%, C.E=69.0%)

Consider hybrid — probe for information, coverage for prediction.

### Topology dynamics
Procela ensures complete auditability. The memories of variables can be used to visualize the topology dynamics. As illustrated in the following figure, the topology evolution for each governance in the AMR study is illustrated. The contact family has three mechanisms, while the environmental and selection families have four each. In total, the AMR case study has eleven competing mechanisms that governance restructures over time.

## License

Same as Procela.

---
