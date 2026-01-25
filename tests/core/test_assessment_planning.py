"""Pytest module for procela.core.assessment.planning."""

from datetime import datetime, timezone

import pytest

from procela.core.action.proposal import ActionProposal
from procela.core.assessment import PlanningResult


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


def test_import() -> None:
    """Test that the module can be imported correctly."""
    assert PlanningResult.__name__ == "PlanningResult"


def test_integration_with_action_proposal() -> None:
    """Integration test with ActionProposal from action module."""
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


def test_frozen_dataclass_behavior() -> None:
    """Test that all dataclasses are frozen (immutable)."""
    pr = PlanningResult(proposals=[])

    # Verify all are immutable
    with pytest.raises(AttributeError):
        # Try to modify a field
        pr.__dict__["_dummy"] = "test"  # type: ignore


if __name__ == "__main__":
    # Run tests directly with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.assessment.planning",
            "--cov-report=term-missing",
        ]
    )
