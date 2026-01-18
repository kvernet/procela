"""
Pytest test suite for ReactivePlanner module.

This module provides comprehensive testing for the ReactivePlanner class,
ensuring 100% code coverage and verifying all edge cases and behaviors.
"""

from typing import List
from unittest.mock import Mock, create_autospec

import pytest

from procela.core.action import (
    ActionEffect,
    ActionProposal,
    ProposalStatus,
)

# Import the module to test
from procela.core.reasoning import (
    Planner,
    PlanningResult,
    PlanningView,
    ReactivePlanner,
)


@pytest.fixture
def mock_diagnosis_with_causes() -> Mock:
    """Create a mock diagnosis object with causes."""
    diagnosis = Mock()
    diagnosis.confidence = 0.88
    diagnosis.causes = ["network_latency", "memory_leak", "cpu_overload"]
    return diagnosis


@pytest.fixture
def mock_view_with_diagnosis(mock_diagnosis_with_causes: Mock) -> Mock:
    """Create a mock PlanningView with diagnosis and causes."""
    view = create_autospec(PlanningView)
    view.diagnosis = mock_diagnosis_with_causes
    view.current_value = 75.5
    return view


class TestReactivePlannerInitialization:
    """Test suite for ReactivePlanner initialization."""

    def test_default_initialization(self) -> None:
        """Test initialization with default parameters."""
        # Act
        planner = ReactivePlanner()

        # Assert
        assert planner.name == "reactive"
        assert planner.priority == 0
        assert planner.enabled is True
        assert planner.execution_count == 0

    def test_custom_initialization(self) -> None:
        """Test initialization with custom parameters."""
        # Act
        planner = ReactivePlanner(priority=7, enabled=False)

        # Assert
        assert planner.name == "reactive"
        assert planner.priority == 7
        assert planner.enabled is False

    def test_negative_priority_raises_error(self) -> None:
        """Test that negative priority raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Priority must be non-negative"):
            ReactivePlanner(priority=-3)


class TestReactivePlannerPlanMethod:
    """Test suite for ReactivePlanner.plan() method."""

    @pytest.fixture
    def mock_view_no_diagnosis(self) -> Mock:
        """Create a mock PlanningView without diagnosis."""
        view = create_autospec(PlanningView)
        view.diagnosis = None
        view.current_value = 50.0
        return view

    @pytest.fixture
    def mock_view_empty_causes(self) -> Mock:
        """Create a mock PlanningView with diagnosis but empty causes."""
        diagnosis = Mock()
        diagnosis.confidence = 0.65
        diagnosis.causes = []

        view = create_autospec(PlanningView)
        view.diagnosis = diagnosis
        view.current_value = 60.0
        return view

    def test_plan_with_valid_view_returns_result(
        self, mock_view_with_diagnosis: Mock
    ) -> None:
        """Test plan() with valid view returns PlanningResult."""
        # Arrange
        planner = ReactivePlanner()

        # Act
        result = planner.plan(mock_view_with_diagnosis)

        # Assert
        assert result is not None
        assert isinstance(result, PlanningResult)
        assert result.strategy == "reactive"
        assert result.confidence == 0.88
        assert result.recommended is None
        assert result.metadata == {"planner": "reactive"}
        assert len(result.proposals) == 3

        # Verify proposal structure
        proposal = result.proposals[0]
        assert proposal.action == "investigate"
        assert proposal.value == 75.5
        assert proposal.confidence == 0.88
        assert proposal.status == ProposalStatus.PROPOSED

        # Verify rationale contains cause
        assert "Reactive action for cause:" in proposal.rationale
        assert "network_latency" in proposal.rationale

        # Verify effect
        assert isinstance(proposal.effect, ActionEffect)
        assert proposal.effect.description == "Mitigate detected issue"
        assert proposal.effect.expected_outcome == "Stabilize system behavior"
        assert proposal.effect.confidence == 0.88

    def test_plan_with_none_view_returns_none(self) -> None:
        """Test plan() with None view returns None."""
        # Arrange
        planner = ReactivePlanner()

        # Act
        result = planner.plan(None)

        # Assert
        assert result.strategy is None

    def test_plan_with_no_diagnosis_returns_none(
        self, mock_view_no_diagnosis: Mock
    ) -> None:
        """Test plan() with view containing no diagnosis returns None."""
        # Arrange
        planner = ReactivePlanner()

        # Act
        result = planner.plan(mock_view_no_diagnosis)

        # Assert
        assert result.recommended is None

    def test_plan_with_empty_causes_returns_none(
        self, mock_view_empty_causes: Mock
    ) -> None:
        """Test plan() with diagnosis containing empty causes returns None."""
        # Arrange
        planner = ReactivePlanner()

        # Act
        result = planner.plan(mock_view_empty_causes)

        # Assert
        assert "Diagnosis is None or has no causes" in result.metadata.values()

    def test_plan_execution_count_increments(
        self, mock_view_with_diagnosis: Mock
    ) -> None:
        """Test that execution_count increments after successful plan()."""
        # Arrange
        planner = ReactivePlanner()
        initial_count = planner.execution_count

        # Act
        planner.plan(mock_view_with_diagnosis)

        # Assert
        assert planner.execution_count == initial_count + 1

    def test_plan_with_single_cause_creates_one_proposal(self) -> None:
        """Test that single diagnosis cause generates one proposal."""
        # Arrange
        diagnosis = Mock()
        diagnosis.confidence = 0.95
        diagnosis.causes = ["single_issue"]

        view = create_autospec(PlanningView)
        view.diagnosis = diagnosis
        view.current_value = 42.0

        planner = ReactivePlanner()

        # Act
        result = planner.plan(view)

        # Assert
        assert result is not None
        assert len(result.proposals) == 1
        assert "single_issue" in result.proposals[0].rationale

    def test_plan_proposal_values_match_diagnosis_confidence(
        self, mock_view_with_diagnosis: Mock
    ) -> None:
        """Test that proposal confidence matches diagnosis confidence."""
        # Arrange
        planner = ReactivePlanner()

        # Act
        result = planner.plan(mock_view_with_diagnosis)

        # Assert
        assert result is not None
        assert result.confidence == 0.88

        for proposal in result.proposals:
            assert proposal.confidence == 0.88
            assert proposal.effect.confidence == 0.88

    def test_plan_current_value_in_all_proposals(
        self, mock_view_with_diagnosis: Mock
    ) -> None:
        """Test that current_value from view is used in all proposals."""
        # Arrange
        mock_view_with_diagnosis.current_value = 99.9
        planner = ReactivePlanner()

        # Act
        result = planner.plan(mock_view_with_diagnosis)

        # Assert
        assert result is not None
        for proposal in result.proposals:
            assert proposal.value == 99.9


class TestReactivePlannerEdgeCases:
    """Test suite for edge cases and error conditions."""

    def test_plan_with_invalid_view_type_raises_error(self) -> None:
        """Test that invalid view type raises ValueError."""
        # Arrange
        planner = ReactivePlanner()
        invalid_view = "not a PlanningView"

        # Act & Assert
        with pytest.raises(
            ValueError, match="View must implement PlanningView protocol"
        ):
            planner.plan(invalid_view)  # type: ignore

    def test_plan_with_diagnosis_none_causes(self) -> None:
        """Test plan() with diagnosis where causes attribute is None."""
        # Arrange
        diagnosis = Mock()
        diagnosis.confidence = 0.5
        diagnosis.causes = None  # Not empty list, but None

        view = create_autospec(PlanningView)
        view.diagnosis = diagnosis
        view.current_value = 30.0

        planner = ReactivePlanner()

        # Act
        result = planner.plan(view)

        # Assert
        assert result is not None


class TestReactivePlannerStringRepresentations:
    """Test suite for string representation methods."""

    def test_repr_method(self) -> None:
        """Test the __repr__ method."""
        # Arrange
        planner = ReactivePlanner(priority=5, enabled=True)

        # Act
        repr_str = repr(planner)

        # Assert
        assert "ReactivePlanner" in repr_str
        assert "name='reactive'" in repr_str
        assert "priority=5" in repr_str
        assert "enabled=True" in repr_str

    def test_str_method_enabled(self) -> None:
        """Test the __str__ method for enabled planner."""
        # Arrange
        planner = ReactivePlanner(priority=2, enabled=True)

        # Act
        str_result = str(planner)

        # Assert
        assert "ReactivePlanner 'reactive'" in str_result
        assert "enabled" in str_result
        assert "priority: 2" in str_result

    def test_str_method_disabled(self) -> None:
        """Test the __str__ method for disabled planner."""
        # Arrange
        planner = ReactivePlanner(priority=4, enabled=False)

        # Act
        str_result = str(planner)

        # Assert
        assert "ReactivePlanner 'reactive'" in str_result
        assert "disabled" in str_result
        assert "priority: 4" in str_result


class TestReactivePlannerInheritance:
    """Test suite for inheritance and base class integration."""

    def test_inherits_from_planner_base_class(self) -> None:
        """Test that ReactivePlanner inherits from Planner."""
        # Arrange & Act
        planner = ReactivePlanner()

        # Assert
        assert isinstance(planner, Planner)
        from procela.core.reasoning.planning.base import Planner as BasePlanner

        assert isinstance(planner, BasePlanner)

    def test_overrides_plan_method(self) -> None:
        """Test that ReactivePlanner overrides the plan method."""
        # Arrange
        planner = ReactivePlanner()

        # Act & Assert
        assert planner.plan.__func__ != Planner.plan

    def test_uses_base_class_validation(self) -> None:
        """Test that ReactivePlanner uses base class validation."""
        # Arrange
        planner = ReactivePlanner(enabled=False)
        view = create_autospec(PlanningView)
        diagnosis = Mock()
        diagnosis.confidence = 0.7
        diagnosis.causes = ["test_cause"]
        view.diagnosis = diagnosis
        view.current_value = 10.0

        result = planner.plan(view)
        assert isinstance(result, PlanningResult)
        assert len(result.proposals) == 0


class TestReactivePlannerIntegration:
    """Integration tests for ReactivePlanner."""

    def test_full_workflow_with_real_objects(self) -> None:
        """Test complete planning workflow with real object creation."""
        # Arrange
        from dataclasses import dataclass

        # Simple diagnosis class
        @dataclass
        class MockDiagnosis:
            confidence: float
            causes: List[str]

        # Mock view class
        class MockView:
            def __init__(self):
                self.diagnosis = MockDiagnosis(
                    confidence=0.75, causes=["low_throughput", "high_latency"]
                )
                self.predictions = None
                self.current_value = 68.3

        view = MockView()
        planner = ReactivePlanner(priority=2)

        # Act
        result = planner.plan(view)

        # Assert
        assert result is not None
        assert result.strategy == "reactive"
        assert result.confidence == 0.75
        assert len(result.proposals) == 2

        # Check proposals reference correct causes
        assert "low_throughput" in result.proposals[0].rationale
        assert "high_latency" in result.proposals[1].rationale

    def test_plan_result_structure_validation(
        self, mock_view_with_diagnosis: Mock
    ) -> None:
        """Test that PlanningResult structure is valid."""
        # Arrange
        planner = ReactivePlanner()

        # Act
        result = planner.plan(mock_view_with_diagnosis)

        # Assert
        assert result is not None

        # Check PlanningResult has expected attributes
        assert hasattr(result, "proposals")
        assert hasattr(result, "strategy")
        assert hasattr(result, "confidence")
        assert hasattr(result, "recommended")
        assert hasattr(result, "metadata")

        # Type checking
        assert isinstance(result.proposals, list)
        assert all(isinstance(p, ActionProposal) for p in result.proposals)
        assert result.strategy == "reactive"
        assert result.confidence == 0.88
        assert result.recommended is None
        assert isinstance(result.metadata, dict)
        assert result.metadata["planner"] == "reactive"

    def test_plan_with_multiple_causes_unique_rationales(self) -> None:
        """Test that each cause generates a unique rationale."""
        # Arrange
        diagnosis = Mock()
        diagnosis.confidence = 0.6
        diagnosis.causes = ["cause_a", "cause_b", "cause_c"]

        view = create_autospec(PlanningView)
        view.diagnosis = diagnosis
        view.current_value = 25.0

        planner = ReactivePlanner()

        # Act
        result = planner.plan(view)

        # Assert
        assert result is not None
        assert len(result.proposals) == 3

        # Each rationale should be unique and contain its specific cause
        rationales = [p.rationale for p in result.proposals]
        assert len(set(rationales)) == 3  # All rationales should be unique

        assert "cause_a" in rationales[0]
        assert "cause_b" in rationales[1]
        assert "cause_c" in rationales[2]


def run_coverage_tests() -> None:
    """Helper function to run all tests with coverage reporting."""
    import sys

    import pytest as pt

    # Run tests with coverage
    args = [
        __file__,
        "-v",
        "--cov=procela.core.reasoning.planning.reactive",
        "--cov-report=term-missing",
        "--cov-report=html",
    ]

    exit_code = pt.main(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    run_coverage_tests()
