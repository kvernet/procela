"""
Exception hierarchy for Procela's active reasoning framework.

This module defines the structured exception classes used throughout the
Procela framework. All framework-specific exceptions inherit from the
`ProcelaException` base class, enabling consistent error handling,
categorization, and recovery strategies across the system.
"""

from __future__ import annotations


class ProcelaException(Exception):
    """Base exception for all Procela-specific errors."""


class SemanticViolation(ProcelaException):
    """
    Raised when a semantic invariant is violated.

    This exception indicates that an operation attempted to violate a
    fundamental semantic rule of the Procela framework.

    Examples
    --------
    >>> from procela.core.exceptions import SemanticViolation
    >>>
    >>> raise SemanticViolation("Cannot perform operation on TimePoint")
    Traceback (most recent call last):
        ...
    procela.core.exceptions.SemanticViolation: Cannot perform operation on TimePoint

    Notes
    -----
    This exception is commonly raised by symbolic entities like `TimePoint`
    when attempting invalid operations such as comparison or arithmetic.
    """


class ResourceExhausted(ProcelaException):
    """
    Raised when a resource limit is exceeded.

    This includes computational resources, memory, or framework-defined
    limits such as maximum recursion depth in reasoning cycles.

    Parameters
    ----------
    message : str, optional
        Descriptive message about the resource exhaustion.

    Examples
    --------
    >>> from procela.core.exceptions import ResourceExhausted
    >>>
    >>> raise ResourceExhausted("Memory allocation exceeded 1GB limit")
    Traceback (most recent call last):
        ...
    procela.core.exceptions.ResourceExhausted: Memory allocation exceeded 1GB limit
    """


class ConstraintViolation(ProcelaException):
    """
    Raised when a system constraint cannot be satisfied.

    This includes both hard constraints (must be satisfied) and
    soft constraints (preference violations).

    Parameters
    ----------
    message : str, optional
        Description of the constraint violation.

    Examples
    --------
    >>> from procela.core.exceptions import ConstraintViolation
    >>>
    >>> raise ConstraintViolation("Action violates temporal precedence")
    Traceback (most recent call last):
        ...
    procela.core.exceptions.ConstraintViolation: Action violates temporal precedence
    """


class InconsistentState(ProcelaException):
    """
    Raised when the system detects an internal inconsistency.

    This indicates a bug or unexpected condition that violates
    framework invariants.

    Parameters
    ----------
    message : str, optional
        Description of the inconsistent state.

    Examples
    --------
    >>> from procela.core.exceptions import InconsistentState
    >>>
    >>> raise InconsistentState("Variable state contradicts its contract")
    Traceback (most recent call last):
        ...
    procela.core.exceptions.InconsistentState: Variable state contradicts its contract

    Notes
    -----
    This exception typically indicates a bug in either the framework
    implementation or in user code that has corrupted internal state.
    """


class ConfigurationError(ProcelaException):
    """
    Raised when framework configuration is invalid or incomplete.

    Parameters
    ----------
    message : str, optional
        Description of the configuration error.

    Examples
    --------
    >>> from procela.core.exceptions import ConfigurationError
    >>>
    >>> raise ConfigurationError("Missing required parameter 'priority'")
    Traceback (most recent call last):
        ...
    procela.core.exceptions.ConfigurationError: Missing required parameter 'priority'
    """


class TimeoutError(ProcelaException):
    """
    Raised when an operation exceeds its allowed time budget.

    Parameters
    ----------
    message : str, optional
        Description of the timeout.

    Examples
    --------
    >>> from procela.core.exceptions import TimeoutError
    >>>
    >>> raise TimeoutError("Reasoning cycle exceeded 5 second limit")
    Traceback (most recent call last):
        ...
    procela.core.exceptions.TimeoutError: Reasoning cycle exceeded 5 second limit

    Notes
    -----
    This is distinct from the built-in `TimeoutError` to avoid
    namespace collisions and to provide Procela-specific context.
    """
