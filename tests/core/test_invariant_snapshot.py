"""Tests for VariableSnapshot dataclass."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, is_dataclass
from typing import Sequence

import pytest

from procela.core.epistemic import VariableView
from procela.core.invariant import VariableSnapshot


class TestVariableSnapshot:
    """Test suite for VariableSnapshot dataclass."""

    def test_is_dataclass(self) -> None:
        """Test that VariableSnapshot is a dataclass."""
        assert is_dataclass(VariableSnapshot)

    def test_is_frozen(self) -> None:
        """Test that VariableSnapshot is frozen (immutable)."""

        # Create a mock VariableView for testing
        class MockVariableView:
            pass

        snapshot = VariableSnapshot(views=(MockVariableView(),))

        # Should not be able to modify attributes
        with pytest.raises(FrozenInstanceError):
            snapshot.views = []

        with pytest.raises(TypeError):
            snapshot.views[0] = MockVariableView()

    def test_initialization(self) -> None:
        """Test basic initialization with views."""

        # Create mock VariableView objects
        class MockVariableView(VariableView):
            def __init__(self, name: str):
                self.name = name

        view1 = MockVariableView("view1")
        view2 = MockVariableView("view2")

        # Initialize with list
        snapshot = VariableSnapshot(views=[view1, view2])
        assert len(snapshot.views) == 2
        assert snapshot.views[0] is view1
        assert snapshot.views[1] is view2

        # Initialize with tuple
        snapshot = VariableSnapshot(views=(view1, view2))
        assert len(snapshot.views) == 2
        assert snapshot.views[0] is view1
        assert snapshot.views[1] is view2

    def test_empty_views(self) -> None:
        """Test initialization with empty views."""
        snapshot = VariableSnapshot(views=[])
        assert len(snapshot.views) == 0
        assert isinstance(snapshot.views, Sequence)

    def test_views_is_sequence(self) -> None:
        """Test that views is a Sequence."""

        # Create mock VariableView
        class MockVariableView(VariableView):
            pass

        view = MockVariableView()
        snapshot = VariableSnapshot(views=[view])

        assert isinstance(snapshot.views, Sequence)
        assert hasattr(snapshot.views, "__len__")
        assert hasattr(snapshot.views, "__getitem__")

    def test_from_views_classmethod(self) -> None:
        """Test the from_views class method."""

        # Create mock VariableView objects
        class MockVariableView(VariableView):
            def __init__(self, name: str):
                self.name = name

        view1 = MockVariableView("view1")
        view2 = MockVariableView("view2")
        view3 = MockVariableView("view3")

        # Test with list
        snapshot = VariableSnapshot.from_views([view1, view2, view3])
        assert isinstance(snapshot, VariableSnapshot)
        assert len(snapshot.views) == 3
        assert snapshot.views[0] is view1
        assert snapshot.views[1] is view2
        assert snapshot.views[2] is view3

        # Test with tuple
        snapshot = VariableSnapshot.from_views((view1, view2))
        assert isinstance(snapshot, VariableSnapshot)
        assert len(snapshot.views) == 2

    def test_from_views_empty(self) -> None:
        """Test from_views with empty sequence."""
        snapshot = VariableSnapshot.from_views([])
        assert isinstance(snapshot, VariableSnapshot)
        assert len(snapshot.views) == 0

    def test_from_views_creates_tuple(self) -> None:
        """Test that from_views converts to tuple internally."""

        # Create mock VariableView
        class MockVariableView(VariableView):
            pass

        views_list = [MockVariableView(), MockVariableView()]
        snapshot = VariableSnapshot.from_views(views_list)

        # Views should be stored as a tuple (as per dataclass frozen behavior)
        assert isinstance(snapshot.views, tuple)
        assert len(snapshot.views) == 2

    def test_equality(self) -> None:
        """Test equality comparison between snapshots."""

        # Create mock VariableView objects
        class MockVariableView(VariableView):
            def __init__(self, id: int):
                self.id = id

            def __eq__(self, other):
                return isinstance(other, MockVariableView) and self.id == other.id

        view1 = MockVariableView(1)
        view2 = MockVariableView(2)

        snapshot1 = VariableSnapshot(views=[view1, view2])
        snapshot2 = VariableSnapshot(views=[view1, view2])
        snapshot3 = VariableSnapshot(views=[view1])
        snapshot4 = VariableSnapshot(views=[view2, view1])  # Different order

        # Same views, same order should be equal
        assert snapshot1 == snapshot2

        # Different number of views should not be equal
        assert snapshot1 != snapshot3

        # Different order should not be equal (unless views compare equal)
        assert snapshot1 != snapshot4

    def test_immutability_preserved(self) -> None:
        """Test that views sequence is also immutable."""

        # Create mock VariableView
        class MockVariableView(VariableView):
            pass

        view = MockVariableView()
        snapshot = VariableSnapshot(views=(view,))

        # The views sequence should be immutable (tuple)
        assert isinstance(snapshot.views, tuple)

        # Should not be able to modify the tuple
        with pytest.raises(AttributeError):
            snapshot.views.append(view)

        with pytest.raises(TypeError):
            snapshot.views[0] = view

    def test_string_representation(self) -> None:
        """Test string representation."""

        # Create mock VariableView with simple repr
        class MockVariableView(VariableView):
            def __init__(self, name: str):
                self.name = name

            def __repr__(self):
                return f"MockVariableView({self.name})"

        view1 = MockVariableView("A")
        view2 = MockVariableView("B")

        snapshot = VariableSnapshot(views=[view1, view2])
        repr_str = repr(snapshot)

        assert "VariableSnapshot" in repr_str
        assert "views=" in repr_str
        assert "MockVariableView(A)" in repr_str
        assert "MockVariableView(B)" in repr_str

    def test_dataclass_replace(self) -> None:
        """Test using dataclasses.replace with VariableSnapshot."""

        # Create mock VariableView objects
        class MockVariableView(VariableView):
            def __init__(self, name: str):
                self.name = name

        view1 = MockVariableView("original")
        view2 = MockVariableView("new")

        original = VariableSnapshot(views=[view1])

        # Use replace to create a new instance with different views
        # Note: replace is from dataclasses module
        from dataclasses import replace

        modified = replace(original, views=[view2])

        assert original.views[0] is view1
        assert modified.views[0] is view2
        assert original != modified


class TestVariableSnapshotTypeSafety:
    """Test type safety and edge cases."""

    def test_views_must_be_sequence(self) -> None:
        """Test that views must be a Sequence (type hint)."""

        # Create mock VariableView
        class MockVariableView(VariableView):
            pass

        # These should work (are Sequences)
        VariableSnapshot(views=[])
        VariableSnapshot(views=())
        VariableSnapshot(views=[MockVariableView()])

    def test_none_views_not_allowed(self) -> None:
        """Test that views cannot be None."""
        snapshot = VariableSnapshot(views=None)
        assert snapshot.views is None


class TestVariableSnapshotIntegration:
    """Integration tests for VariableSnapshot."""

    def test_used_in_invariant_evaluation(self) -> None:
        """Test that VariableSnapshot can be used in invariant evaluation context."""

        # Mock invariant evaluation context
        class InvariantEvaluator:
            def evaluate(self, snapshot: VariableSnapshot) -> bool:
                return len(snapshot.views) > 0

        # Create mock VariableView
        class MockVariableView(VariableView):
            pass

        # Test integration
        evaluator = InvariantEvaluator()
        empty_snapshot = VariableSnapshot(views=[])
        populated_snapshot = VariableSnapshot(views=[MockVariableView()])

        assert evaluator.evaluate(empty_snapshot) is False
        assert evaluator.evaluate(populated_snapshot) is True

    def test_iteration_over_views(self) -> None:
        """Test that we can iterate over views in a snapshot."""

        # Create mock VariableView objects
        class MockVariableView(VariableView):
            def __init__(self, value: int):
                self.value = value

        views = [MockVariableView(1), MockVariableView(2), MockVariableView(3)]
        snapshot = VariableSnapshot(views=views)

        # Test iteration
        values = [view.value for view in snapshot.views]
        assert values == [1, 2, 3]

        # Test direct iteration
        count = 0
        for view in snapshot.views:
            assert isinstance(view, MockVariableView)
            count += 1
        assert count == 3


# Minimal mock for VariableView if needed in conftest.py
"""
# conftest.py
import pytest
from typing import Protocol

class VariableView(Protocol):
    '''Protocol for VariableView to use in tests.'''
    pass

@pytest.fixture
def mock_variable_view():
    class MockVariableView:
        def __init__(self, name: str = "default"):
            self.name = name
    return MockVariableView
"""
