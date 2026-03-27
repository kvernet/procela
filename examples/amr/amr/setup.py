"""Setup for Procela PoC."""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from tqdm import tqdm

from procela import Executive, Timer, setup_logging

from .governance.hooks import create_post_step, create_pre_step
from .governance.invariants.coverage import CoverageDecayInvariant
from .governance.invariants.emergency import NoActiveFamiliesInvariant
from .governance.invariants.fragility import PolicyFragilityInvariant
from .governance.invariants.structural import StructuralProbeInvariant
from .mechanisms.contact import create_contact_family
from .mechanisms.environment import create_environment_family
from .mechanisms.registry import FamilyRegistry
from .mechanisms.selection import create_selection_family
from .memory import MemoryVisualizer
from .variables import (
    ALL_VARIABLES,
    error_colonized,
    init_variables,
    reset_variables,
)
from .viz.cumulative import compute_cumulative_difference
from .viz.plot import create_governance_response_figure
from .world import AMRWorld


def create_simulation(
    governance: str = "none",
    seed: int = 42,
    output_dir: str | Path = "outputs/",
) -> tuple[Executive, FamilyRegistry, AMRWorld]:
    """
    Create a simulation with specified governance strategy.

    Parameters
    ----------
    governance : str
        The governance strategy:
        "none", "fragility", "coverage", "probe", or "all". Default is "none".
    seed : int
        The random seed. Default is 42.
    """
    logger = setup_logging(
        console=False,
        name="Procela PoC",
        log_file=f"{output_dir}/logs/procela_{governance}_{seed}.log",
        json_file=f"{output_dir}/logs/procela_{governance}_{seed}.jsonl",
    )
    # Initialize executive
    executive = Executive(logger=logger)
    executive.set_rng(np.random.default_rng(seed))

    # Reset variables
    reset_variables()

    # Initialize variables
    init_variables()

    # Create ground truth (hidden)
    world = AMRWorld()

    # Create ontology families
    contactFamily = create_contact_family(executive=executive)
    environmentFamily = create_environment_family(executive=executive)
    selectionFamily = create_selection_family(executive=executive)

    # Add all family mechanisms
    for mech in contactFamily.mechanisms:
        executive.add_mechanism(mech)
    for mech in environmentFamily.mechanisms:
        executive.add_mechanism(mech)
    for mech in selectionFamily.mechanisms:
        executive.add_mechanism(mech)

    # Create family registry (useful for governance)
    registry = FamilyRegistry()
    registry.register(contactFamily)
    registry.register(environmentFamily)
    registry.register(selectionFamily)

    # Add governance invariants based on strategy
    if governance == "fragility" or governance == "all":
        executive.add_invariant(
            PolicyFragilityInvariant(
                executive=executive,
                registry=registry,
                fragility_threshold=0.6,
                error_threshold=1.0,
                experiment_duration=10,
                evaluation_window=10,
            )
        )

    if governance == "coverage" or governance == "all":
        executive.add_invariant(
            CoverageDecayInvariant(
                executive=executive,
                registry=registry,
                coverage_threshold=0.85,
                decay_duration=3,
                experiment_duration=10,
                evaluation_window=10,
            )
        )

    if governance == "probe" or governance == "all":
        executive.add_invariant(
            StructuralProbeInvariant(
                executive=executive,
                registry=registry,
                probe_interval=25,
                probe_duration=20,
            )
        )

    executive.add_invariant(
        NoActiveFamiliesInvariant(
            executive=executive,
            registry=registry,
        )
    )

    return executive, registry, world


def run_experiment(
    governance: str = "none",
    steps: int = 160,
    seed: int = 42,
    output_dir: str | Path = "outputs/",
) -> dict[str, Any]:
    """Run a single experiment with given governance strategy."""
    with Timer() as timer:
        executive, registry, world = create_simulation(
            governance=governance,
            seed=seed,
            output_dir=output_dir,
        )

        pre_step = create_pre_step(world=world)
        post_step = create_post_step(registry=registry)
        executive.run(steps=steps, pre_step=pre_step, post_step=post_step)

    # Get statistical result
    result = error_colonized.stats.result()

    mean_error = result.mean
    std_error = result.std

    other_vars = []
    for family in registry.families.values():
        other_vars.append(family.coverage)
    other_vars.append(registry.policy_fragility)

    df = MemoryVisualizer(ALL_VARIABLES + other_vars).to_dataframe()

    # Save the dataframe for analysis and viz
    # path = Path(output_dir)
    # path.mkdir(parents=True, exist_ok=True)
    # file_name = f"governance_{governance}_seed_{seed}.parquet"
    # df.to_parquet(f"{path}/{file_name}")

    return {
        "governance": governance,
        "mean_error": mean_error,
        "std_error": std_error,
        "executive": executive,
        "registry": registry,
        "dataframe": df,
        "elapsed": timer.elapsed,
    }


def run_multiple_experiments(
    governance: str = "none",
    n_runs: int = 10,
    steps: int = 160,
    output_dir: str | Path = "outputs/",
) -> tuple[list[dict[str, Any]], pd.DataFrame, list[np.ndarray | None]]:
    """Run multiple experiments with different random seeds."""
    results = []
    error = []
    cumulatives = []

    for seed in tqdm(range(n_runs)):
        result = run_experiment(
            governance=governance,
            steps=steps,
            seed=seed,
            output_dir=output_dir,
        )
        results.append(result)
        error.append(
            {
                "seed": seed,
                "mean_error": result["mean_error"],
                "std_error": result["std_error"],
            }
        )
        cumulatives.append(compute_cumulative_difference())

        # Create governance response figure
        if seed == 0:
            create_governance_response_figure(
                result=result, base_dir=f"{output_dir}/figures/"
            )

    return results, pd.DataFrame(error), cumulatives
