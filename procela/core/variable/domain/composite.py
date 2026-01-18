"""
Composite value domains for Procela.

This module provides domain classes that combine multiple domains using logical
operations (AND composition).

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/domain/composite.html
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

    Examples
    --------
    >>> from procela.core.variable import (
    ...     RangeDomain, CategoricalDomain, CompositeDomain
    ... )
    >>>
    >>> # Create a domain for positive even numbers
    >>> positive_domain = RangeDomain(min_value=0)
    >>> even_domain = CategoricalDomain([0, 2, 4, 6, 8, 10])
    >>> composite = CompositeDomain(
    ...     [positive_domain, even_domain],
    ...     name="positive_evens"
    ... )
    >>> composite.validate(4)
    True
    >>> composite.validate(3)  # Not even
    False
    >>> composite.validate(-2)  # Not positive
    False

    >>> # Empty composite accepts everything
    >>> empty_composite = CompositeDomain([])
    >>> empty_composite.validate("anything")
    True
    >>> empty_composite.validate(12345)
    True

    >>> # Nested composites
    >>> numeric_range = RangeDomain(min_value=0, max_value=100)
    >>> status_codes = CategoricalDomain(["active", "inactive", "pending"])
    >>> inner_composite = CompositeDomain([numeric_range, status_codes])
    >>> outer_composite = CompositeDomain([inner_composite, RangeDomain(min_value=10)])
    >>> outer_composite.validate(50)  # Will fail - 50 is not a status code
    False
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

        Examples
        --------
        >>> from procela.core.variable import (
        ...     RangeDomain, CategoricalDomain, CompositeDomain
        ... )
        >>>
        >>> # Composite with multiple domains
        >>> range_dom = RangeDomain(min_value=0, max_value=100)
        >>> cat_dom = CategoricalDomain(["A", "B", "C"])
        >>> composite = CompositeDomain(
        ...     [range_dom, cat_dom], name="range_and_category"
        ... )
        >>> len(composite.subdomains)
        2
        >>> composite.name
        'range_and_category'

        >>> # Empty composite
        >>> empty = CompositeDomain([])
        >>> len(empty.subdomains)
        0

        >>> # Single domain composite (useful for uniform interfaces)
        >>> single = CompositeDomain([range_dom])
        >>> len(single.subdomains)
        1
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

        Examples
        --------
        >>> from procela.core.variable import (
        ...     RangeDomain, CategoricalDomain, CompositeDomain
        ... )

        >>> # Composite requiring value between 0-10 AND be either "a" or "b"
        >>> range_dom = RangeDomain(min_value=0, max_value=10)
        >>> cat_dom = CategoricalDomain(["a", "b"])
        >>> composite = CompositeDomain([range_dom, cat_dom])

        >>> composite.validate(5)  # 5 is in range but not in categories
        False
        >>> composite.validate("a")  # "a" is in categories but not numeric
        False
        >>> composite.validate("c")  # Fails both conditions
        False

        >>> # Empty composite always validates
        >>> empty = CompositeDomain([])
        >>> empty.validate("anything")
        True
        >>> empty.validate(None)
        True
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

        Examples
        --------
        >>> from procela.core.variable import (
        ...     RangeDomain, CategoricalDomain, CompositeDomain
        ... )

        >>> # Composite with one passing and one failing domain
        >>> range_dom = RangeDomain(min_value=0, max_value=10)
        >>> cat_dom = CategoricalDomain(["x", "y", "z"])
        >>> composite = CompositeDomain([range_dom, cat_dom])

        >>> # Value 5: passes range, fails categorical
        >>> composite.explain(5)
        "Value 5 is valid in RangeDomain. | Value 5 is not in allowed ..."

        >>> # Value "x": fails range, passes categorical
        >>> composite.explain("x")
        "Value x is not numeric. | Value x is allowed in categories {'z', 'y', 'x'}."

        >>> # Value 15: fails both
        >>> composite.explain(15)
        "Value 15 is greater than maximum 10. | Value 15 is not in allowed ..."

        >>> # Empty composite
        >>> empty = CompositeDomain([])
        >>> empty.explain("anything")
        ''

        >>> # Single domain composite
        >>> single = CompositeDomain([range_dom])
        >>> single.explain(5)
        'Value 5 is valid in RangeDomain.'
        >>> single.explain(15)
        'Value 15 is greater than maximum 10.'
        """
        explanations = [domain.explain(value, stats) for domain in self.subdomains]
        return " | ".join(explanations)
