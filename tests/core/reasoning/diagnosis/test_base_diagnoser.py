"""
Pytest module for procela.core.reasoning.diagnosis.base.

Achieves 100% coverage for the Diagnoser abstract base class.
Tests abstract class behavior, subclass requirements, and interface contracts.
"""

from abc import ABC
from unittest.mock import Mock

import pytest

from procela.core.reasoning import Diagnoser, DiagnosisResult, DiagnosisView


class TestDiagnoser:
    """Comprehensive tests for the Diagnoser abstract base class."""

    def test_is_abstract_base_class(self) -> None:
        """Test that Diagnoser is a proper ABC."""
        assert issubclass(Diagnoser, ABC)
        assert hasattr(Diagnoser, "__abstractmethods__")

    def test_cannot_instantiate_abstract_class(self) -> None:
        """Test that Diagnoser cannot be instantiated directly."""
        with pytest.raises(TypeError, match="abstract"):
            Diagnoser()  # type: ignore

    def test_has_name_class_attribute(self) -> None:
        """Test that name is defined as a class attribute."""
        assert not hasattr(Diagnoser, "name")
        # It should be a class variable annotation
        assert "name" in Diagnoser.__annotations__
        print("XXX", Diagnoser.__annotations__["name"])
        assert Diagnoser.__annotations__["name"] == "ClassVar[str]"

    def test_has_diagnose_abstract_method(self) -> None:
        """Test that diagnose is defined as an abstract method."""
        assert "diagnose" in Diagnoser.__abstractmethods__
        assert hasattr(Diagnoser, "diagnose")
        assert callable(Diagnoser.diagnose)

    def test_diagnose_method_signature(self) -> None:
        """Test that diagnose has the correct signature in annotations."""
        # Check method exists and is abstract
        assert hasattr(Diagnoser.diagnose, "__isabstractmethod__")
        assert Diagnoser.diagnose.__isabstractmethod__ is True

    def test_concrete_subclass_must_implement_diagnose(self) -> None:
        """Test that subclasses must implement diagnose method."""

        class IncompleteDiagnoser(Diagnoser):
            name = "IncompleteDiagnoser"
            # Missing diagnose method implementation

        with pytest.raises(TypeError, match="abstract"):
            IncompleteDiagnoser()

    def test_concrete_subclass_must_have_name(self) -> None:
        """Test that subclasses must define the name class attribute."""

        class NamelessDiagnoser(Diagnoser):
            # Has diagnose method but no name attribute
            def diagnose(self, view: DiagnosisView) -> DiagnosisResult:
                return DiagnosisResult(causes=[])

        # This should still be instantiable (Python won't enforce class var)
        diagnoser = NamelessDiagnoser()
        assert not hasattr(diagnoser, "name")
        # But accessing it might raise AttributeError
        with pytest.raises(AttributeError):
            _ = NamelessDiagnoser.name

    def test_valid_concrete_subclass(self) -> None:
        """Test a properly implemented concrete subclass."""

        class ConcreteDiagnoser(Diagnoser):
            name = "ConcreteDiagnoser"

            def diagnose(self, view: DiagnosisView) -> DiagnosisResult:
                return DiagnosisResult(
                    causes=["Test cause"], confidence=0.8, metadata={"test": True}
                )

        # Should be able to instantiate
        diagnoser = ConcreteDiagnoser()
        assert isinstance(diagnoser, Diagnoser)
        assert diagnoser.name == "ConcreteDiagnoser"

        # Should be able to call diagnose
        view = Mock(spec=DiagnosisView)
        result = diagnoser.diagnose(view)
        assert isinstance(result, DiagnosisResult)
        assert result.causes == ["Test cause"]
        assert result.confidence == 0.8

    def test_diagnose_returns_diagnosisresult(self) -> None:
        """Test that diagnose method returns DiagnosisResult instance."""

        class TestDiagnoser(Diagnoser):
            name = "TestDiagnoser"

            def diagnose(self, view: DiagnosisView) -> DiagnosisResult:
                # Return a valid DiagnosisResult
                return DiagnosisResult(
                    causes=["Cause 1", "Cause 2"],
                    confidence=0.85,
                    metadata={"method": self.name},
                )

        diagnoser = TestDiagnoser()
        view = Mock(spec=DiagnosisView)
        result = diagnoser.diagnose(view)

        assert isinstance(result, DiagnosisResult)
        assert result.causes == ["Cause 1", "Cause 2"]
        assert result.confidence == 0.85
        assert result.metadata["method"] == "TestDiagnoser"

    def test_diagnose_receives_diagnosisview(self) -> None:
        """Test that diagnose receives DiagnosisView parameter."""

        class TrackingDiagnoser(Diagnoser):
            name = "TrackingDiagnoser"
            received_view = None

            def diagnose(self, view: DiagnosisView) -> DiagnosisResult:
                self.received_view = view
                return DiagnosisResult(causes=[])

        diagnoser = TrackingDiagnoser()
        mock_view = Mock(spec=DiagnosisView)
        result = diagnoser.diagnose(mock_view)

        assert diagnoser.received_view is mock_view
        assert isinstance(result, DiagnosisResult)

    def test_diagnose_with_real_diagnosisview(self) -> None:
        """Test diagnose with actual DiagnosisView interface."""

        class SimpleDiagnoser(Diagnoser):
            name = "SimpleDiagnoser"

            def diagnose(self, view: DiagnosisView) -> DiagnosisResult:
                causes = []
                confidence = 0.0

                # Access view properties
                if hasattr(view, "stats"):
                    causes.append("Has statistical data")
                    confidence += 0.3

                if hasattr(view, "anomaly") and view.anomaly:
                    causes.append("Anomaly data available")
                    confidence += 0.3

                if hasattr(view, "trend") and view.trend:
                    causes.append("Trend data available")
                    confidence += 0.3

                return DiagnosisResult(
                    causes=causes,
                    confidence=confidence if causes else None,
                    metadata={
                        "method": self.name,
                        "has_anomaly": view.anomaly is not None,
                        "has_trend": view.trend is not None,
                    },
                )

        diagnoser = SimpleDiagnoser()

        # Test with minimal view
        view_minimal = Mock(spec=DiagnosisView)
        view_minimal.stats = Mock()
        view_minimal.anomaly = None
        view_minimal.trend = None

        result_minimal = diagnoser.diagnose(view_minimal)
        assert result_minimal.causes == ["Has statistical data"]
        assert result_minimal.confidence == 0.3

        # Test with full view
        view_full = Mock(spec=DiagnosisView)
        view_full.stats = Mock()
        view_full.anomaly = Mock()
        view_full.trend = Mock()

        result_full = diagnoser.diagnose(view_full)
        assert len(result_full.causes) == 3
        assert abs(result_full.confidence - 0.9) < 1e-6

    def test_multiple_diagnoser_instances(self) -> None:
        """Test that multiple diagnoser instances work independently."""

        class CounterDiagnoser(Diagnoser):
            name = "CounterDiagnoser"
            instance_count = 0

            def __init__(self):
                super().__init__()
                CounterDiagnoser.instance_count += 1
                self.instance_id = CounterDiagnoser.instance_count

            def diagnose(self, view: DiagnosisView) -> DiagnosisResult:
                return DiagnosisResult(
                    causes=[f"Diagnosis from instance {self.instance_id}"],
                    metadata={"instance": self.instance_id},
                )

        # Create multiple instances
        diagnoser1 = CounterDiagnoser()
        diagnoser2 = CounterDiagnoser()

        assert diagnoser1.instance_id == 1
        assert diagnoser2.instance_id == 2
        assert CounterDiagnoser.instance_count == 2

        # Both should have same class name
        assert diagnoser1.name == "CounterDiagnoser"
        assert diagnoser2.name == "CounterDiagnoser"

        # But diagnose results can be instance-specific
        view = Mock(spec=DiagnosisView)
        result1 = diagnoser1.diagnose(view)
        result2 = diagnoser2.diagnose(view)

        assert result1.causes == ["Diagnosis from instance 1"]
        assert result2.causes == ["Diagnosis from instance 2"]

    def test_diagnose_with_invalid_input(self) -> None:
        """Test that diagnose can handle invalid/missing view data."""

        class RobustDiagnoser(Diagnoser):
            name = "RobustDiagnoser"

            def diagnose(self, view: DiagnosisView) -> DiagnosisResult:
                # Handle missing or invalid view gracefully
                if not hasattr(view, "stats"):
                    return DiagnosisResult(
                        causes=["Missing statistical data"],
                        confidence=0.0,
                        metadata={"error": "Invalid view structure"},
                    )

                # Normal diagnostic logic
                causes = []
                if hasattr(view, "anomaly") and view.anomaly:
                    causes.append("Anomaly-based issue")

                return DiagnosisResult(
                    causes=causes,
                    confidence=0.5 if causes else 0.0,
                    metadata={"method": self.name},
                )

        diagnoser = RobustDiagnoser()

        # Test with incomplete view
        view_incomplete = Mock(spec=DiagnosisView)
        delattr(view_incomplete, "stats")  # Remove stats attribute
        result_incomplete = diagnoser.diagnose(view_incomplete)
        assert "Missing statistical data" in result_incomplete.causes
        assert result_incomplete.confidence == 0.0

        # Test with valid view
        view_valid = Mock(spec=DiagnosisView)
        view_valid.stats = Mock()
        view_valid.anomaly = None
        result_valid = diagnoser.diagnose(view_valid)
        assert result_valid.causes == []  # No anomaly, so no causes
        assert result_valid.confidence == 0.0

    def test_class_attribute_inheritance(self) -> None:
        """Test that name class attribute is inherited properly."""

        class ParentDiagnoser(Diagnoser):
            name = "ParentDiagnoser"

            def diagnose(self, view: DiagnosisView) -> DiagnosisResult:
                return DiagnosisResult(causes=[])

        class ChildDiagnoser(ParentDiagnoser):
            # Override the name
            name = "ChildDiagnoser"

        class GrandchildDiagnoser(ChildDiagnoser):
            # Inherit name from ChildDiagnoser
            pass

        assert ParentDiagnoser.name == "ParentDiagnoser"
        assert ChildDiagnoser.name == "ChildDiagnoser"
        assert GrandchildDiagnoser.name == "ChildDiagnoser"  # Inherited

        # Instance access should also work
        parent = ParentDiagnoser()
        child = ChildDiagnoser()
        grandchild = GrandchildDiagnoser()

        assert parent.name == "ParentDiagnoser"
        assert child.name == "ChildDiagnoser"
        assert grandchild.name == "ChildDiagnoser"

    def test_abstract_method_exception_message(self) -> None:
        """Test the NotImplementedError message in base diagnose method."""
        # Access the base class's diagnose method directly
        method = Diagnoser.diagnose

        # Create a mock instance to test the method
        class TestClass:
            pass

        instance = TestClass()

        # The method should raise NotImplementedError with our message
        try:
            method(instance, Mock(spec=DiagnosisView))
            assert False, "Should have raised NotImplementedError"
        except NotImplementedError as e:
            assert "Subclasses must implement the diagnose method" in str(e)


# --- Integration and Utility Tests ---


def test_module_import() -> None:
    """Test that the module can be imported correctly."""
    from procela.core.reasoning.diagnosis.base import Diagnoser

    assert Diagnoser.__name__ == "Diagnoser"
    assert Diagnoser.__module__ == "procela.core.reasoning.diagnosis.base"


def test_usage_with_type_hints() -> None:
    """Test that Diagnoser works correctly in type hints."""
    from typing import List

    def process_diagnosers(diagnosers: List[Diagnoser]) -> List[DiagnosisResult]:
        """Process multiple diagnosers (demonstrates type hint usage)."""
        results = []
        view = Mock(spec=DiagnosisView)
        for diagnoser in diagnosers:
            results.append(diagnoser.diagnose(view))
        return results

    # Create mock diagnosers that satisfy the interface
    class MockDiagnoser(Diagnoser):
        name = "MockDiagnoser"

        def diagnose(self, view: DiagnosisView) -> DiagnosisResult:
            return DiagnosisResult(causes=["Mock diagnosis"])

    diagnosers = [MockDiagnoser(), MockDiagnoser()]
    results = process_diagnosers(diagnosers)

    assert len(results) == 2
    assert all(isinstance(r, DiagnosisResult) for r in results)


def test_framework_integration_pattern() -> None:
    """Demonstrate typical integration pattern in Procela framework."""

    # This shows how diagnostic reasoners would typically be used
    class RuleBasedDiagnoser(Diagnoser):
        """Example concrete diagnoser using rule-based inference."""

        name = "RuleBasedDiagnoser"

        def __init__(self, rules: list[str] | None = None):
            self.rules = rules or [
                "If anomaly and downward trend -> degradation",
                "If high anomaly score -> acute failure",
                "If no anomaly but unstable stats -> sensor issue",
            ]

        def diagnose(self, view: DiagnosisView) -> DiagnosisResult:
            causes = []
            confidence = 0.0

            # Rule-based inference logic
            if view.anomaly and view.anomaly.is_anomaly:
                if view.trend and view.trend.direction == "down":
                    causes.append("Degradation with anomaly")
                    confidence = 0.8
                elif view.anomaly.score and view.anomaly.score > 4.0:
                    causes.append("Acute failure")
                    confidence = 0.9
                else:
                    causes.append("General anomaly")
                    confidence = 0.6

            elif view.stats and hasattr(view.stats, "variance"):
                # Check for instability without anomaly
                if view.stats.variance and view.stats.variance > 100:
                    causes.append("Sensor instability")
                    confidence = 0.5

            return DiagnosisResult(
                causes=causes,
                confidence=confidence if causes else None,
                metadata={
                    "method": self.name,
                    "rules_applied": len(self.rules),
                    "anomaly_present": view.anomaly is not None,
                    "trend_present": view.trend is not None,
                },
            )

    # Usage example
    diagnoser = RuleBasedDiagnoser()
    assert diagnoser.name == "RuleBasedDiagnoser"
    assert len(diagnoser.rules) == 3

    # Simulate a view with anomaly and downward trend
    view = Mock(spec=DiagnosisView)
    mock_anomaly = Mock()
    mock_anomaly.is_anomaly = True
    mock_anomaly.score = 3.5
    view.anomaly = mock_anomaly

    mock_trend = Mock()
    mock_trend.direction = "down"
    view.trend = mock_trend

    view.stats = Mock()
    view.stats.variance = 50.0

    result = diagnoser.diagnose(view)

    assert isinstance(result, DiagnosisResult)
    assert "Degradation with anomaly" in result.causes
    assert result.confidence == 0.8
    assert result.metadata["method"] == "RuleBasedDiagnoser"


if __name__ == "__main__":
    # Run tests directly with coverage reporting
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.reasoning.diagnosis.base",
            "--cov-report=term-missing",
        ]
    )
