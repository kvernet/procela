"""Cumulative difference for Procela PoC."""

import numpy as np

from ..variables import error_baseline_colonized, error_colonized


def compute_cumulative_difference() -> np.ndarray | None:
    """
    Compute cumulative difference over entire simulation.

    cumulative = sum(|counterfactual_error| - |actual_error|)
    where counterfactual_error is what error WOULD HAVE BEEN
    with optimal intervention.
    """
    if error_colonized.memory is None or error_baseline_colonized.memory is None:
        return None

    count = error_colonized.stats.count
    difference = np.zeros(count)
    cumulative = np.zeros(count)
    for step, (err, errb) in enumerate(
        zip(error_colonized.memory.iter(), error_baseline_colonized.memory.iter())
    ):
        if (
            err[1] is None
            or err[1].value is None
            or errb[1] is None
            or errb[1].value is None
        ):
            continue

        actual_error = err[1].value
        counterfactual_error = errb[1].value

        # Difference for this step
        step_difference = counterfactual_error - actual_error
        difference[step] = step_difference

        # Cumulative difference
        cumulative[step] = cumulative[step - 1] + step_difference

    return cumulative
