"""
Structural equilibrium mechanism.

Proposes a weak, persistent correction of a variable toward a
configurable baseline attractor when no acute destabilizing
mechanisms are active.

Examples
--------
>>> from procela import (
...     HomeostasisMechanism,
...     Variable,
...     RangeDomain,
...     VariableRecord
... )
>>>
>>> X = Variable("X", RangeDomain(0., 50.))
>>> Y = Variable("Y", RangeDomain(-50., 50.))
>>>
>>> mech = HomeostasisMechanism(reads=[X, Y], writes=[Y])
>>>
# Init variables
>>> X.init(VariableRecord(6, confidence=1.0))
>>> Y.init(VariableRecord(2.1, confidence=1.0))
>>>
>>> mech.transform()
>>>
>>> print(len(X.hypotheses))
0
>>> print(len(Y.hypotheses))
1

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/mechanism/homeostasis.html

Examples Reference
------------------
https://procela.org/docs/examples/core/mechanism/homeostasis.html
"""

from __future__ import annotations

from typing import Sequence

from ..memory.record import VariableRecord
from ..variable.variable import Variable
from .base import Mechanism


class HomeostasisMechanism(Mechanism):
    """
    Structural equilibrium mechanism.

    Proposes a weak, persistent correction of a variable toward a
    configurable baseline attractor when no acute destabilizing
    mechanisms are active.

    Examples
    --------
    >>> from procela import (
    ...     HomeostasisMechanism,
    ...     Variable,
    ...     RangeDomain,
    ...     VariableRecord
    ... )
    >>>
    >>> X = Variable("X", RangeDomain(0., 50.))
    >>> Y = Variable("Y", RangeDomain(-50., 50.))
    >>>
    >>> mech = HomeostasisMechanism(reads=[X, Y], writes=[Y])
    >>>
    # Init variables
    >>> X.init(VariableRecord(6, confidence=1.0))
    >>> Y.init(VariableRecord(2.1, confidence=1.0))
    >>>
    >>> mech.transform()
    >>>
    >>> print(len(X.hypotheses))
    0
    >>> print(len(Y.hypotheses))
    1
    """

    def __init__(
        self,
        reads: Sequence[Variable],
        writes: Sequence[Variable],
        name: str = "HomeostasisMechanism",
        baseline_risk: float = 0.2,
        alpha: float = 0.08,
        base_confidence: float = 0.5,
    ) -> None:
        """
        Initialize an instance of HomeostasisMechanism.

        Parameters
        ----------
        reads : Sequence[Variable]
            The sequence of variables read by this mechanism.
        writes : Sequence[Variable]
            The sequence of variables written by this mechanism.
        name : str = "HomeostasisMechanism"
            The mechanism name.
        baseline_risk : float
            The base line risk. Default is 0.2.
        alpha : float
            The alpha parameters. Default is 0.08.
        base_confidence : float
            The base confidence. Default if 0.5.

        Examples
        --------
        >>> from procela import (
        ...     HomeostasisMechanism,
        ...     Variable,
        ...     RangeDomain,
        ...     VariableRecord
        ... )
        >>>
        >>> X = Variable("X", RangeDomain(0., 50.))
        >>> Y = Variable("Y", RangeDomain(-50., 50.))
        >>>
        >>> mech = HomeostasisMechanism(reads=[X, Y], writes=[Y])
        >>>
        # Init variables
        >>> X.init(VariableRecord(6, confidence=1.0))
        >>> Y.init(VariableRecord(2.1, confidence=1.0))
        >>>
        >>> mech.transform()
        >>>
        >>> print(len(X.hypotheses))
        0
        >>> print(len(Y.hypotheses))
        1
        """
        super().__init__(reads=reads, writes=writes)

        self.name = name
        self.baseline_risk = baseline_risk
        self.alpha = alpha
        self.base_confidence = base_confidence

    def transform(self) -> None:
        """Propose a partial correction toward the baseline attractor."""
        variable = self.writes()[0]
        # Defensive checks
        if not variable.has_records():
            return

        current_value = variable.value

        # Compute partial correction
        delta = current_value - self.baseline_risk
        proposed_value = current_value - self.alpha * delta

        # Clamp to variable bounds if defined
        # proposed_value = variable.clamp(proposed_value)

        confidence = self._compute_confidence(variable)

        variable.add_hypothesis(
            VariableRecord(
                value=proposed_value,
                source=self.key(),
                confidence=confidence,
                metadata={
                    "baseline": self.baseline_risk,
                    "alpha": self.alpha,
                    "delta": delta,
                },
                explanation="Partial correction toward the baseline attractor.",
            )
        )

    # ------------------------------------------------------------------
    # Confidence logic
    # ------------------------------------------------------------------
    def _compute_confidence(self, variable: Variable) -> float:
        """
        Confidence increases as the system stabilizes and competition fades.

        Paremeters
        ----------
        variable : Variable
            The variable to compute correction confidence.

        Returns
        -------
        float
            The confidence estimation of the correction.
        """
        confidence = self.base_confidence

        # Fewer competitors → stronger structural dominance
        competitor_count = variable.hypotheses
        competition_factor = 1.0 / (1.0 + len(competitor_count))

        # Lower variance → stronger confidence
        stats = variable.stats.result()
        std = stats.std
        if std is not None:
            stability_factor = 1.0 / (1.0 + std)
        else:
            stability_factor = 1.0

        confidence *= competition_factor * stability_factor

        return float(min(1.0, confidence))
