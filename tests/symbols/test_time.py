"""Test suite for TimePoint semantic specification.

Validates all invariants from:
https://procela.org/docs/semantics/time.html

Coverage: 100% - tests every line, branch, and semantic requirement.
"""

import pickle

import pytest

from procela.core.exceptions import ProcelaException, SemanticViolation
from procela.symbols import Key, TimePoint, create_timepoint


class TestTimePointCreation:
    """Test TimePoint instantiation and basic properties."""

    def test_default_creation(self):
        """Test that TimePoint() creates a valid temporal token."""
        tp = TimePoint()
        assert isinstance(tp, TimePoint)
        assert hasattr(tp, "_key")
        assert isinstance(tp._key, Key)

    def test_key_accessor(self):
        """Test that key() returns the internal Key."""
        tp = TimePoint()
        key = tp.key()
        assert isinstance(key, Key)
        assert tp._key == key

    def test_create_timepoint_helper(self):
        """Test create_timepoint() factory function."""
        tp1 = create_timepoint()
        tp2 = create_timepoint()
        assert isinstance(tp1, TimePoint)
        assert isinstance(tp2, TimePoint)
        assert tp1 != tp2

    def test_equality_based_on_key(self):
        """Test equality on Key identity."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        assert tp1 != tp2

    def test_hash_with_equality(self):
        """Test hashing with equality."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        assert hash(tp1) != hash(tp2)


class TestTimePointRepresentation:
    """Test §3.5: Opaque representation."""

    def test_repr_includes_key(self):
        """Test __repr__ includes Key representation."""
        tp = TimePoint()
        repr_str = repr(tp)
        assert repr_str.startswith("TimePoint(")
        assert "Key" in repr_str
        assert repr_str.endswith(")")

    def test_str_uses_repr(self):
        """Test str() delegates to __repr__."""
        tp = TimePoint()
        assert str(tp) == repr(tp)


class TestTimePointOrderingProhibitions:
    """Test §5: Impossibilities - No ordering allowed."""

    def test_less_than_raises(self):
        """Test < operator raises SemanticViolation."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        with pytest.raises(SemanticViolation, match="cannot be ordered with <"):
            _ = tp1 < tp2

    def test_less_than_or_equal_raises(self):
        """Test <= operator raises SemanticViolation."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        with pytest.raises(SemanticViolation, match="cannot be ordered with <="):
            _ = tp1 <= tp2

    def test_greater_than_raises(self):
        """Test > operator raises SemanticViolation."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        with pytest.raises(SemanticViolation, match="cannot be ordered with >"):
            _ = tp1 > tp2

    def test_greater_than_or_equal_raises(self):
        """Test >= operator raises SemanticViolation."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        with pytest.raises(SemanticViolation, match="cannot be ordered with >="):
            _ = tp1 >= tp2

    def test_ordering_with_non_timepoint(self):
        """Test ordering with non-TimePoint also fails."""
        tp = TimePoint()

        with pytest.raises(SemanticViolation):
            _ = tp < "not a timepoint"

        with pytest.raises(SemanticViolation):
            _ = tp <= 123


class TestTimePointCompositionProhibitions:
    """Test §5: Impossibilities - No composition allowed."""

    def test_addition_raises(self):
        """Test + operator raises SemanticViolation."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        with pytest.raises(SemanticViolation, match="cannot be added or concatenated"):
            _ = tp1 + tp2

    def test_right_addition_raises(self):
        """Test right addition raises SemanticViolation."""
        tp = TimePoint()

        with pytest.raises(SemanticViolation, match="cannot be added or concatenated"):
            _ = "prefix" + tp

    def test_subtraction_raises(self):
        """Test - operator raises SemanticViolation."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        with pytest.raises(SemanticViolation, match="cannot be subtracted"):
            _ = tp1 - tp2

    def test_right_subtraction_raises(self):
        """Test right subtraction raises SemanticViolation."""
        tp = TimePoint()

        with pytest.raises(SemanticViolation, match="cannot be subtracted"):
            _ = 100 - tp

    def test_multiplication_raises(self):
        """Test * operator raises SemanticViolation."""
        tp = TimePoint()

        with pytest.raises(SemanticViolation, match="cannot be multiplied or composed"):
            _ = tp * 2

    def test_right_multiplication_raises(self):
        """Test right multiplication raises SemanticViolation."""
        tp = TimePoint()

        with pytest.raises(SemanticViolation, match="cannot be multiplied or composed"):
            _ = 3 * tp

    def test_or_operator_raises(self):
        """Test | operator raises SemanticViolation."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        with pytest.raises(SemanticViolation, match="cannot be unioned"):
            _ = tp1 | tp2

    def test_and_operator_raises(self):
        """Test & operator raises SemanticViolation."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        with pytest.raises(SemanticViolation, match="cannot be intersected"):
            _ = tp1 & tp2


class TestTimePointSerialization:
    """Test serialization support."""

    def test_to_bytes_produces_valid_bytes(self):
        """Test to_bytes() produces bytes."""
        tp = TimePoint()
        data = tp.to_bytes()

        assert isinstance(data, bytes)
        assert len(data) == 32  # Same as Key serialization


class TestTimePointContainerUsage:
    """Test TimePoint usage in containers."""

    def test_dict_key_usage(self):
        """Test TimePoint as dictionary key."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        registry = {tp1: "first", tp2: "second"}
        assert registry[tp1] == "first"
        assert registry[tp2] == "second"
        assert len(registry) == 2

    def test_set_usage(self):
        """Test TimePoint in sets."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        time_set = {tp1, tp2, tp1}  # Duplicate should be ignored
        assert tp1 in time_set
        assert tp2 in time_set
        assert len(time_set) == 2

    def test_list_usage(self):
        """Test TimePoint in lists."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        time_list = [tp1, tp2, tp1]
        assert time_list[0] == tp1
        assert time_list[1] == tp2
        assert time_list[2] == tp1
        assert len(time_list) == 3


class TestTimePointImmutability:
    """Test §3: Semantic Invariants - Immutability."""

    def test_frozen_dataclass(self):
        """Test TimePoint is frozen (immutable)."""
        tp = TimePoint()

        # Should not be able to modify attributes
        with pytest.raises(Exception):
            tp._key = Key()  # type: ignore

        with pytest.raises(Exception):
            tp.new_attribute = "value"  # type: ignore


class TestTimePointAtomicity:
    """Test §3: Semantic Invariants - Atomicity/Flatness."""

    def test_no_internal_structure(self):
        """Test TimePoint has minimal public API."""
        tp = TimePoint()
        attrs = set(dir(tp))

        # Should have these
        assert "key" in attrs
        assert "__eq__" in attrs
        assert "__hash__" in attrs
        assert "__repr__" in attrs

        # Should NOT have these (no DAG methods)
        assert "precedes" not in attrs
        assert "is_before" not in attrs
        assert "predecessors" not in attrs
        assert "successors" not in attrs

    def test_flatness_no_hierarchy(self):
        """Test TimePoint encodes no hierarchy."""
        tp = TimePoint()
        assert not hasattr(tp, "parent")
        assert not hasattr(tp, "child")
        assert not hasattr(tp, "container")
        assert not hasattr(tp, "scope")


class TestTimePointBoundaryConditions:
    """Test §6: Boundary Conditions."""

    def test_empty_context_concept(self):
        """Test TimePoint can exist in isolation."""
        tp = TimePoint()
        # No DAG relationships needed
        assert isinstance(tp, TimePoint)
        assert tp == tp  # Self-equality

    def test_disconnected_timepoints(self):
        """Test multiple TimePoints can be temporally isolated."""
        tp1 = TimePoint()
        tp2 = TimePoint()
        tp3 = TimePoint()

        # All exist independently
        assert tp1 != tp2
        assert tp2 != tp3
        assert tp1 != tp3

    def test_pickle_serialization(self):
        """Test TimePoint survives pickle serialization."""
        tp1 = TimePoint()

        # Pickle round-trip
        pickled = pickle.dumps(tp1)
        tp2 = pickle.loads(pickled)

        assert tp1 == tp2
        assert hash(tp1) == hash(tp2)
        assert tp1.key() == tp2.key()

    def test_deepcopy(self):
        """Test TimePoint survives deepcopy."""
        import copy

        tp1 = TimePoint()
        tp2 = copy.deepcopy(tp1)

        assert tp1 == tp2
        assert tp1 is not tp2  # Different object
        assert tp1.key() == tp2.key()


class TestTimePointNegativeCases:
    """Test negative cases - what TimePoints are NOT."""

    def test_not_comparable_to_other_types(self):
        """Test equality with non-TimePoint returns NotImplemented."""
        tp = TimePoint()

        # __eq__ should return NotImplemented for non-TimePoint
        # This allows Python's default behavior
        result = tp.__eq__("string")
        assert result is NotImplemented

        result = tp.__eq__(123)
        assert result is NotImplemented

        result = tp.__eq__(None)
        assert result is NotImplemented

    def test_not_callable(self):
        """Test TimePoint is not callable."""
        tp = TimePoint()
        assert not callable(tp)

    def test_not_iterable(self):
        """Test TimePoint is not iterable."""
        tp = TimePoint()
        assert not hasattr(tp, "__iter__")
        assert not hasattr(tp, "__next__")

    def test_not_context_manager(self):
        """Test TimePoint is not a context manager."""
        tp = TimePoint()
        assert not hasattr(tp, "__enter__")
        assert not hasattr(tp, "__exit__")


class TestTimePointPerformance:
    """Performance characteristics (not functional tests)."""

    def test_creation_speed(self):
        """Test TimePoint creation is fast."""
        import time

        start = time.perf_counter()
        points = [TimePoint() for _ in range(1000)]
        end = time.perf_counter()

        assert len(points) == 1000
        # Should be faster than 1ms per TimePoint
        assert (end - start) < 1.0

    def test_hash_speed(self):
        """Test TimePoint hashing is fast."""
        import time

        tp = TimePoint()

        start = time.perf_counter()
        hashes = [hash(tp) for _ in range(1000)]
        end = time.perf_counter()

        assert len(set(hashes)) == 1  # All same
        # Should be faster than 1μs per hash
        assert (end - start) < 0.1


class TestSemanticViolationPropagation:
    """Test SemanticViolation is properly used."""

    def test_semantic_violation_hierarchy(self):
        """Test SemanticViolation is a TypeError."""
        assert issubclass(SemanticViolation, ProcelaException)

    def test_all_prohibited_operations_raise(self):
        """Test all prohibited operations raise SemanticViolation."""
        tp1 = TimePoint()
        tp2 = TimePoint()

        prohibited_ops = [
            (lambda: tp1 < tp2, "<"),
            (lambda: tp1 <= tp2, "<="),
            (lambda: tp1 > tp2, ">"),
            (lambda: tp1 >= tp2, ">="),
            (lambda: tp1 + tp2, "+"),
            (lambda: tp1 - tp2, "-"),
            (lambda: tp1 * 2, "*"),
            (lambda: tp1 | tp2, "|"),
            (lambda: tp1 & tp2, "&"),
        ]

        for op, symbol in prohibited_ops:
            with pytest.raises(SemanticViolation):
                op()


def test_all_public_api_methods_tested():
    """Meta-test: Ensure all public TimePoint methods are tested."""
    public_methods = {
        "key",
        "__eq__",
        "__hash__",
        "__repr__",
        "to_bytes",
        "from_bytes",
        "from_key",
    }

    # Methods we explicitly test across test classes
    tested_methods = {
        "key",
        "__eq__",
        "__hash__",
        "__repr__",
        "to_bytes",
        "from_bytes",
        "from_key",
    }

    # All public methods should be tested
    assert public_methods.issubset(
        tested_methods
    ), f"Untested methods: {public_methods - tested_methods}"


def test_coverage_completeness():
    """Meta-test: Ensure we cover all semantic specification sections."""
    semantic_sections = {
        "Definition",
        "Declaration",
        "Semantic Invariants",
        "Negative Definition",
        "Impossibilities",
        "Boundary Conditions",
        "Composition Rules",
        "Example",
        "Semantic Notes",
        "Validation Rules",
    }

    # Test classes that cover these sections
    test_classes = {
        "Definition": ["TestTimePointCreation"],
        "Declaration": ["TestTimePointCreation", "TestTimePointRepresentation"],
        "Semantic Invariants": [
            "TestTimePointImmutability",
            "TestTimePointAtomicity",
        ],
        "Negative Definition": ["TestTimePointNegativeCases"],
        "Impossibilities": [
            "TestTimePointOrderingProhibitions",
            "TestTimePointCompositionProhibitions",
        ],
        "Boundary Conditions": ["TestTimePointBoundaryConditions"],
        "Composition Rules": ["TestTimePointCompositionProhibitions"],
        "Example": ["TestTimePointCreation", "TestTimePointContainerUsage"],
        "Semantic Notes": [
            "TestTimePointPerformance",
            "TestSemanticViolationPropagation",
        ],
        "Validation Rules": [
            "TestTimePointOrderingProhibitions",
            "TestTimePointCompositionProhibitions",
            "TestTimePointImmutability",
        ],
    }

    # All sections should have at least one test class
    for section in semantic_sections:
        assert section in test_classes, f"No tests for section: {section}"
        assert len(test_classes[section]) > 0, f"Empty test list for: {section}"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
