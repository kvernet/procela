"""Contact family of mechanisms for Procela PoC."""

import numpy as np

from procela import Executive, Mechanism, RangeDomain, VariableRecord

from ..variables import (
    baseline_colonized,
    colonized,
    intervention_code,
    predicted_colonized,
)
from .family import MechanismFamily


class ContactMechanism(Mechanism):
    """Predicts colonization based on patient contact transmission."""

    def __init__(
        self,
        executive: Executive,
        theta: float = 0.03,
        confidence: float = 0.8,
        bias: float = 1.0,
        noise_scale: float = 0.5,
        isolation_effect: float = 0.3,
        description: str = "Contact transmission mechanism",
        name: str = "Contact",
    ) -> None:
        """
        Contact mechanism constructor.

        Parameters
        ----------
        executive : Executive
            The executive.
        theta : float
            Theta parameters. Default is 0.03.
        confidence : float
            The confidence of the mechanism. Default is 0.8.
        bias : float
            The bias. Default is 1.0.
        noise_scale : float
            The noise scale. Default is 0.5.
        isolation_effect : float
            The isolation effect. Default is 0.3.
        description : str
            A description. Default is "Contact transmission mechanism".
        name : str
            The mechanism name. Default is "Contact".
        """
        super().__init__(
            reads=[colonized, intervention_code],
            writes=[predicted_colonized, intervention_code, baseline_colonized],
        )
        self.executive = executive
        self.theta = theta
        self.base_confidence = confidence
        self.bias = bias
        self.noise_scale = noise_scale
        self.isolation_effect = isolation_effect
        self.description = description
        self.name = name

        # For adaptive tracking (optional)
        self.theta_history: list[float] = []
        self.learning_rate = 0.001

    def transform(self) -> None:
        """Transform method."""
        c_value, i_value = [var.value for var in self.reads()]

        if c_value is None or i_value is None or self.executive.rng is None:
            return

        if isinstance(self.executive.rng, np.random.Generator):
            noise = self.executive.rng.normal(0, self.noise_scale)
        else:
            noise = self.executive.rng.gauss(0, self.noise_scale)

        # Intervention effect
        effect_multiplier = 1.0
        if round(i_value) == 1:  # isolation active
            effect_multiplier = 1.0 - self.isolation_effect

        # Prediction with current intervention
        C_hat_with = (
            c_value + self.theta * c_value * self.bias * effect_multiplier + noise
        )

        # Counterfactual without intervention
        C_hat_without = c_value + self.theta * c_value * self.bias + noise

        # Clip
        C_domain = self.reads()[0].domain
        if isinstance(C_domain, RangeDomain):
            min_value = C_domain.min_value
            max_value = C_domain.max_value
            C_hat_with = np.clip(C_hat_with, min_value, max_value)
            C_hat_without = np.clip(C_hat_without, min_value, max_value)

        # Update adaptive theta (if using)
        # This would need last observation to compute error
        if hasattr(self, "update_theta") and len(self.theta_history) > 0:
            last_error = self.theta_history[-1]
            self.theta += self.learning_rate * last_error
            self.theta = max(0.01, min(0.1, self.theta))  # Keep bounded

        # Add hypotheses
        self.writes()[0].add_hypothesis(
            VariableRecord(
                value=C_hat_with, confidence=self.base_confidence, source=self.key()
            )
        )

        # Policy recommendation
        self.writes()[1].add_hypothesis(
            VariableRecord(
                value=1.0,  # isolation
                confidence=self.base_confidence,
                source=self.key(),
            )
        )

        # Baseline counterfactual
        self.writes()[2].add_hypothesis(
            VariableRecord(
                value=C_hat_without,
                confidence=self.base_confidence * 0.9,  # Slightly less confident
                source=self.key(),
            )
        )


class ContactNoisyMechanism(ContactMechanism):
    """Contact noisy mechanism."""

    def __init__(self, executive: Executive) -> None:
        """
        Contact noisy mechanism constructor.

        Parameters
        ----------
        executive : Executive
            The executive.
        """
        super().__init__(
            executive,
            theta=0.03,
            confidence=0.64,
            noise_scale=1.0,
            description="Contact transmission mechanism with noise",
            name="ContactNoisy",
        )


class ContactOverestimateMechanism(ContactMechanism):
    """Contact overestimate mechanism."""

    def __init__(self, executive: Executive) -> None:
        """
        Contact overestimate mechanism constructor.

        Parameters
        ----------
        executive : Executive
            The executive.
        """
        super().__init__(
            executive,
            theta=0.03,
            confidence=0.72,
            bias=1.5,
            description="Contact transmission mechanism with overestimate bias (1.5)",
            name="ContactOverestimate",
        )


def create_contact_family(executive: Executive) -> MechanismFamily:
    """
    Create and populate the contact mechanism family.

    Parameters
    ----------
    executive : Executive
        The executive.

    Returns
    -------
    MechanismFamily
        The mechanism family.
    """
    family = MechanismFamily("contact", sigma=5.0, alpha=0.2)

    family.add(ContactMechanism(executive=executive))
    family.add(ContactNoisyMechanism(executive=executive))
    family.add(ContactOverestimateMechanism(executive=executive))

    return family
