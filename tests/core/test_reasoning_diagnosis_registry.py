"""
Pytest suite for procela.core.reasoning.diagnosis.registry
100% coverage test with actual module imports
"""

import pytest

from procela.core.reasoning import (
    _DIAGNOSER_REGISTRY,
    Diagnoser,
    available_diagnosers,
    clear_diagnoser_registry,
    get_diagnoser,
    get_diagnosers,
    has_diagnoser,
    register_diagnoser,
    unregister_diagnoser,
)


@pytest.fixture(autouse=True)
def reset_registry():
    """
    Reset the registry to its default state before each test.
    This ensures tests don't interfere with each other.
    """
    # Save the original registry state
    original = _DIAGNOSER_REGISTRY.copy()

    # Clear and restore defaults
    _DIAGNOSER_REGISTRY.clear()

    # Re-add the default diagnosers using their actual classes
    # We need to import them dynamically since they might not all exist
    try:
        from procela.core.reasoning.diagnosis.anomaly import AnomalyDiagnoser

        _DIAGNOSER_REGISTRY["anomaly"] = AnomalyDiagnoser
    except ImportError:
        # Create a mock if it doesn't exist, but ensure it's a Diagnoser subclass
        class MockAnomalyDiagnoser(Diagnoser):
            name = "MockAnomalyDiagnoser"

            def diagnose(self, view):
                return {"causes": [], "confidence": 0.0, "metadata": {}}

        _DIAGNOSER_REGISTRY["anomaly"] = MockAnomalyDiagnoser

    try:
        from procela.core.reasoning.diagnosis.statistical import StatisticalDiagnoser

        _DIAGNOSER_REGISTRY["statistical"] = StatisticalDiagnoser
    except ImportError:

        class MockStatisticalDiagnoser(Diagnoser):
            name = "MockStatisticalDiagnoser"

            def diagnose(self, view):
                return {"causes": [], "confidence": 0.0, "metadata": {}}

        _DIAGNOSER_REGISTRY["statistical"] = MockStatisticalDiagnoser

    try:
        from procela.core.reasoning.diagnosis.trend import TrendDiagnoser

        _DIAGNOSER_REGISTRY["trend"] = TrendDiagnoser
    except ImportError:

        class MockTrendDiagnoser(Diagnoser):
            name = "MockTrendDiagnoser"

            def diagnose(self, view):
                return {"causes": [], "confidence": 0.0, "metadata": {}}

        _DIAGNOSER_REGISTRY["trend"] = MockTrendDiagnoser

    yield  # Run the test

    # Restore original state
    _DIAGNOSER_REGISTRY.clear()
    _DIAGNOSER_REGISTRY.update(original)


# ==================== CORE FUNCTION TESTS ====================


def test_get_diagnoser_existing():
    """Test getting an existing diagnoser."""
    diagnoser = get_diagnoser("trend")
    assert isinstance(diagnoser, Diagnoser)


def test_get_diagnoser_with_parameters():
    """Test getting a diagnoser with constructor parameters."""
    # Test with parameters that the actual TrendDiagnoser accepts
    diagnoser = get_diagnoser("trend", significance_threshold=0.3)
    assert isinstance(diagnoser, Diagnoser)


def test_get_diagnoser_nonexistent():
    """Test error when getting a non-existent diagnoser."""
    with pytest.raises(KeyError) as exc_info:
        get_diagnoser("nonexistent")

    assert "not found" in str(exc_info.value)
    assert "Available diagnosers" in str(exc_info.value)


def test_register_diagnoser_valid():
    """Test registering a valid diagnoser subclass."""

    class CustomDiagnoser(Diagnoser):
        name = "CustomDiagnoser"

        def diagnose(self, view):
            return {"causes": ["Custom issue"], "confidence": 0.8, "metadata": {}}

    # Register should work
    register_diagnoser("custom", CustomDiagnoser)

    # Verify it's registered
    assert has_diagnoser("custom")

    # Should be able to instantiate it
    instance = get_diagnoser("custom")
    assert isinstance(instance, CustomDiagnoser)


def test_register_diagnoser_duplicate():
    """Test error when registering duplicate name."""

    class CustomDiagnoser(Diagnoser):
        name = "CustomDiagnoser"

        def diagnose(self, view):
            return {"causes": [], "confidence": 0.0, "metadata": {}}

    # First registration works
    register_diagnoser("duplicate_test", CustomDiagnoser)

    # Second should fail
    with pytest.raises(ValueError) as exc_info:
        register_diagnoser("duplicate_test", CustomDiagnoser)

    assert "already registered" in str(exc_info.value)


def test_register_diagnoser_not_a_class():
    """Test error when registering something that's not a class."""
    not_a_class = "I'm a string, not a class"

    with pytest.raises(TypeError) as exc_info:
        register_diagnoser("invalid", not_a_class)  # type: ignore

    assert "must be a class" in str(exc_info.value)


def test_register_diagnoser_not_diagnoser_subclass():
    """Test error when registering a class that's not a Diagnoser subclass."""

    class NotADiagnoser:
        """This is NOT a subclass of Diagnoser."""

        pass

    with pytest.raises(TypeError) as exc_info:
        register_diagnoser("wrong_base", NotADiagnoser)

    assert "must be a subclass of Diagnoser" in str(exc_info.value)


def test_unregister_diagnoser():
    """Test unregistering a diagnoser."""

    class TempDiagnoser(Diagnoser):
        name = "TempDiagnoser"

        def diagnose(self, view):
            return {"causes": [], "confidence": 0.0, "metadata": {}}

    # First register it
    register_diagnoser("temp", TempDiagnoser)
    assert has_diagnoser("temp")

    # Then unregister it
    unregistered_class = unregister_diagnoser("temp")

    # Should return the class and remove it
    assert unregistered_class == TempDiagnoser
    assert not has_diagnoser("temp")


def test_unregister_nonexistent():
    """Test error when unregistering non-existent diagnoser."""
    with pytest.raises(KeyError) as exc_info:
        unregister_diagnoser("does_not_exist")

    assert "not found in registry" in str(exc_info.value)


def test_get_diagnosers():
    """Test getting all diagnosers."""
    diagnosers = get_diagnosers()

    # Should be a dictionary
    assert isinstance(diagnosers, dict)

    # Should contain at least the default diagnosers
    assert "anomaly" in diagnosers
    assert "statistical" in diagnosers
    assert "trend" in diagnosers

    # Should return a copy, not the original
    diagnosers["test"] = "should_not_affect_original"
    assert "test" not in _DIAGNOSER_REGISTRY


def test_available_diagnosers():
    """Test getting available diagnoser names."""
    available = available_diagnosers()

    # Should be a set
    assert isinstance(available, set)

    # Should contain default names
    assert "anomaly" in available
    assert "statistical" in available
    assert "trend" in available


def test_clear_diagnoser_registry():
    """Test clearing the registry."""

    # Add a custom diagnoser first
    class TestDiagnoser(Diagnoser):
        name = "TestDiagnoser"

        def diagnose(self, view):
            return {"causes": [], "confidence": 0.0, "metadata": {}}

    register_diagnoser("test", TestDiagnoser)
    assert len(get_diagnosers()) >= 4  # 3 defaults + our test

    # Clear it
    clear_diagnoser_registry()

    # Should be empty
    assert len(get_diagnosers()) == 0
    assert len(available_diagnosers()) == 0


def test_has_diagnoser():
    """Test checking if a diagnoser exists."""
    # Default diagnosers should exist
    assert has_diagnoser("anomaly") is True
    assert has_diagnoser("statistical") is True
    assert has_diagnoser("trend") is True

    # Non-existent should return False
    assert has_diagnoser("imaginary") is False


def test_get_diagnoser_instantiation_error():
    """Test get_diagnoser when constructor fails."""

    # Create a diagnoser that requires specific arguments
    class FaultyDiagnoser(Diagnoser):
        name = "FaultyDiagnoser"

        def __init__(self, required_arg: str, **kwargs):
            if not required_arg:
                raise TypeError("required_arg must be provided")
            super().__init__(**kwargs)

        def diagnose(self, view):
            return {"causes": [], "confidence": 0.0, "metadata": {}}

    # Temporarily register it
    original_trend = _DIAGNOSER_REGISTRY.get("trend")
    _DIAGNOSER_REGISTRY["trend"] = FaultyDiagnoser

    try:
        with pytest.raises(TypeError) as exc_info:
            get_diagnoser("trend")  # Missing required_arg

        # Should include our custom error message
        assert "Failed to instantiate diagnoser" in str(exc_info.value)
    finally:
        # Restore original
        if original_trend:
            _DIAGNOSER_REGISTRY["trend"] = original_trend


def test_full_lifecycle_integration():
    """Test complete integration flow."""
    # Start fresh
    clear_diagnoser_registry()

    # Create a custom diagnoser
    class IntegrationDiagnoser(Diagnoser):
        name = "IntegrationDiagnoser"

        def __init__(self, special_value: int = 0, **kwargs):
            self.special_value = special_value
            super().__init__(**kwargs)

        def diagnose(self, view):
            return {
                "causes": [f"Integration issue with value {self.special_value}"],
                "confidence": 0.9,
                "metadata": {"special_value": self.special_value},
            }

    # 1. Register
    register_diagnoser("integration", IntegrationDiagnoser)
    assert has_diagnoser("integration")

    # 2. Get and use
    instance = get_diagnoser("integration", special_value=42)
    assert isinstance(instance, IntegrationDiagnoser)
    assert instance.special_value == 42

    # 3. Verify in available list
    available = available_diagnosers()
    assert "integration" in available

    # 4. Unregister
    unregistered_class = unregister_diagnoser("integration")
    assert unregistered_class == IntegrationDiagnoser
    assert not has_diagnoser("integration")


def test_edge_case_names():
    """Test edge cases with special names."""

    class EdgeDiagnoser(Diagnoser):
        name = "EdgeDiagnoser"

        def diagnose(self, view):
            return {"causes": [], "confidence": 0.0, "metadata": {}}

    # Test empty string name
    register_diagnoser("", EdgeDiagnoser)
    assert has_diagnoser("")
    instance = get_diagnoser("")
    assert isinstance(instance, EdgeDiagnoser)
    unregister_diagnoser("")

    # Test names with special characters
    special_names = ["diagnoser-2.0", "my.diagnoser", "diagnoser_with_underscore"]
    for name in special_names:
        register_diagnoser(name, EdgeDiagnoser)
        assert has_diagnoser(name)
        instance = get_diagnoser(name)
        assert isinstance(instance, EdgeDiagnoser)
        unregister_diagnoser(name)


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    # Run tests directly: python test_registry.py
    # Or with pytest: pytest test_registry.py -v
    pytest.main([__file__, "-v"])
