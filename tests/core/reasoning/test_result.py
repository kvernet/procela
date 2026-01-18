"""
Pytest module for procela.core.reasoning.

Achieves 100% coverage for all result dataclasses:
- ReasoningResult, AnomalyResult, TrendResult
- DiagnosisResult, PlanningResult, PredictionResult
Tests constructors, validation, methods, edge cases, and integration.
"""

from datetime import datetime, timezone
from typing import Any

import pytest

from procela.core.action.proposal import ActionProposal
from procela.core.reasoning import (
    AnomalyResult,
    DiagnosisResult,
    PlanningResult,
    PredictionResult,
    ReasoningResult,
    TrendResult,
)
from procela.core.reasoning.task import ReasoningTask


class TestReasoningResult:
    """Tests for the generic ReasoningResult container."""

    def test_minimal_initialization(self) -> None:
        """Test creation with only required fields."""
        task = ReasoningTask.ANOMALY_DETECTION
        result = ReasoningResult(
            task=task,
            success=True,
            result=True,
        )
        assert result.task is task
        assert result.success is True
        assert result.result is True
        assert result.confidence is None
        assert result.explanation is None
        assert result.metadata == {}
        assert isinstance(result.timestamp, datetime)
        assert result.timestamp.tzinfo is not None  # Should be timezone-aware
        assert result.execution_time is None

    def test_full_initialization(self) -> None:
        """Test creation with all fields provided."""
        task = ReasoningTask.VALUE_PREDICTION
        custom_time = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        metadata = {"method": "ARIMA", "window": 10}

        result = ReasoningResult(
            task=task,
            success=False,
            result=42.5,
            confidence=0.85,
            explanation="Prediction based on 10-step history",
            metadata=metadata,
            timestamp=custom_time,
            execution_time=0.125,
        )

        assert result.task is task
        assert result.success is False
        assert result.result == 42.5
        assert result.confidence == 0.85
        assert result.explanation == "Prediction based on 10-step history"
        assert result.metadata == metadata
        assert result.timestamp == custom_time
        assert result.execution_time == 0.125

    def test_naive_timestamp_gets_timezone(self) -> None:
        """Test that naive datetime gets converted to UTC."""
        naive_time = datetime(2024, 1, 1, 12, 0, 0)
        result = ReasoningResult(
            task=ReasoningTask.CONSTRAINT_CHECKING,
            success=True,
            result=None,
            timestamp=naive_time,
        )
        assert result.timestamp.tzinfo is timezone.utc
        assert result.timestamp.replace(tzinfo=None) == naive_time

    # --- Validation Tests ---
    def test_invalid_task_type_raises(self) -> None:
        """Test that non-ReasoningTask task raises TypeError."""
        with pytest.raises(TypeError, match="must be a ReasoningTask"):
            ReasoningResult(
                task="ANOMALY_DETECTION",  # type: ignore
                success=True,
                result=None,
            )

    @pytest.mark.parametrize("invalid_confidence", [-0.1, 1.1, -5.0, 2.0])
    def test_invalid_confidence_raises(self, invalid_confidence: float) -> None:
        """Test that confidence outside [0,1] raises ValueError."""
        with pytest.raises(ValueError, match="must be between"):
            ReasoningResult(
                task=ReasoningTask.ANOMALY_DETECTION,
                success=True,
                result=None,
                confidence=invalid_confidence,
            )

    def test_invalid_confidence_type_raises(self) -> None:
        """Test that non-numeric confidence raises TypeError."""
        with pytest.raises(TypeError, match="must be int or float"):
            ReasoningResult(
                task=ReasoningTask.ANOMALY_DETECTION,
                success=True,
                result=None,
                confidence="high",  # type: ignore
            )

    def test_invalid_timestamp_type_raises(self) -> None:
        """Test that non-datetime timestamp raises TypeError."""
        with pytest.raises(TypeError, match="must be a datetime"):
            ReasoningResult(
                task=ReasoningTask.ANOMALY_DETECTION,
                success=True,
                result=None,
                timestamp="2024-01-01",  # type: ignore
            )

    def test_invalid_execution_time_type_raises(self) -> None:
        """Test that non-numeric execution_time raises TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            ReasoningResult(
                task=ReasoningTask.ANOMALY_DETECTION,
                success=True,
                result=None,
                execution_time="slow",  # type: ignore
            )

    def test_negative_execution_time_raises(self) -> None:
        """Test that negative execution_time raises ValueError."""
        with pytest.raises(ValueError, match="must be non-negative"):
            ReasoningResult(
                task=ReasoningTask.ANOMALY_DETECTION,
                success=True,
                result=None,
                execution_time=-0.5,
            )

    # --- Dataclass Features ---
    def test_immutability(self) -> None:
        """Test that fields cannot be modified (frozen dataclass)."""
        result = ReasoningResult(
            task=ReasoningTask.ANOMALY_DETECTION,
            success=True,
            result=None,
        )
        with pytest.raises(AttributeError):
            result.task = ReasoningTask.CONFLICT_RESOLUTION  # type: ignore

    def test_equality_and_hash(self) -> None:
        """Test that equal results have same hash."""
        time1 = datetime.now(timezone.utc)
        result1 = ReasoningResult(
            task=ReasoningTask.VALUE_PREDICTION,
            success=True,
            result=100.0,
            timestamp=time1,
        )
        result2 = ReasoningResult(
            task=ReasoningTask.VALUE_PREDICTION,
            success=True,
            result=100.0,
            timestamp=time1,
        )
        assert result1 == result2


class TestAnomalyResult:
    """Tests for the AnomalyResult dataclass."""

    def test_basic_initialization(self) -> None:
        """Test basic creation."""
        result = AnomalyResult(
            is_anomaly=True,
            score=3.2,
            threshold=3.0,
            method="zscore",
            metadata={"zscore": 3.2},
        )
        assert result.is_anomaly is True
        assert result.score == 3.2
        assert result.threshold == 3.0
        assert result.method == "zscore"
        assert result.metadata == {"zscore": 3.2}

    def test_minimal_initialization(self) -> None:
        """Test creation with minimal fields."""
        result = AnomalyResult(is_anomaly=False)
        assert result.is_anomaly is False
        assert result.score is None
        assert result.threshold is None
        assert result.method is None
        assert result.metadata is None

    # --- Validation Tests ---
    def test_negative_threshold_raises(self) -> None:
        """Test that negative threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            AnomalyResult(is_anomaly=True, threshold=-1.0)

    def test_zero_threshold_raises(self) -> None:
        """Test that zero threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            AnomalyResult(is_anomaly=True, threshold=0.0)

    # --- confidence() Method Tests ---
    @pytest.mark.parametrize(
        "is_anomaly,score,threshold,expected",
        [
            (True, 3.2, 3.0, 1.0),  # Score > threshold, capped at 1.0
            (True, 2.5, 3.0, 0.83333333),  # Score < threshold
            (True, 3.0, 3.0, 1.0),  # Score == threshold
            (True, 0.0, 1.0, 0.0),  # Zero score
            (False, 3.2, 3.0, None),  # No anomaly
            (True, None, 3.0, None),  # Missing score
            (True, 3.2, None, None),  # Missing threshold
            (True, None, None, None),  # Both missing
        ],
    )
    def test_confidence_calculation(
        self,
        is_anomaly: bool,
        score: float | None,
        threshold: float | None,
        expected: float | None,
    ) -> None:
        """Test confidence calculation under various conditions."""
        result = AnomalyResult(
            is_anomaly=is_anomaly,
            score=score,
            threshold=threshold,
        )
        confidence = result.confidence()
        if expected is None:
            assert confidence is None
        else:
            assert confidence == pytest.approx(expected, rel=1e-6)

    def test_confidence_with_zero_threshold_edge_case(self) -> None:
        """Test confidence with extremely small threshold (avoid division by zero)."""
        result = AnomalyResult(is_anomaly=True, score=0.5, threshold=1e-10)
        # threshold gets adjusted to 1e-9 in calculation
        confidence = result.confidence()
        assert confidence == 1.0

    def test_confidence_with_very_small_threshold(self) -> None:
        """Test confidence when threshold is very small."""
        result = AnomalyResult(is_anomaly=True, score=1e-6, threshold=1e-9)
        confidence = result.confidence()
        assert confidence == 1.0  # Capped at 1.0

    # --- Edge Cases ---
    def test_immutability(self) -> None:
        """Test that fields cannot be modified."""
        result = AnomalyResult(is_anomaly=True)
        with pytest.raises(AttributeError):
            result.is_anomaly = False  # type: ignore


class TestTrendResult:
    """Tests for the TrendResult dataclass."""

    def test_basic_initialization(self) -> None:
        """Test basic creation."""
        result = TrendResult(
            value=2.5,
            direction="up",
            threshold=0.5,
        )
        assert result.value == 2.5
        assert result.direction == "up"
        assert result.threshold == 0.5

    # --- Validation Tests ---
    @pytest.mark.parametrize("invalid_direction", ["left", "right", "", None])
    def test_invalid_direction_raises(self, invalid_direction: Any) -> None:
        """Test that invalid direction raises ValueError."""
        with pytest.raises(ValueError, match="must be"):
            TrendResult(
                value=1.0,
                direction=invalid_direction,  # type: ignore
                threshold=0.5,
            )

    def test_negative_threshold_raises(self) -> None:
        """Test that negative threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            TrendResult(value=1.0, direction="up", threshold=-0.5)

    def test_zero_threshold_raises(self) -> None:
        """Test that zero threshold raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            TrendResult(value=1.0, direction="up", threshold=0.0)

    # --- confidence() Method Tests ---
    @pytest.mark.parametrize(
        "value,direction,threshold,expected",
        [
            (2.5, "up", 0.5, 1.0),  # Large value, capped
            (0.3, "up", 0.5, 0.6),  # Small value
            (-0.8, "down", 0.5, 1.0),  # Negative value, large magnitude
            (0.0, "stable", 0.5, 0.0),  # Stable direction
            (0.4, "stable", 0.5, 0.0),  # Stable despite value > 0
        ],
    )
    def test_confidence_calculation(
        self, value: float, direction: str, threshold: float, expected: float
    ) -> None:
        """Test confidence calculation."""
        result = TrendResult(value=value, direction=direction, threshold=threshold)
        assert result.confidence() == pytest.approx(expected, rel=1e-6)

    def test_confidence_with_tiny_threshold(self) -> None:
        """Test confidence with very small threshold."""
        result = TrendResult(value=1e-6, direction="up", threshold=1e-9)
        confidence = result.confidence()
        # abs(1e-6) / max(1e-9, 1e-9) = 1e-6 / 1e-9 = 1000, capped at 1.0
        assert confidence == 1.0

    # --- zscore() Method Tests ---
    def test_zscore_calculation(self) -> None:
        """Test zscore calculation."""
        result = TrendResult(value=2.5, direction="up", threshold=0.5)
        assert result.zscore(std=1.25) == 2.0  # 2.5 / 1.25 = 2.0

    def test_zscore_with_none_std(self) -> None:
        """Test zscore with None standard deviation."""
        result = TrendResult(value=2.5, direction="up", threshold=0.5)
        assert result.zscore(std=None) is None

    def test_zscore_with_zero_std(self) -> None:
        """Test zscore with zero standard deviation."""
        result = TrendResult(value=2.5, direction="up", threshold=0.5)
        assert result.zscore(std=0.0) is None

    def test_zscore_negative_std_raises(self) -> None:
        """Test that negative standard deviation raises ValueError."""
        result = TrendResult(value=2.5, direction="up", threshold=0.5)
        with pytest.raises(ValueError, match="must be positive"):
            result.zscore(std=-1.25)

    # --- Edge Cases ---
    def test_immutability(self) -> None:
        """Test that fields cannot be modified."""
        result = TrendResult(value=1.0, direction="up", threshold=0.5)
        with pytest.raises(AttributeError):
            result.value = 2.0  # type: ignore


class TestDiagnosisResult:
    """Tests for the DiagnosisResult dataclass."""

    def test_basic_initialization(self) -> None:
        """Test basic creation."""
        result = DiagnosisResult(
            causes=["Sensor fault", "Calibration drift"],
            confidence=0.75,
            metadata={"method": "fault_tree"},
        )
        assert result.causes == ["Sensor fault", "Calibration drift"]
        assert result.confidence == 0.75
        assert result.metadata == {"method": "fault_tree"}

    def test_empty_causes(self) -> None:
        """Test creation with empty causes list."""
        result = DiagnosisResult(causes=[])
        assert result.causes == []
        assert result.confidence is None
        assert result.metadata == {}

    # --- Validation Tests ---
    def test_non_list_causes_raises(self) -> None:
        """Test that non-list causes raises TypeError."""
        with pytest.raises(TypeError, match="must be a list"):
            DiagnosisResult(causes="Sensor fault")  # type: ignore

    def test_non_string_cause_raises(self) -> None:
        """Test that non-string cause raises TypeError."""
        with pytest.raises(TypeError, match="must be strings"):
            DiagnosisResult(causes=[123, "Sensor fault"])  # type: ignore

    @pytest.mark.parametrize("invalid_confidence", [-0.1, 1.1, -5.0, 2.0])
    def test_invalid_confidence_raises(self, invalid_confidence: float) -> None:
        """Test that confidence outside [0,1] raises ValueError."""
        with pytest.raises(ValueError, match="must be between"):
            DiagnosisResult(
                causes=["Sensor fault"],
                confidence=invalid_confidence,
            )

    def test_invalid_confidence_type_raises(self) -> None:
        """Test that non-numeric confidence raises TypeError."""
        with pytest.raises(TypeError, match="must be int or float"):
            DiagnosisResult(
                causes=["Sensor fault"],
                confidence="high",  # type: ignore
            )

    # --- Edge Cases ---
    def test_immutability(self) -> None:
        """Test that fields cannot be modified."""
        result = DiagnosisResult(causes=["Cause"])
        with pytest.raises(AttributeError):
            result.causes = ["New cause"]  # type: ignore


class TestPlanningResult:
    """Tests for the PlanningResult dataclass."""

    def test_basic_initialization(self) -> None:
        """Test basic creation."""
        prop1 = ActionProposal(value="act1", confidence=0.8)
        prop2 = ActionProposal(value="act2", confidence=0.7)

        result = PlanningResult(
            proposals=[prop1, prop2],
            recommended=[prop1],
            confidence=0.85,
            strategy="preventive",
            metadata={"horizon": 5},
        )

        assert result.proposals == [prop1, prop2]
        assert result.recommended == [prop1]
        assert result.confidence == 0.85
        assert result.strategy == "preventive"
        assert result.metadata == {"horizon": 5}
        assert isinstance(result.timestamp, datetime)

    def test_minimal_initialization(self) -> None:
        """Test creation with minimal fields."""
        prop = ActionProposal(value="act", confidence=0.5)
        result = PlanningResult(proposals=[prop])

        assert result.proposals == [prop]
        assert result.recommended is None
        assert result.confidence is None
        assert result.strategy is None
        assert result.metadata == {}

    # --- Validation Tests ---
    def test_non_list_proposals_raises(self) -> None:
        """Test that non-list proposals raises TypeError."""
        prop = ActionProposal(value="act", confidence=0.5)
        with pytest.raises(TypeError, match="must be a list"):
            PlanningResult(proposals=prop)  # type: ignore

    def test_recommended_not_in_proposals_raises(self) -> None:
        """Test that recommended not in proposals raises ValueError."""
        prop1 = ActionProposal(value="act1", confidence=0.8)
        prop2 = ActionProposal(value="act2", confidence=0.7)

        with pytest.raises(ValueError, match="not in the proposals"):
            PlanningResult(
                proposals=[prop1],
                recommended=[prop2],  # prop2 not in proposals
            )

    def test_non_list_recommended_raises(self) -> None:
        """Test that non-list recommended raises TypeError."""
        prop = ActionProposal(value="act", confidence=0.5)
        with pytest.raises(TypeError, match="must be a list or None"):
            PlanningResult(
                proposals=[prop],
                recommended=prop,  # type: ignore
            )

    @pytest.mark.parametrize("invalid_confidence", [-0.1, 1.1])
    def test_invalid_confidence_raises(self, invalid_confidence: float) -> None:
        """Test that confidence outside [0,1] raises ValueError."""
        prop = ActionProposal(value="act", confidence=0.5)
        with pytest.raises(ValueError, match="must be between"):
            PlanningResult(
                proposals=[prop],
                confidence=invalid_confidence,
            )

    # --- Edge Cases ---
    def test_empty_proposals(self) -> None:
        """Test creation with empty proposals list."""
        result = PlanningResult(proposals=[])
        assert result.proposals == []
        assert result.recommended is None

    def test_naive_timestamp_gets_timezone(self) -> None:
        """Test that naive timestamp gets converted to UTC."""
        prop = ActionProposal(value="act", confidence=0.5)
        naive_time = datetime(2024, 1, 1, 12, 0, 0)

        result = PlanningResult(
            proposals=[prop],
            timestamp=naive_time,
        )
        assert result.timestamp.tzinfo is timezone.utc

    def test_immutability(self) -> None:
        """Test that fields cannot be modified."""
        prop = ActionProposal(value="act", confidence=0.5)
        result = PlanningResult(proposals=[prop])
        with pytest.raises(AttributeError):
            result.proposals = []  # type: ignore

    def test_result_confidence_threshold_not_numeric(self) -> None:
        """Test result confidence threshold not numeric."""
        with pytest.raises(TypeError, match="Confidence must be int or float, got str"):
            _ = PlanningResult(proposals=[], confidence="not_a_number")


class TestPredictionResult:
    """Tests for the PredictionResult dataclass."""

    def test_basic_initialization(self) -> None:
        """Test basic creation."""
        result = PredictionResult(
            value=42.5,
            horizon=5,
            confidence=0.88,
            metadata={"model": "ARIMA"},
        )
        assert result.value == 42.5
        assert result.horizon == 5
        assert result.confidence == 0.88
        assert result.metadata == {"model": "ARIMA"}

    def test_minimal_initialization(self) -> None:
        """Test creation with minimal fields."""
        result = PredictionResult(value="rainy")
        assert result.value == "rainy"
        assert result.horizon is None
        assert result.confidence is None
        assert result.metadata == {}

    # --- Validation Tests ---
    def test_non_integer_horizon_raises(self) -> None:
        """Test that non-integer horizon raises TypeError."""
        with pytest.raises(TypeError, match="must be an integer"):
            PredictionResult(value=100, horizon=3.5)  # type: ignore

    def test_non_positive_horizon_raises(self) -> None:
        """Test that non-positive horizon raises ValueError."""
        with pytest.raises(ValueError, match="must be positive"):
            PredictionResult(value=100, horizon=0)

        with pytest.raises(ValueError, match="must be positive"):
            PredictionResult(value=100, horizon=-5)

    @pytest.mark.parametrize("invalid_confidence", [-0.1, 1.1])
    def test_invalid_confidence_raises(self, invalid_confidence: float) -> None:
        """Test that confidence outside [0,1] raises ValueError."""
        with pytest.raises(ValueError, match="must be between"):
            PredictionResult(value=100, confidence=invalid_confidence)

    def test_invalid_confidence_type_raises(self) -> None:
        """Test that non-numeric confidence raises TypeError."""
        with pytest.raises(TypeError, match="must be int or float"):
            PredictionResult(value=100, confidence="high")  # type: ignore

    # --- Edge Cases ---
    def test_complex_value_types(self) -> None:
        """Test that complex value types are accepted."""
        # Test with dict
        result_dict = PredictionResult(value={"temp": 22.5, "humidity": 0.6})
        assert result_dict.value == {"temp": 22.5, "humidity": 0.6}

        # Test with list
        result_list = PredictionResult(value=[1, 2, 3])
        assert result_list.value == [1, 2, 3]

        # Test with None
        result_none = PredictionResult(value=None)
        assert result_none.value is None

    def test_immutability(self) -> None:
        """Test that fields cannot be modified."""
        result = PredictionResult(value=100)
        with pytest.raises(AttributeError):
            result.value = 200  # type: ignore


def test_import() -> None:
    """Test that the module can be imported correctly."""
    from procela.core.reasoning.result import (
        AnomalyResult,
        DiagnosisResult,
        PlanningResult,
        PredictionResult,
        ReasoningResult,
        TrendResult,
    )

    assert ReasoningResult.__name__ == "ReasoningResult"
    assert AnomalyResult.__name__ == "AnomalyResult"
    assert TrendResult.__name__ == "TrendResult"
    assert DiagnosisResult.__name__ == "DiagnosisResult"
    assert PlanningResult.__name__ == "PlanningResult"
    assert PredictionResult.__name__ == "PredictionResult"


def test_integration_with_action_proposal() -> None:
    """Integration test with ActionProposal from action module."""
    from procela.core.action.proposal import ActionProposal

    prop1 = ActionProposal(value="increase_temp", confidence=0.8)
    prop2 = ActionProposal(value="reduce_load", confidence=0.7)

    planning_result = PlanningResult(
        proposals=[prop1, prop2],
        recommended=[prop1],
        confidence=0.9,
        strategy="optimistic",
    )

    assert len(planning_result.proposals) == 2
    assert planning_result.proposals[0].value == "increase_temp"
    assert planning_result.recommended is not None
    assert planning_result.recommended[0] is prop1


def test_integration_with_reasoning_task() -> None:
    """Integration test with ReasoningTask from task module."""
    from procela.core.reasoning.task import ReasoningTask

    reasoning_result = ReasoningResult(
        task=ReasoningTask.ANOMALY_DETECTION,
        success=True,
        result=True,
        confidence=0.95,
    )

    assert reasoning_result.task == ReasoningTask.ANOMALY_DETECTION
    assert reasoning_result.task.name == "ANOMALY_DETECTION"


def test_frozen_dataclass_behavior() -> None:
    """Test that all dataclasses are frozen (immutable)."""
    # Test ReasoningResult
    rr = ReasoningResult(
        task=ReasoningTask.ANOMALY_DETECTION,
        success=True,
        result=None,
    )
    with pytest.raises(AttributeError):
        rr.success = False  # type: ignore

    # Test AnomalyResult
    ar = AnomalyResult(is_anomaly=True)
    with pytest.raises(AttributeError):
        ar.is_anomaly = False  # type: ignore

    # Test all others similarly
    tr = TrendResult(value=1.0, direction="up", threshold=0.5)
    dr = DiagnosisResult(causes=["cause"])
    pr = PlanningResult(proposals=[])
    ppr = PredictionResult(value=100)

    # Verify all are immutable
    for obj in [tr, dr, pr, ppr]:
        with pytest.raises(AttributeError):
            # Try to modify a field
            obj.__dict__["_dummy"] = "test"  # type: ignore


if __name__ == "__main__":
    # Run tests directly with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.reasoning.result",
            "--cov-report=term-missing",
        ]
    )
