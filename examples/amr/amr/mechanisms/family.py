"""Mechanism family for Procela PoC."""

import numpy as np

from procela import Key, KeyAuthority, Mechanism, RangeDomain, Variable, VariableRecord

from ..variables import colonized, predicted_colonized


class MechanismFamily:
    """Group of mechanisms sharing an ontology."""

    def __init__(self, name: str, sigma: float = 5.0, alpha: float = 0.2) -> None:
        """Mechanism family constructor."""
        self.name = name
        self.sigma = sigma
        self.alpha = alpha

        self.mechanisms: list[Mechanism] = []
        self.mechanism_keys: list[Key] = []

        # Coverage variable for this family
        self.coverage = Variable(
            name=f"{self.name}_coverage",
            domain=RangeDomain(0.0, 1.0),
            description=f"Rolling prediction accuracy for {self.name} family",
            policy=None,
        )
        self.smoothed_coverage = None

        self._key = KeyAuthority.issue(self)

    def key(self) -> Key:
        """Return a unique key of the mechanism family."""
        return self._key

    def add(self, mech: Mechanism) -> None:
        """Add a mechanism."""
        if mech not in self.mechanisms:
            self.mechanisms.append(mech)
            self.mechanism_keys.append(mech.key())

    def disable(self) -> None:
        """Disable all mechanisms in this family."""
        for mech in self.mechanisms:
            mech.disable()

    def enable(self) -> None:
        """Enable all mechanisms in this family."""
        for mech in self.mechanisms:
            mech.enable()

    def compute_coverage(self) -> None:
        """Compute coverage based on predictions from previous step."""
        prev_hypotheses_list = predicted_colonized.get(start=-2, size=1, reverse=False)

        if not prev_hypotheses_list:
            return

        prev_hypotheses, _, _ = prev_hypotheses_list[0]

        # Current observed value
        observed = colonized.value
        if observed is None:
            return

        coverages = []
        for mech_key in self.mechanism_keys:
            # Find this mechanism's prediction from previous step
            mech_hyp = next(
                (
                    h
                    for h in prev_hypotheses
                    if h.record and h.record.source == mech_key
                ),
                None,
            )
            if (
                mech_hyp
                and mech_hyp.record is not None
                and mech_hyp.record.value is not None
            ):
                error = abs(mech_hyp.record.value - observed)
                coverage = np.exp(-error / self.sigma)
                coverages.append(coverage)
            else:
                coverages.append(0.0)  # No prediction = zero coverage

        current_coverage = np.mean(coverages)
        if self.smoothed_coverage is None:
            self.smoothed_coverage = current_coverage
        else:
            self.smoothed_coverage = (
                self.alpha * current_coverage
                + (1 - self.alpha) * self.smoothed_coverage
            )

        self.coverage.set(
            VariableRecord(
                value=self.smoothed_coverage, confidence=0.99, source=self._key
            )
        )
