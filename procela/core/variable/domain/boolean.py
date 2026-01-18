"""
Boolean value domains for Procela.

This module provides a specialized domain for boolean (True/False) values.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/domain/boolean.html
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

    Examples
    --------
    >>> from procela.core.variable import BooleanDomain
    >>>
    >>> # Basic usage
    >>> bool_domain = BooleanDomain(name="flag")
    >>> bool_domain.validate(True)
    True
    >>> bool_domain.validate(False)
    True
    >>> bool_domain.validate(1)
    True
    >>> bool_domain.validate(0)
    True
    >>> bool_domain.validate("True")  # String, not boolean
    False

    >>> # Empty name is allowed
    >>> default_bool = BooleanDomain()
    >>> default_bool.categories
    {False, True}
    >>> default_bool.name
    ''

    >>> # Inherits explain functionality
    >>> domain = BooleanDomain()
    >>> domain.explain(True)
    'Value True is allowed in categories {False, True}.'
    >>> domain.explain(1)
    'Value 1 is allowed in categories {False, True}.'
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

        Examples
        --------
        >>> from procela.core.variable import BooleanDomain
        >>>
        >>> # Create a named boolean domain
        >>> flag_domain = BooleanDomain(name="enabled_flag")
        >>> flag_domain.name
        'enabled_flag'
        >>> flag_domain.categories
        {False, True}

        >>> # Create an unnamed boolean domain
        >>> default_domain = BooleanDomain()
        >>> default_domain.name
        ''
        >>> len(default_domain.categories)
        2

        >>> # All boolean domains have the same categories
        >>> domain1 = BooleanDomain(name="d1")
        >>> domain2 = BooleanDomain(name="d2")
        >>> domain1.categories == domain2.categories
        True
        """
        super().__init__([True, False], name=name)
