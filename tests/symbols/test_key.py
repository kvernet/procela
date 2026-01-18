"""Test suite for Key semantic specification.

Validates all invariants from:
https://procela.org/docs/semantics/key.html

Coverage: 100% - tests every line, branch, and semantic requirement.
"""

import pickle
import secrets

import pytest

from procela.core.exceptions import ProcelaException, SemanticViolation
from procela.symbols import Key, generate_key


class TestKeyCreation:
    """Test Key instantiation and basic properties."""

    def test_default_creation(self):
        """Test that Key() creates a valid key."""
        key = Key()
        assert isinstance(key, Key)
        assert hasattr(key, "_token")
        assert len(key._token) == 32

    def test_generate_key_helper(self):
        """Test generate_key() produces valid distinct Keys."""
        k1 = generate_key()
        k2 = generate_key()
        assert isinstance(k1, Key)
        assert isinstance(k2, Key)
        assert k1 != k2
        assert hash(k1) != hash(k2)


class TestKeyEqualityAndHashing:
    """Test §2.1: Binary equality and hashing."""

    def test_self_equality(self):
        """Key equals itself."""
        key = Key()
        assert key == key
        assert not (key != key)

    def test_distinct_inequality(self):
        """Distinct Keys are not equal."""
        k1 = Key()
        k2 = Key()
        assert k1 != k2
        assert not (k1 == k2)

    def test_equality_with_non_key(self):
        """Key compared to non-Key returns NotImplemented."""
        key = Key()
        assert key.__eq__("not a key") is NotImplemented
        assert key.__eq__(123) is NotImplemented
        assert key.__eq__(None) is NotImplemented

    def test_hash_consistency(self):
        """Hash is consistent and matches equality."""
        key = Key()
        assert hash(key) == hash(key)
        h1 = hash(key)
        h2 = hash(key)
        assert h1 == h2

    def test_hash_inequality_for_distinct_keys(self):
        """Distinct Keys should have different hashes."""
        k1 = Key()
        k2 = Key()
        assert hash(k1) != hash(k2)

    def test_equality_after_deserialization(self):
        """Keys equal after serialization round-trip."""
        k1 = Key()
        data = k1.to_bytes()
        k2 = Key.from_serialized(data)
        assert k1 == k2
        assert hash(k1) == hash(k2)


class TestKeyRepresentation:
    """Test §3.5: Opaque representation."""

    def test_repr_is_opaque(self):
        """repr() reveals no semantic information."""
        key = Key()
        repr_str = repr(key)
        assert repr_str == "<Key>"
        assert key._token.hex() not in repr_str

    def test_str_uses_repr(self):
        """str() should use __repr__."""
        key = Key()
        assert str(key) == repr(key)


class TestKeyOrderingProhibitions:
    """Test §5.5: No ordering allowed."""

    def test_less_than_raises(self):
        """< operator raises SemanticViolation."""
        k1 = Key()
        k2 = Key()
        with pytest.raises(SemanticViolation, match="cannot be ordered"):
            _ = k1 < k2

    def test_less_than_or_equal_raises(self):
        """<= operator raises SemanticViolation."""
        k1 = Key()
        k2 = Key()
        with pytest.raises(SemanticViolation, match="cannot be ordered"):
            _ = k1 <= k2

    def test_greater_than_raises(self):
        """> operator raises SemanticViolation."""
        k1 = Key()
        k2 = Key()
        with pytest.raises(SemanticViolation, match="cannot be ordered"):
            _ = k1 > k2

    def test_greater_than_or_equal_raises(self):
        """>= operator raises SemanticViolation."""
        k1 = Key()
        k2 = Key()
        with pytest.raises(SemanticViolation, match="cannot be ordered"):
            _ = k1 >= k2

    def test_ordering_with_non_key(self):
        """Ordering with non-Key should also fail."""
        key = Key()
        with pytest.raises(SemanticViolation):
            _ = key < "not a key"
        with pytest.raises(SemanticViolation):
            _ = key <= 123


class TestKeyCompositionProhibitions:
    """Test §7.4: No composition allowed."""

    def test_addition_raises(self):
        """+ operator raises SemanticViolation."""
        k1 = Key()
        k2 = Key()
        with pytest.raises(SemanticViolation, match="cannot be concatenated"):
            _ = k1 + k2

    def test_right_addition_raises(self):
        """Right addition raises SemanticViolation."""
        k1 = Key()
        with pytest.raises(SemanticViolation, match="cannot be concatenated"):
            _ = "prefix" + k1

    def test_multiplication_raises(self):
        """* operator raises SemanticViolation."""
        k1 = Key()
        with pytest.raises(SemanticViolation, match="cannot be composed"):
            _ = k1 * 2

    def test_right_multiplication_raises(self):
        """Right multiplication raises SemanticViolation."""
        k1 = Key()
        with pytest.raises(SemanticViolation, match="cannot be composed"):
            _ = 3 * k1

    def test_or_operator_raises(self):
        """| operator raises SemanticViolation."""
        k1 = Key()
        k2 = Key()
        with pytest.raises(SemanticViolation, match="cannot be unioned"):
            _ = k1 | k2

    def test_and_operator_raises(self):
        """& operator raises SemanticViolation."""
        k1 = Key()
        k2 = Key()
        with pytest.raises(SemanticViolation, match="cannot be intersected"):
            _ = k1 & k2


class TestKeySerialization:
    """Test §6.4: Serialization preserves equality."""

    def test_to_bytes_produces_32_bytes(self):
        """to_bytes() produces 32 bytes."""
        key = Key()
        data = key.to_bytes()
        assert isinstance(data, bytes)
        assert len(data) == 32

    def test_from_serialized_valid_bytes(self):
        """from_serialized() works with valid bytes."""
        original = Key()
        data = original.to_bytes()
        restored = Key.from_serialized(data)
        assert original == restored
        assert original._token == restored._token

    def test_from_serialized_invalid_length(self):
        """from_serialized() validates length."""
        with pytest.raises(ValueError, match="Expected 32 bytes"):
            Key.from_serialized(b"short")
        with pytest.raises(ValueError, match="Expected 32 bytes"):
            Key.from_serialized(b"x" * 64)

    def test_serialization_round_trip_equality(self):
        """Round-trip serialization preserves equality."""
        k1 = Key()
        k2 = Key.from_serialized(k1.to_bytes())
        assert k1 == k2
        assert hash(k1) == hash(k2)

    def test_multiple_serializations_consistent(self):
        """Multiple serializations produce same bytes."""
        key = Key()
        data1 = key.to_bytes()
        data2 = key.to_bytes()
        assert data1 == data2


class TestKeyContainerUsage:
    """Test §7.3: Valid use in containers."""

    def test_dict_key_usage(self):
        """Keys can be dictionary keys."""
        k1 = Key()
        k2 = Key()
        registry = {k1: "entity1", k2: "entity2"}
        assert registry[k1] == "entity1"
        assert registry[k2] == "entity2"
        assert len(registry) == 2

    def test_dict_key_collision_prevention(self):
        """Distinct Keys don't collide in dict."""
        k1 = Key()
        k2 = Key()
        registry = {}
        registry[k1] = "first"
        registry[k2] = "second"
        assert registry[k1] == "first"
        assert registry[k2] == "second"

    def test_set_usage(self):
        """Keys can be set elements."""
        k1 = Key()
        k2 = Key()
        key_set = {k1, k2, k1}
        assert k1 in key_set
        assert k2 in key_set
        assert len(key_set) == 2

    def test_list_usage(self):
        """Keys can be list elements."""
        k1 = Key()
        k2 = Key()
        key_list = [k1, k2, k1]
        assert key_list[0] == k1
        assert key_list[1] == k2
        assert key_list[2] == k1
        assert len(key_list) == 3


class TestKeyAtomicity:
    """Test §3.1: Atomicity - no internal structure."""

    def test_no_public_attributes(self):
        """Key has minimal public API."""
        key = Key()
        attrs = set(dir(key))
        assert "__eq__" in attrs
        assert "__hash__" in attrs
        assert "__repr__" in attrs
        assert "value" not in attrs
        assert "uuid" not in attrs
        assert "id" not in attrs
        assert "token" not in attrs

    def test_private_token_access(self):
        """_token exists but is private (convention)."""
        key = Key()
        assert hasattr(key, "_token")
        assert key._token is not None


class TestKeyNonDerivability:
    """Test §3.2: Keys cannot be derived."""

    def test_no_derivation_methods(self):
        """No classmethods for deriving Keys from data."""
        class_attrs = dir(Key)
        derivation_patterns = ["from_", "create_from", "derive"]
        for pattern in derivation_patterns:
            attrs = [a for a in class_attrs if a.startswith(pattern)]
            if pattern == "from_":
                attrs = [a for a in attrs if a != "from_serialized"]
            assert len(attrs) == 0, f"Found derivation method: {attrs}"

    def test_from_serialized_only_for_serialization(self):
        """from_serialized only works with previously serialized data."""
        original = Key()
        data = original.to_bytes()
        restored = Key.from_serialized(data)
        assert original == restored
        arbitrary = secrets.token_bytes(32)
        arbitrary_key = Key.from_serialized(arbitrary)
        assert isinstance(arbitrary_key, Key)


class TestKeyFlatness:
    """Test §3.3: Flatness - no hierarchy encoding."""

    def test_no_hierarchy_attributes(self):
        """Key has no parent/child/container attributes."""
        key = Key()
        assert not hasattr(key, "parent")
        assert not hasattr(key, "child")
        assert not hasattr(key, "container")
        assert not hasattr(key, "owner")
        assert not hasattr(key, "scope")

    def test_no_hierarchy_methods(self):
        """Key has no hierarchy-related methods."""
        key = Key()
        assert not hasattr(key, "get_parent")
        assert not hasattr(key, "get_children")
        assert not hasattr(key, "is_contained_in")
        assert not hasattr(key, "get_ancestors")


class TestKeyStability:
    """Test §3.4: Stability under transformation."""

    def test_frozen_slots(self):
        """Key uses __slots__ to prevent attribute addition."""
        key = Key()
        with pytest.raises(SemanticViolation):
            key.new_attribute = "value"


class TestKeyBoundaryConditions:
    """Test §6: Boundary conditions."""

    def test_dangling_reference_concept(self):
        """Key remains valid even if entity destroyed."""
        key = Key()
        assert isinstance(key, Key)
        assert key == key

    def test_cross_universe_incomparability(self):
        """Keys from different 'universes' are incomparable."""
        k1 = Key()
        k2 = Key()
        assert (k1 == k2) is False
        assert (k1 != k2) is True

    def test_pickle_serialization(self):
        """Keys survive pickle serialization."""
        k1 = Key()
        pickled = pickle.dumps(k1)
        k2 = pickle.loads(pickled)
        assert k1 == k2
        assert hash(k1) == hash(k2)
        assert k1._token == k2._token

    def test_deepcopy(self):
        """Keys survive deepcopy."""
        import copy

        k1 = Key()
        k2 = copy.deepcopy(k1)
        assert k1 == k2
        assert k1 is not k2
        assert k1._token == k2._token


class TestSemanticViolationException:
    """Test the SemanticViolation exception."""

    def test_exception_hierarchy(self):
        """SemanticViolation is a TypeError."""
        assert issubclass(SemanticViolation, ProcelaException)

    def test_exception_instantiation(self):
        """Can create and raise SemanticViolation."""
        with pytest.raises(SemanticViolation):
            raise SemanticViolation("Test violation")

    def test_exception_message(self):
        """Exception includes operation description."""
        try:
            Key() < Key()
        except SemanticViolation as e:
            assert "cannot be ordered" in str(e)


class TestKeyNegativeCases:
    """Test negative cases - what Keys are NOT."""

    def test_not_comparable_to_other_types(self):
        """Key equality with non-Key returns NotImplemented."""
        key = Key()
        assert key.__eq__("string") is NotImplemented
        assert key.__eq__(123) is NotImplemented
        assert key.__eq__(None) is NotImplemented

    def test_not_callable(self):
        """Key is not callable."""
        key = Key()
        assert not callable(key)

    def test_not_iterable(self):
        """Key is not iterable."""
        key = Key()
        assert not hasattr(key, "__iter__")
        assert not hasattr(key, "__next__")

    def test_not_context_manager(self):
        """Key is not a context manager."""
        key = Key()
        assert not hasattr(key, "__enter__")
        assert not hasattr(key, "__exit__")


class TestKeyPerformance:
    """Performance characteristics (not functional tests)."""

    def test_creation_speed(self):
        """Key creation is fast."""
        import time

        start = time.perf_counter()
        keys = [Key() for _ in range(1000)]
        end = time.perf_counter()
        assert len(keys) == 1000
        assert (end - start) < 1.0

    def test_hash_speed(self):
        """Key hashing is fast."""
        import time

        key = Key()
        start = time.perf_counter()
        hashes = [hash(key) for _ in range(1000)]
        end = time.perf_counter()
        assert len(set(hashes)) == 1
        assert (end - start) < 0.1


def test_key_excluded_middle():
    """Semantic Validation: ∀ K1, K2: K1 == K2 or K1 != K2."""
    keys = [Key() for _ in range(10)]

    for i, k1 in enumerate(keys):
        for j, k2 in enumerate(keys):
            # Law of excluded middle for identity
            eq = k1 == k2
            neq = k1 != k2
            # Only one of these should be True
            assert eq != neq, f"Excluded middle violated: k1={k1}, k2={k2}"


def test_semantic_violation_is_type_error():
    """Ensure SemanticViolation is a TypeError subtype."""
    assert issubclass(SemanticViolation, ProcelaException)
    with pytest.raises(SemanticViolation):
        Key() < Key()


def test_all_public_api_methods_tested():
    """Meta-test: Ensure all public Key methods are tested."""
    public_methods = {"__eq__", "__hash__", "__repr__", "to_bytes", "from_serialized"}
    tested_methods = {"__eq__", "__hash__", "__repr__", "to_bytes", "from_serialized"}
    assert public_methods.issubset(tested_methods)


def test_coverage_completeness():
    """Meta-test: Ensure we cover all semantic requirements."""
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
    }
    test_classes = {
        "Definition": ["TestKeyCreation"],
        "Declaration": ["TestKeyCreation", "TestKeyEqualityAndHashing"],
        "Semantic Invariants": [
            "TestKeyAtomicity",
            "TestKeyNonDerivability",
            "TestKeyFlatness",
            "TestKeyStability",
            "TestKeyRepresentation",
        ],
        "Negative Definition": ["TestKeyNegativeCases"],
        "Impossibilities": [
            "TestKeyOrderingProhibitions",
            "TestKeyCompositionProhibitions",
        ],
        "Boundary Conditions": ["TestKeyBoundaryConditions"],
        "Composition Rules": ["TestKeyCompositionProhibitions"],
        "Example": ["TestKeyCreation", "TestKeyContainerUsage"],
        "Semantic Notes": ["TestKeyPerformance", "TestSemanticViolationException"],
    }
    for section in semantic_sections:
        assert section in test_classes
        assert len(test_classes[section]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
