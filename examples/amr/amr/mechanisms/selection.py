"""Selection family of mechanisms for Procela PoC."""

import numpy as np

from procela import Executive, Mechanism, RangeDomain, VariableRecord

from ..variables import (
    antibiotic_usage,
    baseline_colonized,
    colonized,
    intervention_code,
    predicted_colonized,
)
from .family import MechanismFamily


class SelectionMechanism(Mechanism):
    """
    Predicts colonization based on antibiotic selection pressure.

    Equation: C(t+1) = C(t) + θ * A(t) * bias * (1 - stewardship_effect)
    where stewardship_effect applies when intervention=3.

    Assumes
    -------
    - Existing colonized patients remain colonized
    - Each unit of antibiotic usage produces θ new colonizations
    - Antibiotic restriction reduces this effect

    References
    ----------
    - Lipsitch, M., & Samore, M. H. (2002). Antimicrobial use and antimicrobial
      resistance: a population perspective. Emerging Infectious Diseases, 8(4), 347.
    - Austin, D. J., Kristinsson, K. G., & Anderson, R. M. (1999). The relationship
      between the volume of antimicrobial consumption in human communities and the
      frequency of resistance. Proceedings of the National Academy of Sciences, 96(3),
      1152-1156.
    """

    def __init__(
        self,
        executive: Executive,
        theta: float = 0.05,
        confidence: float = 0.8,
        noise_scale: float = 0.5,
        bias: float = 1.0,
        stewardship_effect: float = 0.6,
        description: str = "Antibiotic selection mechanism",
        name: str = "Selection",
    ) -> None:
        """
        Mechanism selection constructor.

        Parameters
        ----------
        executive : Executive
            The executive.
        theta : float
            Theta parameters. Default is 0.05.
        confidence : float
            The confidence of the mechanism. Default is 0.8.
        noise_scale : float
            The noise scale. Default is 0.5.
        bias : float
            The bias. Default is 1.0.
        stewardship_effect : float
            The stewardship effect. Default is 0.6.
        description : str
            A description. Default is "Antibiotic selection mechanism".
        name : str
            The mechanism name. Default is "Selection".
        """
        super().__init__(
            reads=[colonized, antibiotic_usage, intervention_code],
            writes=[predicted_colonized, intervention_code, baseline_colonized],
        )
        self.executive = executive
        self.theta = theta
        self.base_confidence = confidence
        self.noise_scale = noise_scale
        self.bias = bias
        self.stewardship_effect = stewardship_effect
        self.description = description
        self.name = name

    def transform(self) -> None:
        """Transform method."""
        c_value, a_value, i_value = [var.value for var in self.reads()]

        if None in (c_value, a_value, i_value) or self.executive.rng is None:
            return

        if isinstance(self.executive.rng, np.random.Generator):
            noise = self.executive.rng.normal(0, self.noise_scale)
        else:
            noise = self.executive.rng.gauss(0, self.noise_scale)

        # Intervention effect
        effect_multiplier = 1.0
        if round(i_value) == 3:  # stewardship active
            effect_multiplier = 1.0 - self.stewardship_effect

        # Prediction WITH current intervention
        C_hat_with = (
            c_value + self.theta * a_value * self.bias * effect_multiplier + noise
        )

        # Counterfactual WITHOUT intervention
        C_hat_without = c_value + self.theta * a_value * self.bias + noise

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
                value=3.0,  # stewardship
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


class SelectionNoisyMechanism(SelectionMechanism):
    """Higher noise variant."""

    def __init__(self, executive: Executive) -> None:
        """
        Noisy selection mechanism constructor.

        Parameters
        ----------
        executive : Executive
            The executive.
        """
        super().__init__(
            executive,
            theta=0.05,
            confidence=0.8,
            noise_scale=1.5,
            bias=1.0,
            stewardship_effect=0.6,
            description="Selection mechanism with high noise",
            name="SelectionNoisy",
        )


class SelectionBiasedMechanism(SelectionMechanism):
    """Consistently overestimates antibiotic effect."""

    def __init__(self, executive: Executive) -> None:
        """
        Bias selection mechanism constructor.

        Parameters
        ----------
        executive : Executive
            The executive.
        """
        super().__init__(
            executive,
            theta=0.05,
            confidence=0.68,
            noise_scale=0.5,
            bias=1.4,  # Fixed overestimate bias
            stewardship_effect=0.6,
            description="Selection mechanism with overestimate bias (1.4)",
            name="SelectionBiased",
        )


class SelectionUnderestimateMechanism(SelectionMechanism):
    """Consistently underestimates antibiotic effect."""

    def __init__(self, executive: Executive) -> None:
        """
        Underestimate selection mechanism constructor.

        Parameters
        ----------
        executive : Executive
            The executive.
        """
        super().__init__(
            executive,
            theta=0.05,
            confidence=0.72,
            noise_scale=0.5,
            bias=0.6,  # Fixed underestimate bias
            stewardship_effect=0.6,
            description="Selection mechanism with underestimate bias (0.6)",
            name="SelectionUnderestimate",
        )


def create_selection_family(executive: Executive) -> MechanismFamily:
    """
    Create and populate the selection mechanism family.

    Parameters
    ----------
    executive : Executive
        The executive.

    Returns
    -------
    MechanismFamily
        The mechanism family.
    """
    family = MechanismFamily("selection", sigma=5.0, alpha=0.2)

    family.add(SelectionMechanism(executive=executive))
    family.add(SelectionNoisyMechanism(executive=executive))
    family.add(SelectionBiasedMechanism(executive=executive))
    family.add(SelectionUnderestimateMechanism(executive=executive))

    return family
