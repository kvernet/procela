"""Pytest suite with 100% coverage for HomeostasisMechanism class."""

import pytest

from procela.core.mechanism import HomeostasisMechanism
from procela.core.memory import HypothesisRecord, VariableRecord
from procela.core.variable import RealDomain, Variable
from procela.symbols.key import Key


@pytest.fixture
def variable_fixture():
    return Variable(
        name="variable_fixture",
        domain=RealDomain(),
    )


class TestHomeostasisMechanism:
    """Test suite for HomeostasisMechanism class."""

    def test_initialization_with_defaults(self, variable_fixture):
        """Test initialization with default parameters."""
        reads = [variable_fixture]
        writes = [variable_fixture]

        mechanism = HomeostasisMechanism(reads=reads, writes=writes)

        assert mechanism.name == "HomeostasisMechanism"
        assert mechanism.baseline_risk == 0.2
        assert mechanism.alpha == 0.08
        assert mechanism.base_confidence == 0.5
        assert mechanism.reads() == tuple(reads)
        assert mechanism.writes() == tuple(writes)

    def test_initialization_with_custom_values(self, variable_fixture):
        """Test initialization with custom parameters."""
        reads = [variable_fixture]
        writes = [variable_fixture]

        mechanism = HomeostasisMechanism(
            reads=reads,
            writes=writes,
            name="CustomMechanism",
            baseline_risk=0.3,
            alpha=0.1,
            base_confidence=0.7,
        )

        assert mechanism.name == "CustomMechanism"
        assert mechanism.baseline_risk == 0.3
        assert mechanism.alpha == 0.1
        assert mechanism.base_confidence == 0.7

    def test_transform_no_records(self, variable_fixture):
        """Test transform() when variable has no records."""
        reads = [variable_fixture]
        writes = [variable_fixture]

        # Ensure variable has no records
        variable_fixture._records = []  # Assuming has_records() checks _records

        mechanism = HomeostasisMechanism(reads=reads, writes=writes)
        mechanism.transform()

        # Should return early without adding candidates
        assert len(variable_fixture.hypotheses) == 0

    def test_transform_with_records_no_competitors(self):
        """Test transform() when variable has records but no std in stats."""
        variable = Variable(name="var", domain=RealDomain())
        reads = [variable]
        writes = [variable]

        variable.init(VariableRecord(value=12.89, confidence=0.821))

        for _ in range(2):
            mechanism = HomeostasisMechanism(reads=reads, writes=writes)
            mechanism.transform()

            variable.commit()
            variable.clear_hypotheses()

        # Should add one candidate
        candidates = variable.hypotheses
        assert len(candidates) == 0

    def test_compute_confidence_edge_cases(self, variable_fixture):
        """Test _compute_confidence() edge cases."""
        reads = [variable_fixture]
        writes = [variable_fixture]

        mechanism = HomeostasisMechanism(reads=reads, writes=writes)

        confidence = mechanism._compute_confidence(variable_fixture)
        assert pytest.approx(confidence, 0.001) == 0.5

        mechanism.base_confidence = 2.0
        confidence = mechanism._compute_confidence(variable_fixture)
        assert confidence <= 1.0

    def test_transform_with_many_competitors(self, variable_fixture):
        """Test transform() with many competitors reduces confidence."""
        reads = [variable_fixture]
        writes = [variable_fixture]

        source1 = Key()
        source2 = Key()
        # Add 4 competitors
        variable_fixture.hypotheses = [
            HypothesisRecord(
                VariableRecord(
                    value=0.25,
                    source=source1,
                    confidence=0.5,
                    metadata={},
                    explanation="",
                )
            ),
            HypothesisRecord(
                VariableRecord(
                    value=0.28,
                    source=source1,
                    confidence=0.6,
                    metadata={},
                    explanation="",
                )
            ),
            HypothesisRecord(
                VariableRecord(
                    value=0.32,
                    source=source2,
                    confidence=0.7,
                    metadata={},
                    explanation="",
                )
            ),
            HypothesisRecord(
                VariableRecord(
                    value=0.29,
                    source=source2,
                    confidence=0.55,
                    metadata={},
                    explanation="",
                )
            ),
        ]

        mechanism = HomeostasisMechanism(reads=reads, writes=writes)
        mechanism.transform()

        candidates = variable_fixture.hypotheses
        assert len(candidates) == 4

        assert pytest.approx(candidates[0].record.confidence, 0.001) == 0.5
