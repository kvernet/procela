"""Hook events for Procela PoC."""

from typing import Callable

from procela import Executive, Variable, VariableRecord

from ..mechanisms.registry import FamilyRegistry
from ..variables import (
    baseline_colonized,
    colonized,
    error_baseline_colonized,
    error_colonized,
    predicted_colonized,
    regime,
)
from ..world import AMRWorld


def compute_error(variable: Variable) -> float:
    """
    Compute prediction error.

    Parameters
    ----------
    variable : Variable
        The variable to compute the prediction error.

    Returns
    -------
    float
        The prediction error.
    """
    # Get previous step's resolved conclusion
    result = variable.get(start=-2, size=1)

    if result:
        _, conclusion, _ = result[0]

        if conclusion:
            # Current observed value
            observed = colonized.value
            # Resolved value
            predicted = conclusion.value

            if observed is not None and predicted is not None:
                return float(abs(predicted - observed))

    if colonized.value:
        if regime.value == 0:  # selection
            return float(colonized.value / (1 - 0.6))  # stewardship effectiveness
        elif regime.value == 1:  # environmental
            return float(colonized.value / (1 - 0.5))  # cleaning effectiveness
        else:  # contact
            return float(colonized.value / (1 - 0.3))  # isolation effectiveness

    return 0.0


def create_pre_step(world: AMRWorld) -> Callable[[Executive, int], None]:
    """
    Create pre_step.

    Parameters
    ----------
    world : AMRWorld
        The hidden AMR world.

    Returns
    -------
    Callable[[Executive, int], None]
        The pre step event or None.
    """

    def pre_step(executive: Executive, step: int) -> None:
        if step == 0:
            return
        world.step(step)

    return pre_step


def create_post_step(registry: FamilyRegistry) -> Callable[[Executive, int], None]:
    """
    Create post_step.

    Parameters
    ----------
    registry: FamilyRegistry
        The family registry.

    Returns
    -------
    Callable[[Executive, int], None]
        The post step event or None.
    """

    def post_step(executive: Executive, step: int) -> None:
        if step > 0:
            # Predicted colonized error
            error = compute_error(predicted_colonized)
            error_colonized.set(VariableRecord(value=error, confidence=0.99))

            # Baseline colonized error
            error = compute_error(baseline_colonized)
            error_baseline_colonized.set(VariableRecord(value=error, confidence=0.99))

        registry.compute_metrics()

    return post_step
