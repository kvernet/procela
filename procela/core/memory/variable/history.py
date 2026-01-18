"""
Immutable history of VariableRecords for a variable.

Manages a chronological collection of VariableRecords, providing
efficient querying and filtering capabilities. Each history is
immutable; operations return new instances rather than modifying
existing ones.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/memory/variable/history.html
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
    Immutable history node for a Variable.

    Each instance represents exactly one appended record and a complete,
    incremental epistemic state.
    """

    _record: VariableRecord | None = field(default=None, repr=False)
    _previous: Key | None = field(default=None, repr=False)
    _config: dict[str, Any] = field(default_factory=dict, repr=False)

    _stats: HistoryStatistics = field(init=False, repr=False)
    _key: Key = field(init=False, repr=False, compare=True, hash=True)

    def __post_init__(self) -> None:
        """Post init validation."""
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
        """Return a new VariableHistory with the given record appended."""
        if not isinstance(record, VariableRecord):
            raise TypeError(f"record should be a VariableRecord, get {record!r}")

        return VariableHistory(
            _record=record,
            _previous=self._key,
            _config=self._config,
        )

    def key(self) -> Key:
        """Return the identity key of this history."""
        return self._key

    def previous_key(self) -> Key | None:
        """Return the key of the previous history node, if any."""
        return self._previous

    def stats(self) -> HistoryStatistics:
        """Return the epistemic statistics of this history."""
        return self._stats

    def iter_records(self) -> Iterable[VariableRecord]:
        """
        Explicit traversal of records (newest → oldest).

        This traversal is structural and non-epistemic.
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
        """Stream filtered records (newest → oldest)."""
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
        """Get records based on criteria."""
        records = list(self.iter_filtered_records(key=key, time=time, source=source))
        records.reverse()
        return records

    def latest(self) -> VariableRecord | None:
        """Get the latest record."""
        return self._record


@dataclass(frozen=True)
class ReasoningHistory:
    """
    Immutable history node for reasoning.

    Each instance represents exactly one appended record and a complete,
    incremental epistemic state.
    """

    _result: ReasoningResult | None = field(default=None, repr=False)
    _previous: Key | None = field(default=None, repr=False)

    _key: Key = field(init=False, repr=False, compare=True, hash=True)

    def __post_init__(self) -> None:
        """Post init validation."""
        object.__setattr__(self, "_key", KeyAuthority.issue(self))

    def new(self, result: ReasoningResult) -> ReasoningHistory:
        """Return a new ReasoningHistory with the given result appended."""
        if not isinstance(result, ReasoningResult):
            raise TypeError(f"result should be a ReasoningResult, get {result!r}")

        return ReasoningHistory(
            _result=result,
            _previous=self._key,
        )

    def key(self) -> Key:
        """Return the identity key of this history."""
        return self._key

    def previous_key(self) -> Key | None:
        """Return the key of the previous history node, if any."""
        return self._previous

    def iter_results(self) -> Iterable[ReasoningResult]:
        """
        Explicit traversal of results (newest → oldest).

        This traversal is structural and non-epistemic.
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
        """Stream filtered results (newest → oldest)."""
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
        """Get results based on criteria."""
        results = list(self.iter_filtered_results(task=task, success=success))
        results.reverse()
        return results

    def latest(self, task: ReasoningTask | None = None) -> ReasoningResult | None:
        """Get the latest result."""
        results = self.get_results(task=task, success=None)
        return results[0] if results is not None and len(results) > 0 else None

    def __len__(self) -> int:
        """Get length of a reasoning history."""
        return len(list(self.iter_results()))
