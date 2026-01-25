"""
Mechanism template abstraction for Procela.

This module defines the `MechanismTemplate` class, representing an abstract
causal capability that is independent of concrete variable bindings. Templates
declare which variables a mechanism may read and write, and define how
transformations are performed once instantiated.

Mechanism templates are intended for structural exploration, optimization,
and configuration by executive-level components. They are **not executed
directly**; execution occurs only through instantiated mechanisms.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/mechanism/template.html

Examples Reference
------------------
https://procela.org/docs/examples/core/mechanism/template.html
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from ...symbols.key import Key


class MechanismTemplate(ABC):
    """
    Abstract causal capability to instantiate different variable bindings.

    Mechanism templates provide a blueprint for how a mechanism interacts
    with variables. They specify which variables are read and written, and
    define the `transform` method for generating candidate variable proposals.

    Attributes
    ----------
    None. Concrete implementations define specific inputs, outputs,
    and transformation logic.

    Notes
    -----
    - Templates are **structural**: they define potential causality but do not
      perform actual variable mutations.
    - Concrete `Mechanism` instances will bind the template to actual variable keys.
    """

    @abstractmethod
    def reads(self) -> Sequence[Key]:
        """
        Return the variable keys this template may read.

        Returns
        -------
        Sequence[Key]
            Admissible input variable keys.
        """
        raise NotImplementedError

    @abstractmethod
    def writes(self) -> Sequence[Key]:
        """
        Return the variable keys this template may write.

        Returns
        -------
        Sequence[Key]
            Admissible output variable keys.
        """
        raise NotImplementedError

    @abstractmethod
    def transform(
        self,
        inputs: list[Key],
        outputs: list[Key],
    ) -> None:
        """
        Produce candidate proposals for output variables.

        Parameters
        ----------
        inputs : list[Key]
            Variable keys to read. Implementations may inspect current
            values and history.
        outputs : list[Key]
            Variable keys to propose updates for.

        Notes
        -----
        - Must not commit variable state directly.
        - Proposals must be submitted via Variable.add_candidate().
        """
        raise NotImplementedError
