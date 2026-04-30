"""Family registry for Procela PoC."""

from collections import deque
from typing import Deque

import numpy as np

from procela import RangeDomain, Variable, VariableRecord

from ..variables import intervention_code
from .family import MechanismFamily


class FamilyRegistry:
    """Family registry."""

    def __init__(self, window: int = 5) -> None:
        """
        Family registry constructor.

        Parameters
        ----------
        window : int
            The window size to compute policy fragility. Default is 5.
        """
        self.window = window
        self.fragility_history: Deque[float] = deque(maxlen=window)
        self.families: dict[str, MechanismFamily] = {}

        # Governance variables
        self.policy_fragility = Variable(
            name="policy_fragility",
            domain=RangeDomain(0.0, 1.0),
            description="Disagreement on intervention policy",
            units="fragility",
            policy=None,
        )

    def register(self, family: MechanismFamily) -> None:
        """
        Register a family with the registry.

        Parameters
        ----------
        family : MechanismFamily
            The mechanism family to register.
        """
        self.families[family.name] = family

    def unregister(self, family_name: str) -> None:
        """
        Remove a family from registry.

        Parameters
        ----------
        family_name : str
            The family name to unregister.
        """
        if family_name in self.families:
            del self.families[family_name]

    def compute_metrics(self) -> None:
        """Compute the metrics."""
        for family in self.families.values():
            family.compute_coverage()

        self.compute_policy_fragility()

    def compute_policy_fragility(self) -> None:
        """Compute the policy fragility."""
        # Get current hypotheses for intervention_code
        if intervention_code.memory is None:
            return None
        hypotheses, _, _, _ = intervention_code.memory.latest()

        values = [
            h.record.value
            for h in hypotheses
            if h.record and h.record.value is not None
        ]

        if len(values) < 2:
            fragility = 0.0
        else:
            # Normalized range
            fragility = (max(values) - min(values)) / 3.0

        self.fragility_history.append(fragility)
        smoothed = np.mean(self.fragility_history)

        self.policy_fragility.set(
            VariableRecord(
                value=smoothed,
                confidence=0.99,
            )
        )
