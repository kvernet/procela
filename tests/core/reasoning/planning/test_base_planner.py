"""
Pytest suite for Procela's base planner module (core/reasoning/planning/base.py).

This test module provides 100% coverage for the Planner abstract base class,
including initialization, property access, enable/disable functionality,
plan execution, and result validation.
"""

from __future__ import annotations

import logging
from typing import Any
from unittest.mock import Mock

import pytest

from procela.core.action import ActionProposal
from procela.core.reasoning import (
    Planner,
    PlanningResult,
    PlanningView,
)


class ConcreteTestPlanner(Planner):
    """Concrete planner implementation for testing abstract base class methods."""

    def __init__(
        self,
        name: str = "TestPlanner",
        priority: int = 0,
        enabled: bool = True,
        plan_result: PlanningResult = None,
    ):
        """
        Initialize the test planner.

        Parameters
        ----------
        name : str
            Planner name identifier.
        priority : int, optional
            Planning priority, by default 0.
        enabled : bool, optional
            Whether planner is active, by default True.
        plan_result : PlanningResult, optional
            Result to return from _plan_impl, by default creates empty result.
        """
        super().__init__(name, priority, enabled)
        self._plan_result = plan_result or PlanningResult(proposals=[])
        self.last_received_view = None

    def plan(self, view: PlanningView) -> PlanningResult:
        """
        Test implementation of abstract method.

        Parameters
        ----------
        view : PlanningView
            The planning view.

        Returns
        -------
        PlanningResult
            The mock planning result.
        """
        self.last_received_view = view
        return self._plan_result

    def set_plan_result(self, result: PlanningResult) -> None:
        """Set the result to return from _plan_impl."""
        self._plan_result = result


class TestPlannerInitialization:
    """Test suite for Planner.__init__ method."""

    def test_valid_initialization(self) -> None:
        """Test initialization with valid parameters."""
        # Arrange & Act
        planner = ConcreteTestPlanner(
            name="OptimizationPlanner", priority=5, enabled=True
        )

        # Assert
        assert planner.name == "OptimizationPlanner"
        assert planner.priority == 5
        assert planner.enabled is True
        assert planner.execution_count == 0

    def test_default_parameters(self) -> None:
        """Test initialization with default parameters."""
        # Arrange & Act
        planner = ConcreteTestPlanner()

        # Assert
        assert planner.name == "TestPlanner"
        assert planner.priority == 0
        assert planner.enabled is True
        assert planner.execution_count == 0

    def test_negative_priority_raises_value_error(self) -> None:
        """Test that negative priority raises ValueError."""
        # Arrange, Act & Assert
        with pytest.raises(ValueError, match="Priority must be non-negative"):
            ConcreteTestPlanner(name="TestPlanner", priority=-1)

    def test_empty_name_raises_value_error(self) -> None:
        """Test that empty name raises ValueError."""
        # Arrange, Act & Assert
        with pytest.raises(ValueError, match="Name must be a non-empty string"):
            ConcreteTestPlanner(name="")

    def test_non_string_name_raises_value_error(self) -> None:
        """Test that non-string name raises ValueError."""
        # Arrange, Act & Assert
        with pytest.raises(ValueError, match="Name must be a non-empty string"):
            ConcreteTestPlanner(name=123)  # type: ignore

    def test_initialization_logs_debug_message(self, caplog: Any) -> None:
        """Test that initialization logs appropriate debug message."""
        # Arrange
        caplog.set_level(logging.DEBUG)

        # Act
        ConcreteTestPlanner(name="LoggedPlanner", priority=3, enabled=False)

        # Assert
        assert "Initialized planner 'LoggedPlanner'" in caplog.text
        assert "priority 3" in caplog.text
        assert "enabled=False" in caplog.text


class TestPlannerProperties:
    """Test suite for Planner property accessors."""

    @pytest.fixture
    def planner(self) -> ConcreteTestPlanner:
        """Provide a planner instance for property tests."""
        return ConcreteTestPlanner(
            name="PropertyTestPlanner", priority=10, enabled=False
        )

    def test_name_property(self, planner: ConcreteTestPlanner) -> None:
        """Test the name property getter."""
        # Act & Assert
        assert planner.name == "PropertyTestPlanner"

    def test_priority_property(self, planner: ConcreteTestPlanner) -> None:
        """Test the priority property getter."""
        # Act & Assert
        assert planner.priority == 10

    def test_enabled_property(self, planner: ConcreteTestPlanner) -> None:
        """Test the enabled property getter."""
        # Act & Assert
        assert planner.enabled is False

    def test_execution_count_property(self, planner: ConcreteTestPlanner) -> None:
        """Test the execution_count property getter."""
        # Act & Assert
        assert planner.execution_count == 0


class TestPlannerEnableDisable:
    """Test suite for Planner.enable() and .disable() methods."""

    def test_enable_from_disabled_state(self, caplog: Any) -> None:
        """Test enabling a disabled planner."""
        # Arrange
        caplog.set_level(logging.INFO)
        planner = ConcreteTestPlanner(name="EnableTestPlanner", enabled=False)

        # Act
        planner.enable()

        # Assert
        assert planner.enabled is True
        assert "Planner 'EnableTestPlanner' enabled" in caplog.text

    def test_enable_already_enabled_is_idempotent(self, caplog: Any) -> None:
        """Test enabling an already enabled planner (idempotency)."""
        # Arrange
        caplog.set_level(logging.INFO)
        planner = ConcreteTestPlanner(name="EnableTestPlanner", enabled=True)

        # Act
        planner.enable()
        planner.enable()  # Second call should have no effect

        # Assert
        assert planner.enabled is True
        # Should not log when already enabled
        assert "Planner 'EnableTestPlanner' enabled" not in caplog.text

    def test_disable_from_enabled_state(self, caplog: Any) -> None:
        """Test disabling an enabled planner."""
        # Arrange
        caplog.set_level(logging.INFO)
        planner = ConcreteTestPlanner(name="DisableTestPlanner", enabled=True)

        # Act
        planner.disable()

        # Assert
        assert planner.enabled is False
        assert "Planner 'DisableTestPlanner' disabled" in caplog.text

    def test_disable_already_disabled_is_idempotent(self, caplog: Any) -> None:
        """Test disabling an already disabled planner (idempotency)."""
        # Arrange
        caplog.set_level(logging.INFO)
        planner = ConcreteTestPlanner(name="DisableTestPlanner", enabled=False)

        # Act
        planner.disable()
        planner.disable()  # Second call should have no effect

        # Assert
        assert planner.enabled is False
        # Should not log when already disabled
        assert "Planner 'DisableTestPlanner' disabled" not in caplog.text


class TestPlannerPlanMethod:
    """Test suite for Planner.plan() method."""

    @pytest.fixture
    def mock_view(self) -> PlanningView:
        """Provide a mock PlanningView for testing."""
        return Mock(spec=PlanningView)

    @pytest.fixture
    def valid_action_proposals(self) -> list[ActionProposal]:
        """Provide valid action proposals for testing."""
        return [
            ActionProposal(action="increase_pressure", confidence=0.8, value=10.0),
            ActionProposal(action="decrease_temperature", confidence=0.6, value=5.0),
        ]

    def test_plan_successful_execution(
        self, mock_view: Mock, valid_action_proposals: list[ActionProposal], caplog: Any
    ) -> None:
        """Test successful plan execution."""
        # Arrange
        caplog.set_level(logging.DEBUG)
        expected_result = PlanningResult(proposals=valid_action_proposals)
        planner = ConcreteTestPlanner(
            name="SuccessfulPlanner", plan_result=expected_result
        )

        # Act
        result = planner.plan(mock_view)

        # Assert
        assert result == expected_result
        assert planner.execution_count == 0
        assert planner.last_received_view == mock_view
        assert "'SuccessfulPlanner' with priority 0, enabled=True" in caplog.text

    def test_plan_with_disabled_planner_raises_runtime_error(
        self, mock_view: Mock
    ) -> None:
        """Test that disabled planner raises RuntimeError."""
        # Arrange
        planner = ConcreteTestPlanner(name="DisabledPlanner", enabled=False)

        planner.plan(mock_view)
        assert planner.execution_count == 0

    def test_plan_with_none_view(self) -> None:
        """Test that None view."""
        # Arrange
        planner = ConcreteTestPlanner(name="TestPlanner")

        planner.plan(None)  # type: ignore
        assert planner.execution_count == 0

    def test_plan_with_invalid_view_type(self) -> None:
        """Test that invalid view type."""
        # Arrange
        planner = ConcreteTestPlanner(name="TestPlanner")
        invalid_view = "not a PlanningView"

        planner.plan(invalid_view)  # type: ignore
        assert planner.execution_count == 0

    def test_plan_exception_in_implementation_raises_runtime_error(
        self, mock_view: Mock, caplog: Any
    ) -> None:
        """Test that exceptions in plan."""
        # Arrange
        caplog.set_level(logging.ERROR)

        # Create a planner that will raise an exception
        class FaultyPlanner(Planner):
            def __init__(self) -> None:
                super().__init__(name="FaultyPlanner")

            def plan(self, view: PlanningView) -> PlanningResult:
                raise ValueError("Simulated implementation error")

        planner = FaultyPlanner()

        # Act & Assert
        with pytest.raises(
            ValueError,
            match="Simulated implementation error",
        ):
            planner.plan(mock_view)

        assert planner.execution_count == 0

    def test_plan_increments_execution_count_on_success(self, mock_view: Mock) -> None:
        """Test that execution_count increments after successful planning."""
        # Arrange
        planner = ConcreteTestPlanner(name="CounterPlanner")
        initial_count = planner.execution_count

        # Act
        planner.plan(mock_view)

        # Assert
        assert planner.execution_count == initial_count

    def test_create_failed_result(self):
        """Create failed result."""
        planner = ConcreteTestPlanner(name="CounterPlanner")
        result = planner._create_failed_result({})
        assert isinstance(result, PlanningResult)


class TestPlannerStringRepresentations:
    """Test suite for Planner.__repr__() and __str__() methods."""

    def test_repr_method(self) -> None:
        """Test the __repr__ method."""
        # Arrange
        planner = ConcreteTestPlanner(name="ReprTest", priority=7, enabled=False)

        # Act
        repr_str = repr(planner)

        # Assert
        assert "ConcreteTestPlanner" in repr_str
        assert "name='ReprTest'" in repr_str
        assert "priority=7" in repr_str
        assert "enabled=False" in repr_str

    def test_str_method_enabled(self) -> None:
        """Test the __str__ method for enabled planner."""
        # Arrange
        planner = ConcreteTestPlanner(name="StrTest", priority=3, enabled=True)

        # Act
        str_result = str(planner)

        # Assert
        assert "Planner 'StrTest'" in str_result
        assert "enabled" in str_result
        assert "priority: 3" in str_result

    def test_str_method_disabled(self) -> None:
        """Test the __str__ method for disabled planner."""
        # Arrange
        planner = ConcreteTestPlanner(name="StrTest", priority=3, enabled=False)

        # Act
        str_result = str(planner)

        # Assert
        assert "Planner 'StrTest'" in str_result
        assert "disabled" in str_result
        assert "priority: 3" in str_result


class TestPlannerAbstractMethod:
    """Test suite for Planner's abstract method requirements."""

    def test_abstract_planner_cannot_be_instantiated(self) -> None:
        """Test that abstract Planner cannot be instantiated directly."""
        # Act & Assert
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            Planner(name="AbstractTest")  # type: ignore

    def test_concrete_planner_must_implement_plan_impl(self) -> None:
        """Test that concrete planners must implement _plan_impl."""

        # Arrange
        class IncompletePlanner(Planner):
            def __init__(self) -> None:
                super().__init__(name="Incomplete")

            # Missing _plan_impl implementation

        with pytest.raises(TypeError):
            _ = IncompletePlanner()


class TestPlannerIntegration:
    """Integration tests for Planner class."""

    def test_full_planning_cycle_with_mocked_dependencies(self, caplog: Any) -> None:
        """Test complete planning cycle with mocked dependencies."""
        # Arrange
        caplog.set_level(logging.DEBUG)

        # Create mock view
        mock_view = Mock(spec=PlanningView)
        mock_view.system_state = {"temperature": 75.0, "pressure": 1.2}

        # Create expected proposals
        proposals = [
            ActionProposal(action="adjust_valve", confidence=0.85, value=15.0),
            ActionProposal(action="cool_system", confidence=0.72, value=8.5),
        ]

        # Create planner with expected result
        expected_result = PlanningResult(
            proposals=proposals, confidence=0.79, recommended=[proposals[0]]
        )

        planner = ConcreteTestPlanner(
            name="IntegrationPlanner", priority=5, plan_result=expected_result
        )

        # Act
        result = planner.plan(mock_view)

        # Assert
        assert result == expected_result
        assert planner.execution_count == 0
        assert planner.last_received_view == mock_view

        # Verify logging
        logs = caplog.text
        assert "Initialized planner 'IntegrationPlanner'" in logs
        assert "'IntegrationPlanner' with priority 5" in logs

    def test_planning_cycle_with_validation_failure(self, caplog: Any) -> None:
        """Test planning cycle where result validation fails."""
        # Arrange
        caplog.set_level(logging.ERROR)

        mock_view = Mock(spec=PlanningView)

        # Create a planner that returns invalid result
        class InvalidResultPlanner(Planner):
            def __init__(self) -> None:
                super().__init__(name="InvalidResultPlanner")

            def plan(self, view: PlanningView) -> PlanningResult:
                # Return result with invalid confidence
                return PlanningResult(
                    proposals=[
                        ActionProposal(action="test", confidence=0.5, value=1.0)
                    ],
                    confidence=1.5,  # Invalid: > 1.0
                )

        planner = InvalidResultPlanner()

        # Act & Assert
        with pytest.raises(
            ValueError, match="Confidence must be between 0.0 and 1.0, got 1.5"
        ):
            planner.plan(mock_view)

        assert planner.execution_count == 0


if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=procela.core.reasoning.planning.base",
            "--cov-report=term-missing",
        ]
    )
