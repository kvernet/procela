"""
Pytest suite for procela.core.reasoning.prediction.registry
100% coverage test suite for the predictor registry module.
"""

from typing import Any

import pytest

# Import the module itself to access private registry
import procela.core.reasoning.prediction.registry as registry_module

# Import the actual registry module
from procela.core.reasoning import (
    EWMAPredictor,
    LastPredictor,
    MeanPredictor,
    Predictor,
    TrendPredictor,
    available_predictors,
    clear_predictor_registry,
    get_predictor,
    get_predictors,
    has_predictor,
    register_predictor,
    unregister_predictor,
)

# ==================== TEST FIXTURES ====================


@pytest.fixture(autouse=True)
def reset_registry():
    """
    Reset the registry to its default state before each test.
    This ensures tests don't interfere with each other.
    """
    # Save original state
    original_registry = registry_module._PREDICTOR_REGISTRY.copy()

    # Clear and restore defaults
    registry_module._PREDICTOR_REGISTRY.clear()
    registry_module._PREDICTOR_REGISTRY.update(
        {
            "ewma": EWMAPredictor,
            "last": LastPredictor,
            "mean": MeanPredictor,
            "trend": TrendPredictor,
        }
    )

    yield  # Run the test

    # Restore original state
    registry_module._PREDICTOR_REGISTRY.clear()
    registry_module._PREDICTOR_REGISTRY.update(original_registry)


# Mock predictor classes for testing custom registration
class MockBasePredictor(Predictor):
    """Mock base predictor for testing."""

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs

    def predict(self, view, horizon=None):
        return [0.0]


class MockCustomPredictor(MockBasePredictor):
    """Custom predictor for testing registration."""

    pass


class FaultyPredictor(MockBasePredictor):
    """Predictor that raises TypeError on instantiation."""

    def __init__(self, required_arg: str, **kwargs: Any) -> None:
        if not required_arg:
            raise TypeError("required_arg must be provided")
        super().__init__(**kwargs)


# ==================== TEST GET_PREDICTOR ====================


class TestGetPredictor:
    """Tests for get_predictor function."""

    def test_get_existing_predictor_default(self):
        """Test get_predictor with existing predictor (no kwargs)."""
        predictor = get_predictor("ewma")
        assert isinstance(predictor, EWMAPredictor)

    def test_get_existing_predictor_with_kwargs(self):
        """Test get_predictor with constructor arguments."""
        predictor = get_predictor("ewma", alpha=0.5)
        assert isinstance(predictor, EWMAPredictor)
        assert predictor.alpha == 0.5

    def test_get_all_default_predictors(self):
        """Test getting all default predictors."""
        ewma_predictor = get_predictor("ewma", alpha=0.3)
        last_predictor = get_predictor("last", allow_none=True)
        mean_predictor = get_predictor("mean")
        trend_predictor = get_predictor("trend", extrapolation_factor=1.2)

        assert isinstance(ewma_predictor, EWMAPredictor)
        assert isinstance(last_predictor, LastPredictor)
        assert isinstance(mean_predictor, MeanPredictor)
        assert isinstance(trend_predictor, TrendPredictor)

    def test_get_nonexistent_predictor(self):
        """Test get_predictor with non-existent name."""
        with pytest.raises(KeyError) as exc_info:
            get_predictor("nonexistent")

        assert "Predictor 'nonexistent' not found" in str(exc_info.value)
        assert "Available predictors" in str(exc_info.value)

    def test_get_predictor_instantiation_error(self):
        """Test get_predictor when constructor fails."""
        # Temporarily register a faulty predictor
        original_trend = registry_module._PREDICTOR_REGISTRY["trend"]
        registry_module._PREDICTOR_REGISTRY["trend"] = FaultyPredictor

        try:
            with pytest.raises(TypeError) as exc_info:
                get_predictor("trend")  # Missing required_arg

            assert "Failed to instantiate predictor 'trend'" in str(exc_info.value)
            assert "required_arg" in str(exc_info.value)
        finally:
            # Restore original
            registry_module._PREDICTOR_REGISTRY["trend"] = original_trend


# ==================== TEST REGISTER_PREDICTOR ====================


class TestRegisterPredictor:
    """Tests for register_predictor function."""

    def test_register_new_predictor(self):
        """Test registering a new custom predictor."""
        initial_count = len(get_predictors())
        register_predictor("custom", MockCustomPredictor)

        predictors = get_predictors()
        assert len(predictors) == initial_count + 1
        assert "custom" in predictors
        assert predictors["custom"] is MockCustomPredictor

        # Verify it can be instantiated
        custom_instance = get_predictor("custom", param="test")
        assert isinstance(custom_instance, MockCustomPredictor)

    def test_register_duplicate_name(self):
        """Test registering with duplicate name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            register_predictor("ewma", MockCustomPredictor)

        assert "already registered" in str(exc_info.value)
        assert "'ewma'" in str(exc_info.value)

    def test_register_non_class_object(self):
        """Test registering a non-class object raises TypeError."""
        not_a_class = MockBasePredictor()  # Instance, not class

        with pytest.raises(TypeError) as exc_info:
            register_predictor("bad", not_a_class)  # type: ignore

        assert "must be a class" in str(exc_info.value)

    def test_register_wrong_base_class(self):
        """Test registering class not derived from Predictor."""

        class NotAPredictor:
            pass

        with pytest.raises(TypeError) as exc_info:
            register_predictor("bad", NotAPredictor)  # type: ignore

        assert "must be a subclass of Predictor" in str(exc_info.value)


# ==================== TEST UNREGISTER_PREDICTOR ====================


class TestUnregisterPredictor:
    """Tests for unregister_predictor function."""

    def test_unregister_existing_predictor(self):
        """Test unregistering an existing predictor."""
        initial_count = len(get_predictors())
        predictor_class = unregister_predictor("trend")

        predictors = get_predictors()
        assert len(predictors) == initial_count - 1
        assert "trend" not in predictors
        assert predictor_class is TrendPredictor

    def test_unregister_nonexistent_predictor(self):
        """Test unregistering a predictor that doesn't exist."""
        with pytest.raises(KeyError) as exc_info:
            unregister_predictor("nonexistent")

        assert "not found in registry" in str(exc_info.value)

    def test_unregister_and_reregister(self):
        """Test that unregistering allows re-registering with same name."""
        # Unregister
        unregister_predictor("mean")
        assert "mean" not in get_predictors()

        # Register new class with same name
        register_predictor("mean", MockCustomPredictor)
        assert get_predictors()["mean"] is MockCustomPredictor


# ==================== TEST GET_PREDICTORS ====================


class TestGetPredictors:
    """Tests for get_predictors function."""

    def test_get_predictors_returns_dict(self):
        """Test get_predictors returns a dictionary."""
        predictors = get_predictors()
        assert isinstance(predictors, dict)

    def test_get_predictors_returns_copy(self):
        """Test get_predictors returns a copy, not the original."""
        predictors = get_predictors()

        # Modify the returned dict
        predictors["modified"] = MockCustomPredictor

        # Original should not be affected
        assert "modified" not in registry_module._PREDICTOR_REGISTRY

    def test_get_predictors_includes_all_defaults(self):
        """Test get_predictors includes all default predictors."""
        predictors = get_predictors()

        assert "ewma" in predictors
        assert "last" in predictors
        assert "mean" in predictors
        assert "trend" in predictors
        assert len(predictors) == 4


# ==================== TEST AVAILABLE_PREDICTORS ====================


class TestAvailablePredictors:
    """Tests for available_predictors function."""

    def test_available_predictors_returns_set(self):
        """Test available_predictors returns a set."""
        available = available_predictors()
        assert isinstance(available, set)

    def test_available_predictors_has_defaults(self):
        """Test available_predictors includes default names."""
        available = available_predictors()

        assert "ewma" in available
        assert "last" in available
        assert "mean" in available
        assert "trend" in available
        assert len(available) == 4

    def test_available_predictors_updates_with_registry(self):
        """Test available_predictors reflects registry changes."""
        # Add new predictor
        register_predictor("custom", MockCustomPredictor)

        # Check updated
        updated = available_predictors()
        assert "custom" in updated
        assert len(updated) == 5

    def test_available_predictors_empty_after_clear(self):
        """Test available_predictors empty after clearing registry."""
        clear_predictor_registry()
        available = available_predictors()
        assert len(available) == 0


# ==================== TEST CLEAR_PREDICTOR_REGISTRY ====================


class TestClearPredictorRegistry:
    """Tests for clear_predictor_registry function."""

    def test_clear_registry_empties_registry(self):
        """Test clear_predictor_registry removes all entries."""
        assert len(get_predictors()) > 0

        clear_predictor_registry()

        assert len(get_predictors()) == 0
        assert len(available_predictors()) == 0

    def test_clear_registry_and_rebuild(self):
        """Test registry can be rebuilt after clearing."""
        # Clear
        clear_predictor_registry()
        assert len(get_predictors()) == 0

        # Add new predictors
        register_predictor("predictor1", MockCustomPredictor)
        register_predictor("predictor2", MockCustomPredictor)

        # Verify rebuild
        assert len(get_predictors()) == 2


# ==================== TEST HAS_PREDICTOR ====================


class TestHasPredictor:
    """Tests for has_predictor function."""

    def test_has_predictor_existing(self):
        """Test has_predictor returns True for existing predictors."""
        assert has_predictor("ewma") is True
        assert has_predictor("last") is True
        assert has_predictor("mean") is True
        assert has_predictor("trend") is True

    def test_has_predictor_nonexistent(self):
        """Test has_predictor returns False for non-existent predictor."""
        assert has_predictor("nonexistent") is False

    def test_has_predictor_after_changes(self):
        """Test has_predictor reflects registry modifications."""
        # Initially false
        assert not has_predictor("dynamic")

        # Add
        register_predictor("dynamic", MockCustomPredictor)
        assert has_predictor("dynamic")

        # Remove
        unregister_predictor("dynamic")
        assert not has_predictor("dynamic")


# ==================== TEST INTEGRATION ====================


class TestIntegration:
    """Integration tests covering multiple functions together."""

    def test_full_lifecycle_integration(self):
        """Test complete lifecycle of a predictor in the registry."""
        # 1. Start with default registry
        default_count = len(get_predictors())

        # 2. Create and register custom predictor
        class IntegrationPredictor(Predictor):
            def __init__(self, special_value: int = 0, **kwargs: Any):
                self.special_value = special_value
                super().__init__(**kwargs)

            def predict(self, view, horizon=None):
                return [float(self.special_value)]

        register_predictor("integration", IntegrationPredictor)
        assert len(get_predictors()) == default_count + 1

        # 3. Get and use the predictor
        instance = get_predictor("integration", special_value=42)
        assert isinstance(instance, IntegrationPredictor)
        assert instance.special_value == 42

        # 4. Check it's in available list
        assert "integration" in available_predictors()

        # 5. Unregister it
        unregistered_class = unregister_predictor("integration")
        assert unregistered_class is IntegrationPredictor
        assert not has_predictor("integration")

    def test_error_recovery_flow(self):
        """Test error handling and recovery."""
        # Try to get non-existent (should fail)
        with pytest.raises(KeyError):
            get_predictor("missing")

        # Registry should still be intact
        assert len(get_predictors()) == 4

        # Try to register invalid class (should fail)
        with pytest.raises(TypeError):
            register_predictor("bad", "not a class")  # type: ignore

        # Registry should still be intact
        assert len(get_predictors()) == 4

        # Valid operations should still work
        predictor = get_predictor("ewma", alpha=0.3)
        assert isinstance(predictor, EWMAPredictor)


# ==================== TEST EDGE CASES ====================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_register_with_empty_string_name(self):
        """Test registering with empty string as name."""
        register_predictor("", MockCustomPredictor)
        assert has_predictor("")

        # Should be able to get it
        instance = get_predictor("")
        assert isinstance(instance, MockCustomPredictor)

        # Clean up
        unregister_predictor("")

    def test_special_characters_in_name(self):
        """Test registering with special characters in name."""
        special_names = ["predictor-2.0", "my_predictor", "predictor.v1"]

        for name in special_names:
            register_predictor(name, MockCustomPredictor)
            assert has_predictor(name)
            instance = get_predictor(name)
            assert isinstance(instance, MockCustomPredictor)
            unregister_predictor(name)

    def test_case_sensitivity(self):
        """Test that registry is case-sensitive."""
        register_predictor("Trend", MockCustomPredictor)  # Capital T

        # "Trend" and "trend" should be different
        assert has_predictor("Trend")
        assert has_predictor("trend")  # Lowercase exists by default
        assert get_predictors()["Trend"] is MockCustomPredictor
        assert get_predictors()["trend"] is TrendPredictor


# ==================== TEST COVERAGE VERIFICATION ====================


def test_all_functions_exist():
    """Verify all documented functions exist and are callable."""
    # Test all public functions
    functions = [
        get_predictor,
        register_predictor,
        unregister_predictor,
        get_predictors,
        available_predictors,
        clear_predictor_registry,
        has_predictor,
    ]

    for func in functions:
        assert callable(func)

    # Verify module has private registry
    assert hasattr(registry_module, "_PREDICTOR_REGISTRY")
    assert isinstance(registry_module._PREDICTOR_REGISTRY, dict)


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
