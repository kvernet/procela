"""Main simulation file."""

import argparse
from typing import Any

from amr import (
    create_cumulative_difference_figure,
    create_governance_stats_figure,
    create_mechanisms_contrib_figure,
    create_observable_figure,
    create_topology_figure,
    run_multiple_experiments,
)


def simulate(
    n_runs: int = 50, steps: int = 160, output_dir: str = "outputs/"
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Simulate the AMR case study."""
    results = {}
    df_stats = {}
    cumulatives = {}
    for governance in ["none", "fragility", "coverage", "probe", "all"]:
        print(f"Running {governance} governance for {args.r} events.")

        # Run multiple experiments for the governance
        results[governance], df_stats[governance], cumulatives[governance] = (
            run_multiple_experiments(
                governance=governance, n_runs=n_runs, steps=steps, output_dir=output_dir
            )
        )

    return results, df_stats, cumulatives


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procela PoC simulation.")

    parser.add_argument("-r", type=int, help="The number of runs.", default=50)

    parser.add_argument(
        "-s", type=int, help="The number of steps to execute.", default=160
    )

    parser.add_argument(
        "-o",
        type=str,
        help="The output directory to save the logs, dataframes and figures.",
        default="outputs/",
    )

    args = parser.parse_args()

    results, df_stats, cumulatives = simulate(args.r, args.s, args.o)

    # Create observable figure
    base_dir = f"{args.o}/figures/"
    create_observable_figure(df=results["none"][0]["dataframe"], base_dir=base_dir)

    # Create mechanisms contrib figure
    for result in results.values():
        create_mechanisms_contrib_figure(result=result[0], base_dir=base_dir)

    # Create governance stats figure
    create_governance_stats_figure(df_stats, base_dir=base_dir)

    # Create cumulative difference figure
    create_cumulative_difference_figure(cumulatives=cumulatives, base_dir=base_dir)

    # Create topology figure
    create_topology_figure(results=results, base_dir=base_dir)

    print("\n\nSimulation time elapsed for 1st run")
    for gov, result in results.items():
        print(result[0]["governance"], result[0]["elapsed"])
