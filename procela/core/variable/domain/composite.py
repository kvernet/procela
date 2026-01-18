"""
Composite value domains for Procela.

This module provides domain classes that combine multiple domains using logical
operations (AND composition).

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/domain/composite.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/variable/domain/composite.html
"""

from __future__ import annotations

from typing import Any

from ...memory.variable.statistics import HistoryStatistics
from .value import ValueDomain


class CompositeDomain(ValueDomain):
    """
    Domain composed of multiple other domains using AND composition.

    A composite domain validates a value against multiple sub-domains.
    A value is valid only if it passes validation for ALL sub-domains
    (logical AND operation). This allows creating complex constraints by
    combining simpler domains.

    Attributes
    ----------
    subdomains : list[ValueDomain]
        List of sub-domains that the value must satisfy. The order in the
        list may affect the explanation output but not validation logic.
    name : str
        Optional name for the domain, inherited from ValueDomain.

    Notes
    -----
    - Validation uses short-circuit evaluation: stops at first failing domain
    - Explanation concatenates all sub-domain explanations
    - Empty subdomain list results in a domain that accepts all values
    - The composite can contain other CompositeDomain instances (nesting)

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/variable/domain/composite.html

    Examples Reference
    -------------------
    https://procela.org/docs/examples/core/variable/domain/composite.html
    """

    def __init__(self, subdomains: list[ValueDomain], name: str = "") -> None:
        """
        Initialize a CompositeDomain with a list of sub-domains.

        Parameters
        ----------
        subdomains : list[ValueDomain]
            List of domain instances that the value must satisfy.
            Can be empty, in which case the composite accepts all values.
        name : str, optional
            Name for the domain. Default is empty string.

        Notes
        -----
        The subdomains list is stored by reference, not copied. Modifying
        the original list after creating the CompositeDomain will affect
        the domain's behavior.
        """
        super().__init__(name)
        self.subdomains = subdomains

    def validate(self, value: Any, stats: HistoryStatistics | None = None) -> bool:
        """
        Validate that a value satisfies ALL sub-domains.

        Performs logical AND validation across all sub-domains.
        Uses short-circuit evaluation: stops at first failing domain.

        Parameters
        ----------
        value : Any
            Value to validate against all sub-domains.
        stats : HistoryStatistics | None, optional
            Additional stats for validation. Passed to each sub-domain's
            validate method. Default is None.

        Returns
        -------
        bool
            True if ALL sub-domains validate the value as True,
            False if ANY sub-domain validates the value as False.

        Notes
        -----
        - Empty subdomain list returns True for any value
        - Order of validation follows the subdomains list order
        - HistoryStatistics is passed to each sub-domain unchanged
        """
        return all(domain.validate(value, stats) for domain in self.subdomains)

    def explain(self, value: Any, stats: HistoryStatistics | None = None) -> str:
        """
        Generate combined explanation from all sub-domains.

        Concatenates explanations from all sub-domains using " | " separator.
        This provides insight into which domains passed or failed.

        Parameters
        ----------
        value : Any
            Value to generate explanations for.
        stats : HistoryStatistics | None, optional
            Additional stats for explanation. Passed to each sub-domain's
            explain method. Default is None.

        Returns
        -------
        str
            String containing all sub-domain explanations concatenated
            with " | " separator. For empty subdomain list, returns empty string.

        Notes
        -----
        - Explanations are generated even for domains that pass validation
        - The separator " | " is used to visually separate explanations
        - Order of explanations follows the subdomains list order
        """
        explanations = [domain.explain(value, stats) for domain in self.subdomains]
        return " | ".join(explanations)
