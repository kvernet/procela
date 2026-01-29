"""Tests for HomeostasisMechanism class."""

from __future__ import annotations

from unittest.mock import Mock, create_autospec

import pytest

from procela.core.mechanism import HomeostasisMechanism, Mechanism
from procela.core.memory import VariableRecord
from procela.core.variable import RealDomain, Variable


class TestHomeostasisMechanism:
    """Test suite for HomeostasisMechanism class."""

    def test_initialization_defaults(self) -> None:
        """Test initialization with default values."""
        # Create mock variables
        read_var = create_autospec(Variable)
        write_var = create_autospec(Variable)

        mechanism = HomeostasisMechanism(reads=[read_var], writes=[write_var])

        assert mechanism.name == "HomeostasisMechanism"
        assert mechanism.baseline_risk == 0.2
        assert mechanism.alpha == 0.08
        assert mechanism.base_confidence == 0.5
        assert mechanism.reads() == (read_var,)
        assert mechanism.writes() == (write_var,)

    def test_initialization_custom_values(self) -> None:
        """Test initialization with custom values."""
        read_var = create_autospec(Variable)
        write_var = create_autospec(Variable)

        mechanism = HomeostasisMechanism(
            reads=[read_var],
            writes=[write_var],
            name="CustomHomeostasis",
            baseline_risk=0.5,
            alpha=0.1,
            base_confidence=0.8,
        )

        assert mechanism.name == "CustomHomeostasis"
        assert mechanism.baseline_risk == 0.5
        assert mechanism.alpha == 0.1
        assert mechanism.base_confidence == 0.8

    def test_transform_no_records(self) -> None:
        """Test transform() when variable has no records."""
        # Create mechanism with mock write variable
        write_var = create_autospec(Variable)
        write_var.has_records.return_value = False

        mechanism = HomeostasisMechanism(
            reads=[create_autospec(Variable)], writes=[write_var]
        )

        # Should return early without adding candidates
        mechanism.transform()

        write_var.has_records.assert_called_once()
        write_var.add_candidate.assert_not_called()

    def test_transform_with_records(self) -> None:
        """Test transform() when variable has records."""
        # Create mechanism with mock write variable
        write_var = create_autospec(Variable)
        write_var.has_records.return_value = True
        write_var.value = 0.3  # Current value

        mechanism = HomeostasisMechanism(
            reads=[create_autospec(Variable)],
            writes=[write_var],
            baseline_risk=0.2,
            alpha=0.1,
            base_confidence=0.7,
        )

        # Mock _compute_confidence to return fixed value
        mechanism._compute_confidence = Mock(return_value=0.5)

        mechanism.transform()

        write_var.has_records.assert_called_once()

        # Verify add_candidate was called with correct parameters
        write_var.add_candidate.assert_called_once()
        call_args = write_var.add_candidate.call_args[0][0]

        assert isinstance(call_args, VariableRecord)
        # Calculate expected value: current - alpha * (current - baseline)
        # 0.3 - 0.1 * (0.3 - 0.2) = 0.3 - 0.1 * 0.1 = 0.29
        assert call_args.value == pytest.approx(0.29)
        assert call_args.source == mechanism.key()
        assert call_args.confidence == 0.5
        assert (
            call_args.explanation == "Partial correction toward the baseline attractor."
        )
        assert "baseline" in call_args.metadata
        assert "alpha" in call_args.metadata
        assert "delta" in call_args.metadata

    def test_compute_confidence_no_competitors(self) -> None:
        """Test _compute_confidence with no competitors."""
        mechanism = HomeostasisMechanism(
            reads=[create_autospec(Variable)],
            writes=[create_autospec(Variable)],
            base_confidence=0.6,
        )

        variable = create_autospec(Variable)
        variable.candidates.return_value = []  # No competitors
        variable.history.return_value = [
            Mock(stats=Mock(return_value=Mock(stats=Mock(return_value=Mock(std=None)))))
        ]

        confidence = mechanism._compute_confidence(variable)

        variable.candidates.assert_called_once_with(exclude=mechanism.key())

        # competition_factor = 1.0 / (1.0 + 0) = 1.0
        # stability_factor = 1.0 (since std is None)
        # confidence = 0.6 * 1.0 * 1.0 = 0.6
        assert confidence == pytest.approx(0.6)

    def test_compute_confidence_with_competitors(self) -> None:
        """Test _compute_confidence with competitors."""
        mechanism = HomeostasisMechanism(
            reads=[create_autospec(Variable)],
            writes=[create_autospec(Variable)],
            base_confidence=0.8,
        )

        variable = create_autospec(Variable)
        variable.candidates.return_value = [Mock(), Mock()]  # 2 competitors
        variable.history.return_value = [
            Mock(stats=Mock(return_value=Mock(stats=Mock(return_value=Mock(std=None)))))
        ]

        confidence = mechanism._compute_confidence(variable)

        # competition_factor = 1.0 / (1.0 + 2) = 1/3 ≈ 0.333
        # stability_factor = 1.0
        # confidence = 0.8 * 0.333 * 1.0 ≈ 0.266
        assert confidence == pytest.approx(0.8 * (1.0 / 3.0))

    def test_compute_confidence_with_std(self) -> None:
        """Test _compute_confidence with standard deviation."""
        mechanism = HomeostasisMechanism(
            reads=[create_autospec(Variable)],
            writes=[create_autospec(Variable)],
            base_confidence=0.5,
        )

        variable = create_autospec(Variable)
        variable.candidates.return_value = [Mock()]  # 1 competitor
        stats_mock = Mock(std=0.2)  # std = 0.2
        variable.history.return_value = [
            Mock(stats=Mock(return_value=Mock(stats=Mock(return_value=stats_mock))))
        ]

        confidence = mechanism._compute_confidence(variable)

        # competition_factor = 1.0 / (1.0 + 1) = 0.5
        # stability_factor = 1.0 / (1.0 + 0.2) = 1/1.2 ≈ 0.833
        # confidence = 0.5 * 0.5 * 0.833 ≈ 0.208
        expected = 0.5 * (1.0 / 2.0) * (1.0 / 1.2)
        assert confidence == pytest.approx(expected)

    def test_compute_confidence_capped_at_one(self) -> None:
        """Test _compute_confidence is capped at 1.0."""
        mechanism = HomeostasisMechanism(
            reads=[create_autospec(Variable)],
            writes=[create_autospec(Variable)],
            base_confidence=2.0,  # > 1.0
        )

        variable = create_autospec(Variable)
        variable.candidates.return_value = []  # No competitors
        variable.history.return_value = [
            Mock(stats=Mock(return_value=Mock(stats=Mock(return_value=Mock(std=None)))))
        ]

        confidence = mechanism._compute_confidence(variable)

        # Should be capped at 1.0
        assert confidence == 1.0

    def test_transform_negative_delta(self) -> None:
        """Test transform() with negative delta (value below baseline)."""
        write_var = create_autospec(Variable)
        write_var.has_records.return_value = True
        write_var.value = 0.1  # Below baseline of 0.2

        mechanism = HomeostasisMechanism(
            reads=[create_autospec(Variable)],
            writes=[write_var],
            baseline_risk=0.2,
            alpha=0.1,
        )

        mechanism._compute_confidence = Mock(return_value=0.5)
        mechanism.transform()

        call_args = write_var.add_candidate.call_args[0][0]
        # delta = 0.1 - 0.2 = -0.1
        # proposed_value = 0.1 - 0.1 * (-0.1) = 0.1 + 0.01 = 0.11
        assert call_args.value == pytest.approx(0.11)
        assert call_args.metadata["delta"] == pytest.approx(-0.1)

    def test_transform_zero_delta(self) -> None:
        """Test transform() with zero delta (value at baseline)."""
        write_var = create_autospec(Variable)
        write_var.has_records.return_value = True
        write_var.value = 0.2  # At baseline

        mechanism = HomeostasisMechanism(
            reads=[create_autospec(Variable)],
            writes=[write_var],
            baseline_risk=0.2,
            alpha=0.1,
        )

        mechanism._compute_confidence = Mock(return_value=0.5)
        mechanism.transform()

        call_args = write_var.add_candidate.call_args[0][0]
        # delta = 0.2 - 0.2 = 0
        # proposed_value = 0.2 - 0.1 * 0 = 0.2
        assert call_args.value == pytest.approx(0.2)
        assert call_args.metadata["delta"] == pytest.approx(0.0)

    def test_inherits_from_mechanism(self) -> None:
        """Test that HomeostasisMechanism inherits from Mechanism."""
        read_var = create_autospec(Variable)
        write_var = create_autospec(Variable)

        mechanism = HomeostasisMechanism(reads=[read_var], writes=[write_var])

        assert isinstance(mechanism, Mechanism)

    def test_key_method_available(self) -> None:
        """Test that key() method is available from parent class."""
        mechanism = HomeostasisMechanism(
            reads=[create_autospec(Variable)], writes=[create_autospec(Variable)]
        )

        # Should have key() method from Mechanism
        assert hasattr(mechanism, "key")
        assert callable(mechanism.key)

    def test_compute_confidence_competition_factor_range(self) -> None:
        """Test competition factor ranges from 0 to 1."""
        mechanism = HomeostasisMechanism(
            reads=[create_autospec(Variable)],
            writes=[create_autospec(Variable)],
            base_confidence=1.0,
        )

        variable = create_autospec(Variable)
        variable.history.return_value = [
            Mock(stats=Mock(return_value=Mock(stats=Mock(return_value=Mock(std=None)))))
        ]

        # Test with 0 competitors
        variable.candidates.return_value = []
        confidence = mechanism._compute_confidence(variable)
        assert confidence == pytest.approx(1.0)  # competition_factor = 1.0

        # Test with many competitors
        variable.candidates.return_value = [Mock()] * 10  # 10 competitors
        confidence = mechanism._compute_confidence(variable)
        # competition_factor = 1.0 / (1.0 + 10) ≈ 0.0909
        assert confidence == pytest.approx(1.0 / 11.0)

    def test_compute_confidence_stability_factor_range(self) -> None:
        """Test stability factor ranges based on std."""
        mechanism = HomeostasisMechanism(
            reads=[create_autospec(Variable)],
            writes=[create_autospec(Variable)],
            base_confidence=1.0,
        )

        variable = create_autospec(Variable)
        variable.candidates.return_value = []  # No competitors

        # Test with std = 0 (maximum stability)
        stats_mock = Mock(std=0.0)
        variable.history.return_value = [
            Mock(stats=Mock(return_value=Mock(stats=Mock(return_value=stats_mock))))
        ]
        confidence = mechanism._compute_confidence(variable)
        # stability_factor = 1.0 / (1.0 + 0) = 1.0
        assert confidence == pytest.approx(1.0)

        # Test with large std (low stability)
        stats_mock = Mock(std=10.0)
        variable.history.return_value = [
            Mock(stats=Mock(return_value=Mock(stats=Mock(return_value=stats_mock))))
        ]
        confidence = mechanism._compute_confidence(variable)
        # stability_factor = 1.0 / (1.0 + 10) ≈ 0.0909
        assert confidence == pytest.approx(1.0 / 11.0)


class TestHomeostasisMechanismEdgeCases:
    """Test edge cases for HomeostasisMechanism."""

    def test_multiple_write_variables(self) -> None:
        """Test behavior with multiple write variables."""
        # Create multiple write variables
        write_var1 = create_autospec(Variable)
        write_var1.has_records.return_value = True
        write_var1.value = 0.3

        write_var2 = create_autospec(Variable)
        write_var2.has_records.return_value = True
        write_var2.value = 0.4

        mechanism = HomeostasisMechanism(
            reads=[create_autospec(Variable)],
            writes=[write_var1, write_var2],
            baseline_risk=0.2,
            alpha=0.1,
        )

        mechanism._compute_confidence = Mock(return_value=0.5)
        mechanism.transform()

        # Should only process first write variable (as per implementation)
        write_var1.add_candidate.assert_called_once()
        write_var2.add_candidate.assert_not_called()

    def test_empty_reads_writes(self) -> None:
        """Test initialization with empty reads/writes."""
        mechanism = HomeostasisMechanism(reads=[], writes=[])

        assert mechanism.reads() == ()
        assert mechanism.writes() == ()

    def test_history_empty(self) -> None:
        """Test _compute_confidence when history is empty."""
        mechanism = HomeostasisMechanism(
            reads=[Variable(name="x", domain=RealDomain())],
            writes=[Variable(name="y", domain=RealDomain())],
        )

        variable = Variable(name="z", domain=RealDomain())

        # Should not crash
        confidence = mechanism._compute_confidence(variable)
        assert confidence == mechanism.base_confidence


# Helper fixtures for common test setup
@pytest.fixture
def mock_variable():
    """Create a mock Variable for testing."""
    from unittest.mock import Mock

    variable = Mock()
    variable.has_records.return_value = True
    variable.value = 0.3
    variable.candidates.return_value = []
    variable.history.return_value = [
        Mock(stats=Mock(return_value=Mock(stats=Mock(return_value=Mock(std=None)))))
    ]
    return variable


@pytest.fixture
def homeostasis_mechanism(mock_variable):
    """Create a HomeostasisMechanism for testing."""
    return HomeostasisMechanism(reads=[mock_variable], writes=[mock_variable])
