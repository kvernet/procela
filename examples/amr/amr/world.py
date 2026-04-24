"""
Ground truth AMR environment with regime shifts.

0 - 60     selection pressure dominates
61 - 110   environmental contamination event
111 - 160  contact transmission dominates
"""

import numpy as np

from procela import RangeDomain, VariableRecord

from .variables import antibiotic_usage, colonized, environmental_load, regime


class AMRWorld:
    """
    Ground truth AMR environment.

    Generates observations for colonization (C),
    antibiotic usage (A), and environmental load (E).
    """

    def __init__(self, seed: int = 42) -> None:
        """
        AMR World constructor.

        Parameters
        ----------
        seed : int
            The random seed for reproducibility. Default is 42.
        """
        self.rng = np.random.default_rng(seed)

        # transmission coefficients
        self.alpha = 0.05  # antibiotic selection
        self.beta = 0.08  # environmental transmission
        self.gamma = 0.03  # contact transmission

        # clearance
        self.delta = 0.02

        # noise scale
        self.noise = 0.25

    def _regime(self, step: int) -> str:
        """
        Regime at the current step.

        Parameters
        ----------
        step : int
            The current simulation step.

        Returns
        -------
        str
            The regime to that step.
        """
        if step <= 60:
            return "selection"
        elif step <= 110:
            return "environment"
        else:
            return "contact"

    def update_environment(self) -> None:
        """
        Update antibiotic usage and environmental load.

        These evolve slowly with noise.
        """
        A_val = max(0.0, antibiotic_usage.value + self.rng.normal(0, 1.1))
        E_val = max(0.0, environmental_load.value + self.rng.normal(0, 2.0))

        antibiotic_usage.set(VariableRecord(value=A_val, confidence=0.99))
        environmental_load.set(VariableRecord(value=E_val, confidence=0.99))

    def step(self, step: int) -> None:
        """
        Generate next colonization observation.

        Parameters
        ----------
        step : int
            The current simulation step.
        """
        self.update_environment()

        C_t = colonized.value
        A_t = antibiotic_usage.value
        E_t = environmental_load.value

        regime_name = self._regime(step)
        regime_dict = {"selection": 0, "environment": 1, "contact": 2}
        regime.set(VariableRecord(value=regime_dict[regime_name], confidence=0.99))

        if regime_name == "selection":
            lam = self.alpha * A_t

        elif regime_name == "environment":
            lam = self.beta * E_t

        else:  # contact
            lam = self.gamma * C_t

        noise = self.rng.normal(0, self.noise)

        C_next = C_t + lam - self.delta * C_t + noise

        # clamp to domain
        domain = colonized.domain
        if isinstance(domain, RangeDomain):
            C_next = np.clip(C_next, domain.min_value, domain.max_value)

        colonized.set(VariableRecord(value=C_next, confidence=0.99))
