"""
Statistics for variable histories in Procela memory tracking.

This module defines immutable, incremental statistics associated with
a variable's history in Procela's memory subsystem. These statistics
include count, sum, sum of squares, min, max, last value, confidence
sum, exponentially weighted moving average (EWMA), and set of sources.

The main class provided is:

- HistoryStatistics: Represents an immutable snapshot of accumulated
  statistics over a sequence of variable records.

The statistics tracked by this class are useful for summarizing numeric
valued observations from a variable's history.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ....symbols.key import Key
from .record import VariableRecord


@dataclass(frozen=True)
class HistoryStatistics:
    """
    Incremental, immutable statistics associated with a VariableHistory.

    This object is semantically authoritative and fully derived from
    a sequence of `VariableRecord` instances. It is frozen (immutable)
    and can be updated only by creating a new instance via the
    `update` method.

    Attributes
    ----------
    count : int
        Number of numeric records incorporated into the statistics.
    sum : float
        Sum of all numeric values from the records.
    sumsq : float
        Sum of squares of all numeric values.
    min : float | None
        Minimum of the observed values, or `None` if no values.
    max : float | None
        Maximum of the observed values, or `None` if no values.
    last_value : float | None
        Most recent numeric value observed, or `None` if no values.
    confidence_sum : float
        Accumulated confidence from records.
    ewma : float | None
        Exponentially weighted moving average of observed values, or
        `None` if no values.
    sources : frozenset[Key]
        Frozen set of associated source keys encountered.

    Methods
    -------
    empty()
        Return a fresh `HistoryStatistics` with no data.
    update(record, alpha=0.3)
        Return an updated statistics object incorporating `record`.
    mean()
        Return the arithmetic mean of the values.
    std()
        Return the population standard deviation.
    confidence()
        Return the mean confidence of the records.
    """

    count: int = 0
    sum: float = 0.0
    sumsq: float = 0.0
    min: float | None = None
    max: float | None = None
    last_value: float | None = None
    confidence_sum: float = 0.0
    ewma: float | None = None
    sources: frozenset[Key] = frozenset()

    @classmethod
    def empty(cls) -> HistoryStatistics:
        """
        Create an empty statistics state.

        The returned object represents no observations.

        Returns
        -------
        HistoryStatistics
            A statistics instance with zero count and no values.
        """
        return cls(
            count=0,
            sum=0.0,
            sumsq=0.0,
            min=None,
            max=None,
            last_value=None,
            confidence_sum=0.0,
            ewma=None,
            sources=frozenset(),
        )

    def update(self, record: VariableRecord, alpha: float = 0.3) -> HistoryStatistics:
        """
        Return a new statistics state updated with a record.

        Only numeric `record.value` (int or float) contributes to the
        statistics. Non-numeric values are ignored and return the current
        state.

        Parameters
        ----------
        record : VariableRecord
            The record containing a value and optional confidence and source.
        alpha : float, optional
            Smoothing factor for exponentially weighted moving average (EWMA),
            must be non-negative (default is 0.3).

        Returns
        -------
        HistoryStatistics
            A fresh statistics instance reflecting the updated state.

        Raises
        ------
        ValueError
            If `alpha` is negative.
        """
        value = record.value
        if not isinstance(value, int | float):
            return self

        if alpha < 0:
            raise ValueError("alpha should be non-negative")

        new_min = value if self.min is None else min(self.min, value)
        new_max = value if self.max is None else max(self.max, value)

        ewma = value if self.ewma is None else alpha * value + (1 - alpha) * self.ewma

        new_sources = self.sources
        if record.source is not None:
            new_sources = self.sources | {record.source}

        return HistoryStatistics(
            count=self.count + 1,
            sum=self.sum + float(value),
            sumsq=self.sumsq + float(value) ** 2,
            min=new_min,
            max=new_max,
            last_value=value,
            confidence_sum=self.confidence_sum + (record.confidence or 0.0),
            ewma=ewma,
            sources=new_sources,
        )

    def mean(self) -> float | None:
        """
        Return the arithmetic mean of the observed values.

        Returns
        -------
        float | None
            The mean if `count > 0`, otherwise `None`.
        """
        if self.count == 0 or self.sum is None:
            return None
        return self.sum / self.count

    def std(self) -> float | None:
        """
        Return the population standard deviation.

        If fewer than two values have been observed, `None` is returned.

        Returns
        -------
        float | None
            Standard deviation of the observations or `None`.
        """
        mean = self.mean()
        if self.count < 2 or mean is None:
            return None
        variance = (self.sumsq / self.count) - mean**2
        return math.sqrt(variance)

    def confidence(self) -> float | None:
        """
        Return the mean confidence for the records.

        Returns
        -------
        float | None
            Average confidence if `count > 0`, otherwise `None`.
        """
        if self.count == 0 or self.confidence_sum is None:
            return None
        return self.confidence_sum / self.count

    def __repr__(self) -> str:
        """Human-readable representation of a HistoryStatistics."""
        return (
            f"HistoryStatistics("
            f"count={self.count}, "
            f"mean={self.mean()}, "
            f"std={self.std()}, "
            f"min={self.min}, "
            f"max={self.max}, "
            f"confidence={self.confidence()}, "
            f"ewma={self.ewma}, "
            f"sources={len(self.sources)}"
            f")"
        )
