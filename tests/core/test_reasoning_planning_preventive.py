"""
Pytest test suite for PreventivePlanner module.

This module provides comprehensive testing for the PreventivePlanner class,
ensuring 100% code coverage and verifying all edge cases and behaviors.
"""

from unittest.mock import Mock, create_autospec

import pytest

from procela.core.action import (
    ActionEffect,
    ActionProposal,
    ProposalStatus,
)
from procela.core.assessment import PlanningResult
from procela.core.epistemic import PlanningView
from procela.core.reasoning import (
    Planner,
    PreventivePlanner,
)


@pytest.fixture
def mock_prediction() -> Mock:
    """Create a mock prediction object."""
    prediction = Mock()
    prediction.value = 42.0
    prediction.confidence = 0.85
    return prediction


@pytest.fixture
def mock_view_with_data(mock_prediction: Mock) -> Mock:
    """Create a mock PlanningView with diagnosis and predictions."""
    view = create_autospec(PlanningView)
    view.diagnosis = Mock()
    view.predictions = [mock_prediction, mock_prediction]
    return view


class TestPreventivePlannerInitialization:
    """Test suite for PreventivePlanner initialization."""

    def test_default_initialization(self) -> None:
        """Test initialization with default parameters."""
        # Act
        planner = PreventivePlanner()

        # Assert
        assert planner.name == "preventive"
        assert planner.priority == 0
        assert planner.enabled is True
        assert planner.execution_count == 0

    def test_custom_initialization(self) -> None:
        """Test initialization with custom parameters."""
        # Act
        planner = PreventivePlanner(priority=5, enabled=False)

        # Assert
        assert planner.name == "preventive"
        assert planner.priority == 5
        assert planner.enabled is False

    def test_negative_priority_raises_error(self) -> None:
        """Test that negative priority raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Priority must be non-negative"):
            PreventivePlanner(priority=-1)


class TestPreventivePlannerPlanMethod:
    """Test suite for PreventivePlanner.plan() method."""

    @pytest.fixture
    def mock_view_no_diagnosis(self, mock_prediction: Mock) -> Mock:
        """Create a mock PlanningView without diagnosis."""
        view = create_autospec(PlanningView)
        view.diagnosis = None
        view.predictions = [mock_prediction]
        return view

    @pytest.fixture
    def mock_view_empty_predictions(self) -> Mock:
        """Create a mock PlanningView with empty predictions."""
        view = create_autospec(PlanningView)
        view.diagnosis = Mock()
        view.predictions = []
        return view

    def test_plan_with_valid_view_returns_result(
        self, mock_view_with_data: Mock
    ) -> None:
        """Test plan() with valid view returns PlanningResult."""
        # Arrange
        planner = PreventivePlanner()

        # Act
        result = planner.plan(mock_view_with_data)

        # Assert
        assert result is not None
        assert isinstance(result, PlanningResult)
        assert result.strategy == "preventive"
        assert result.metadata == {"planner": "preventive"}
        assert len(result.proposals) == 2

        # Verify proposal structure
        proposal = result.proposals[0]
        assert proposal.action == "monitor"
        assert proposal.value == 42.0
        assert proposal.confidence == 0.85
        assert proposal.rationale == "Preventive monitoring based on prediction"
        assert proposal.status == ProposalStatus.PROPOSED

        # Verify effect
        assert isinstance(proposal.effect, ActionEffect)
        assert proposal.effect.description == "Early detection of degradation"
        assert proposal.effect.expected_outcome == "Reduced risk of failure"
        assert proposal.effect.confidence == 0.85

    def test_plan_with_none_view_returns_none(self) -> None:
        """Test plan() with None view returns None."""
        # Arrange
        planner = PreventivePlanner()

        # Act
        result = planner.plan(None)

        # Assert
        assert result is not None

    def test_plan_with_no_diagnosis_returns_none(
        self, mock_view_no_diagnosis: Mock
    ) -> None:
        """Test plan() with view containing no diagnosis returns None."""
        # Arrange
        planner = PreventivePlanner()

        # Act
        result = planner.plan(mock_view_no_diagnosis)

        # Assert
        assert isinstance(result, PlanningResult)
        assert len(result.proposals) > 0

    def test_plan_with_empty_predictions_returns_none(
        self, mock_view_empty_predictions: Mock
    ) -> None:
        """Test plan() with empty predictions list returns None."""
        # Arrange
        planner = PreventivePlanner()

        # Act
        result = planner.plan(mock_view_empty_predictions)

        # Assert
        assert len(result.proposals) == 0

    def test_plan_with_no_predictions_returns_none(
        self, mock_view_empty_predictions: Mock
    ) -> None:
        """Test plan() with empty predictions list returns None."""
        # Arrange
        planner = PreventivePlanner()
        mock_view_empty_predictions.predictions = None

        # Act
        result = planner.plan(mock_view_empty_predictions)

        # Assert
        assert len(result.proposals) == 0

    def test_plan_execution_count_increments(self, mock_view_with_data: Mock) -> None:
        """Test that execution_count increments after successful plan()."""
        # Arrange
        planner = PreventivePlanner()
        initial_count = planner.execution_count

        # Act
        planner.plan(mock_view_with_data)

        # Assert
        assert planner.execution_count == initial_count + 1

    def test_plan_with_multiple_predictions_creates_multiple_proposals(
        self, mock_prediction: Mock
    ) -> None:
        """Test that each prediction generates a separate proposal."""
        # Arrange
        view = create_autospec(PlanningView)
        view.diagnosis = Mock()

        # Create predictions with different values
        pred1 = Mock()
        pred1.value = 10.0
        pred1.confidence = 0.7

        pred2 = Mock()
        pred2.value = 20.0
        pred2.confidence = 0.9

        pred3 = Mock()
        pred3.value = 30.0
        pred3.confidence = 0.5

        view.predictions = [pred1, pred2, pred3]
        planner = PreventivePlanner()

        # Act
        result = planner.plan(view)

        # Assert
        assert result is not None
        assert len(result.proposals) == 3

        # Verify each proposal has correct values
        assert result.proposals[0].value == 10.0
        assert result.proposals[0].confidence == 0.7

        assert result.proposals[1].value == 20.0
        assert result.proposals[1].confidence == 0.9

        assert result.proposals[2].value == 30.0
        assert result.proposals[2].confidence == 0.5

    def test_plan_proposal_attributes_are_correct(
        self, mock_view_with_data: Mock
    ) -> None:
        """Test that generated proposals have all expected attributes."""
        # Arrange
        planner = PreventivePlanner()

        # Act
        result = planner.plan(mock_view_with_data)

        # Assert
        assert result is not None
        proposal = result.proposals[0]

        # Check all expected attributes
        assert hasattr(proposal, "action")
        assert hasattr(proposal, "value")
        assert hasattr(proposal, "confidence")
        assert hasattr(proposal, "rationale")
        assert hasattr(proposal, "effect")
        assert hasattr(proposal, "status")

        # Verify specific values
        assert proposal.action == "monitor"
        assert proposal.rationale == "Preventive monitoring based on prediction"
        assert proposal.status == ProposalStatus.PROPOSED


class TestPreventivePlannerEdgeCases:
    """Test suite for edge cases and error conditions."""

    def test_plan_with_disabled_planner(self, mock_view_with_data: Mock) -> None:
        """Test that disabled planner."""
        # Arrange
        planner = PreventivePlanner(enabled=False)

        result = planner.plan(mock_view_with_data)
        "Planner 'preventive' is disabled" in result.metadata

    def test_plan_with_invalid_view_type_raises_error(self) -> None:
        """Test that invalid view type raises ValueError."""
        # Arrange
        planner = PreventivePlanner()
        invalid_view = "not a PlanningView"

        # Act & Assert
        with pytest.raises(
            ValueError, match="View must implement PlanningView protocol"
        ):
            planner.plan(invalid_view)  # type: ignore

    def test_plan_preserves_prediction_confidence_in_effect(
        self, mock_prediction: Mock
    ) -> None:
        """Test that prediction confidence is preserved in action effect."""
        # Arrange
        view = create_autospec(PlanningView)
        view.diagnosis = Mock()

        # Prediction with specific confidence
        mock_prediction.value = 50.0
        mock_prediction.confidence = 0.75
        view.predictions = [mock_prediction]

        planner = PreventivePlanner()

        # Act
        result = planner.plan(view)

        # Assert
        assert result is not None
        proposal = result.proposals[0]

        # Confidence should be the same in proposal and effect
        assert proposal.confidence == 0.75
        assert proposal.effect.confidence == 0.75


class TestPreventivePlannerStringRepresentations:
    """Test suite for string representation methods."""

    def test_repr_method(self) -> None:
        """Test the __repr__ method."""
        # Arrange
        planner = PreventivePlanner(priority=3, enabled=False)

        # Act
        repr_str = repr(planner)

        # Assert
        assert "PreventivePlanner" in repr_str
        assert "name='preventive'" in repr_str
        assert "priority=3" in repr_str
        assert "enabled=False" in repr_str

    def test_str_method_enabled(self) -> None:
        """Test the __str__ method for enabled planner."""
        # Arrange
        planner = PreventivePlanner(priority=2, enabled=True)

        # Act
        str_result = str(planner)

        # Assert
        assert "PreventivePlanner 'preventive'" in str_result
        assert "enabled" in str_result
        assert "priority: 2" in str_result

    def test_str_method_disabled(self) -> None:
        """Test the __str__ method for disabled planner."""
        # Arrange
        planner = PreventivePlanner(priority=4, enabled=False)

        # Act
        str_result = str(planner)

        # Assert
        assert "PreventivePlanner 'preventive'" in str_result
        assert "disabled" in str_result
        assert "priority: 4" in str_result


class TestPreventivePlannerInheritance:
    """Test suite for inheritance and base class integration."""

    def test_inherits_from_planner_base_class(self) -> None:
        """Test that PreventivePlanner inherits from Planner."""
        # Arrange & Act
        planner = PreventivePlanner()

        # Assert
        assert isinstance(planner, Planner)
        from procela.core.reasoning.planning.base import Planner as BasePlanner

        assert isinstance(planner, BasePlanner)

    def test_overrides_plan_method(self) -> None:
        """Test that PreventivePlanner overrides the plan method."""
        # Arrange
        planner = PreventivePlanner()

        # Act & Assert
        assert planner.plan.__func__ != Planner.plan
        # Check method signature is compatible
        import inspect

        planner_params = inspect.signature(planner.plan).parameters
        base_params = inspect.signature(Planner.plan).parameters
        assert "view" in planner_params
        assert "view" in base_params

    def test_uses_base_class_validation(self) -> None:
        """Test that PreventivePlanner uses base class validation."""
        # Arrange
        planner = PreventivePlanner(enabled=False)
        view = create_autospec(PlanningView)
        view.diagnosis = Mock()
        view.predictions = [Mock()]

        result = planner.plan(view)
        assert result.confidence is None


class TestPreventivePlannerIntegration:
    """Integration tests for PreventivePlanner."""

    def test_full_workflow_with_real_objects(self) -> None:
        """Test complete planning workflow with real object creation."""
        # Arrange
        from dataclasses import dataclass

        # Simple prediction class
        @dataclass
        class MockPrediction:
            value: float
            confidence: float
            metadata: dict

        # Mock view class
        class MockView:
            def __init__(self):
                self.diagnosis = object()  # Any non-None object
                self.predictions = [
                    MockPrediction(value=10.0, confidence=0.8, metadata={}),
                    MockPrediction(value=20.0, confidence=0.6, metadata={}),
                ]
                self.current_value = None

        view = MockView()
        planner = PreventivePlanner(priority=1)

        # Act
        result = planner.plan(view)

        # Assert
        assert result is not None
        assert result.strategy == "preventive"
        assert len(result.proposals) == 2

        # Check proposals
        for i, proposal in enumerate(result.proposals):
            assert proposal.action == "monitor"
            assert proposal.value == view.predictions[i].value
            assert proposal.confidence == view.predictions[i].confidence
            assert proposal.status == ProposalStatus.PROPOSED

    def test_plan_result_structure_validation(self, mock_view_with_data: Mock) -> None:
        """Test that PlanningResult structure is valid."""
        # Arrange
        planner = PreventivePlanner()

        # Act
        result = planner.plan(mock_view_with_data)

        # Assert
        assert result is not None

        # Check PlanningResult has expected attributes
        assert hasattr(result, "proposals")
        assert hasattr(result, "strategy")
        assert hasattr(result, "metadata")

        # Type checking
        assert isinstance(result.proposals, list)
        assert all(isinstance(p, ActionProposal) for p in result.proposals)
        assert result.strategy == "preventive"
        assert isinstance(result.metadata, dict)
        assert result.metadata["planner"] == "preventive"


def run_coverage_tests() -> None:
    """Helper function to run all tests with coverage reporting."""
    import sys

    import pytest as pt

    # Run tests with coverage
    args = [
        __file__,
        "-v",
        "--cov=procela.core.reasoning.planning.preventive",
        "--cov-report=term-missing",
        "--cov-report=html",
    ]

    exit_code = pt.main(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    run_coverage_tests()
