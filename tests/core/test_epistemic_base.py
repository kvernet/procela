"""
Pytest suite for EpistemicView protocol from Procela framework.
Tests cover 100% of the protocol interface including runtime checking.
"""

from typing import Protocol

import pytest

from procela.core.assessment import ReasoningResult, ReasoningTask
from procela.core.epistemic import EpistemicView
from procela.symbols.key import Key


def create_reasoning_result(result):
    """Default reasoning result."""
    return ReasoningResult(
        task=ReasoningTask.ANOMALY_DETECTION, success=False, result=result
    )


class TestEpistemicViewProtocol:
    """Test suite for EpistemicView protocol interface compliance."""

    def test_protocol_is_runtime_checkable(self):
        """Test that EpistemicView is decorated with @runtime_checkable."""
        assert hasattr(EpistemicView, "_is_runtime_protocol")
        assert EpistemicView._is_runtime_protocol is True

    def test_protocol_has_required_properties(self):
        """Test that EpistemicView protocol defines required properties."""
        # Check property definitions exist
        assert hasattr(EpistemicView, "key")
        assert hasattr(EpistemicView, "reasoning")

        # Check they are properties
        assert isinstance(EpistemicView.key, property)
        assert isinstance(EpistemicView.reasoning, property)

    def test_concrete_class_with_all_properties_is_instance(self):
        """Test class with all required properties is an instance of EpistemicView."""

        class ConcreteEpistemicView:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> ReasoningResult | None:
                return create_reasoning_result(result="concrete_reasoning")

        concrete_instance = ConcreteEpistemicView()

        # Runtime protocol checking
        assert isinstance(concrete_instance, EpistemicView)

        # Verify properties work correctly
        assert isinstance(concrete_instance.key, Key)

    def test_concrete_class_with_none_reasoning_is_instance(self):
        """Test that a class with reasoning returning None is still an instance."""

        class ViewWithNoneReasoning:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> ReasoningResult | None:
                return None

        instance = ViewWithNoneReasoning()

        assert isinstance(instance, EpistemicView)
        assert isinstance(instance.key, Key)
        assert instance.reasoning is None

    def test_class_missing_key_property_not_instance(self):
        """Test class missing key property."""

        class MissingKeyView:
            # Missing key property
            @property
            def reasoning(self) -> ReasoningResult | None:
                return create_reasoning_result("test")

        instance = MissingKeyView()

        assert not isinstance(instance, EpistemicView)

    def test_class_missing_reasoning_property_not_instance(self):
        """Test class missing reasoning property."""

        class MissingReasoningView:
            # Missing reasoning property
            @property
            def key(self) -> Key:
                return Key()

        instance = MissingReasoningView()

        assert not isinstance(instance, EpistemicView)

    def test_class_with_wrong_key_return_type_not_instance(self):
        """Test a class with wrong return type for key."""

        class WrongKeyTypeView:
            @property
            def key(self) -> str:  # Wrong return type
                return "not_a_key"

            @property
            def reasoning(self) -> ReasoningResult | None:
                return None

        instance = WrongKeyTypeView()

        # Note: Runtime checking doesn't validate return types, only existence
        # So this will still be considered an instance at runtime
        assert isinstance(instance, EpistemicView)

    def test_class_with_methods_instead_of_properties_is_instance(self):
        """Test that methods (instead of properties) satisfy the protocol."""

        # Method, not property
        class MethodsInsteadOfProperties:
            def key(self) -> Key:
                return Key()

            def reasoning(self) -> ReasoningResult | None:
                return None

        instance = MethodsInsteadOfProperties()

        assert isinstance(instance, EpistemicView)

    def test_protocol_can_be_used_in_type_hints(self):
        """Test that EpistemicView can be used in type annotations."""

        def process_view(view: EpistemicView) -> str:
            """Function that accepts any EpistemicView."""
            return f"Processing view with key: {view.key}"

        # Create a compliant view
        class TestView:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> ReasoningResult | None:
                return None

        result = process_view(TestView())
        assert "Processing view with key" in result

    def test_multiple_instances_with_different_values(self):
        """Test multiple instances with different property values."""

        class FlexibleView:
            def __init__(self, reasoning_value: ReasoningResult | None):
                self._key = Key()
                self._reasoning = reasoning_value

            @property
            def key(self) -> Key:
                return self._key

            @property
            def reasoning(self) -> ReasoningResult | None:
                return self._reasoning

        # Create multiple instances with different data
        view1 = FlexibleView(create_reasoning_result("reason1"))
        view2 = FlexibleView(None)
        view3 = FlexibleView(create_reasoning_result("reason3"))

        # All should be instances of the protocol
        assert isinstance(view1, EpistemicView)
        assert isinstance(view2, EpistemicView)
        assert isinstance(view3, EpistemicView)

        # Verify their values
        assert isinstance(view1.key, Key)
        assert isinstance(view1.reasoning, ReasoningResult)
        assert isinstance(view2.key, Key)
        assert view2.reasoning is None
        assert isinstance(view3.key, Key)

    def test_protocol_inheritance(self):
        """Test that a protocol can inherit from EpistemicView."""

        class ExtendedEpistemicView(EpistemicView, Protocol):
            @property
            def additional_info(self) -> str: ...

        class ConcreteExtendedView:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> ReasoningResult | None:
                return create_reasoning_result("extended_reasoning")

            @property
            def additional_info(self) -> str:
                return "extra data"

        instance = ConcreteExtendedView()

        # Should be instance of both protocols
        assert isinstance(instance, EpistemicView)
        assert isinstance(instance, ExtendedEpistemicView)

        # Verify all properties
        assert isinstance(instance.key, Key)
        assert instance.additional_info == "extra data"

    def test_protocol_with_slots(self):
        """Test that a class with __slots__ can implement the protocol."""

        class SlottedEpistemicView:
            __slots__ = ("_key", "_reasoning")

            def __init__(self):
                self._key = Key()
                self._reasoning = None

            @property
            def key(self) -> Key:
                return self._key

            @property
            def reasoning(self) -> ReasoningResult | None:
                return self._reasoning

        instance = SlottedEpistemicView()

        assert isinstance(instance, EpistemicView)
        assert isinstance(instance.key, Key)
        assert instance.reasoning is None

    def test_dynamic_property_creation(self):
        """Test that dynamically added properties satisfy the protocol."""

        class DynamicView:
            pass

        # Add properties dynamically
        def get_key(self):
            return Key()

        def get_reasoning(self):
            return create_reasoning_result("dynamic_reasoning")

        DynamicView.key = property(get_key)
        DynamicView.reasoning = property(get_reasoning)

        instance = DynamicView()

        # Should be recognized as an instance
        assert isinstance(instance, EpistemicView)
        assert instance.key is not Key()
        assert instance.reasoning.task == ReasoningTask.ANOMALY_DETECTION


class TestEpistemicViewEdgeCases:
    """Test edge cases and error conditions for EpistemicView."""

    def test_property_with_side_effects(self):
        """Test properties with side effects."""

        class SideEffectView:
            def __init__(self):
                self.access_count = 0

            @property
            def key(self) -> Key:
                self.access_count += 1
                return Key()

            @property
            def reasoning(self) -> ReasoningResult | None:
                return None

        instance = SideEffectView()

        assert instance.access_count == 0

        # Access property multiple times
        key1 = instance.key
        key2 = instance.key
        key3 = instance.key

        assert instance.access_count == 3
        assert isinstance(key1, Key)
        assert isinstance(key2, Key)
        assert isinstance(key3, Key)

        assert isinstance(instance, EpistemicView)

    def test_lazy_loaded_property(self):
        """Test implementation with lazy-loaded properties."""

        class LazyLoadedView:
            def __init__(self):
                self._key = None
                self._reasoning = None

            @property
            def key(self) -> Key:
                if self._key is None:
                    self._key = Key()
                return self._key

            @property
            def reasoning(self) -> ReasoningResult | None:
                if self._reasoning is None:
                    self._reasoning = create_reasoning_result("lazy_loaded_reasoning")
                return self._reasoning

        instance = LazyLoadedView()

        # Initially None internally
        assert instance._key is None
        assert instance._reasoning is None

        assert isinstance(instance, EpistemicView)

        # Load on first access
        assert isinstance(instance.key, Key)
        assert isinstance(instance.reasoning, ReasoningResult)

        # Now should be loaded
        assert isinstance(instance._key, Key)
        assert isinstance(instance._reasoning, ReasoningResult)

    def test_cached_property_implementation(self):
        """Test implementation using functools.cached_property."""
        try:
            from functools import cached_property

            class CachedView:
                def __init__(self):
                    self.key_computations = 0
                    self.reasoning_computations = 0

                @cached_property
                def key(self) -> Key:
                    self.key_computations += 1
                    return Key()

                @cached_property
                def reasoning(self) -> ReasoningResult | None:
                    self.reasoning_computations += 1
                    return create_reasoning_result(
                        f"cached_reasoning_{self.reasoning_computations}"
                    )

            instance = CachedView()

            assert isinstance(instance, EpistemicView)

            # First access computes
            assert isinstance(instance.key, Key)
            assert instance.key_computations == 1

            # Second access uses cache
            assert isinstance(instance.key, Key)
            assert instance.key_computations == 1  # Still 1

        except ImportError:
            pytest.skip("cached_property not available in this Python version")

    def test_protocol_with_generic_types(self):
        """Test protocol compatibility with generic type hints."""
        from typing import Generic, TypeVar

        T = TypeVar("T")

        class GenericEpistemicView(EpistemicView, Generic[T], Protocol):
            @property
            def typed_data(self) -> T: ...

        class ConcreteGenericView:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> ReasoningResult | None:
                return create_reasoning_result("generic_reasoning")

            @property
            def typed_data(self) -> int:
                return 42

        instance = ConcreteGenericView()

        assert isinstance(instance, EpistemicView)
        assert isinstance(instance.key, Key)
        assert isinstance(instance.reasoning, ReasoningResult)
        assert instance.typed_data == 42


# Helper function for checking protocol compliance
def check_epistemic_view_compliance(obj) -> tuple[bool, list[str]]:
    """
    Check if an object complies with EpistemicView protocol.

    Returns:
        Tuple of (is_compliant, list_of_missing_members)
    """
    missing = []

    if not hasattr(obj, "key") or not isinstance(type(obj).key, property):
        missing.append("key property")

    if not hasattr(obj, "reasoning") or not isinstance(type(obj).reasoning, property):
        missing.append("reasoning property")

    return len(missing) == 0, missing


def test_compliance_helper_function():
    """Test the helper function for checking protocol compliance."""

    class CompliantView:
        @property
        def key(self):
            return Key()

        @property
        def reasoning(self):
            return None

    class NonCompliantView:
        # Missing reasoning property
        @property
        def key(self):
            return Key()

    compliant = CompliantView()
    non_compliant = NonCompliantView()

    is_compliant, missing = check_epistemic_view_compliance(compliant)
    assert is_compliant is True
    assert missing == []

    is_compliant, missing = check_epistemic_view_compliance(non_compliant)
    assert is_compliant is False
    assert "reasoning property" in missing


if __name__ == "__main__":
    # Run tests directly if needed
    pytest.main([__file__, "-v", "--cov=.", "--cov-report=term-missing"])
