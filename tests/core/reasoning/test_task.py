"""
Pytest module for procela.core.reasoning.task.

Achieves 100% coverage for ReasoningTask enumeration,
testing all enum members, custom methods, edge cases, and error handling.
"""

from enum import Enum

import pytest

from procela.core.reasoning import ReasoningTask


class TestReasoningTask:
    """Comprehensive tests for the ReasoningTask enumeration."""

    # --- Test Enum Structure and Members ---
    def test_enum_is_proper_subclass(self) -> None:
        """Test that ReasoningTask is a proper Enum subclass."""
        assert issubclass(ReasoningTask, Enum)
        assert hasattr(ReasoningTask, "__members__")

    def test_all_members_present(self) -> None:
        """Test that all expected reasoning tasks are defined."""
        expected_members = [
            "ANOMALY_DETECTION",
            "CONFLICT_RESOLUTION",
            "ACTION_PROPOSAL",
            "VALUE_PREDICTION",
            "CAUSAL_DIAGNOSIS",
            "UNCERTAINTY_QUANTIFICATION",
            "CONSTRAINT_CHECKING",
            "TREND_ANALYSIS",
            "PATTERN_RECOGNITION",
            "SENSITIVITY_ANALYSIS",
            "INTERVENTION_PLANNING",
        ]

        actual_members = list(ReasoningTask.__members__.keys())
        assert len(actual_members) == len(expected_members)
        for member in expected_members:
            assert member in actual_members
            assert hasattr(ReasoningTask, member)

    def test_member_count(self) -> None:
        """Test that exactly 11 reasoning tasks are defined."""
        assert len(list(ReasoningTask)) == 11

    # --- Test Member Values and Properties ---
    def test_auto_values_assigned(self) -> None:
        """Test that auto() assigns sequential integer values starting from 1."""
        expected_value = 1
        for task in ReasoningTask:
            assert task.value == expected_value
            expected_value += 1

    def test_member_names_and_values(self) -> None:
        """Test specific member names and their corresponding values."""
        assert ReasoningTask.ANOMALY_DETECTION.value == 1
        assert ReasoningTask.ANOMALY_DETECTION.name == "ANOMALY_DETECTION"

        assert ReasoningTask.INTERVENTION_PLANNING.value == 10
        assert ReasoningTask.INTERVENTION_PLANNING.name == "INTERVENTION_PLANNING"

    # --- Test Custom __str__ Method ---
    def test_str_representation(self) -> None:
        """Test the custom string representation of tasks."""
        test_cases = [
            (ReasoningTask.ANOMALY_DETECTION, "Anomaly Detection"),
            (ReasoningTask.CONFLICT_RESOLUTION, "Conflict Resolution"),
            (ReasoningTask.ACTION_PROPOSAL, "Action Proposal"),
            (ReasoningTask.VALUE_PREDICTION, "Value Prediction"),
            (ReasoningTask.CAUSAL_DIAGNOSIS, "Causal Diagnosis"),
            (ReasoningTask.UNCERTAINTY_QUANTIFICATION, "Uncertainty Quantification"),
            (ReasoningTask.CONSTRAINT_CHECKING, "Constraint Checking"),
            (ReasoningTask.TREND_ANALYSIS, "Trend Analysis"),
            (ReasoningTask.PATTERN_RECOGNITION, "Pattern Recognition"),
            (ReasoningTask.SENSITIVITY_ANALYSIS, "Sensitivity Analysis"),
            (ReasoningTask.INTERVENTION_PLANNING, "Intervention Planning"),
        ]

        for task, expected_str in test_cases:
            assert str(task) == expected_str

    # --- Test description Method ---
    def test_description_all_tasks(self) -> None:
        """Test that all tasks have non-empty descriptions."""
        for task in ReasoningTask:
            description = task.description()
            assert isinstance(description, str)
            assert len(description) > 0
            assert description.endswith(".")  # Should be a complete sentence

    def test_description_specific_tasks(self) -> None:
        """Test specific task descriptions."""
        description = ReasoningTask.ANOMALY_DETECTION.description()
        assert "deviations from expected behavior" in description
        description = ReasoningTask.CONFLICT_RESOLUTION.description()
        assert "Resolves contradictions" in description
        description = ReasoningTask.VALUE_PREDICTION.description()
        assert "Forecasts future values" in description
        description = ReasoningTask.CAUSAL_DIAGNOSIS.description()
        assert "Identifies root causes" in description

    # --- Test Enum Operations ---
    def test_iteration(self) -> None:
        """Test that the enum can be iterated in definition order."""
        tasks = list(ReasoningTask)
        assert len(tasks) == 11
        assert tasks[0] is ReasoningTask.ANOMALY_DETECTION
        assert tasks[-1] is ReasoningTask.CAUSAL_DIAGNOSIS
        assert all(isinstance(task, ReasoningTask) for task in tasks)

    def test_membership(self) -> None:
        """Test membership testing for enum values."""
        assert ReasoningTask.ANOMALY_DETECTION in ReasoningTask
        assert ReasoningTask.INTERVENTION_PLANNING in ReasoningTask

        # Test that non-members are not in the enum
        class OtherEnum(Enum):
            OTHER = 1

        assert OtherEnum.OTHER not in ReasoningTask

    def test_comparison(self) -> None:
        """Test equality and identity comparisons."""
        task1 = ReasoningTask.ANOMALY_DETECTION
        task2 = ReasoningTask.ANOMALY_DETECTION
        task3 = ReasoningTask.CONFLICT_RESOLUTION

        # Identity
        assert task1 is task2
        # Equality
        assert task1 == task2
        # Inequality
        assert task1 != task3
        assert not (task1 == task3)

    def test_hashability(self) -> None:
        """Test that tasks are hashable (can be used in sets/dicts)."""
        task_set = {
            ReasoningTask.ANOMALY_DETECTION,
            ReasoningTask.CONFLICT_RESOLUTION,
            ReasoningTask.ANOMALY_DETECTION,  # Duplicate should be ignored
        }
        assert len(task_set) == 2
        assert ReasoningTask.ANOMALY_DETECTION in task_set

        # Test dictionary usage
        task_dict = {
            ReasoningTask.ACTION_PROPOSAL: "important",
            ReasoningTask.VALUE_PREDICTION: "forecast",
        }
        assert task_dict[ReasoningTask.ACTION_PROPOSAL] == "important"

    # --- Test Edge Cases ---
    def test_repr_contains_info(self) -> None:
        """Test that the repr() contains both name and value."""
        task = ReasoningTask.ANOMALY_DETECTION
        repr_str = repr(task)
        assert "ANOMALY_DETECTION" in repr_str
        assert "1" in repr_str  # Should contain the value

    def test_name_and_value_properties(self) -> None:
        """Test the .name and .value properties."""
        task = ReasoningTask.CAUSAL_DIAGNOSIS
        assert task.name == "CAUSAL_DIAGNOSIS"
        assert task.value == 11


# --- Integration and Smoke Tests ---
def test_import() -> None:
    """Test that the module can be imported correctly."""
    from procela.core.reasoning.task import ReasoningTask

    assert ReasoningTask.__name__ == "ReasoningTask"


def test_enum_usage_in_context() -> None:
    """Test typical usage patterns for the ReasoningTask enum."""
    # Typical usage: selecting a task
    selected_task = ReasoningTask.ANOMALY_DETECTION

    # Using in a switch-like pattern
    if selected_task == ReasoningTask.ANOMALY_DETECTION:
        assert selected_task.description().startswith("Identifies")

    # Using in a mapping
    task_handlers = {
        ReasoningTask.ANOMALY_DETECTION: lambda: "handle_anomaly",
        ReasoningTask.VALUE_PREDICTION: lambda: "handle_prediction",
    }
    assert callable(task_handlers[ReasoningTask.ANOMALY_DETECTION])

    # String representation for UI/displays
    display_name = str(ReasoningTask.CONSTRAINT_CHECKING)
    assert display_name == "Constraint Checking"


if __name__ == "__main__":
    # Run tests directly with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.reasoning.task",
            "--cov-report=term-missing",
        ]
    )
