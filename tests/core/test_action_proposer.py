"""
Test suite for procela.core.action.proposer module.
100% coverage for ActionProposer class.
"""

from typing import List
from unittest.mock import create_autospec

import pytest

from procela.core.action import (
    ActionEffect,
    ActionProposal,
    ActionProposer,
)
from procela.core.assessment import (
    AnomalyResult,
    StatisticsResult,
    TrendResult,
)
from procela.core.epistemic import VariableView


class TestActionProposer:
    """Test cases for ActionProposer class."""

    # ------------------------------------------------------------
    # Test: View validation
    # ------------------------------------------------------------
    def test_propose_none_view(self):
        """Test propose with None view returns empty list."""
        proposer = ActionProposer()

        result = proposer.propose(None)

        assert result == []
        assert len(result) == 0

    def test_propose_invalid_view_type(self):
        """Test propose raises TypeError with invalid view type."""
        proposer = ActionProposer()

        with pytest.raises(TypeError) as exc_info:
            proposer.propose("not a VariableView")

        assert "`view` should be a VariableView instance" in str(exc_info.value)
        assert "got" in str(exc_info.value)

    # ------------------------------------------------------------
    # Test: No proposals (empty view)
    # ------------------------------------------------------------
    def test_propose_empty_view_no_proposals(self):
        """Test propose with view that has no data for proposals."""
        proposer = ActionProposer()

        # Create minimal VariableView with no anomaly, low confidence, or trend
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.8  # High confidence (> 0.5)
        stats_mock.value = 100.0
        view_mock.stats = stats_mock
        view_mock.anomaly = None  # No anomaly
        view_mock.trend = None  # No trend

        result = proposer.propose(view_mock)

        # Should return empty list
        assert result == []
        assert len(result) == 0

    # ------------------------------------------------------------
    # Test: Anomaly-driven proposal
    # ------------------------------------------------------------
    def test_propose_anomaly_detected(self):
        """Test propose creates anomaly investigation proposal when anomaly detected."""
        proposer = ActionProposer()

        # Create VariableView with anomaly
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.8
        stats_mock.value = 150.0  # Some value
        view_mock.stats = stats_mock

        # Create anomaly result
        anomaly_mock = create_autospec(AnomalyResult)
        anomaly_mock.is_anomaly = True
        anomaly_mock.score = 3.2
        anomaly_mock.threshold = 2.5
        anomaly_mock.confidence.return_value = 0.9
        view_mock.anomaly = anomaly_mock
        view_mock.trend = None

        result = proposer.propose(view_mock)

        # Should have one proposal for anomaly investigation
        assert len(result) == 1
        proposal = result[0]

        assert isinstance(proposal, ActionProposal)
        assert proposal.action == "investigate_anomaly"
        assert proposal.value is None
        assert proposal.confidence == 0.9  # From anomaly.confidence()

        # Check effect
        assert isinstance(proposal.effect, ActionEffect)
        assert "Investigate anomalous variable value" in proposal.effect.description
        assert "Root cause identified" in proposal.effect.expected_outcome
        assert proposal.effect.confidence == 0.9

        # Check metadata
        assert proposal.metadata["anomaly_score"] == 3.2
        assert proposal.metadata["threshold"] == 2.5
        assert proposal.metadata["last_value"] == 150.0

    def test_propose_anomaly_not_detected(self):
        """Test propose doesn't create anomaly proposal when no anomaly."""
        proposer = ActionProposer()

        # Create VariableView with anomaly but is_anomaly = False
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.8
        stats_mock.value = 100.0
        view_mock.stats = stats_mock

        anomaly_mock = create_autospec(AnomalyResult)
        anomaly_mock.is_anomaly = False  # Not an anomaly
        anomaly_mock.score = 1.5
        anomaly_mock.threshold = 2.5
        view_mock.anomaly = anomaly_mock
        view_mock.trend = None

        result = proposer.propose(view_mock)

        # Should NOT create anomaly proposal
        assert result == []

    # ------------------------------------------------------------
    # Test: Low-confidence epistemic proposal
    # ------------------------------------------------------------
    def test_propose_low_confidence(self):
        """Test propose creates improvement proposal when confidence is low."""
        proposer = ActionProposer()

        # Create VariableView with low confidence
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.3  # Low confidence (< 0.5)
        stats_mock.value = 100.0
        view_mock.stats = stats_mock
        view_mock.anomaly = None
        view_mock.trend = None

        result = proposer.propose(view_mock)

        # Should have one proposal for improving observation
        assert len(result) == 1
        proposal = result[0]

        assert isinstance(proposal, ActionProposal)
        assert proposal.action == "improve_observation"
        assert proposal.value is None
        assert proposal.confidence == 0.7  # 1.0 - 0.3

        # Check effect
        assert isinstance(proposal.effect, ActionEffect)
        assert "Increase observation reliability" in proposal.effect.description
        assert "Higher confidence" in proposal.effect.expected_outcome
        assert proposal.effect.confidence == 0.7

        # Check metadata
        assert proposal.metadata["reason"] == "low aggregated confidence"
        assert proposal.metadata["current_confidence"] == 0.3

    def test_propose_confidence_none(self):
        """Test propose handles None confidence from stats."""
        proposer = ActionProposer()

        # Create VariableView with None confidence
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = None  # None confidence
        stats_mock.value = 100.0
        view_mock.stats = stats_mock
        view_mock.anomaly = None
        view_mock.trend = None

        result = proposer.propose(view_mock)

        # Should NOT create low-confidence proposal (confidence is None, not < 0.5)
        assert result == []

    def test_propose_confidence_exactly_0_5(self):
        """Test propose with confidence exactly 0.5 (boundary case)."""
        proposer = ActionProposer()

        # Create VariableView with confidence = 0.5
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.5  # Exactly 0.5
        stats_mock.value = 100.0
        view_mock.stats = stats_mock
        view_mock.anomaly = None
        view_mock.trend = None

        result = proposer.propose(view_mock)

        # Should NOT create proposal (0.5 is not < 0.5)
        assert result == []

    # ------------------------------------------------------------
    # Test: Trend-based proposal
    # ------------------------------------------------------------
    def test_propose_trend_upward(self):
        """Test propose creates trend monitoring proposal for upward trend."""
        proposer = ActionProposer()

        # Create VariableView with upward trend
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.8
        stats_mock.value = 100.0
        view_mock.stats = stats_mock
        view_mock.anomaly = None

        # Create trend result with upward direction
        trend_mock = create_autospec(TrendResult)
        trend_mock.direction = "up"
        trend_mock.value = 2.5
        trend_mock.threshold = 2.0
        trend_mock.confidence.return_value = 0.85
        view_mock.trend = trend_mock

        result = proposer.propose(view_mock)

        # Should have one proposal for trend monitoring
        assert len(result) == 1
        proposal = result[0]

        assert isinstance(proposal, ActionProposal)
        assert proposal.action == "monitor_trend"
        assert proposal.value is None
        assert proposal.confidence == 0.85  # From trend.confidence()

        # Check effect
        assert isinstance(proposal.effect, ActionEffect)
        assert "Monitor variable trend (up)" in proposal.effect.description
        assert "Early detection" in proposal.effect.expected_outcome
        assert proposal.effect.confidence == 0.85

        # Check metadata
        assert proposal.metadata["trend_direction"] == "up"
        assert proposal.metadata["trend_value"] == 2.5
        assert proposal.metadata["threshold"] == 2.0

    def test_propose_trend_downward(self):
        """Test propose creates trend monitoring proposal for downward trend."""
        proposer = ActionProposer()

        # Create VariableView with downward trend
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.8
        stats_mock.value = 100.0
        view_mock.stats = stats_mock
        view_mock.anomaly = None

        trend_mock = create_autospec(TrendResult)
        trend_mock.direction = "down"
        trend_mock.value = -1.8
        trend_mock.threshold = 1.5
        trend_mock.confidence.return_value = 0.75
        view_mock.trend = trend_mock

        result = proposer.propose(view_mock)

        assert len(result) == 1
        proposal = result[0]
        assert proposal.action == "monitor_trend"
        assert proposal.metadata["trend_direction"] == "down"
        assert proposal.metadata["trend_value"] == -1.8

    def test_propose_trend_stable(self):
        """Test propose doesn't create trend proposal for stable trend."""
        proposer = ActionProposer()

        # Create VariableView with stable trend
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.8
        stats_mock.value = 100.0
        view_mock.stats = stats_mock
        view_mock.anomaly = None

        trend_mock = create_autospec(TrendResult)
        trend_mock.direction = "stable"  # Should NOT trigger proposal
        trend_mock.value = 0.5
        trend_mock.threshold = 2.0
        view_mock.trend = trend_mock

        result = proposer.propose(view_mock)

        # Should NOT create trend proposal for "stable"
        assert result == []

    # ------------------------------------------------------------
    # Test: Multiple proposals
    # ------------------------------------------------------------
    def test_propose_all_three_conditions(self):
        """Test propose creates all three types of proposals when all conditions met."""
        proposer = ActionProposer()

        # Create VariableView that triggers all three proposal types
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.3  # Low confidence
        stats_mock.value = 150.0
        view_mock.stats = stats_mock

        # Add anomaly
        anomaly_mock = create_autospec(AnomalyResult)
        anomaly_mock.is_anomaly = True
        anomaly_mock.score = 3.2
        anomaly_mock.threshold = 2.5
        anomaly_mock.confidence.return_value = 0.9
        view_mock.anomaly = anomaly_mock

        # Add trend
        trend_mock = create_autospec(TrendResult)
        trend_mock.direction = "up"
        trend_mock.value = 2.5
        trend_mock.threshold = 2.0
        trend_mock.confidence.return_value = 0.85
        view_mock.trend = trend_mock

        result = proposer.propose(view_mock)

        # Should have all three proposals
        assert len(result) == 3

        # Find each proposal by action
        actions = {p.action for p in result}
        assert actions == {
            "investigate_anomaly",
            "improve_observation",
            "monitor_trend",
        }

        # Verify anomaly proposal
        anomaly_proposal = next(p for p in result if p.action == "investigate_anomaly")
        assert anomaly_proposal.confidence == 0.9
        assert anomaly_proposal.metadata["anomaly_score"] == 3.2

        # Verify low-confidence proposal
        confidence_proposal = next(
            p for p in result if p.action == "improve_observation"
        )
        assert confidence_proposal.confidence == 0.7  # 1.0 - 0.3
        assert confidence_proposal.metadata["current_confidence"] == 0.3

        # Verify trend proposal
        trend_proposal = next(p for p in result if p.action == "monitor_trend")
        assert trend_proposal.confidence == 0.85
        assert trend_proposal.metadata["trend_direction"] == "up"

    # ------------------------------------------------------------
    # Test: Edge cases
    # ------------------------------------------------------------
    def test_propose_trend_none_confidence(self):
        """Test propose handles trend with None confidence."""
        proposer = ActionProposer()

        # Create VariableView with trend but None confidence
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.8
        stats_mock.value = 100.0
        view_mock.stats = stats_mock
        view_mock.anomaly = None

        trend_mock = create_autospec(TrendResult)
        trend_mock.direction = "up"
        trend_mock.value = 2.5
        trend_mock.threshold = 2.0
        trend_mock.confidence.return_value = None  # None confidence
        view_mock.trend = trend_mock

        result = proposer.propose(view_mock)

        # Should still create trend proposal (confidence() returns None)
        # The code uses trend.confidence() directly
        assert len(result) == 1
        proposal = result[0]
        assert proposal.action == "monitor_trend"
        # confidence would be None from trend.confidence()

    def test_propose_anomaly_none_confidence(self):
        """Test propose handles anomaly with None confidence."""
        proposer = ActionProposer()

        # Create VariableView with anomaly but None confidence
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.8
        stats_mock.value = 150.0
        view_mock.stats = stats_mock

        anomaly_mock = create_autospec(AnomalyResult)
        anomaly_mock.is_anomaly = True
        anomaly_mock.score = 3.2
        anomaly_mock.threshold = 2.5
        anomaly_mock.confidence.return_value = None  # None confidence
        view_mock.anomaly = anomaly_mock
        view_mock.trend = None

        result = proposer.propose(view_mock)

        # Should still create anomaly proposal
        assert len(result) == 1
        proposal = result[0]
        assert proposal.action == "investigate_anomaly"
        # confidence would be None from anomaly.confidence()

    def test_propose_stats_none_value(self):
        """Test propose handles stats with None value."""
        proposer = ActionProposer()

        # Create VariableView with None value
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.8
        stats_mock.value = None  # None value
        view_mock.stats = stats_mock

        anomaly_mock = create_autospec(AnomalyResult)
        anomaly_mock.is_anomaly = True
        anomaly_mock.score = 3.2
        anomaly_mock.threshold = 2.5
        anomaly_mock.confidence.return_value = 0.9
        view_mock.anomaly = anomaly_mock
        view_mock.trend = None

        result = proposer.propose(view_mock)

        # Should still create anomaly proposal
        assert len(result) == 1
        proposal = result[0]
        assert proposal.action == "investigate_anomaly"
        assert proposal.metadata["last_value"] is None

    # ------------------------------------------------------------
    # Test: Order of proposals
    # ------------------------------------------------------------
    def test_propose_order(self):
        """Test proposals are created in expected order."""
        proposer = ActionProposer()

        # Create view that triggers all proposals
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.3  # Low confidence
        stats_mock.value = 150.0
        view_mock.stats = stats_mock

        anomaly_mock = create_autospec(AnomalyResult)
        anomaly_mock.is_anomaly = True
        anomaly_mock.score = 3.2
        anomaly_mock.threshold = 2.5
        anomaly_mock.confidence.return_value = 0.9
        view_mock.anomaly = anomaly_mock

        trend_mock = create_autospec(TrendResult)
        trend_mock.direction = "up"
        trend_mock.value = 2.5
        trend_mock.threshold = 2.0
        trend_mock.confidence.return_value = 0.85
        view_mock.trend = trend_mock

        result = proposer.propose(view_mock)

        # Proposals should be in the order they're created in the code:
        # 1. Anomaly proposal
        # 2. Low-confidence proposal
        # 3. Trend proposal
        assert len(result) == 3
        assert result[0].action == "investigate_anomaly"
        assert result[1].action == "improve_observation"
        assert result[2].action == "monitor_trend"

    # ------------------------------------------------------------
    # Test: Realistic scenarios
    # ------------------------------------------------------------
    def test_propose_realistic_sensor_scenario(self):
        """Test propose with realistic sensor data scenario."""
        proposer = ActionProposer()

        # Simulate a sensor with drifting values and low confidence
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.4  # Low confidence
        stats_mock.value = 85.5  # High value
        view_mock.stats = stats_mock

        # No anomaly (value is high but not anomalous)
        anomaly_mock = create_autospec(AnomalyResult)
        anomaly_mock.is_anomaly = False
        view_mock.anomaly = anomaly_mock

        # Upward trend (sensor drifting high)
        trend_mock = create_autospec(TrendResult)
        trend_mock.direction = "up"
        trend_mock.value = 1.8
        trend_mock.threshold = 1.5
        trend_mock.confidence.return_value = 0.88
        view_mock.trend = trend_mock

        result = proposer.propose(view_mock)

        # Should have 2 proposals: low-confidence and trend
        assert len(result) == 2
        actions = {p.action for p in result}
        assert "improve_observation" in actions
        assert "monitor_trend" in actions
        assert "investigate_anomaly" not in actions  # No anomaly

    def test_propose_server_monitoring_scenario(self):
        """Test propose with server monitoring scenario."""
        proposer = ActionProposer()

        # Simulate server CPU monitoring
        view_mock = create_autospec(VariableView)
        stats_mock = create_autospec(StatisticsResult)
        stats_mock.confidence = 0.95  # High confidence
        stats_mock.value = 98.7  # Very high CPU
        view_mock.stats = stats_mock

        # Anomaly detected (CPU spike)
        anomaly_mock = create_autospec(AnomalyResult)
        anomaly_mock.is_anomaly = True
        anomaly_mock.score = 4.2  # Strong anomaly
        anomaly_mock.threshold = 3.0
        anomaly_mock.confidence.return_value = 0.95
        view_mock.anomaly = anomaly_mock

        # Stable trend (not trending, just spiked)
        trend_mock = create_autospec(TrendResult)
        trend_mock.direction = "stable"
        view_mock.trend = trend_mock

        result = proposer.propose(view_mock)

        # Should have 1 proposal: anomaly investigation
        assert len(result) == 1
        proposal = result[0]
        assert proposal.action == "investigate_anomaly"
        assert proposal.metadata["last_value"] == 98.7
        assert proposal.metadata["anomaly_score"] == 4.2


# ------------------------------------------------------------
# Test utilities
# ------------------------------------------------------------
def test_imports():
    """Test that all necessary imports work."""
    from procela.core.action.effect import ActionEffect
    from procela.core.action.proposal import ActionProposal
    from procela.core.action.proposer import ActionProposer
    from procela.core.epistemic import VariableView

    assert ActionProposer is not None
    assert VariableView is not None
    assert ActionEffect is not None
    assert ActionProposal is not None


def test_class_structure():
    """Test ActionProposer class structure."""
    proposer = ActionProposer()

    # Should have propose method
    assert hasattr(proposer, "propose")
    assert callable(proposer.propose)

    # Check method signature
    import inspect

    sig = inspect.signature(proposer.propose)
    params = list(sig.parameters.keys())
    assert params == ["view"]

    # Check return type annotation
    assert sig.return_annotation == List[
        ActionProposal
    ] or "list[ActionProposal]" in str(sig.return_annotation)


# ------------------------------------------------------------
# Running the tests
# ------------------------------------------------------------
if __name__ == "__main__":
    # Simple test runner
    import unittest

    unittest.main()
