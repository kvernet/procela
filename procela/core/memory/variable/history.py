"""
History structures for variable memory.

This module defines immutable, append-only history structures used to
track the evolution of variable records and reasoning results over time.
Each history instance represents a complete epistemic state derived from
its predecessor and a newly appended element.

Histories are persistent and immutable: all update operations return new
history instances without mutating existing ones.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/memory/variable/history.html

Examples Reference
------------------
https://procela.org/docs/examples/core/memory/variable/history.html
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from ....symbols.key import Key
from ....symbols.time import TimePoint
from ...key_authority import KeyAuthority
from ...reasoning.result import ReasoningResult
from ...reasoning.task import ReasoningTask
from .record import VariableRecord
from .statistics import HistoryStatistics


@dataclass(frozen=True)
class VariableHistory:
    """
    Immutable history of variable records.

    Each instance represents a single node in a persistent history chain,
    containing one record and a reference to the previous history node.
    Together, the chain encodes the full chronological evolution of a
    variable's epistemic state.

    The history is traversed structurally from newest to oldest and supports
    filtering, aggregation, and statistical inspection.

    Parameters
    ----------
    _record : VariableRecord
        The record stored at this history node.
    _previous : VariableHistory | None
        The previous history node, or None if this is the root.
    _config : dict[str, Any]
        The variable history configuration.

    Attributes
    ----------
    _record : VariableRecord
        The record associated with this history node.
    _previous : VariableHistory | None
        Reference to the previous history node.
    _config : dict[str, Any]
        The variable history configuration.
    _stats : HistoryStatistics
        The statistics of the variable records computed incrementally.
    _key : Key
        The unique identity of the VariableHistory

    Notes
    -----
    This structure is immutable. Any operation that conceptually appends
    a record returns a new `VariableHistory` instance.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/memory/variable/history.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/memory/variable/history.html
    """

    _record: VariableRecord | None = field(default=None, repr=False)
    _previous: Key | None = field(default=None, repr=False)
    _config: dict[str, Any] = field(default_factory=dict, repr=False)

    _stats: HistoryStatistics = field(init=False, repr=False)
    _key: Key = field(init=False, repr=False, compare=True, hash=True)

    def __post_init__(self) -> None:
        """Validate the history node after initialization."""
        previous_history: Any | None = None
        if self._previous:
            previous_history = KeyAuthority.resolve(self._previous)
            if not isinstance(previous_history, VariableHistory):
                raise TypeError(
                    f"_previous should be a {VariableHistory.__name__}, "
                    f"got {type(previous_history)}"
                )

        previous_stats = (
            HistoryStatistics.empty()
            if previous_history is None
            else previous_history._stats
        )

        anomaly_cfg = self._config.get("anomaly", {})
        alpha = anomaly_cfg.get("alpha", 0.3)

        object.__setattr__(
            self,
            "_stats",
            (
                previous_stats
                if self._record is None
                else previous_stats.update(self._record, alpha=alpha)
            ),
        )
        object.__setattr__(self, "_key", KeyAuthority.issue(self))

    def new(self, record: VariableRecord) -> VariableHistory:
        """
        Append a new record to the history.

        Parameters
        ----------
        record : VariableRecord
            The record to append.

        Returns
        -------
        VariableHistory
            A new history instance representing the extended history.
        """
        if not isinstance(record, VariableRecord):
            raise TypeError(f"record should be a VariableRecord, get {record!r}")

        return VariableHistory(
            _record=record,
            _previous=self._key,
            _config=self._config,
        )

    def key(self) -> Key:
        """
        Return the unique identity key of this history node.

        Returns
        -------
        Key
            A key uniquely identifying this history state.
        """
        return self._key

    def previous_key(self) -> Key | None:
        """
        Return the identity key of the previous history node.

        Returns
        -------
        Key | None
            The key of the previous history node, or None if this node is the root.
        """
        return self._previous

    def stats(self) -> HistoryStatistics:
        """Return the epistemic statistics of this history."""
        """
        Get epistemic statistics for the history.

        Returns
        -------
        HistoryStatistics
            The HistoryStatistics containing statistical summaries derived from the
            accumulated records in the history.
        """
        return self._stats

    def iter_records(self) -> Iterable[VariableRecord]:
        """
        Iterate over records from newest to oldest.

        Yields
        ------
        VariableRecord
            Records in reverse chronological order.
        """
        current: VariableHistory | None = self

        while current is not None:
            record = current._record
            if record is not None:
                yield record

            prev_key = current._previous
            if prev_key is None:
                break

            resolved = KeyAuthority.resolve(prev_key)
            current = resolved if isinstance(resolved, VariableHistory) else None

    def iter_filtered_records(
        self,
        *,
        key: Key | None = None,
        time: TimePoint | None = None,
        source: Key | None = None,
    ) -> Iterable[VariableRecord]:
        """
        Iterate over filtered records from newest to oldest.

        Parameters
        ----------
        **criteria
            Arbitrary filtering criteria applied to each record.

        Yields
        ------
        VariableRecord
            Records matching the specified criteria.
        """
        for record in self.iter_records():
            if key is not None and record.key() != key:
                continue
            if time is not None and record.time != time:
                continue
            if source is not None and record.source != source:
                continue
            yield record

    def get_records(
        self,
        *,
        key: Key | None = None,
        time: TimePoint | None = None,
        source: Key | None = None,
    ) -> list[VariableRecord]:
        """
        Retrieve records matching the specified criteria.

        Parameters
        ----------
        **criteria
            Arbitrary filtering criteria applied to records.

        Returns
        -------
        list[VariableRecord]
            Records matching the given criteria.
        """
        records = list(self.iter_filtered_records(key=key, time=time, source=source))
        records.reverse()
        return records

    def latest(self) -> VariableRecord | None:
        """
        Return the most recent record.

        Returns
        -------
        VariableRecord
            The latest record in the history.
        """
        return self._record


@dataclass(frozen=True)
class ReasoningHistory:
    """
    Immutable history of reasoning results.

    Each instance represents a single reasoning outcome and a reference to
    the previous reasoning history node, forming a persistent chain that
    encodes the evolution of reasoning over time.

    The structure supports structural traversal, filtering, and inspection.

    Parameters
    ----------
    _result : ReasoningResult
        The reasoning result stored at this history node.
    _previous : Key | None
        The previous history key, or None if this is the root.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/memory/variable/history.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/memory/variable/history.html
    """

    _result: ReasoningResult | None = field(default=None, repr=False)
    _previous: Key | None = field(default=None, repr=False)

    _key: Key = field(init=False, repr=False, compare=True, hash=True)

    def __post_init__(self) -> None:
        """
        Validate the reasoning history node after initialization.

        Ensures consistency between the reasoning result and the previous
        history state.
        """
        object.__setattr__(self, "_key", KeyAuthority.issue(self))

    def new(self, result: ReasoningResult) -> ReasoningHistory:
        """
        Append a new reasoning result to the history.

        Parameters
        ----------
        result : ReasoningResult
            The reasoning result to append.

        Returns
        -------
        ReasoningHistory
            A new history instance representing the extended reasoning history.
        """
        if not isinstance(result, ReasoningResult):
            raise TypeError(f"result should be a ReasoningResult, get {result!r}")

        return ReasoningHistory(
            _result=result,
            _previous=self._key,
        )

    def key(self) -> Key:
        """
        Return the unique identity key of this reasoning history node.

        Returns
        -------
        Key
            A key uniquely identifying this reasoning history state.
        """
        return self._key

    def previous_key(self) -> Key | None:
        """
        Return the identity key of the previous reasoning history node.

        Returns
        -------
        Key | None
            The key of the previous history node, or None if this is the root.
        """
        return self._previous

    def iter_results(self) -> Iterable[ReasoningResult]:
        """
        Iterate over reasoning results from newest to oldest.

        Yields
        ------
        ReasoningResult
            Reasoning results in reverse chronological order.
        """
        current: ReasoningHistory | None = self

        while current is not None:
            result = current._result
            if result is not None:
                yield result

            prev_key = current._previous
            if prev_key is None:
                break

            resolved = KeyAuthority.resolve(prev_key)
            current = resolved if isinstance(resolved, ReasoningHistory) else None

    def iter_filtered_results(
        self,
        *,
        task: ReasoningTask | None = None,
        success: bool | None = True,
    ) -> Iterable[ReasoningResult]:
        """
        Iterate over filtered reasoning results from newest to oldest.

        Parameters
        ----------
        **criteria
            Arbitrary filtering criteria applied to each result.

        Yields
        ------
        ReasoningResult
            Results matching the specified criteria.
        """
        for result in self.iter_results():
            if task is not None and result.task != task:
                continue
            if success is not None and success != result.success:
                continue
            yield result

    def get_results(
        self,
        *,
        task: ReasoningTask | None = None,
        success: bool | None = True,
    ) -> list[ReasoningResult]:
        """
        Retrieve reasoning results matching the specified criteria.

        Parameters
        ----------
        **criteria
            Arbitrary filtering criteria applied to results.

        Returns
        -------
        list[ReasoningResult]
            Results matching the given criteria.
        """
        results = list(self.iter_filtered_results(task=task, success=success))
        results.reverse()
        return results

    def latest(self, task: ReasoningTask | None = None) -> ReasoningResult | None:
        """
        Return the most recent reasoning result.

        Parameters
        ----------
        task : ReasoningTask | None
            The latest reasoning result with that reasoning task if task is not None.

        Returns
        -------
        ReasoningResult
            The latest reasoning result in the history.
        """
        results = self.get_results(task=task, success=None)
        return results[0] if results is not None and len(results) > 0 else None

    def __len__(self) -> int:
        """
        Return the number of reasoning results in the history.

        Returns
        -------
        int
            The length of the reasoning history.
        """
        return len(list(self.iter_results()))
