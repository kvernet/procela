"""
Statistics for variable in Procela memory tracking.

This module defines immutable, incremental statistics computed on
a variable's memory in Procela. These statistics include count, sum,
sum of squares, min, max, last value, confidence sum, exponentially
weighted moving average (EWMA), and set of sources.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/memory/variable/statistics.html

Examples Reference
------------------
https://procela.org/docs/examples/core/memory/variable/statistics.html
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ...symbols.key import Key
from ..assessment.statistics import StatisticsResult
from .record import VariableRecord


@dataclass(frozen=True)
class MemoryStatistics:
    """
    Incremental, immutable statistics computed on a VariableMemory.

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
        Most recent value observed, or `None` if no values.
    confidence_sum : float
        Accumulated confidence from records.
    ewma : float | None
        Exponentially weighted moving average of observed values, or
        `None` if no values.
    sources : frozenset[Key]
        Frozen set of associated source keys encountered.
    """

    count: int = 0
    sum: float | None = None
    sumsq: float | None = None
    min: float | None = None
    max: float | None = None
    last_value: float | None = None
    confidence_sum: float = 0.0
    ewma: float | None = None
    sources: frozenset[Key] = frozenset()

    @classmethod
    def empty(cls) -> MemoryStatistics:
        """
        Create an empty statistics state.

        The returned object represents no observations.

        Returns
        -------
        MemoryStatistics
            A statistics instance with zero count and no values.
        """
        return cls(
            count=0,
            sum=None,
            sumsq=None,
            min=None,
            max=None,
            last_value=None,
            confidence_sum=0.0,
            ewma=None,
            sources=frozenset(),
        )

    def update(
        self, record: VariableRecord | None, alpha: float = 0.3
    ) -> MemoryStatistics:
        """
        Return a new statistics instance updated with a record.

        Only numeric `record.value` (int or float) contributes to the
        numeric computations. Non-numeric values are ignored and return
        the current state with count + 1.

        Parameters
        ----------
        record : VariableRecord
            The record containing a value and optional confidence and source.
        alpha : float, optional
            Smoothing factor for exponentially weighted moving average (EWMA),
            must be non-negative (default is 0.3).

        Returns
        -------
        MemoryStatistics
            A new statistics instance reflecting the updated state.

        Raises
        ------
        ValueError
            If `alpha` is negative.
        """
        if alpha < 0:
            raise ValueError("alpha should be non-negative")

        count = self.count if self.count is not None else 0
        if record is None:
            new_value = self.last_value
            new_sum = self.sum
            new_sumsq = self.sumsq
            new_min = self.min
            new_max = self.max
            new_confidence_sum = self.confidence_sum
            new_ewma = self.ewma
            new_sources = self.sources
        else:
            new_value = record.value
            if not isinstance(new_value, int | float):
                new_sum = self.sum
                new_sumsq = self.sumsq
                new_min = self.min
                new_max = self.max
                new_ewma = self.ewma
            else:
                new_value = float(new_value)
                valuesq = new_value**2
                new_sum = self.sum + new_value if self.sum is not None else new_value
                new_sumsq = self.sumsq + valuesq if self.sumsq is not None else valuesq
                new_min = new_value if self.min is None else min(self.min, new_value)
                new_max = new_value if self.max is None else max(self.max, new_value)
                new_ewma = (
                    new_value
                    if self.ewma is None
                    else alpha * new_value + (1 - alpha) * self.ewma
                )

            new_sources = self.sources
            if record.source is not None:
                new_sources = self.sources | {record.source}
            new_confidence_sum = self.confidence_sum + (record.confidence or 0.0)

        return MemoryStatistics(
            count=count + 1,
            sum=new_sum,
            sumsq=new_sumsq,
            min=new_min,
            max=new_max,
            last_value=new_value,
            confidence_sum=new_confidence_sum,
            ewma=new_ewma,
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
        sumsq = self.sumsq
        mean = self.mean()
        if self.count < 2 or mean is None or sumsq is None:
            return None
        variance = (sumsq / self.count) - mean**2
        variance = max(variance, 0.0)
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
        """
        Human-readable representation of a MemoryStatistics.

        Returns
        -------
        str
            Human-readable representation.
        """
        return (
            f"MemoryStatistics("
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

    def result(self) -> StatisticsResult:
        """
        Return the statistics result from the memory.

        Returns
        -------
        StatisticsResult
            The statistics result.
        """
        return StatisticsResult(
            count=self.count,
            sum=self.sum,
            min=self.min,
            max=self.max,
            mean=self.mean(),
            std=self.std(),
            value=self.last_value,
            ewma=self.ewma,
            confidence=self.confidence(),
        )
