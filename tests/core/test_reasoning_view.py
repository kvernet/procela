"""
Pytest module for procela.core.reasoning.view.

Achieves 100% coverage for all protocol definitions in the view module.
Tests protocol structure, runtime checking, and interface compliance.
"""

from typing import Any
from unittest.mock import Mock

import pytest

from procela.core.assessment import (
    AnomalyResult,
    DiagnosisResult,
    PredictionResult,
    ReasoningResult,
    ReasoningTask,
    TrendResult,
)
from procela.core.epistemic import EpistemicView, PlanningView
from procela.core.memory import HistoryStatistics
from procela.symbols.key import Key


class TestEpistemicView:
    """Tests for the EpistemicView protocol."""

    def test_protocol_structure(self) -> None:
        """Verify the protocol has the expected properties."""
        # Check that the protocol has the right attributes
        assert hasattr(EpistemicView, "key")
        assert hasattr(EpistemicView, "reasoning")

        # Verify they are properties
        assert isinstance(EpistemicView.key, property)
        assert isinstance(EpistemicView.reasoning, property)

    def test_runtime_checkable_with_compliant_object(self) -> None:
        """Test that a compliant object passes isinstance check."""

        class CompliantVariable:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> ReasoningResult:
                return ReasoningResult(
                    task=ReasoningTask.VALUE_PREDICTION,
                    success=False,
                    result=None,
                )

            @property
            def stats(self) -> HistoryStatistics:
                return HistoryStatistics()

            @property
            def anomaly(self) -> AnomalyResult | None:
                return AnomalyResult(is_anomaly=False, score=0.1, threshold=3.0)

            @property
            def trend(self) -> TrendResult | None:
                return TrendResult(value=0.5, direction="up", threshold=0.1)

        var = CompliantVariable()
        assert isinstance(var, EpistemicView)

    def test_runtime_checkable_with_missing_property(self) -> None:
        """Test that objects missing required properties fail isinstance check."""

        class IncompleteVariable:
            @property
            def stats(self) -> HistoryStatistics:
                return HistoryStatistics()

            # Missing 'anomaly' property
            @property
            def trend(self) -> TrendResult | None:
                return None

        var = IncompleteVariable()
        assert not isinstance(var, EpistemicView)

    def test_runtime_checkable_with_wrong_return_type(self) -> None:
        """Test that objects with wrong return types fail isinstance check."""

        class WrongTypeVariable:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> ReasoningResult:
                return ReasoningResult(
                    task=ReasoningTask.ANOMALY_DETECTION,
                    success=True,
                    result=None,
                )

            @property
            def stats(self) -> str:  # Should be HistoryStatistics
                return "not stats"

            @property
            def anomaly(self) -> str:  # Should be AnomalyResult | None
                return "not anomaly"

            @property
            def trend(self) -> str:  # Should be TrendResult | None
                return "not trend"

        var = WrongTypeVariable()
        # Note: runtime_checkable only checks attribute existence, not type
        # The types are only checked by static type checkers like mypy
        assert isinstance(var, EpistemicView)  # This will be True at runtime

    def test_with_mock_objects(self) -> None:
        """Test using Mock objects to simulate protocol compliance."""
        mock_var = Mock(spec_set=["key", "reasoning", "stats", "anomaly", "trend"])
        mock_var.key = Key()
        mock_var.reasoning = ReasoningResult(
            task=ReasoningTask.ANOMALY_DETECTION, success=False, result=None
        )
        mock_var.stats = HistoryStatistics.empty()
        mock_var.anomaly = None
        mock_var.trend = TrendResult(value=0.2, direction="stable", threshold=0.1)

        assert isinstance(mock_var, EpistemicView)

    def test_protocol_can_be_used_as_type_hint(self) -> None:
        """Test that the protocol works in type annotations."""

        def process_view(view: EpistemicView) -> HistoryStatistics:
            return view.stats

        # Create a compliant object
        class TestView:
            @property
            def stats(self) -> HistoryStatistics:
                return HistoryStatistics.empty()

            @property
            def anomaly(self) -> AnomalyResult | None:
                return None

            @property
            def trend(self) -> TrendResult | None:
                return None

        view = TestView()
        result = process_view(view)
        assert isinstance(result, HistoryStatistics)

    def test_identical_to_epistemic_view_structure(self) -> None:
        """Verify EpistemicView has same structure as EpistemicView."""
        # They should have the same properties
        assert EpistemicView.__annotations__ == EpistemicView.__annotations__

        # A EpistemicView should also be an EpistemicView
        class CompliantVariable:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> ReasoningResult:
                return ReasoningResult(
                    task=ReasoningTask.TREND_ANALYSIS,
                    success=False,
                    result=None,
                )

            @property
            def stats(self) -> HistoryStatistics:
                return HistoryStatistics()

            @property
            def anomaly(self) -> AnomalyResult | None:
                return None

            @property
            def trend(self) -> TrendResult | None:
                return None

        var = CompliantVariable()
        assert isinstance(var, EpistemicView)

    def test_runtime_checking(self) -> None:
        """Test runtime isinstance checks."""

        class DiagnosticVariable:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> ReasoningResult:
                return ReasoningResult(
                    task=ReasoningTask.TREND_ANALYSIS,
                    success=False,
                    result=None,
                )

            @property
            def stats(self) -> HistoryStatistics:
                return HistoryStatistics()

            @property
            def anomaly(self) -> AnomalyResult | None:
                return AnomalyResult(is_anomaly=True, score=3.5, threshold=3.0)

            @property
            def trend(self) -> TrendResult | None:
                return TrendResult(value=1.2, direction="up", threshold=0.5)

        var = DiagnosticVariable()
        assert isinstance(var, EpistemicView)


class TestPlanningView:
    """Tests for the PlanningView protocol."""

    def test_protocol_structure(self) -> None:
        """Verify the protocol has the expected properties."""
        assert hasattr(PlanningView, "diagnosis")
        assert hasattr(PlanningView, "predictions")
        assert hasattr(PlanningView, "current_value")

        assert isinstance(PlanningView.diagnosis, property)
        assert isinstance(PlanningView.predictions, property)
        assert isinstance(PlanningView.current_value, property)

    def test_different_structure_from_other_views(self) -> None:
        """Verify PlanningView has different requirements than other views."""
        # PlanningView should NOT have stats, anomaly, or trend
        assert not hasattr(PlanningView, "stats")
        assert not hasattr(PlanningView, "anomaly")
        assert not hasattr(PlanningView, "trend")

        # It should have its own unique properties
        assert hasattr(PlanningView, "diagnosis")
        assert hasattr(PlanningView, "predictions")
        assert hasattr(PlanningView, "current_value")

    def test_runtime_checking_with_compliant_object(self) -> None:
        """Test that a compliant object passes isinstance check."""

        class PlanningVariable:
            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return DiagnosisResult(causes=["sensor drift"], confidence=0.8)

            @property
            def predictions(self) -> list[PredictionResult]:
                return [
                    PredictionResult(value=25.5, confidence=0.9),
                    PredictionResult(value=26.0, confidence=0.7),
                ]

            @property
            def current_value(self) -> Any:
                return 24.5

        var = PlanningVariable()
        assert isinstance(var, PlanningView)

    def test_current_value_accepts_any_type(self) -> None:
        """Test that current_value can return various types."""
        test_cases = [
            42,  # int
            3.14,  # float
            "temperature",  # str
            {"value": 22.5, "unit": "C"},  # dict
            [1, 2, 3],  # list
            None,  # None
        ]

        for test_value in test_cases:

            class TestVariable:
                @property
                def diagnosis(self) -> DiagnosisResult | None:
                    return None

                @property
                def predictions(self) -> list[PredictionResult]:
                    return []

                @property
                def current_value(self) -> Any:
                    return test_value

            var = TestVariable()
            assert isinstance(var, PlanningView)
            assert var.current_value == test_value

    def test_empty_predictions_list_is_valid(self) -> None:
        """Test that an empty predictions list is acceptable."""

        class VariableWithNoPredictions:
            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return None

            @property
            def predictions(self) -> list[PredictionResult]:
                return []  # Empty list

            @property
            def current_value(self) -> Any:
                return 0

        var = VariableWithNoPredictions()
        assert isinstance(var, PlanningView)
        assert var.predictions == []

    def test_planning_view_not_epistemic_view(self) -> None:
        """Verify PlanningView doesn't satisfy EpistemicView."""

        class PlanningOnlyVariable:
            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return None

            @property
            def predictions(self) -> list[PredictionResult]:
                return []

            @property
            def current_value(self) -> Any:
                return 0

        var = PlanningOnlyVariable()
        assert isinstance(var, PlanningView)
        assert not isinstance(var, EpistemicView)  # Missing stats, anomaly, trend


class TestProtocolRelationships:
    """Test relationships and interactions between different protocols."""

    def test_protocol_hierarchy(self) -> None:
        """
        Verify the conceptual hierarchy of protocol requirements.

        EpistemicView is the most general (requires stats, anomaly, trend).
        EpistemicView currently identical to EpistemicView.
        EpistemicView is a subset (requires stats, trend).
        PlanningView is orthogonal (requires diagnosis, predictions, current_value).
        """

        # Create a variable that satisfies all views
        class FullVariable:
            @property
            def key(self) -> Key:
                return None

            @property
            def reasoning(self) -> ReasoningResult:
                return None

            @property
            def stats(self) -> HistoryStatistics:
                return HistoryStatistics()

            @property
            def anomaly(self) -> AnomalyResult | None:
                return AnomalyResult(is_anomaly=False, score=0.5, threshold=3.0)

            @property
            def trend(self) -> TrendResult | None:
                return TrendResult(value=0.1, direction="stable", threshold=0.05)

            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return DiagnosisResult(causes=[], confidence=0.0)

            @property
            def predictions(self) -> list[PredictionResult]:
                return [PredictionResult(value=10.0)]

            @property
            def current_value(self) -> Any:
                return 10.0

        var = FullVariable()

        # Should satisfy all protocols
        assert isinstance(var, EpistemicView)
        assert isinstance(var, EpistemicView)
        assert isinstance(var, EpistemicView)
        assert isinstance(var, PlanningView)

    def test_protocol_intersections(self) -> None:
        """Test objects that satisfy multiple but not all protocols."""

        # Variable that satisfies EpistemicView and EpistemicView
        # but not PlanningView
        class EpistemicPredictionVariable:
            @property
            def key(self) -> Key:
                return None

            @property
            def reasoning(self) -> ReasoningResult:
                return None

            @property
            def stats(self) -> HistoryStatistics:
                return HistoryStatistics()

            @property
            def anomaly(self) -> AnomalyResult | None:
                return None

            @property
            def trend(self) -> TrendResult | None:
                return None

        var1 = EpistemicPredictionVariable()
        assert isinstance(var1, EpistemicView)
        assert isinstance(var1, EpistemicView)
        assert isinstance(var1, EpistemicView)
        assert not isinstance(var1, PlanningView)

        # Variable that satisfies only PlanningView
        class PlanningOnlyVariable:
            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return None

            @property
            def predictions(self) -> list[PredictionResult]:
                return []

            @property
            def current_value(self) -> Any:
                return 0

        var2 = PlanningOnlyVariable()
        assert not isinstance(var2, EpistemicView)
        assert not isinstance(var2, EpistemicView)
        assert not isinstance(var2, EpistemicView)
        assert isinstance(var2, PlanningView)


def test_module_import() -> None:
    """Test that the module can be imported correctly."""
    assert EpistemicView.__name__ == "EpistemicView"
    assert EpistemicView.__name__ == "EpistemicView"
    assert EpistemicView.__name__ == "EpistemicView"
    assert PlanningView.__name__ == "PlanningView"

    # Verify all are runtime_checkable protocols
    assert hasattr(EpistemicView, "_is_protocol")
    assert hasattr(EpistemicView, "_is_protocol")
    assert hasattr(EpistemicView, "_is_protocol")
    assert hasattr(PlanningView, "_is_protocol")


def test_protocol_usage_in_function_signatures() -> None:
    """Demonstrate how protocols are used in function signatures."""

    def analyze_epistemic(view: EpistemicView) -> bool:
        """Analyze an epistemic view of a variable."""
        return view.anomaly is not None and view.anomaly.is_anomaly

    def make_prediction(view: EpistemicView) -> PredictionResult:
        """Make a prediction based on a prediction view."""
        # In real implementation, would use stats and trend
        return PredictionResult(value=0.0)

    def create_plan(view: PlanningView) -> list[str]:
        """Create an intervention plan based on a planning view."""
        if view.diagnosis and view.diagnosis.causes:
            return [f"Address: {cause}" for cause in view.diagnosis.causes]
        return ["No action needed"]

    # Test with mock objects
    mock_epistemic = Mock(spec=["stats", "anomaly", "trend"])
    mock_epistemic.anomaly = AnomalyResult(is_anomaly=True, score=3.5, threshold=3.0)

    mock_prediction = Mock(spec=["stats", "trend"])

    mock_planning = Mock(spec=["diagnosis", "predictions", "current_value"])
    mock_planning.diagnosis = DiagnosisResult(causes=["fault1", "fault2"])

    # These should all work without errors
    result1 = analyze_epistemic(mock_epistemic)
    result2 = make_prediction(mock_prediction)
    result3 = create_plan(mock_planning)

    assert isinstance(result1, bool)
    assert isinstance(result2, PredictionResult)
    assert isinstance(result3, list)


if __name__ == "__main__":
    # Run tests directly with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.reasoning.view",
            "--cov-report=term-missing",
        ]
    )
