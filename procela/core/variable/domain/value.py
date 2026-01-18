"""
Value domain semantic definitions for Procela.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/domain/value.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/variable/domain/value.html
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ...memory.variable.statistics import HistoryStatistics


class ValueDomain(ABC):
    """
    Abstract base class for value domains in Procela.

    A value domain defines a set of valid values and provides methods
    to validate values and explain domain constraints.

    Attributes
    ----------
    name : str
        Optional name for the domain. Used for identification and debugging.

    Methods
    -------
    __init__(name: str = "")
        Initialize the value domain with an optional name.
    validate(value: Any, stats: HistoryStatistics | None = None) -> bool
        Validate that a value belongs to the domain.
    explain(value: Any, stats: HistoryStatistics | None = None) -> str
        Explain why a value is valid or invalid.

    Notes
    -----
    This is an abstract base class. Subclasses must implement the
    `validate` and `explain` methods.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/variable/domain/value.html

    Examples Reference
    -------------------
    https://procela.org/docs/examples/core/variable/domain/value.html
    """

    name: str

    def __init__(self, name: str = "") -> None:
        """
        Initialize a ValueDomain instance.

        Parameters
        ----------
        name : str, optional
            Name for the domain. Default is empty string.
            Useful for debugging and when domains are used in collections.
        """
        self.name = name

    @abstractmethod
    def validate(self, value: Any, stats: HistoryStatistics | None = None) -> bool:
        """
        Validate that a value belongs to the domain.

        Parameters
        ----------
        value : Any
            Value to validate against the domain constraints.
        stats : HistoryStatistics | None, optional
            Additional stats for validation. Default is None.

        Returns
        -------
        bool
            True if the value is valid according to domain constraints,
            False otherwise.

        Raises
        ------
        NotImplementedError
            If not implemented by subclass.

        Notes
        -----
        The `stats` parameter allows for hostorical validation where
        validity may depend on external factors (e.g., "value must be
        within one standard deviation of a reference mean").
        """
        raise NotImplementedError

    @abstractmethod
    def explain(self, value: Any, stats: HistoryStatistics | None = None) -> str:
        """
        Explain why a value is valid or invalid.

        Provides a human-readable explanation of domain constraints and
        why a particular value does or does not satisfy them.

        Parameters
        ----------
        value : Any
            Value to explain validation for.
        stats : HistoryStatistics | None, optional
            Additional stats for the explanation. May include
            information needed to generate a meaningful explanation.
            Default is None.

        Returns
        -------
        str
            Human-readable explanation of domain constraints and
            validation result for the given value.

        Raises
        ------
        NotImplementedError
            If not implemented by subclass.

        Notes
        -----
        The explanation should be helpful for users to understand
        why a value was rejected or what constraints apply.
        """
        raise NotImplementedError

    def trend_threshold(
        self,
        stats: HistoryStatistics,
        *,
        absolute: float | None = None,
        std_factor: float | None = None,
    ) -> float | None:
        """
        Exposes optional trend_threshold.

        This method exposes optional semantic hooks but
        does not define trend logic by default.

        Parameters
        ----------
        stats : HistoryStatistics,
            Additional stats for the trend. May include
            information needed to compute the trend.
        absolute : float | None = None
            The abosulte value of the trend threshold.
        std_factor : float | None = None
            The standard deviation factor of the trend threshold.
        """
        return None
