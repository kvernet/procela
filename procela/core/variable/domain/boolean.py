"""
Boolean value domains for Procela.

This module provides a specialized domain for boolean (True/False) values.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/domain/boolean.html

Examples Reference
-------------------
https://procela.org/docs/examples/core/variable/domain/boolean.html
"""

from __future__ import annotations

from .categorical import CategoricalDomain


class BooleanDomain(CategoricalDomain):
    """
    Domain for boolean values (True and False).

    A specialized categorical domain that only allows the two boolean values
    True and False. This domain inherits from CategoricalDomain and is
    initialized with the fixed set {True, False}.

    Attributes
    ----------
    categories : set
        Always contains {True, False}. Inherited from CategoricalDomain.
    name : str
        Optional name for the domain, inherited from ValueDomain.

    Notes
    -----
    - This is a convenience class for the common case of boolean variables
    - Since it inherits from CategoricalDomain, it uses set membership
      for validation
    - Boolean values in Python are instances of `bool`, which is a subclass
      of `int` (True == 1, False == 0), but validation uses exact type matching
    """

    def __init__(self, name: str = "") -> None:
        """
        Initialize a BooleanDomain with the fixed categories {True, False}.

        Parameters
        ----------
        name : str, optional
            Name for the domain. Default is empty string.
            Useful when multiple boolean domains are used in a system.

        Notes
        -----
        The initialization always calls the parent class constructor with
        the fixed list [True, False]. This ensures the categories set
        always contains exactly these two values.
        """
        super().__init__([True, False], name=name)
