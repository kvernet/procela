"""
KeyAuthority — Process-global identity authority.

This module defines the KeyAuthority, responsible for issuing and validating
globally unique Key instances within a single Procela runtime. It serves
as the single source of truth for Key identity resolution and ensures that
no Key collisions occur within the current process.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/key_authority.html
"""

from __future__ import annotations

import threading

from ..symbols.key import Key
from .exceptions import SemanticViolation


class KeyAuthority:
    """
    Process-global authority responsible for issuing unique identity keys.

    Maintains a global registry of all issued Keys within a runtime context,
    ensuring Key uniqueness and providing owner resolution capabilities.
    Thread-safe by design for concurrent access across multiple mechanisms.

    Example
    -------
        >>> # Issue a Key with owner binding
        >>> owner = object()
        >>> key = KeyAuthority.issue(owner=owner)
        >>>
        >>> # Resolve owner later
        >>> resolved = KeyAuthority.resolve(key)
        >>> resolved is owner
        True
        >>>
        >>> # Issue without owner (anonymous Key)
        >>> anonymous_key = KeyAuthority.issue()
        >>> KeyAuthority.resolve(anonymous_key) is None
        True
    """

    _lock = threading.Lock()
    _registry: dict[Key, object] = {}

    def __new__(cls) -> KeyAuthority:
        """
        Prevent instantiation.

        Raises
        ------
        TypeError
            Always raised to prevent creation of KeyAuthority instances.
        """
        raise TypeError("KeyAuthority may not be instantiated")

    @classmethod
    def issue(cls, owner: object | None = None) -> Key:
        """
        Issue a process-globally unique Key and optionally bind it to an owner.

        Generates a new Key and registers it in the global registry.
        If an owner is provided, the Key is associated with that owner
        for later resolution.

        Parameters
        ----------
        owner : object or None, optional
            Object to associate with the issued Key. Used for debugging,
            introspection, and ownership tracking. If None, the Key is
            issued without owner binding (default).

        Returns
        -------
        Key
            Newly issued unique Key instance.

        Raises
        ------
        SemanticViolation
            If Key uniqueness is violated (astronomically unlikely but
            theoretically possible with random token generation).

        Notes
        -----
        Thread safety is ensured via class-level locking. Multiple
        concurrent calls will be serialized to maintain registry
        consistency.

        Example
        -------
        >>> # Issue Key with mechanism owner
        >>> mechanism = SomeMechanism()
        >>> key = KeyAuthority.issue(owner=mechanism)
        >>>
        >>> # Issue anonymous Key for transient use
        >>> temp_key = KeyAuthority.issue()
        """
        with cls._lock:
            key = Key()
            if key in cls._registry:
                raise SemanticViolation(
                    "Key uniqueness violation detected during generation."
                )
            cls._registry[key] = owner
            return key

    @classmethod
    def resolve(cls, key: Key) -> object | None:
        """
        Return the object associated with a Key, if any.

        Looks up the Key in the registry and returns the
        associated owner object, or None if the Key was issued
        without owner or is not registered.

        Parameters
        ----------
        key : Key
            Key to look up in the registry.

        Returns
        -------
        object or None
            Owner object associated with the Key, or None if no
            owner is bound or Key is not in registry.

        Notes
        -----
        This method is primarily for debugging, introspection, and
        diagnostic purposes. Production code should generally not
        depend on Key ownership resolution.

        The registry is append-only; once a Key is registered, it
        remains in the registry for the lifetime of the process.

        Example
        -------
        >>> # Issue and later resolve
        >>> owner = SomeEntity()
        >>> key = KeyAuthority.issue(owner=owner)
        >>>
        >>> # Later, perhaps in different context
        >>> resolved = KeyAuthority.resolve(key)
        >>> resolved is owner
        True
        """
        return cls._registry.get(key)
