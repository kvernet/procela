"""
Exception hierarchy for Procela's active reasoning framework.

This module defines the structured exception classes used throughout the
Procela framework. All framework-specific exceptions inherit from the
`ProcelaException` base class, enabling consistent error handling,
categorization, and recovery strategies across the system.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/exceptions.html

Examples Reference
------------------
https://procela.org/docs/examples/core/exceptions.html
"""

from __future__ import annotations


class ProcelaException(Exception):
    """
    Base exception for all Procela-specific errors.

    Parameters
    ----------
    message : str, optional
        Descriptive message about the exception.
    """


class SemanticViolation(ProcelaException):
    """
    Raised when a semantic invariant is violated.

    This exception indicates that an operation attempted to violate a
    fundamental semantic rule of the Procela framework.
    """


class ConstraintViolation(ProcelaException):
    """
    Raised when a system constraint cannot be satisfied.

    This includes both hard constraints (must be satisfied) and
    soft constraints (preference violations).
    """


class InconsistentState(ProcelaException):
    """
    Raised when the system detects an internal inconsistency.

    This indicates a bug or unexpected condition that violates
    framework invariants.
    """


class ConfigurationError(ProcelaException):
    """Raised when framework configuration is invalid or incomplete."""


class TimeoutError(ProcelaException):
    """Raised when an operation exceeds its allowed time budget."""


class ExecutionError(ProcelaException):
    """Raised when an error occurs during execution."""
