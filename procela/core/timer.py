"""
Performance Timer for the Procela Framework.

This module provides a context manager for precise performance timing
of code execution. It uses `time.perf_counter()` for high-resolution
measurements suitable for benchmarking and performance analysis.
"""

from __future__ import annotations

import time
from typing import Any


class Timer:
    """
    Context manager for precise performance timing.

    This class provides a simple yet effective way to measure execution
    time of code blocks using Python's context manager protocol. It's
    particularly useful for benchmarking, profiling, and performance
    monitoring within the Procela framework.

    Parameters
    ----------
    None
        The Timer is initialized without parameters.

    Attributes
    ----------
    start : float | None
        The timestamp when the timer was started (in seconds from
        `time.perf_counter()`). `None` if timer hasn't been started.
    end : float | None
        The timestamp when the timer was stopped (in seconds from
        `time.perf_counter()`). `None` if timer hasn't been stopped.
    elapsed : float | None
        The elapsed time in seconds between `start` and `end`.
        `None` if timer hasn't been fully executed.

    Methods
    -------
    __enter__() -> Timer
        Start the timer and return the Timer instance.
    __exit__(*args: Any) -> None
        Stop the timer and calculate elapsed time.

    Examples
    --------
    >>> import time
    >>> from procela.core.timer import Timer
    >>>
    >>> # Basic usage as context manager
    >>> with Timer() as timer:
    ...     # Code to time goes here
    ...     time.sleep(0.1)
    >>> print(f"Elapsed time: {timer.elapsed:.6f} seconds")
    Elapsed time: 0.100123 seconds
    >>>
    >>> # Access individual timing components
    >>> print(f"Started at: {timer.start}")
    >>> print(f"Ended at: {timer.end}")
    >>> print(f"Elapsed: {timer.elapsed}")
    """

    def __enter__(self) -> Timer:
        """
        Start the timer when entering the context.

        This method is called when entering the `with` statement context.
        It records the current time using `time.perf_counter()` for
        high-resolution timing.

        Returns
        -------
        Timer
            The Timer instance itself, allowing access to timing
            attributes within the context block.

        Notes
        -----
        - Uses `time.perf_counter()` which provides the highest available
          resolution timer for benchmarking.
        - The timer is not started until this method is called.
        - Multiple calls to `__enter__` on the same instance will
          overwrite previous start times.

        Examples
        --------
        >>> from procela.core.timer import Timer
        >>>
        >>> with Timer() as t:
        ...     # Timer is now running
        ...     print(f"Timer started at: {t.start}")
        ...     # Perform some operations
        """
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        """
        Stop the timer when exiting the context.

        This method is called when exiting the `with` statement context,
        whether by normal completion or exception. It records the end time
        and calculates the elapsed time.

        Parameters
        ----------
        *args : Any
            Standard context manager exit arguments (exc_type, exc_val,
            exc_tb). These are ignored by this implementation as the timer
            should complete regardless of exceptions.

        Notes
        -----
        - The timer will stop and calculate elapsed time even if an
          exception occurs within the context block.
        - The elapsed time calculation uses the same high-resolution
          timer as the start for consistency.
        - If `__exit__` is called without a preceding `__enter__` call,
          an AttributeError will occur when trying to access `self.start`.

        Examples
        --------
        >>> import time
        >>> from procela.core.timer import Timer
        >>>
        >>> timer = Timer()
        >>> with timer:
        ...     time.sleep(0.05)
        >>> # Timer has automatically stopped
        >>> print(f"Elapsed: {timer.elapsed:.4f} seconds")
        Elapsed: 0.0501 seconds
        """
        self.end = time.perf_counter()
        self.elapsed = self.end - self.start
