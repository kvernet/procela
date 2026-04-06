# Examples

This section contains practical examples demonstrating Procela's capabilities, from basic simulations to advanced governance patterns. Each example is fully runnable and includes detailed explanations.

This provides:

- Clear three-level organization (Beginner, Intermediate, Advanced)
- Brief descriptions of what each level covers
- Links to specific examples
- Prerequisites and setup instructions
- Consistent example structure
- Contribution guidelines

## Example Levels

The examples are organized by complexity to help you progress at your own pace:

| Level | Focus | Prerequisites | Time to Complete |
|-------|-------|---------------|------------------|
| **Beginner** | Core concepts and basic workflows | Python basics | 5-10 min each |
| **Intermediate** | Governance patterns and multi-variable systems | Beginner examples | 15-30 min each |
| **Advanced** | Custom policies, performance optimization, real-world case studies | Intermediate examples | 30-60 min each |

---

## 🟢 Beginner Examples

*Start here if you're new to Procela*

These examples introduce the fundamental abstractions: Variables, Mechanisms, and the Executive.

- **[Temperature Simulation](./beginner/temperature-simulation.md)** - Your first complete simulation with a single variable and competing mechanisms

- **[Simple Growth Model](./beginner/simple-growth.md)** - Population growth with two competing theories (linear vs logistic)

- **[Basic Governance](./beginner/basic-governance.md)** - Adding a simple invariant that monitors prediction confidence

- **[Multiple Variables](./beginner/multiple-variables.md)** - Working with interconnected variables (predator-prey system)

**What you'll learn:**

- Creating and configuring Variables
- Implementing custom Mechanisms
- Running simulations with the Executive
- Basic governance with SystemInvariant

---

## 🟡 Intermediate Examples

*Deepen your understanding of governance and epistemic signals*

These examples explore adaptive behavior, signal monitoring, and structural changes.

- **[Fragility Detection and Response](./intermediate/fragility-detection.md)** - Automatically detect policy sensitivity and switch resolution strategies

- **[Coverage-Based Mechanism Selection](./intermediate/coverage-selection.md)** - Monitor prediction accuracy and disable underperforming mechanisms

- **[Multi-Variable Governance](./intermediate/multi-variable.md)** - Coordinate governance across multiple related variables

- **[Custom Epistemic Signals](./intermediate/custom-signals.md)** - Define domain-specific signals (volatility, momentum, bias)

- **[Checkpoint and Restore](./intermediate/checkpoint-restore.md)** - Save and restore simulation state for long-running experiments

**What you'll learn:**

- Implementing adaptive governance strategies
- Creating and using custom epistemic signals
- Managing multiple variables with dependencies
- Saving/restoring simulation state

---

## 🔴 Advanced Examples

*Push the boundaries of epistemic governance*

These examples demonstrate complex patterns, performance optimization, and real-world applications.

- **[AMR Case Study](./advanced/amr-case-study.md)** - Complete antimicrobial resistance simulation with competing ontology families (Contact, Environmental, Selection)

- **[Ensemble Mechanisms](./advanced/ensemble-mechanisms.md)** - Combine multiple mechanisms with adaptive weighting

- **[Structural Probing](./advanced/structural-probing.md)** - Actively experiment with different mechanism configurations

- **[Performance Optimization](./advanced/performance.md)** - Techniques for large-scale simulations (parallel execution, memory management)

- **[Custom Resolution Policies](./advanced/custom-policies.md)** - Implement domain-specific voting and aggregation strategies

- **[Distributed Simulation](./advanced/distributed.md)** - Run multiple scenarios in parallel across CPU cores or cluster

- **[Reinforcement Learning Integration](./advanced/rl-integration.md)** - Use Procela as an environment for RL agents

**What you'll learn:**

- Real-world research applications (epidemiology, climate science)
- Advanced governance patterns (probing, exploration/exploitation)
- Performance tuning for large-scale simulations
- Integration with external tools (RL, optimization, visualization)

---

## Running the Examples

### Prerequisites

```bash
# Install Procela
pip install procela

# For visualization examples
pip install matplotlib

# For data analysis examples
pip install numpy pandas
```

### Getting the Code

All examples are available in the [GitHub repository](https://github.com/kvernet/procela/tree/main/examples):

```bash
git clone https://github.com/kvernet/procela.git
cd procela/examples
```

### Running an Example

```bash
# Run a specific example
python beginner/simple_growth.py

# Or with verbose output
python beginner/simple_growth.py --verbose

# Save results to file
python beginner/simple_growth.py --output results.json
```

## Example Structure

Each example follows a consistent structure:

```python
"""
Example: [Name]
Level: [Beginner/Intermediate/Advanced]
Concepts: [Variables, Mechanisms, Governance, ...]
"""

# 1. Imports
from procela import *

# 2. Define components (Variables, Mechanisms, Governance)
class MyMechanism(Mechanism):
    # ...

# 3. Create and configure
executive = Executive(mechanisms=[...])

# 4. Run simulation
executive.run(steps=100)

# 5. Analyze results
print(f"Final value: {variable.value}")
```

## Contributing Examples

Have an interesting use case or tutorial? We welcome contributions!

1. Fork the repository
2. Add your example to the appropriate level directory
3. Include docstrings and comments
4. Submit a pull request

See [CONTRIBUTING.md](../contributing.md) for detailed guidelines.

## Next Steps

- **New to Procela?** Start with the [Getting Started Guide](../getting-started/quickstart.md)
- **Ready to build?** Jump to the [Beginner Examples](#-beginner-examples)
- **Research application?** Check the [AMR Case Study](./advanced/amr-case-study.md)
- **API questions?** Visit the [API Reference](../api/reference.md)
