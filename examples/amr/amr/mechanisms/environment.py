"""Environmental family of mechanisms for Procela PoC."""

import numpy as np

from procela import Executive, Mechanism, RangeDomain, VariableRecord

from ..variables import (
    baseline_colonized,
    colonized,
    environmental_load,
    intervention_code,
    predicted_colonized,
)
from .family import MechanismFamily


class EnvironmentalMechanism(Mechanism):
    """
    Predicts colonization based on environmental reservoir.

    Equation: C(t+1) = C(t) + θ * E(t) * bias * (1 - cleaning_effect)
    where cleaning_effect applies when intervention=2.

    Assumes:
    - Existing colonized patients remain colonized
    - New colonizations proportional to environmental load
    - Cleaning reduces environmental contribution
    """

    def __init__(
        self,
        executive: Executive,
        theta: float = 0.08,
        confidence: float = 0.8,
        noise_scale: float = 0.5,
        bias: float = 1.0,
        cleaning_effect: float = 0.5,
        description: str = "Environmental transmission mechanism",
        name: str = "Environmental",
    ) -> None:
        """Environmental mechanism constructor."""
        super().__init__(
            reads=[colonized, environmental_load, intervention_code],
            writes=[predicted_colonized, intervention_code, baseline_colonized],
        )
        self.executive = executive
        self.theta = theta
        self.base_confidence = confidence
        self.noise_scale = noise_scale
        self.bias = bias
        self.cleaning_effect = cleaning_effect
        self.description = description
        self.name = name

    def transform(self) -> None:
        """Transform method."""
        c_value, e_vale, i_value = [var.value for var in self.reads()]

        if None in (c_value, e_vale, i_value) or self.executive.rng is None:
            return

        if isinstance(self.executive.rng, np.random.Generator):
            noise = self.executive.rng.normal(0, self.noise_scale)
        else:
            noise = self.executive.rng.gauss(0, self.noise_scale)

        # Intervention effect
        effect_multiplier = 1.0
        if round(i_value) == 2:  # cleaning active
            effect_multiplier = 1.0 - self.cleaning_effect

        # Prediction WITH current intervention
        C_hat_with = (
            c_value + self.theta * e_vale * self.bias * effect_multiplier + noise
        )

        # Counterfactual WITHOUT intervention
        C_hat_without = c_value + self.theta * e_vale * self.bias + noise

        # Clip
        C_domain = self.reads()[0].domain
        if isinstance(C_domain, RangeDomain):
            min_value = C_domain.min_value
            max_value = C_domain.max_value
            C_hat_with = np.clip(C_hat_with, min_value, max_value)
            C_hat_without = np.clip(C_hat_without, min_value, max_value)

        # Add hypotheses
        self.writes()[0].add_hypothesis(
            VariableRecord(
                value=C_hat_with, confidence=self.base_confidence, source=self.key()
            )
        )

        self.writes()[1].add_hypothesis(
            VariableRecord(
                value=2.0,  # cleaning
                confidence=self.base_confidence,
                source=self.key(),
            )
        )

        self.writes()[2].add_hypothesis(
            VariableRecord(
                value=C_hat_without,
                confidence=self.base_confidence * 0.9,
                source=self.key(),
            )
        )


class EnvironmentalNoisyMechanism(EnvironmentalMechanism):
    """Environmental noisy mechanism."""

    def __init__(self, executive: Executive) -> None:
        """Environmental noisy mechanism constructor."""
        super().__init__(
            executive,
            theta=0.08,
            confidence=0.64,
            noise_scale=1.0,
            bias=1.0,  # No bias, just noise
            cleaning_effect=0.5,
            description="Environmental mechanism with high noise",
            name="EnvironmentalNoisy",
        )


class EnvironmentalLaggedMechanism(EnvironmentalMechanism):
    """Environmental lagged mechanism."""

    def __init__(self, executive: Executive) -> None:
        """Environmental lagged mechanism constructor."""
        super().__init__(
            executive,
            theta=0.08,
            confidence=0.68,
            noise_scale=0.5,
            bias=0.7,  # ← Lag = under-response bias
            cleaning_effect=0.5,
            description="Environmental mechanism with lag (bias=0.7)",
            name="EnvironmentalLagged",
        )


class EnvironmentalOverestimateMechanism(EnvironmentalMechanism):
    """Environmental overestimate mechanism."""

    def __init__(self, executive: Executive) -> None:
        """Environmental overestimate mechanism constructor."""
        super().__init__(
            executive,
            theta=0.08,
            confidence=0.72,
            noise_scale=0.5,
            bias=1.3,  # ← Overestimate bias
            cleaning_effect=0.5,
            description="Environmental mechanism with overestimate bias",
            name="EnvironmentalOverestimate",
        )


def create_environment_family(executive: Executive) -> MechanismFamily:
    """Create and populate the environmental mechanism family."""
    family = MechanismFamily("environmental", sigma=5.0, alpha=0.2)

    family.add(EnvironmentalMechanism(executive=executive))
    family.add(EnvironmentalNoisyMechanism(executive=executive))
    family.add(EnvironmentalLaggedMechanism(executive=executive))
    family.add(EnvironmentalOverestimateMechanism(executive=executive))

    return family
