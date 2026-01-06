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

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Optional

from ....symbols.key import Key
from ....symbols.time import TimePoint
from .record import VariableRecord


@dataclass(frozen=True)
class VariableHistory:
    """
    Immutable history of VariableRecords for a variable.

    Example:
    -------
        >>> from procela.symbols import Key
        >>> from procela.core.memory import VariableRecord, VariableHistory
        >>>
        >>> # Create empty history
        >>> history = VariableHistory()
        >>>
        >>> # Add records over time
        >>> key1 = Key()
        >>> record1 = VariableRecord(value=42, key=key1)
        >>> history1 = history.add_record(record1)
        >>>
        >>> record2 = VariableRecord(value=43, key=key1)
        >>> history2 = history1.add_record(record2)
        >>>
        >>> # Query records
        >>> len(history2)
        2
        >>> history2.get_records(key=key1)
        [VariableRecord(...), VariableRecord(...)]
        >>> history2.latest(key1).value
        43
        >>> history2.all_keys()
        {<Key>}
    """

    _records: tuple[VariableRecord, ...] = field(default_factory=tuple, repr=False)

    def __post_init__(self) -> None:
        """
        Validate record invariants.

        Ensures confidence values are within valid bounds if provided.

        Raises
        ------
            TypeError: If _records is not a tuple
        """
        if not isinstance(self._records, tuple):
            raise TypeError(f"_records must be a tuple, got {self._records!r}")

        for record in self._records:
            if not isinstance(record, VariableRecord):
                raise TypeError(f"record must be a VariableRecord, got {record!r}")

    def add_record(self, record: VariableRecord) -> VariableHistory:
        """
        Return a new VariableHistory with `record` appended.

        Creates a new immutable history containing all previous records
        plus the new record. The original history remains unchanged.

        Parameters
        ----------
            record: VariableRecord to add.

        Returns
        -------
            VariableHistory: New instance including the new record.

        Example
        -------
            >>> history = VariableHistory()
            >>> new_history = history.add_record(record)
            >>> len(new_history) == len(history) + 1
            True
        """
        if not isinstance(record, VariableRecord):
            raise TypeError(f"record must be a VariableRecord, got {record!r}")
        return VariableHistory(self._records + (record,))

    def get_records(
        self,
        key: Optional[Key] = None,
        time: Optional[TimePoint] = None,
        source: Optional[Key] = None,
    ) -> list[VariableRecord]:
        """
        Query records optionally filtered by key, time, or source.

        Returns all records matching the specified filters. Multiple
        filters are combined with AND logic. Empty filter returns
        all records in chronological order.

        Parameters
        ----------
            key: Optional Key to filter by record identity
            time: Optional TimePoint to filter by temporal position
            source: Optional Key to filter by record source/provenance

        Returns
        -------
            list[VariableRecord]: Filtered records in chronological order.

        Example
        -------
            >>> # Get all records from specific source
            >>> source_key = Key()
            >>> records = history.get_records(source=source_key)
            >>>
            >>> # Get records at specific time
            >>> time_point = TimePoint()
            >>> records = history.get_records(time=time_point)
            >>>
            >>> # Combine filters
            >>> records = history.get_records(key=source_key, time=time_point)
        """
        results = list(self._records)
        if key is not None:
            results = [r for r in results if r.key() == key]
        if time is not None:
            results = [r for r in results if r.time == time]
        if source is not None:
            results = [r for r in results if r.source == source]
        return results

    def latest(self, key: Key) -> Optional[VariableRecord]:
        """
        Return the most recent record for the given Key.

        Searches records in reverse chronological order to find the
        most recent entry with the specified key. Returns None if no
        matching records exist.

        Parameters
        ----------
            key: Key identifying which record series to examine

        Returns
        -------
            Optional[VariableRecord]: Most recent matching record,
                                     or None if no matches exist.

        Example
        -------
            >>> key = Key()
            >>> latest = history.latest(key)
            >>> if latest:
            ...     print(f"Latest value: {latest.value}")
        """
        for record in reversed(self._records):
            if record.key() == key:
                return record
        return None

    def all_keys(self) -> set[Key]:
        """
        Return all Keys present in this history.

        Returns
        -------
            set[Key]: Unique keys of all records in this history.

        Example
        -------
            >>> keys = history.all_keys()
            >>> for key in keys:
            ...     print(f"Variable {key} has records")
        """
        return {r.key() for r in self._records}

    def __len__(self) -> int:
        """
        Return the number of records in this history.

        Returns
        -------
            int: Total count of VariableRecords.

        Example
        -------
            >>> len(history)
            0
        """
        return len(self._records)

    def __iter__(self) -> Iterator[VariableRecord]:
        """
        Return iterator over records in chronological order.

        Enables direct iteration over the history:

        Example
        -------
            >>> for record in history:
            ...     print(record.value)

        Returns
        -------
            iterator: Iterator yielding VariableRecords in insertion order.
        """
        return iter(self._records)
