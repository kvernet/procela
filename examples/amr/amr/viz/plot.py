"""Plot for Procela PoC."""

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from procela import Executive

from ..mechanisms.registry import FamilyRegistry
from ..variables import (
    error_colonized,
    experiment_status,
    predicted_colonized,
    regime,
)

plt.style.use("share/style.mplstyle")


def get_true_regime() -> list:
    """Get the true regime."""
    if regime.memory is None:
        return []
    true_regime = [r.value for _, r, _ in regime.memory.iter() if r is not None]
    true_regime.reverse()
    return true_regime


def _add_regime_background(
    ax: plt.Figure,
    steps: list[float],
    y_min: float | None = None,
    y_max: float | None = None,
) -> None:
    """Add regime background."""
    # Add regime background
    colors = ["red", "green", "blue"]
    regime_names = ["Selection", "Environmental", "Contact"]

    y_min = y_min or ax.get_ylim()[0]
    y_max = y_max or ax.get_ylim()[1]
    for regime_val in [0, 1, 2]:
        mask = [r == regime_val for r in get_true_regime()][: len(steps)]
        if any(mask):
            ax.fill_between(
                steps,
                y_min,
                y_max,
                where=mask,
                color=colors[regime_val],
                alpha=0.2,
                label=regime_names[regime_val],
            )


def _add_experiment_overlays(axes: list[plt.Figure]) -> None:
    """Add experiment overlays."""
    # Add experiment overlays
    if experiment_status.memory:
        for _, r, _ in experiment_status.memory.iter():
            if r is None:
                continue
            data = r.metadata
            color = "green" if data["success"] else "red"
            for ax in axes:
                ax.axvspan(data["start"], data["end"], alpha=0.3, color=color)


def create_observable_figure(
    df: pd.DataFrame,
    base_dir: str | Path,
) -> None:
    """Create figure of observables."""
    save_path = Path(base_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    for name in ["colonized", "antibiotic_usage", "environmental_load", "regime"]:
        _, ax = plt.subplots()
        steps = df[df.name == name].step
        values = df[df.name == name].value
        ax.plot(steps, values)
        ax.set_xlabel("Time step")
        ax.set_ylabel(name.capitalize().replace("_", " "))

        # Create regime background
        _add_regime_background(ax=ax, steps=steps, y_max=max(values) * 1.1)
        ax.legend()

        plt.savefig(f"{save_path}/{name}.png")
        plt.close()


def create_mechanisms_contrib_figure(
    result: dict[str, Any],
    base_dir: str | Path,
) -> None:
    """Create mechanisms contrib figure."""
    save_path = Path(base_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    governance = result["governance"]
    executive: Executive = result["executive"]
    registry: FamilyRegistry = result["registry"]
    df: pd.DataFrame = result["dataframe"]

    # Mechanisms contribution
    plt.figure()
    for mech in executive.mechanisms():
        col_name = f"mech_{mech.name}_avg_val"
        db = df[df.name == "predicted_colonized"][[col_name, "step"]].dropna()

        plt.plot(db["step"], db[col_name], "--", label=mech.name)

    plt.plot(
        df[df.name == "predicted_colonized"].step,
        df[df.name == "predicted_colonized"].value,
        label="Predicted",
    )
    plt.plot(
        df[df.name == "colonized"].step,
        df[df.name == "colonized"].value,
        label="Observed",
    )

    # plt.title(f"Governance strategy {governance}")
    plt.xlabel("Time step")
    plt.ylabel("Patients")

    plt.legend()
    plt.savefig(f"{save_path}/mech_contrib_gov_{governance}.png")
    plt.close()

    # Metrics
    _, axes = plt.subplots(nrows=2, ncols=2, sharex=True)
    steps = df[df.name == "intervention_code"].step
    values = df[df.name == "intervention_code"].value
    axes[0, 0].plot(steps, values)
    axes[0, 0].set_ylabel("Intervention code")
    # Create regime background
    _add_regime_background(ax=axes[0, 0], steps=steps, y_max=max(values) * 1.1)
    axes[0, 0].legend()

    steps = df[df.name == "error_colonized"].step
    values = df[df.name == "error_colonized"].value
    axes[0, 1].plot(steps, values)
    axes[0, 1].set_ylabel("Error colonized")
    # Create regime background
    _add_regime_background(ax=axes[0, 1], steps=steps, y_max=max(values) * 1.1)
    axes[0, 1].legend()

    for family in registry.families.values():
        col_name = family.coverage.name
        steps = df[df.name == col_name].step
        values = df[df.name == col_name].value
        axes[1, 0].plot(steps, values, label=col_name[: len(col_name) - 9].title())
    axes[1, 0].set_xlabel("Time step")
    axes[1, 0].set_ylabel("Coverage")
    # Create regime background
    _add_regime_background(ax=axes[1, 0], steps=steps)
    axes[1, 0].legend()

    steps = df[df.name == "policy_fragility"].step
    values = df[df.name == "policy_fragility"].value
    axes[1, 1].plot(steps, values)
    axes[1, 1].set_xlabel("Time step")
    axes[1, 1].set_ylabel("Policy fragility")
    # Create regime background
    _add_regime_background(ax=axes[1, 1], steps=steps)
    axes[1, 1].legend()

    plt.savefig(f"{save_path}/metrics_gov_{governance}.png")
    plt.close()

    # Coverage
    _, ax = plt.subplots()
    for family in registry.families.values():
        col_name = family.coverage.name
        steps = df[df.name == col_name].step
        values = df[df.name == col_name].value
        ax.plot(steps, values, label=col_name[: len(col_name) - 9].title())
    ax.set_xlabel("Time step")
    ax.set_ylabel("Coverage")
    # Create regime background
    _add_regime_background(ax=ax, steps=steps)
    ax.legend()
    plt.savefig(f"{save_path}/coverage_{governance}.png")
    plt.close()


def create_governance_stats_figure(
    results: dict[str, Any],
    base_dir: str | Path,
) -> None:
    """Create governance stats figure."""
    save_path = Path(base_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    df = results["none"]
    mm_none = float(df["mean_error"].mean())
    sm_none = float(df["std_error"].mean())

    names: list[str] = []
    means: tuple[list[float], list[float]] = [], []
    stds: tuple[list[float], list[float]] = [], []
    for governance, df in results.items():
        mm = float(df["mean_error"].mean())
        me = float(df["mean_error"].std())

        sm = float(df["std_error"].mean())
        se = float(df["std_error"].std())

        mm_improv = "-"
        sm_improv = "-"
        if governance != "none":
            mm_improv = f"{(mm_none - mm) / mm_none:.3%}"

            sm_improv = f"{(sm_none - sm) / sm_none:.3%}"

        print(f"\n{governance} governance:")
        print(f"  Mean error: {mm:.3f} ± {me:.3f} (improvement: {mm_improv})")
        print(f"  Std dev:    {sm:.3f} ± {se:.3f} (improvement: {sm_improv})")

        names.append(governance)
        means[0].append(mm)
        means[1].append(me)

        stds[0].append(sm)
        stds[1].append(se)

    _, axes = plt.subplots(2, 1)
    axes[0].errorbar(
        names,
        means[0],
        yerr=means[1],
        fmt="o",  # marker style
        color="blue",  # marker/line color
        ecolor="red",  # error bar color
        elinewidth=2,  # error bar line width
        capsize=5,  # size of error bar caps
        capthick=2,  # thickness of caps
    )
    axes[0].set_ylabel("Mean error")

    axes[1].errorbar(
        names,
        stds[0],
        yerr=stds[1],
        fmt="o",  # marker style
        color="green",  # marker/line color
        ecolor="red",  # error bar color
        elinewidth=2,  # error bar line width
        capsize=5,  # size of error bar caps
        capthick=2,  # thickness of caps
    )
    axes[1].set_xlabel("Governance")
    axes[1].set_ylabel("Std error")

    # Save figure
    plt.savefig(f"{save_path}/governance_stats.png")
    plt.close()


def create_governance_response_figure(
    result: dict[str, Any],
    base_dir: str | Path,
) -> plt.Figure | None:
    """Create governance response figure under regime shifts."""
    save_path = Path(base_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    governance: FamilyRegistry = result["governance"]
    registry: FamilyRegistry = result["registry"]

    steps, errors = [], []
    confidences: dict[str, list[float]] = {
        name: [] for name in registry.families.keys()
    }

    if error_colonized.memory is None or predicted_colonized.memory is None:
        return None

    for step, (err, pred) in enumerate(
        zip(
            error_colonized.memory.iter(),
            predicted_colonized.memory.iter(),
        )
    ):
        steps.append(step)
        errors.append(err[1].value if err[1] is not None else float("inf"))

        total_conf = 0.0
        family_conf = {name: 0.0 for name in registry.families.keys()}

        hypotheses = pred[0]
        if hypotheses:
            for h in hypotheses:
                for name, f in registry.families.items():
                    if (
                        h.record
                        and h.record.confidence
                        and h.record.source in f.mechanism_keys
                    ):
                        family_conf[name] += h.record.confidence
                        total_conf += h.record.confidence

        for name in registry.families:
            if total_conf > 0:
                confidences[name].append(family_conf[name] / total_conf)
            else:
                confidences[name].append(0)

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    # Create regime background
    # _add_regime_background(
    #    ax=ax1, steps=steps,
    #    y_max=max(errors)*1.1
    # )

    ax1.plot(steps, errors, "k-", linewidth=1, label="Prediction error")
    ax1.set_ylabel("Absolute error")
    ax1.set_ylim(0, max(errors) * 1.1)
    ax1.legend(loc="upper right")
    # ax1.set_title('(a) Prediction error with regime shifts')

    # Bottom plot: Family dominance
    for name, values in confidences.items():
        ax2.plot(steps, values, linewidth=2, label=name.capitalize())

    ax2.set_xlabel("Time step")
    ax2.set_ylabel("Confidence share")
    ax2.set_ylim(0, 1)
    ax2.legend(loc="upper right")
    # ax2.set_title('(b) Ontology family dominance')

    # Add experiment overlays
    _add_experiment_overlays(axes=[ax1, ax2])

    # Save figure
    plt.savefig(f"{save_path}/governance_response_gov_{governance}.png")
    plt.close()

    return fig


def create_cumulative_difference_figure(
    cumulatives: dict[str, np.ndarray],
    base_dir: str | Path,
) -> plt.Figure:
    """Create cumulative difference comparison figure."""
    save_path = Path(base_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots()

    final_difference = {}
    # Plot cumulative curves
    for name, cumulative in cumulatives.items():
        cumulative = np.array(cumulative)
        steps = np.arange(cumulative.shape[1])
        cumulative_mean = np.mean(cumulative, axis=0)
        cumulative_std = np.std(cumulative, axis=0)
        ax.plot(steps[:-1], cumulative_mean[:-1], "-", linewidth=2, label=f"{name}")

        # Add confidence bands (±1 std)
        ax.fill_between(
            steps,
            cumulative_mean - cumulative_std,
            cumulative_mean + cumulative_std,
            alpha=0.25,
        )

        final_difference[name] = float(cumulative_mean[:-1][-1])

    print("\nFinal diff")
    diff_none = final_difference["none"]
    for governance, diff in final_difference.items():
        if governance != "none":
            improvement = (
                (diff - diff_none) / diff_none * 100 if diff_none != 0 else 0.0
            )
            print(f"\n{governance} governance:")
            print(f"  Improvement: {improvement:.1f}")

    # Add regime
    ylim = ax.get_ylim()
    _add_regime_background(ax=ax, steps=steps, y_max=ylim[1])

    # Labels and title
    ax.set_xlabel("Time step", fontsize=12)
    ax.set_ylabel("Cumulative difference", fontsize=12)

    # Legend
    ax.legend(loc="upper left", fontsize=10)

    # Grid for readability
    ax.grid(True, alpha=0.3)

    plt.savefig(f"{save_path}/cumulative_difference.png")
    plt.close()

    return fig


def create_topology_figure(
    results: dict[str, Any],
    base_dir: str | Path,
) -> None:
    """Create topology figure."""
    save_path = Path(base_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    _, ax = plt.subplots()

    for name, values in results.items():
        df = values[0]["dataframe"]

        db = df[df.name == "predicted_colonized"][
            ["unique_mechanisms", "step"]
        ].dropna()

        plt.plot(db["step"], db["unique_mechanisms"], "-", label=name)

        plt.legend()

    # _add_regime_background(ax, db["step"], y_max=None)

    plt.xlabel("Time step")
    plt.ylabel("Active mechanisms")

    plt.savefig(f"{save_path}/topology_evolution.png")
