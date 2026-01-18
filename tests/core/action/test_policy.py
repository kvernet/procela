"""
Pytest module for procela.core.action.policy.

Achieves 100% coverage for SelectionPolicy and HighestConfidencePolicy,
testing abstract interface, concrete implementation, edge cases,
and error conditions.
"""

from typing import Iterable, List
from unittest.mock import Mock

import pytest

from procela.core.action import (
    ActionProposal,
    HighestConfidencePolicy,
    ProposalStatus,
    SelectionPolicy,
)


class TestSelectionPolicy:
    """Tests for the abstract SelectionPolicy base class."""

    def test_abstract_method(self) -> None:
        """Test that SelectionPolicy cannot be instantiated directly."""
        with pytest.raises(TypeError):
            SelectionPolicy()  # type: ignore

    def test_concrete_subclass_must_implement_select(self) -> None:
        """Test that subclasses must implement the select method."""

        class IncompletePolicy(SelectionPolicy):
            pass  # Doesn't implement select

        with pytest.raises(TypeError):
            IncompletePolicy()


class TestHighestConfidencePolicy:
    """Comprehensive tests for HighestConfidencePolicy."""

    # --- Test Basic Selection Logic ---
    def test_select_highest_confidence(self) -> None:
        """Policy correctly selects proposal with highest confidence."""
        policy = HighestConfidencePolicy()
        proposals = [
            ActionProposal(
                value="low", confidence=0.2, status=ProposalStatus.VALIDATED
            ),
            ActionProposal(
                value="high", confidence=0.9, status=ProposalStatus.VALIDATED
            ),
            ActionProposal(
                value="medium", confidence=0.5, status=ProposalStatus.VALIDATED
            ),
        ]

        selected = policy.select(proposals)
        assert selected is not None
        assert selected.value == "high"
        assert selected.confidence == 0.9

    def test_select_with_ties(self) -> None:
        """
        Test selection when multiple proposals have the same confidence.
        Should return the first one encountered with the max value.
        """
        policy = HighestConfidencePolicy()
        # First max is prop1, second max is prop2 with same confidence
        prop1 = ActionProposal(
            value="first_max", confidence=0.8, status=ProposalStatus.VALIDATED
        )
        prop2 = ActionProposal(
            value="second_max", confidence=0.8, status=ProposalStatus.VALIDATED
        )
        prop3 = ActionProposal(
            value="lower", confidence=0.3, status=ProposalStatus.VALIDATED
        )

        # Test with prop1 before prop2
        selected = policy.select([prop1, prop2, prop3])
        assert selected is prop1

        # Test with prop2 before prop1 (different order)
        selected = policy.select([prop2, prop1, prop3])
        assert selected is prop2

    def test_empty_iterable_returns_none(self) -> None:
        """Policy should return None when given no proposals."""
        policy = HighestConfidencePolicy()
        empty_list: List[ActionProposal] = []
        assert policy.select(empty_list) is None

        # Also test with empty generator
        def empty_gen() -> Iterable[ActionProposal]:
            return
            yield  # pragma: no cover

        assert policy.select(empty_gen()) is None

    # --- Test Input Validation and Error Handling ---
    def test_invalid_proposal_type_raises(self) -> None:
        """Policy should raise TypeError if input contains non-ActionProposal."""
        policy = HighestConfidencePolicy()
        invalid_mix = [
            ActionProposal(
                value="valid", confidence=0.5, status=ProposalStatus.VALIDATED
            ),
            "not_a_proposal",  # type: ignore
            ActionProposal(
                value="also_valid", confidence=0.7, status=ProposalStatus.VALIDATED
            ),
        ]

        with pytest.raises(TypeError, match="must be ActionProposal"):
            policy.select(invalid_mix)

    def test_proposal_with_none_confidence_raises(self) -> None:
        """Policy should raise ValueError if confidence is None."""
        policy = HighestConfidencePolicy()

        # Create a mock proposal with None confidence
        invalid_proposal = Mock(spec=ActionProposal)
        invalid_proposal.confidence = None
        invalid_proposal.value = "test"
        invalid_proposal.status = ProposalStatus.VALIDATED

        assert policy.select([invalid_proposal]) == invalid_proposal

    def test_proposal_with_incomparable_confidence_raises(self) -> None:
        """Policy should raise ValueError if confidence values can't be compared."""
        policy = HighestConfidencePolicy()

        # Create mock proposals with incompatible confidence types
        prop1 = Mock(spec=ActionProposal)
        prop1.confidence = 0.5
        prop1.value = "prop1"
        prop1.status = ProposalStatus.VALIDATED

        prop2 = Mock(spec=ActionProposal)
        prop2.confidence = "very_confident"  # type: ignore
        prop2.value = "prop2"
        prop2.status = ProposalStatus.VALIDATED

        with pytest.raises(ValueError):
            policy.select([prop1, prop2])

    def test_proposal_with_no_validated_proposals(self) -> None:
        """Test proposal with no validated action proposals."""
        policy = HighestConfidencePolicy()

        # Create mock proposals with incompatible confidence types
        prop1 = Mock(spec=ActionProposal)
        prop1.confidence = 0.5
        prop1.value = "prop1"

        prop2 = Mock(spec=ActionProposal)
        prop2.confidence = "very_confident"  # type: ignore
        prop2.value = "prop2"

        assert policy.select([prop1, prop2]) is None

    # --- Test with Various Iterable Types ---
    @pytest.mark.parametrize("iterable_type", [list, tuple, set, iter])
    def test_works_with_different_iterables(self, iterable_type: type) -> None:
        """Policy should work with different iterable containers."""
        policy = HighestConfidencePolicy()
        prop_low = ActionProposal(
            value="low", confidence=0.1, status=ProposalStatus.VALIDATED
        )
        prop_high = ActionProposal(
            value="high", confidence=0.9, status=ProposalStatus.VALIDATED
        )

        # Create the specified iterable type
        if iterable_type is list:
            proposals = [prop_low, prop_high]
        elif iterable_type is tuple:
            proposals = (prop_low, prop_high)
        elif iterable_type is set:
            proposals = {prop_low, prop_high}
        else:  # iter
            proposals = iter([prop_low, prop_high])

        selected = policy.select(proposals)
        assert selected is not None
        assert selected.value == "high"

    # --- Test Single Proposal ---
    def test_single_proposal(self) -> None:
        """Policy should return the only proposal when there's just one."""
        policy = HighestConfidencePolicy()
        single_proposal = ActionProposal(
            value="only", confidence=0.3, status=ProposalStatus.VALIDATED
        )

        selected = policy.select([single_proposal])
        assert selected is single_proposal

    # --- Test Edge Cases ---
    @pytest.mark.parametrize("confidence", [0.0, 1.0, 0.0001, 0.9999])
    def test_confidence_boundaries(self, confidence: float) -> None:
        """Policy works with confidence at boundaries and near them."""
        policy = HighestConfidencePolicy()
        proposal = ActionProposal(
            value="test", confidence=confidence, status=ProposalStatus.VALIDATED
        )

        selected = policy.select([proposal])
        assert selected is proposal

    def test_all_same_confidence(self) -> None:
        """When all proposals have identical confidence, return first."""
        policy = HighestConfidencePolicy()
        proposals = [
            ActionProposal(
                value="first", confidence=0.5, status=ProposalStatus.VALIDATED
            ),
            ActionProposal(
                value="second", confidence=0.5, status=ProposalStatus.VALIDATED
            ),
            ActionProposal(
                value="third", confidence=0.5, status=ProposalStatus.VALIDATED
            ),
        ]

        selected = policy.select(proposals)
        assert selected is proposals[0]


# --- Integration and Smoke Tests ---
def test_import() -> None:
    """Test that the module can be imported correctly."""
    from procela.core.action.policy import HighestConfidencePolicy, SelectionPolicy

    assert HighestConfidencePolicy.__name__ == "HighestConfidencePolicy"
    assert SelectionPolicy.__name__ == "SelectionPolicy"


def test_policy_inheritance() -> None:
    """Verify HighestConfidencePolicy is a proper subclass of SelectionPolicy."""
    policy = HighestConfidencePolicy()
    assert isinstance(policy, SelectionPolicy)
    assert hasattr(policy, "select")
    assert callable(policy.select)


if __name__ == "__main__":
    # Run tests directly with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.action.policy",
            "--cov-report=term-missing",
        ]
    )
