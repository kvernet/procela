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

from ..variable.variable import Variable


class MechanismTemplate(ABC):
    """
    Abstract causal capability to instantiate different variable bindings.

    Mechanism templates provide a blueprint for how a mechanism interacts
    with variables. They specify which variables are read and written, and
    define the `transform` method for generating candidate variable proposals.

    Attributes
    ----------
    None. Concrete implementations define specific reads, writes,
    and transformation logic.

    Notes
    -----
    - Templates are **structural**: they define potential causality but do not
      perform actual variable mutations.
    - Concrete `Mechanism` instances will bind the template to actual variables.
    """

    @abstractmethod
    def reads(self) -> Sequence[Variable]:
        """
        Return the variables this template may read.

        Returns
        -------
        Sequence[Variable]
            Admissible variables this template may read.
        """
        raise NotImplementedError

    @abstractmethod
    def writes(self) -> Sequence[Variable]:
        """
        Return the variables this template may write.

        Returns
        -------
        Sequence[Variable]
            Admissible variables this template may write.
        """
        raise NotImplementedError

    @abstractmethod
    def transform(
        self,
        inputs: list[Variable],
        outputs: list[Variable],
    ) -> None:
        """
        Produce candidate proposals for written variables.

        Parameters
        ----------
        inputs : list[Variable]
            Variables to read. Implementations may inspect current
            values and memory.
        outputs : list[Variable]
            Variables to propose updates for.

        Notes
        -----
        - Must not commit variable state directly.
        - Proposals must be submitted via Variable.add_candidate().
        """
        raise NotImplementedError
