"""
Test suite for procela.core.reasoning.planning.operator module.
100% coverage for the exact PlanningOperator code.
"""

from unittest.mock import Mock, patch

import pytest

from procela.core.assessment import PlanningResult
from procela.core.epistemic import PlanningView
from procela.core.reasoning import PlanningOperator


class TestPlanningOperator:
    """Test cases for the PlanningOperator class."""

    @pytest.fixture
    def mock_planner(self):
        """Create a mock planner."""
        planner = Mock()
        planner.plan.return_value = Mock(spec=PlanningResult)
        return planner

    @pytest.fixture
    def mock_planning_view(self):
        """Create a mock PlanningView."""
        return Mock(spec=PlanningView)

    @pytest.fixture
    def mock_planning_result(self):
        """Create a mock PlanningResult."""
        return Mock(spec=PlanningResult)

    def test_init_with_name_and_kwargs(self, mock_planner):
        """Test initialization with name and keyword arguments."""
        name = "threshold_planner"
        kwargs = {"threshold": 0.95, "strategy": "aggressive"}

        with patch(
            "procela.core.reasoning.planning.operator.get_planner",
            return_value=mock_planner,
        ) as mock_get_planner:
            operator = PlanningOperator(name, **kwargs)

            # Verify get_planner was called correctly
            mock_get_planner.assert_called_once_with(name, **kwargs)

            # Verify planner was assigned
            assert operator.planner == mock_planner

    def test_init_with_different_planner_names(self):
        """Test initialization with various planner names."""
        test_cases = [
            ("simple_planner", {"max_steps": 10}),
            ("optimal_planner", {"optimize_for": "efficiency"}),
            ("heuristic_planner", {"heuristic": "distance"}),
            ("reinforcement_planner", {"learning_rate": 0.01}),
        ]

        for name, kwargs in test_cases:
            with patch(
                "procela.core.reasoning.planning.operator.get_planner"
            ) as mock_get_planner:
                mock_planner = Mock()
                mock_get_planner.return_value = mock_planner

                operator = PlanningOperator(name, **kwargs)

                mock_get_planner.assert_called_once_with(name, **kwargs)
                assert operator.planner == mock_planner

    def test_init_with_empty_kwargs(self):
        """Test initialization with no keyword arguments."""
        name = "simple_planner"

        with patch(
            "procela.core.reasoning.planning.operator.get_planner"
        ) as mock_get_planner:
            mock_planner = Mock()
            mock_get_planner.return_value = mock_planner

            operator = PlanningOperator(name)  # No kwargs

            mock_get_planner.assert_called_once_with(name)
            assert operator.planner == mock_planner

    def test_plan_method(self, mock_planner, mock_planning_view, mock_planning_result):
        """Test the plan method delegates to the planner."""
        mock_planner.plan.return_value = mock_planning_result

        with patch(
            "procela.core.reasoning.planning.operator.get_planner",
            return_value=mock_planner,
        ):
            operator = PlanningOperator("test_planner")
            result = operator.plan(mock_planning_view)

            mock_planner.plan.assert_called_once_with(mock_planning_view)
            assert result == mock_planning_result

    def test_plan_with_concrete_view(self):
        """Test plan method with a more concrete view object."""
        mock_planner = Mock()
        expected_result = Mock(spec=PlanningResult)
        mock_planner.plan.return_value = expected_result

        # Create a realistic PlanningView mock
        mock_view = Mock(spec=PlanningView)
        mock_view.state = {"current": 75.5, "target": 60.0}
        mock_view.constraints = {"max_resources": 100, "time_limit": 300}

        with patch(
            "procela.core.reasoning.planning.operator.get_planner",
            return_value=mock_planner,
        ):
            operator = PlanningOperator("optimal_planner")
            result = operator.plan(mock_view)

            mock_planner.plan.assert_called_once_with(mock_view)
            assert result == expected_result

    def test_plan_method_propagates_exceptions(self, mock_planner, mock_planning_view):
        """Test that exceptions from planner are propagated correctly."""
        test_exception = ValueError("Invalid planning view")
        mock_planner.plan.side_effect = test_exception

        with patch(
            "procela.core.reasoning.planning.operator.get_planner",
            return_value=mock_planner,
        ):
            operator = PlanningOperator("failing_planner")

            with pytest.raises(ValueError) as exc_info:
                operator.plan(mock_planning_view)

            assert str(exc_info.value) == "Invalid planning view"
            mock_planner.plan.assert_called_once_with(mock_planning_view)

    def test_plan_with_none_view(self, mock_planner):
        """Test plan method with None view."""
        mock_planner.plan.return_value = Mock(spec=PlanningResult)

        with patch(
            "procela.core.reasoning.planning.operator.get_planner",
            return_value=mock_planner,
        ):
            operator = PlanningOperator("test_planner")

            # Should pass None to planner's plan method
            result = operator.plan(None)

            mock_planner.plan.assert_called_once_with(None)
            assert result == mock_planner.plan.return_value

    def test_type_annotations_preserved(self):
        """Test that type annotations are correctly defined."""
        import inspect

        # Check __init__ signature
        init_sig = inspect.signature(PlanningOperator.__init__)
        init_params = list(init_sig.parameters.keys())

        assert init_params == ["self", "name", "kwargs"]
        assert init_sig.parameters["name"].annotation == "str"
        assert init_sig.parameters["kwargs"].annotation == "Any"

        # Check plan signature
        plan_sig = inspect.signature(PlanningOperator.plan)
        plan_params = list(plan_sig.parameters.keys())

        assert plan_params == ["self", "view"]
        assert plan_sig.parameters["view"].annotation == "PlanningView"
        assert plan_sig.return_annotation == "PlanningResult"

    def test_class_docstring(self):
        """Test that the class has the expected docstring."""
        assert "Base class for planning operators." in PlanningOperator.__doc__
        assert "Compute a plan using the operator." in PlanningOperator.plan.__doc__

    def test_operator_with_complex_kwargs(self):
        """Test operator initialization with complex keyword arguments."""
        complex_kwargs = {
            "threshold": 0.95,
            "strategy": "adaptive",
            "parameters": {
                "learning_rate": 0.01,
                "exploration": 0.1,
                "discount_factor": 0.99,
            },
            "constraints": ["resource_limit", "time_limit"],
            "verbose": True,
        }

        with patch(
            "procela.core.reasoning.planning.operator.get_planner"
        ) as mock_get_planner:
            mock_planner = Mock()
            mock_get_planner.return_value = mock_planner

            operator = PlanningOperator("advanced_planner", **complex_kwargs)

            mock_get_planner.assert_called_once_with(
                "advanced_planner", **complex_kwargs
            )
            assert operator.planner == mock_planner

    def test_plan_result_inspection(self, mock_planner, mock_planning_view):
        """Test that we can inspect the planning result."""
        # Create a realistic planning result
        mock_result = Mock(spec=PlanningResult)
        mock_result.success = True
        mock_result.steps = ["action1", "action2", "action3"]
        mock_result.cost = 42.5
        mock_result.confidence = 0.87

        mock_planner.plan.return_value = mock_result

        with patch(
            "procela.core.reasoning.planning.operator.get_planner",
            return_value=mock_planner,
        ):
            operator = PlanningOperator("test_planner")
            result = operator.plan(mock_planning_view)

            # Verify result properties
            assert result.success is True
            assert result.steps == ["action1", "action2", "action3"]
            assert result.cost == 42.5
            assert result.confidence == 0.87


class TestIntegration:
    """Integration tests for the PlanningOperator."""

    def test_full_workflow_integration(self):
        """Test a complete planning workflow from initialization to result."""
        # Create realistic mocks
        mock_view = Mock(spec=PlanningView)
        mock_view.current_state = {"temperature": 75.5, "pressure": 1.2}
        mock_view.goal_state = {"temperature": 70.0, "pressure": 1.0}
        mock_view.constraints = {"max_energy": 1000, "time_limit": 600}

        mock_result = Mock(spec=PlanningResult)
        mock_result.success = True
        mock_result.plan = [
            {"action": "cool", "duration": 60, "energy": 200},
            {"action": "stabilize", "duration": 120, "energy": 100},
            {"action": "verify", "duration": 30, "energy": 50},
        ]
        mock_result.total_cost = 350
        mock_result.confidence = 0.92

        mock_planner = Mock()
        mock_planner.plan.return_value = mock_result

        with patch(
            "procela.core.reasoning.planning.operator.get_planner",
            return_value=mock_planner,
        ):
            # Initialize operator with configuration
            operator = PlanningOperator(
                "optimal_planner",
                optimization_criteria="minimal_energy",
                timeout=30,
                max_depth=100,
            )

            # Perform planning
            result = operator.plan(mock_view)

            # Verify full workflow
            assert operator.planner == mock_planner
            mock_planner.plan.assert_called_once_with(mock_view)
            assert result == mock_result
            assert result.success is True
            assert len(result.plan) == 3
            assert result.total_cost == 350

    def test_multiple_operator_instances(self):
        """Test that multiple operator instances work independently."""
        with patch(
            "procela.core.reasoning.planning.operator.get_planner"
        ) as mock_get_planner:
            # Create two different mock planners
            mock_planner1 = Mock()
            mock_planner2 = Mock()

            # Configure get_planner to return different planners
            def get_planner_side_effect(name, **kwargs):
                if name == "planner1":
                    return mock_planner1
                elif name == "planner2":
                    return mock_planner2
                return Mock()

            mock_get_planner.side_effect = get_planner_side_effect

            # Create two operators with different configurations
            operator1 = PlanningOperator("planner1", strategy="fast")
            operator2 = PlanningOperator("planner2", strategy="optimal")

            # Verify they have different planners
            assert operator1.planner == mock_planner1
            assert operator2.planner == mock_planner2
            assert operator1.planner != operator2.planner

            # Test they work independently
            mock_view = Mock(spec=PlanningView)

            result1 = Mock(spec=PlanningResult)
            result2 = Mock(spec=PlanningResult)
            mock_planner1.plan.return_value = result1
            mock_planner2.plan.return_value = result2

            assert operator1.plan(mock_view) == result1
            assert operator2.plan(mock_view) == result2

            # Verify each planner was called
            mock_planner1.plan.assert_called_once_with(mock_view)
            mock_planner2.plan.assert_called_once_with(mock_view)

    def test_realistic_planning_scenario(self):
        """Test a realistic planning scenario with complex constraints."""
        # Simulate a resource allocation planning scenario
        mock_view = Mock(spec=PlanningView)
        mock_view.resources = {
            "cpu": {"current": 85, "limit": 100},
            "memory": {"current": 65, "limit": 80},
            "storage": {"current": 45, "limit": 60},
        }
        mock_view.objectives = [
            {"metric": "cpu", "target": 70, "priority": "high"},
            {"metric": "memory", "target": 50, "priority": "medium"},
        ]

        mock_result = Mock(spec=PlanningResult)
        mock_result.success = True
        mock_result.actions = [
            {"type": "rebalance", "resource": "cpu", "amount": -15},
            {"type": "cleanup", "resource": "memory", "amount": -15},
        ]

        mock_planner = Mock()
        mock_planner.plan.return_value = mock_result

        with patch(
            "procela.core.reasoning.planning.operator.get_planner",
            return_value=mock_planner,
        ):
            operator = PlanningOperator(
                "resource_planner",
                algorithm="genetic",
                population_size=100,
                generations=50,
                mutation_rate=0.1,
            )

            result = operator.plan(mock_view)

            # Verify the planner was called with the view
            mock_planner.plan.assert_called_once_with(mock_view)

            # Verify result
            assert result.success is True
            assert len(result.actions) == 2


def test_coverage_completeness():
    """Additional tests to ensure 100% coverage of all code paths."""

    # Test that the __init__ method properly stores the planner
    with patch(
        "procela.core.reasoning.planning.operator.get_planner"
    ) as mock_get_planner:
        mock_planner = Mock()
        mock_get_planner.return_value = mock_planner

        operator = PlanningOperator("test_planner", param1="value1", param2=123)

        # Verify constructor arguments passed correctly
        mock_get_planner.assert_called_once_with(
            "test_planner", param1="value1", param2=123
        )
        assert hasattr(operator, "planner")
        assert operator.planner == mock_planner

    # Test plan method with edge case view
    with patch(
        "procela.core.reasoning.planning.operator.get_planner"
    ) as mock_get_planner:
        mock_planner = Mock()
        mock_get_planner.return_value = mock_planner

        operator = PlanningOperator("test_planner")

        # Test with empty view
        empty_view = Mock(spec=PlanningView)
        empty_view.data = {}

        mock_result = Mock(spec=PlanningResult)
        mock_planner.plan.return_value = mock_result

        result = operator.plan(empty_view)

        mock_planner.plan.assert_called_once_with(empty_view)
        assert result == mock_result

    # Test with planner that returns None (edge case)
    with patch(
        "procela.core.reasoning.planning.operator.get_planner"
    ) as mock_get_planner:
        mock_planner = Mock()
        mock_planner.plan.return_value = None

        mock_get_planner.return_value = mock_planner

        operator = PlanningOperator("none_returning_planner")
        result = operator.plan(Mock(spec=PlanningView))

        assert result is None


def test_error_handling_edge_cases():
    """Test edge cases in error handling."""

    # Test with get_planner raising exception
    with patch(
        "procela.core.reasoning.planning.operator.get_planner"
    ) as mock_get_planner:
        mock_get_planner.side_effect = KeyError("Unknown planner: unknown_planner")

        with pytest.raises(KeyError) as exc_info:
            PlanningOperator("unknown_planner")

        assert "unknown_planner" in str(exc_info.value)

    # Test with planner.plan raising various exceptions
    exception_types = [
        ValueError("Invalid planning parameters"),
        TypeError("Unsupported view type"),
        RuntimeError("Planning timeout"),
        AttributeError("Missing required attribute"),
    ]

    for exception in exception_types:
        with patch(
            "procela.core.reasoning.planning.operator.get_planner"
        ) as mock_get_planner:
            mock_planner = Mock()
            mock_planner.plan.side_effect = exception
            mock_get_planner.return_value = mock_planner

            operator = PlanningOperator("test_planner")

            # Verify exception is propagated
            with pytest.raises(type(exception)) as exc_info:
                operator.plan(Mock(spec=PlanningView))

            assert str(exception) in str(exc_info.value)


def test_operator_attributes():
    """Test operator attributes and methods."""
    with patch(
        "procela.core.reasoning.planning.operator.get_planner"
    ) as mock_get_planner:
        mock_planner = Mock()
        mock_get_planner.return_value = mock_planner

        operator = PlanningOperator("test_planner")

        # Check attributes
        assert hasattr(operator, "planner")
        assert operator.planner == mock_planner

        # Check methods
        assert hasattr(operator, "plan")
        assert callable(operator.plan)

        # Check that plan method has correct signature
        import inspect

        sig = inspect.signature(operator.plan)
        params = list(sig.parameters.keys())
        assert params == ["view"]


def test_module_structure():
    """Test that the module has the expected structure."""
    from procela.core.reasoning.planning import operator

    # Check exports
    assert hasattr(operator, "PlanningOperator")

    # Check imports are accessible
    assert operator.PlanningResult is not None
    assert operator.PlanningView is not None
    assert operator.get_planner is not None
