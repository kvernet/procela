"""
Pytest test suite for planner registry module.

This module provides comprehensive testing for the planner registry functions,
ensuring 100% code coverage and verifying all edge cases and behaviors.
"""

from unittest.mock import Mock

import pytest

from procela.core.reasoning import (
    _PLANNER_REGISTRY,
    Planner,
    PreventivePlanner,
    ReactivePlanner,
    available_planners,
    clear_planner_registry,
    get_planner,
    get_planners,
    has_planner,
    register_planner,
    unregister_planner,
)


class TestPlannerRegistryInitialState:
    """Test suite for the initial state of the planner registry."""

    def test_initial_registry_contains_default_planners(self) -> None:
        """Test that registry starts with default planners."""
        # Act & Assert
        assert "preventive" in _PLANNER_REGISTRY
        assert "reactive" in _PLANNER_REGISTRY
        assert _PLANNER_REGISTRY["preventive"] == PreventivePlanner
        assert _PLANNER_REGISTRY["reactive"] == ReactivePlanner

    def test_get_planners_returns_copy(self) -> None:
        """Test that get_planners() returns a copy, not the original."""
        # Act
        registry_copy = get_planners()

        # Assert
        assert registry_copy is not _PLANNER_REGISTRY
        assert registry_copy == _PLANNER_REGISTRY

        # Modify copy should not affect original
        registry_copy["test"] = Mock()
        assert "test" not in _PLANNER_REGISTRY

    def test_available_planners_returns_correct_set(self) -> None:
        """Test that available_planners() returns correct set."""
        # Act
        planners = available_planners()

        # Assert
        assert isinstance(planners, set)
        assert planners == {"preventive", "reactive"}

    def test_has_planner_with_existing_planners(self) -> None:
        """Test has_planner() with existing planners."""
        # Act & Assert
        assert has_planner("preventive") is True
        assert has_planner("reactive") is True
        assert has_planner("nonexistent") is False


class TestGetPlannerFunction:
    """Test suite for get_planner() function."""

    def test_get_existing_planner_with_default_args(self) -> None:
        """Test getting an existing planner with default arguments."""
        # Act
        planner = get_planner("preventive")

        # Assert
        assert isinstance(planner, PreventivePlanner)
        assert planner.name == "preventive"
        assert planner.priority == 0
        assert planner.enabled is True

    def test_get_existing_planner_with_custom_args(self) -> None:
        """Test getting an existing planner with custom arguments."""
        # Act
        planner = get_planner("reactive", priority=5, enabled=False)

        # Assert
        assert isinstance(planner, ReactivePlanner)
        assert planner.name == "reactive"
        assert planner.priority == 5
        assert planner.enabled is False

    def test_get_nonexistent_planner_raises_key_error(self) -> None:
        """Test getting a non-existent planner raises KeyError."""
        # Act & Assert
        with pytest.raises(KeyError) as exc_info:
            get_planner("nonexistent")

        assert "Planner 'nonexistent' not found" in str(exc_info.value)
        assert "Available planners" in str(exc_info.value)

    def test_get_planner_with_invalid_args_raises_type_error(self) -> None:
        """Test that invalid constructor args raise TypeError."""
        # Act & Assert
        with pytest.raises(TypeError) as exc_info:
            # PreventivePlanner expects priority to be int, not str
            get_planner("preventive", priority="invalid")

        assert "Failed to instantiate planner" in str(exc_info.value)
        assert "preventive" in str(exc_info.value)

    def test_get_planner_error_message_includes_available_planners(self) -> None:
        """Test that error message includes sorted available planners."""
        # Act & Assert
        with pytest.raises(KeyError) as exc_info:
            get_planner("unknown")

        error_msg = str(exc_info.value)
        assert "preventive" in error_msg
        assert "reactive" in error_msg
        # Check they're in alphabetical order
        assert error_msg.index("preventive") < error_msg.index("reactive")


class TestRegisterPlannerFunction:
    """Test suite for register_planner() function."""

    class CustomPlanner(Planner):
        """Custom planner for testing registration."""

        name = "custom"

        def __init__(self, priority=0, enabled=True):
            super().__init__(self.name, priority, enabled)

        def plan(self, view):
            # Dummy implementation
            pass

    def test_register_valid_planner(self) -> None:
        """Test registering a valid planner class."""
        # Arrange
        initial_count = len(_PLANNER_REGISTRY)

        # Act
        register_planner("custom", self.CustomPlanner)

        # Assert
        assert len(_PLANNER_REGISTRY) == initial_count + 1
        assert "custom" in _PLANNER_REGISTRY
        assert _PLANNER_REGISTRY["custom"] == self.CustomPlanner

        # Cleanup
        _PLANNER_REGISTRY.pop("custom")

    def test_register_existing_name_raises_value_error(self) -> None:
        """Test registering with existing name raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            register_planner("preventive", self.CustomPlanner)

        assert "already registered" in str(exc_info.value)

    def test_register_non_class_raises_type_error(self) -> None:
        """Test registering a non-class raises TypeError."""
        # Arrange
        non_class = "not a class"

        # Act & Assert
        with pytest.raises(TypeError) as exc_info:
            register_planner("invalid", non_class)  # type: ignore

        assert "must be a class" in str(exc_info.value)

    def test_register_non_planner_subclass_raises_type_error(self) -> None:
        """Test registering a class not subclassing Planner raises TypeError."""

        # Arrange
        class NotAPlanner:
            pass

        # Act & Assert
        with pytest.raises(TypeError) as exc_info:
            register_planner("invalid", NotAPlanner)

        assert "must be a subclass of planner" in str(exc_info.value)

    def test_register_and_retrieve_custom_planner(self) -> None:
        """Test full cycle: register, get, use custom planner."""
        # Arrange & Act
        register_planner("custom_planner", self.CustomPlanner)

        # Assert registration worked
        assert has_planner("custom_planner") is True

        # Test instantiation through get_planner
        planner = get_planner("custom_planner", priority=3)
        assert isinstance(planner, self.CustomPlanner)
        assert planner.name == "custom"
        assert planner.priority == 3

        # Cleanup
        unregister_planner("custom_planner")


class TestUnregisterPlannerFunction:
    """Test suite for unregister_planner() function."""

    class TestPlanner(Planner):
        """Test planner for unregistration tests."""

        name = "test"

        def _plan_impl(self, view):
            pass

    def test_unregister_existing_planner(self) -> None:
        """Test unregistering an existing planner."""
        # Arrange
        register_planner("test_planner", self.TestPlanner)
        initial_count = len(_PLANNER_REGISTRY)

        # Act
        planner_class = unregister_planner("test_planner")

        # Assert
        assert len(_PLANNER_REGISTRY) == initial_count - 1
        assert "test_planner" not in _PLANNER_REGISTRY
        assert planner_class == self.TestPlanner

    def test_unregister_nonexistent_planner_raises_key_error(self) -> None:
        """Test unregistering a non-existent planner raises KeyError."""
        # Act & Assert
        with pytest.raises(KeyError) as exc_info:
            unregister_planner("nonexistent")

        assert "not found in registry" in str(exc_info.value)
        assert "Available planners" in str(exc_info.value)

    def test_unregister_default_planner(self) -> None:
        """Test unregistering one of the default planners."""
        # Arrange
        assert "preventive" in _PLANNER_REGISTRY
        initial_count = len(_PLANNER_REGISTRY)

        # Act
        planner_class = unregister_planner("preventive")

        # Assert
        assert len(_PLANNER_REGISTRY) == initial_count - 1
        assert "preventive" not in _PLANNER_REGISTRY
        assert planner_class == PreventivePlanner

        # Restore for other tests
        _PLANNER_REGISTRY["preventive"] = PreventivePlanner


class TestClearPlannerRegistryFunction:
    """Test suite for clear_planner_registry() function."""

    def test_clear_registry(self) -> None:
        """Test clearing the entire registry."""

        # Arrange
        # Add a custom planner to ensure we clear more than defaults
        class TempPlanner(Planner):
            name = "temp"

            def _plan_impl(self, view):
                pass

        register_planner("temp", TempPlanner)
        assert len(_PLANNER_REGISTRY) > 0

        # Act
        clear_planner_registry()

        # Assert
        assert len(_PLANNER_REGISTRY) == 0
        assert available_planners() == set()

        # Restore defaults for other tests
        _PLANNER_REGISTRY.update(
            {"preventive": PreventivePlanner, "reactive": ReactivePlanner}
        )

    def test_clear_empty_registry(self) -> None:
        """Test clearing an already empty registry."""
        # Arrange
        # Clear registry first
        _PLANNER_REGISTRY.clear()
        assert len(_PLANNER_REGISTRY) == 0

        # Act (should not raise)
        clear_planner_registry()

        # Assert
        assert len(_PLANNER_REGISTRY) == 0

        # Restore defaults
        _PLANNER_REGISTRY.update(
            {"preventive": PreventivePlanner, "reactive": ReactivePlanner}
        )


class TestPlannerRegistryIntegration:
    """Integration tests for the planner registry system."""

    class IntegrationPlanner(Planner):
        """Planner for integration testing."""

        name = "integration"

        def __init__(
            self, priority: int = 0, enabled: bool = True, custom_param: str = "default"
        ):
            super().__init__(self.name, priority, enabled)
            self.custom_param = custom_param

        def plan(self, view):
            # Dummy implementation
            pass

    def test_full_registry_lifecycle(self) -> None:
        """Test complete lifecycle: register, use, unregister."""
        # Arrange
        initial_planners = available_planners()

        # Act & Assert - Registration
        register_planner("integration", self.IntegrationPlanner)
        assert "integration" in available_planners()
        assert len(available_planners()) == len(initial_planners) + 1

        # Act & Assert - Instantiation
        planner = get_planner("integration", priority=7, custom_param="test")
        assert isinstance(planner, self.IntegrationPlanner)
        assert planner.name == "integration"
        assert planner.priority == 7
        assert planner.custom_param == "test"

        # Act & Assert - Unregistration
        planner_class = unregister_planner("integration")
        assert planner_class == self.IntegrationPlanner
        assert "integration" not in available_planners()
        assert available_planners() == initial_planners

    def test_registry_isolation_between_tests(self) -> None:
        """Test that registry modifications don't leak between tests."""
        # This test verifies that tests are independent
        # It should always see the default state at the beginning
        assert "preventive" in _PLANNER_REGISTRY
        assert "reactive" in _PLANNER_REGISTRY
        assert len(_PLANNER_REGISTRY) == 2

    def test_multiple_custom_planners(self) -> None:
        """Test registering and using multiple custom planners."""

        # Arrange
        class PlannerA(Planner):
            # name = "planner_a"
            def __init__(self, name="planner_a", priority=0, enabled=True):
                super().__init__(name, priority, enabled)

            def plan(self, view):
                pass

        class PlannerB(Planner):
            name = "planner_b"

            def __init__(self, name="planner_b", priority=0, enabled=True):
                super().__init__(name, priority, enabled)

            def plan(self, view):
                pass

        # Act
        register_planner("a", PlannerA)
        register_planner("b", PlannerB)

        # Assert
        assert has_planner("a") is True
        assert has_planner("b") is True
        assert has_planner("c") is False

        # Test instantiation
        planner_a = get_planner("a", priority=1)
        planner_b = get_planner("b", priority=2)

        assert isinstance(planner_a, PlannerA)
        assert isinstance(planner_b, PlannerB)

        # Cleanup
        unregister_planner("a")
        unregister_planner("b")


class TestPlannerRegistryEdgeCases:
    """Test suite for edge cases and error conditions."""

    def test_register_planner_with_same_class_different_name(self) -> None:
        """Test registering same class under different names."""

        # Arrange
        class MultiNamePlanner(Planner):
            name = "multi"

            def _plan_impl(self, view):
                pass

        # Act
        register_planner("name1", MultiNamePlanner)
        register_planner("name2", MultiNamePlanner)  # Same class, different name

        # Assert
        assert has_planner("name1") is True
        assert has_planner("name2") is True
        assert _PLANNER_REGISTRY["name1"] == MultiNamePlanner
        assert _PLANNER_REGISTRY["name2"] == MultiNamePlanner

        # Cleanup
        unregister_planner("name1")
        unregister_planner("name2")

    def test_unregister_and_reregister(self) -> None:
        """Test unregistering and re-registering a planner."""

        # Arrange
        class ReRegisterPlanner(Planner):
            name = "reregister"

            def _plan_impl(self, view):
                pass

        # Act & Assert - First registration
        register_planner("test", ReRegisterPlanner)
        assert has_planner("test") is True

        # Unregister
        unregister_planner("test")
        assert has_planner("test") is False

        # Re-register
        register_planner("test", ReRegisterPlanner)
        assert has_planner("test") is True

        # Cleanup
        unregister_planner("test")

    def test_get_planners_after_modifications(self) -> None:
        """Test that get_planners() reflects registry modifications."""

        # Arrange
        class DynamicPlanner(Planner):
            name = "dynamic"

            def _plan_impl(self, view):
                pass

        initial_copy = get_planners()

        # Act - Modify registry
        register_planner("dynamic", DynamicPlanner)

        # Assert - New copy should include modification
        new_copy = get_planners()
        assert "dynamic" in new_copy
        assert "dynamic" not in initial_copy

        # Cleanup
        unregister_planner("dynamic")


def run_coverage_tests() -> None:
    """Helper function to run all tests with coverage reporting."""
    import sys

    import pytest as pt

    # Run tests with coverage
    args = [
        __file__,
        "-v",
        "--cov=procela.core.reasoning.planning.registry",
        "--cov-report=term-missing",
        "--cov-report=html",
    ]

    exit_code = pt.main(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    run_coverage_tests()
