# Executive: The Orchestrator

The **Executive** is the central nervous system of any Procela simulation. It orchestrates mechanisms, variables, and governance units, ensuring they work together coherently while maintaining complete auditability and reproducibility.

This guide covers:

- Core responsibilities and architecture
- Basic and advanced configuration
- State management and checkpointing
- Parallel and distributed execution
- Event system for extensibility
- Performance optimization techniques
- Error handling and recovery
- Practical examples for different use cases
- Best practices for production use

## Core Responsibilities

The Executive handles:

- **Scheduling**: Executes mechanisms
- **State Management**: Maintains random state, step counter, and system history
- **Resolution**: Coordinates variable policy resolution
- **Governance**: Triggers governance units at appropriate phases
- **Auditability**: Tracks every action for reproducibility
- **Error Handling**: Manages failures and rollbacks

## Basic Executive Usage

### Creating and Running a Simulation

```python
from procela import Executive, Mechanism, Variable

# Create components
X = Variable("X", RangeDomain(0, 100))
Y = Variable("Y", RangeDomain(0, 100))

mechanisms = [MyMechanism(), AnotherMechanism()]

# Create executive
executive = Executive(mechanisms=mechanisms)

# Initialize and run
executive.run(steps=100)

# Access results
print(f"Final X: {X.value}, Final Y: {Y.value}")
```

### Executive Lifecycle

```python
# 1. Creation
executive = Executive(mechanisms=mechanisms)

# 3. Execution
executive.run(steps=100)  # Run simulation

# 4. (Optional) Reset or continue
executive.reset()  # Reset a new world with same configurations
executive.run(steps=50)  # Run additional steps
```

## Executive Architecture

### Internal Structure

```
┌─────────────────────────────────────────────────────────────┐
│                        EXECUTIVE                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Mechanisms  │  │  Variables  │  │    Governance       │  │
│  │   Registry  │  │  Registry   │  │      Units          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Execution Pipeline                     │    │
│  │  ┌──────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐  │    │
│  │  │ PRE  │→ │MECHANISMS│→ │RESOLVE  │→ │  POST    │  │    │
│  │  │Phase │  │  Phase   │  │ Phase   │  │  Phase   │  │    │
│  │  └──────┘  └──────────┘  └─────────┘  └──────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Random    │  │   History   │  │    Checkpoint       │  │
│  │    State    │  │    Store    │  │     Manager         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Execution Pipeline

Each simulation step follows this pipeline:

```python
def step(self):
    """Execute one simulation step"""

    # Phase 1: PRE
    self._check_invariants(InvariantPhase.PRE)

    # Phase 2: MECHANISM EXECUTION
    for mechanism in self.active_mechanisms:
        mechanism.transform()

    # # Phase 3: RUNTIME
    self._check_invariants(InvariantPhase.RUNTIME)

    # Phase 3: RESOLUTION
    for variable in self.variables:
        variable.resolve()

    # Phase 4: POST
    self._check_invariants(InvariantPhase.POST)

    self._step_index += 1
```

## Advanced Configuration

### Custom Execution Order

Control the order of mechanism execution:

```python
class OrderedExecutive(Executive):
    """Executive with explicit mechanism ordering"""

    def __init__(self, mechanisms, execution_order=None):
        super().__init__(mechanisms=mechanisms)
        self.execution_order = execution_order or mechanisms

    def _execute_mechanisms(self):
        """Execute in specified order"""
        for mechanism in self.execution_order:
            if mechanism.is_enabled():
                mechanism.run()
```

### Conditional Execution

Execute mechanisms based on conditions:

```python
class ConditionalExecutive(Executive):
    """Executive that conditionally executes mechanisms"""

    def __init__(self, mechanisms, condition_func=None):
        super().__init__(mechanisms=mechanisms)
        self.condition_func = condition_func

    def step(self):
        """Execute step with conditional mechanisms"""
        if self.condition_func:
            # Determine which mechanisms should run
            to_execute = [m for m in self.mechanisms()
                         if m.is_enabled and self.condition_func(m, self)]
        else:
            to_execute = self.mechanisms()

        # Execute selected mechanisms
        for mechanism in to_execute:
            mechanism.run()

        # Resolution
        for variable in self.writable():
            variable.resolve_conflict()
```

## State Management

### Random State Control

```python
import numpy as np

class ReproducibleExecutive(Executive):
    """Executive with deterministic random behavior"""

    def __init__(self, mechanisms, random_seed=42):
        super().__init__(mechanisms=mechanisms)
        self.random_seed = random_seed
        self.random_state = np.random.RandomState(random_seed)

    def step(self):
        """Execute with deterministic random state"""
        # Set random state for all mechanisms
        for mechanism in self.mechanisms():
            mechanism.random_state = self.random_state

        super().step()

    def reset_random_state(self):
        """Reset random state to initial seed"""
        self.random_state = np.random.RandomState(self.random_seed)
```

### Checkpoint and Restore

```python
from procela import Executive, Mechanism

class CheckpointManager:
    """Manages simulation checkpoints"""

    def __init__(self, executive: Executive):
        self.executive = executive
        self.checkpoints = {}

    def save_checkpoint(self, name):
        """Save current simulation state"""
        checkpoint = self.executive.create_checkpoint()
        self.checkpoints[name] = checkpoint
        return checkpoint

    def restore_checkpoint(self, name):
        """Restore simulation state from checkpoint"""
        checkpoint = self.checkpoints.get(name)
        self.executive.restore_checkpoint(checkpoint)

# Usage
executive = Executive(mechanisms=mechanisms)
checkpoint_mgr = CheckpointManager(executive)

executive.run(steps=50)
checkpoint_mgr.save_checkpoint('after_50_steps')

# Continue or experiment
executive.run(steps=25)
checkpoint_mgr.restore_checkpoint('after_50_steps')  # Rollback
```

## Parallel Execution

### Multi-Threaded Mechanism Execution

```python
from concurrent.futures import ThreadPoolExecutor
import threading

from procela import Executive

class ParallelExecutive(Executive):
    """Executive that executes mechanisms in parallel"""

    def __init__(self, mechanisms, max_workers=None):
        super().__init__(mechanisms=mechanisms)
        self.max_workers = max_workers or len(mechanisms)
        self.lock = threading.Lock()

    def step(self):
        """Execute mechanisms concurrently"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all mechanisms for execution
            futures = [
                executor.submit(self._safe_transform, mechanism)
                for mechanism in self.mechanisms()
            ]

            # Wait for completion
            for future in futures:
                future.result()

    def _safe_transform(self, mechanism):
        """Thread-safe mechanism execution"""
        try:
            mechanism.transform()
        except Exception as e:
            with self.lock:
                print(f"Error in {mechanism.key()}: {e}")
            raise
```

### Distributed Execution (Batch Processing)

```python
from procela import Executive

class BatchExecutive:
    """Executive for batch processing of multiple scenarios"""

    def __init__(self, mechanism_factory, n_scenarios=10):
        super().__init__(mechanisms=mechanism_factory())
        self.mechanism_factory = mechanism_factory
        self.n_scenarios = n_scenarios
        self.results = []

    def run_scenarios(self, steps=100):
        """Run multiple scenarios in parallel"""
        import multiprocessing as mp

        with mp.Pool(processes=mp.cpu_count()) as pool:
            scenarios = [
                pool.apply_async(self._run_scenario, (steps, seed))
                for seed in range(self.n_scenarios)
            ]

            self.results = [s.get() for s in scenarios]

        return self.results

    def _run_scenario(self, steps, seed):
        """Run single scenario"""
        mechanisms = self.mechanism_factory()
        executive = Executive(mechanisms=mechanisms)
        executive.rng.seed(seed)
        executive.run(steps=steps)

        return {
            'seed': seed,
            'final_values': {var.name: var.value for var in executive.variables()},
            'memory': {var.name: var.memory for var in executive.variables()}
        }
```

## Event System

### Custom Event Handlers

```python
from procela import Executive

class EventDrivenExecutive(Executive):
    """Executive with event emission"""

    def __init__(self, mechanisms):
        super().__init__(mechanisms=mechanisms)
        self.event_handlers = {
            'pre_step': [],
            'post_mechanism': [],
            'post_resolution': [],
            'post_step': [],
            'error': []
        }

    def on(self, event, handler):
        """Register event handler"""
        if event in self.event_handlers:
            self.event_handlers[event].append(handler)

    def _emit(self, event, *args, **kwargs):
        """Emit event to registered handlers"""
        for handler in self.event_handlers.get(event, []):
            try:
                handler(*args, **kwargs)
            except Exception as e:
                print(f"Error in event handler: {e}")

    def step(self):
        """Execute step with events"""
        try:
            self._emit('pre_step', self.step_index())

            # Execute mechanisms
            for mechanism in self.mechanisms():
                if mechanism.is_enabled():
                    mechanism.run()
                    self._emit('post_mechanism', mechanism, self.step_index())

            # Resolve variables
            for variable in self.writable():
                variable.resolve_conflict()
            self._emit('post_resolution', self.variables(), self.step_index())

            self._step_index += 1
            self._emit('post_step', self.step_index())

        except Exception as e:
            self._emit('error', e, self.step_index())
            raise

# Usage
executive = EventDrivenExecutive(mechanisms)

def log_step(step):
    print(f"Starting step {step}")

def log_variables(variables, step):
    print(f"Step {step}: X={variables[0].value:.2f}")

executive.on('pre_step', log_step)
executive.on('post_resolution', log_variables)

executive.run(steps=10)
```

## Performance Optimization

### Lazy Variable Resolution

```python
from procela import Executive, InvariantPhase

class OptimizedExecutive(Executive):
    """Executive with performance optimizations"""

    def __init__(self, mechanisms, lazy_resolution=False):
        super().__init__(mechanisms=mechanisms)
        self.lazy_resolution = lazy_resolution
        self._resolution_cache = {}

    def step(self):
        """Optimized step execution"""
        # Phase 1: PRE invariants
        self._check_invariants(InvariantPhase.PRE)

        # Phase 2: Execute mechanisms
        for mechanism in self.mechanisms():
            mechanism.run()

        # Phase 3: RUNTIME invariants
        self._check_invariants(InvariantPhase.RUNTIME)

        # Phase 4: Resolve variables (with caching)
        for variable in self.writable():
            if self.lazy_resolution:
                # Only resolve if value was requested
                self._mark_dirty(variable)
            else:
                variable.resolve_conflict()

        # Phase 5: POST invariants
        self._check_invariants(InvariantPhase.POST)

        self._step_index += 1

    def get_variable_value(self, variable):
        """Lazy resolution - resolve only when needed"""
        if self.lazy_resolution and variable in self._dirty_variables:
            variable.resolve_conflict()
            self._dirty_variables.remove(variable)
        return variable.value
```

### Profiling and Monitoring

```python
import numpy as np
import cProfile
import pstats
from io import StringIO

from procela import Executive, InvariantPhase, Timer

class ProfiledExecutive(Executive):
    """Executive with built-in profiling"""

    def __init__(self, mechanisms, profile=False):
        super().__init__(mechanisms=mechanisms)
        self.profile = profile
        self.profiler = cProfile.Profile() if profile else None
        self.timings = {
            'mechanisms': [],
            'resolution': [],
            'governance': []
        }

    def run(self, steps=100):
        """Run with profiling"""
        if self.profile:
            self.profiler.enable()

        try:
            with Timer() as timer:
                super().run(steps)
        finally:
            elapsed = timer.elapsed

            if self.profile:
                self.profiler.disable()
                self._print_profile_stats()

            print(f"\nTotal execution time: {elapsed:.2f}s")

    def _print_profile_stats(self):
        """Print profiling statistics"""
        s = StringIO()
        ps = pstats.Stats(self.profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions
        print(s.getvalue())

    def _timed_execute(self, name, func):
        """Time execution of a function"""
        with Timer() as timer:
            result = func()
        self.timings[name].append(timer.elapsed)
        return result

    def step(self):
        """Step with timing"""
        # Time mechanisms
        self._timed_execute('mechanisms', self._execute_mechanisms)

        # Time resolution
        self._timed_execute('resolution', self._resolve_variables)

        # Time governance
        self._timed_execute('governance', lambda: self._check_invariants(InvariantPhase.POST))

        self.step_counter += 1

    def print_timing_report(self):
        """Print performance report"""
        print("\n=== Performance Report ===")
        for name, timings in self.timings.items():
            if timings:
                avg = np.mean(timings) * 1000  # ms
                total = np.sum(timings)
                print(f"{name:15s}: avg={avg:.2f}ms, total={total:.2f}s, calls={len(timings)}")
```

## Error Handling and Recovery

### Robust Executive with Recovery

```python
import time

from procela import Executive

class RobustExecutive(Executive):
    """Executive with error recovery mechanisms"""

    def __init__(self, mechanisms, max_retries=3):
        super().__init__(mechanisms=mechanisms)
        self.max_retries = max_retries
        self.error_log = []

    def step(self):
        """Execute step with retry logic"""
        retries = 0
        last_error = None

        while retries < self.max_retries:
            try:
                # Save checkpoint before step
                checkpoint = self.create_checkpoint()

                # Execute step
                super().step()

                # Success
                return

            except Exception as e:
                last_error = e
                retries += 1

                # Log error
                self.error_log.append({
                    'step': self.step_index(),
                    'error': str(e),
                    'retry': retries
                })

                # Restore checkpoint
                self.restore_checkpoint(checkpoint)

                print(f"⚠️ Error at step {self.step_index()}, retry {retries}/{self.max_retries}: {e}")

                # Exponential backoff
                time.sleep(0.1 * (2 ** retries))

        # Max retries exceeded
        raise RuntimeError(
            f"Failed to execute step {self.step_index()} after "
            f"{self.max_retries} retries"
        ) from last_error
```

## Practical Examples

### Example 1: Multi-Step Training Simulation

```python
from procela import Executive

class TrainingExecutive(Executive):
    """Executive for training simulations with phases"""

    def __init__(self, mechanisms, phase_durations):
        super().__init__(mechanisms=mechanisms)
        self.phase_durations = phase_durations
        self.current_phase = 0
        self.phase_results = []

    def run(self):
        """Run through training phases"""
        for phase, duration in enumerate(self.phase_durations):
            self.current_phase = phase
            print(f"\n=== Phase {phase + 1}/{len(self.phase_durations)} ===")

            # Configure for this phase
            self._configure_phase(phase)

            # Run phase
            super().run(steps=duration)

            # Record results
            self.phase_results.append({
                'phase': phase,
                'final_state': {var.name: var.value for var in self.variables()},
                'metrics': self._compute_metrics()
            })

            # Transition to next phase
            self._transition_phase(phase)

        return self.phase_results

    def _configure_phase(self, phase):
        """Configure executive for specific phase"""
        if phase == 0:
            # Exploration phase
            for mechanism in self.mechanisms():
                mechanism.exploration_rate = 0.5
        elif phase == 1:
            # Exploitation phase
            for mechanism in self.mechanisms():
                mechanism.exploration_rate = 0.1
```

### Example 2: Adaptive Executive

```python
import numpy as np

from procela import Executive, HighestConfidencePolicy, WeightedVotingPolicy

class AdaptiveExecutive(Executive):
    """Executive that adapts its behavior based on signals"""

    def __init__(self, mechanisms, performance_threshold=0.5):
        super().__init__(mechanisms=mechanisms)
        self.performance_threshold = performance_threshold
        self.performance_history = []

    def step(self):
        """Adaptive step execution"""
        # Normal execution
        super().step()

        # Monitor performance
        performance = self._compute_performance()
        self.performance_history.append(performance)

        # Adapt if performance drops
        if len(self.performance_history) > 10:
            recent_avg = np.mean(self.performance_history[-10:])

            if recent_avg < self.performance_threshold:
                self._adapt_execution()

    def _adapt_execution(self):
        """Adapt execution strategy"""
        print("⚠️ Performance below threshold, adapting...")

        # Option 1: Increase governance sensitivity
        for invariant in self._invariants:
            if hasattr(invariant, 'threshold'):
                invariant.threshold *= 0.9

        # Option 2: Activate backup mechanisms
        for mechanism in self.mechanisms():
            if hasattr(mechanism, 'backup_mode'):
                mechanism.backup_mode = True

        # Option 3: Change resolution policies
        for variable in self.variables():
            if isinstance(variable.policy, WeightedVotingPolicy):
                variable.policy = HighestConfidencePolicy()
```

## Best Practices

### 1. Use Random Number Generator with seeds for Reproducibility
```python
import random
import numpy as np

from procela import Executive

# Good
rng = np.random.default_rng(42)
# or
#rng = random.Random(42)

executive = Executive(mechanisms=mechanisms, rng=rng)

# Bad - non-deterministic
executive = Executive(mechanisms=mechanisms)
```

### 2. Monitor Performance
```python
# Track execution time for large simulations
from procela import Executive, Timer

executive = Executive(...)

with Timer() as timer:
    executive.run(steps=10000)

print(f"Execution time: {timer.elapsed:.2f}s")
```

## Next Steps

- Learn about [Variables](variables.md) that the Executive orchestrates
- Explore [Mechanisms](mechanisms.md) that the Executive executes
- Understand [Governance](governance.md) that the Executive triggers
- See the [API Reference](../api/reference.md) for complete Executive documentation
