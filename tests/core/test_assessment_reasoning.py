"""Pytest module for procela.core.assessment.reasoning."""

from datetime import datetime, timezone

import pytest

from procela.core.assessment import ReasoningResult, ReasoningTask


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


def test_import() -> None:
    """Test that the module can be imported correctly."""
    assert ReasoningResult.__name__ == "ReasoningResult"


def test_integration_with_reasoning_task() -> None:
    """Integration test with ReasoningTask from task module."""
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
    result = ReasoningResult(
        task=ReasoningTask.ANOMALY_DETECTION,
        success=True,
        result=None,
    )
    with pytest.raises(AttributeError):
        # Try to modify a field
        result.__dict__["_dummy"] = "test"  # type: ignore


if __name__ == "__main__":
    # Run tests directly with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.assessment.reasoning",
            "--cov-report=term-missing",
        ]
    )
