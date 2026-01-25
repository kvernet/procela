"""
Pytest suite with 100% coverage for PlanningView protocol.
Uses the actual implementations of DiagnosisResult, PredictionResult, and PlanningView.
"""

from dataclasses import FrozenInstanceError, asdict, fields, replace
from typing import Any

import pytest

from procela.core.assessment import DiagnosisResult, PredictionResult
from procela.core.epistemic import PlanningView


class TestPlanningViewProtocolDefinition:
    """Test the PlanningView protocol definition and structure."""

    def test_protocol_is_runtime_checkable(self):
        """Test that PlanningView is decorated with @runtime_checkable."""
        assert hasattr(PlanningView, "_is_runtime_protocol")
        assert PlanningView._is_runtime_protocol is True

    def test_protocol_has_required_properties(self):
        """Test that PlanningView defines all required properties."""
        assert hasattr(PlanningView, "diagnosis")
        assert hasattr(PlanningView, "predictions")
        assert hasattr(PlanningView, "current_value")

        assert isinstance(PlanningView.diagnosis, property)
        assert isinstance(PlanningView.predictions, property)
        assert isinstance(PlanningView.current_value, property)


class TestPlanningViewProtocolCompliance:
    """Test classes that comply with the PlanningView protocol."""

    def test_concrete_class_with_all_properties_is_instance(self):
        """Test a class with all required properties is recognized as PlanningView."""

        class ConcretePlanningView:
            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return DiagnosisResult(causes=["test_cause"], confidence=0.8)

            @property
            def predictions(self) -> list[PredictionResult]:
                return [
                    PredictionResult(value="pred1", horizon=1, confidence=0.7),
                    PredictionResult(value="pred2", horizon=2, confidence=0.6),
                ]

            @property
            def current_value(self) -> Any:
                return "current_state"

        instance = ConcretePlanningView()

        # Runtime protocol checking
        assert isinstance(instance, PlanningView)

        # Verify properties work correctly
        assert instance.diagnosis == DiagnosisResult(
            causes=["test_cause"], confidence=0.8
        )
        assert len(instance.predictions) == 2
        assert instance.current_value == "current_state"

    def test_class_with_none_diagnosis_is_instance(self):
        """Test that a class with None diagnosis still satisfies the protocol."""

        class ViewWithNoneDiagnosis:
            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return None

            @property
            def predictions(self) -> list[PredictionResult]:
                return []

            @property
            def current_value(self) -> Any:
                return 42

        instance = ViewWithNoneDiagnosis()

        assert isinstance(instance, PlanningView)
        assert instance.diagnosis is None
        assert instance.predictions == []
        assert instance.current_value == 42

    def test_class_with_empty_predictions_is_instance(self):
        """Test that a class with empty predictions list satisfies the protocol."""

        class ViewWithEmptyPredictions:
            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return DiagnosisResult(causes=["cause1"])

            @property
            def predictions(self) -> list[PredictionResult]:
                return []

            @property
            def current_value(self) -> Any:
                return {"status": "active"}

        instance = ViewWithEmptyPredictions()

        assert isinstance(instance, PlanningView)
        assert instance.diagnosis == DiagnosisResult(causes=["cause1"])
        assert instance.predictions == []
        assert instance.current_value == {"status": "active"}

    def test_class_with_complex_current_value_is_instance(self):
        """Test with complex current_value types."""

        class ViewWithComplexValue:
            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return DiagnosisResult(
                    causes=["error1", "error2"],
                    confidence=0.9,
                    metadata={"source": "system"},
                )

            @property
            def predictions(self) -> list[PredictionResult]:
                return [
                    PredictionResult(
                        value={"temperature": 25.5, "pressure": 101.3},
                        horizon=5,
                        confidence=0.85,
                        metadata={"model": "weather_v1"},
                    )
                ]

            @property
            def current_value(self) -> Any:
                return {
                    "temperature": 22.5,
                    "humidity": 65.0,
                    "status": "normal",
                    "timestamp": "2024-01-01T12:00:00",
                }

        instance = ViewWithComplexValue()

        assert isinstance(instance, PlanningView)
        assert instance.diagnosis.causes == ["error1", "error2"]
        assert len(instance.predictions) == 1
        assert instance.current_value["temperature"] == 22.5

    def test_class_with_missing_property_not_instance(self):
        """Test class missing any property is NOT recognized as PlanningView."""

        # Missing diagnosis property
        class MissingDiagnosisView:
            @property
            def predictions(self) -> list[PredictionResult]:
                return []

            @property
            def current_value(self) -> Any:
                return None

        instance = MissingDiagnosisView()
        assert not isinstance(instance, PlanningView)

    def test_class_with_methods_instead_of_properties(self):
        """Test that methods (instead of properties) satisfy the protocol."""

        class MethodsInsteadOfProperties:
            def diagnosis(self) -> DiagnosisResult | None:
                return None

            def predictions(self) -> list[PredictionResult]:
                return []

            def current_value(self) -> Any:
                return None

        instance = MethodsInsteadOfProperties()
        assert isinstance(instance, PlanningView)


class TestPlanningViewWithRealDataClasses:
    """Test compliance using actual DiagnosisResult and PredictionResult."""

    def test_full_featured_planning_view(self):
        """Test a comprehensive PlanningView implementation."""

        class FullPlanningView:
            def __init__(self):
                self._diagnosis = DiagnosisResult(
                    causes=["overload", "network_latency"],
                    confidence=0.75,
                    metadata={"priority": "high", "timestamp": "2024-01-01"},
                )
                self._predictions = [
                    PredictionResult(
                        value="recovery",
                        horizon=1,
                        confidence=0.8,
                        metadata={"action": "scale_up"},
                    ),
                    PredictionResult(
                        value="degraded",
                        horizon=3,
                        confidence=0.6,
                        metadata={"action": "monitor"},
                    ),
                    PredictionResult(
                        value="failure",
                        horizon=10,
                        confidence=0.3,
                        metadata={"action": "alert"},
                    ),
                ]
                self._current_value = {
                    "load": 85.5,
                    "status": "degraded",
                    "active_connections": 1250,
                }

            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return self._diagnosis

            @property
            def predictions(self) -> list[PredictionResult]:
                return self._predictions

            @property
            def current_value(self) -> Any:
                return self._current_value

        view = FullPlanningView()

        assert isinstance(view, PlanningView)

        # Test diagnosis
        assert view.diagnosis.confidence == 0.75
        assert "overload" in view.diagnosis.causes
        assert view.diagnosis.metadata["priority"] == "high"

        # Test predictions
        assert len(view.predictions) == 3
        assert view.predictions[0].value == "recovery"
        assert view.predictions[1].horizon == 3
        assert view.predictions[2].confidence == 0.3

        # Test current value
        assert view.current_value["load"] == 85.5
        assert view.current_value["active_connections"] == 1250

    def test_mutable_predictions_list(self):
        """Test that predictions returns a list (which is mutable)."""

        class ViewWithMutablePredictions:
            def __init__(self):
                self._predictions_list = [
                    PredictionResult(value=1),
                    PredictionResult(value=2),
                ]

            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return None

            @property
            def predictions(self) -> list[PredictionResult]:
                return self._predictions_list

            @property
            def current_value(self) -> Any:
                return "test"

        view = ViewWithMutablePredictions()

        assert isinstance(view, PlanningView)

        # Can modify the list (but this doesn't affect protocol compliance)
        view._predictions_list.append(PredictionResult(value=3))
        assert len(view.predictions) == 3

    def test_dynamic_current_value(self):
        """Test current_value that changes dynamically."""

        class DynamicPlanningView:
            def __init__(self):
                self._counter = 0

            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return DiagnosisResult(causes=["dynamic"])

            @property
            def predictions(self) -> list[PredictionResult]:
                return [PredictionResult(value=self._counter + 1)]

            @property
            def current_value(self) -> Any:
                return self._counter

        view = DynamicPlanningView()

        assert isinstance(view, PlanningView)
        assert view.current_value == 0
        assert view.predictions[0].value == 1

        # Simulate state change
        view._counter = 5
        assert view.current_value == 5
        assert view.predictions[0].value == 6


class TestPlanningViewEdgeCases:
    """Test edge cases and special scenarios."""

    def test_lazy_loaded_properties(self):
        """Test implementation with lazy-loaded properties."""

        class LazyPlanningView:
            def __init__(self):
                self._diagnosis_loaded = False
                self._predictions_loaded = False
                self._current_value_loaded = False

            @property
            def diagnosis(self) -> DiagnosisResult | None:
                if not self._diagnosis_loaded:
                    self._diagnosis_value = DiagnosisResult(
                        causes=["lazy_loaded"], confidence=0.9
                    )
                    self._diagnosis_loaded = True
                return self._diagnosis_value

            @property
            def predictions(self) -> list[PredictionResult]:
                if not self._predictions_loaded:
                    self._predictions_value = [
                        PredictionResult(value="lazy_pred", horizon=1)
                    ]
                    self._predictions_loaded = True
                return self._predictions_value

            @property
            def current_value(self) -> Any:
                if not self._current_value_loaded:
                    self._current_value_data = {"loaded": True}
                    self._current_value_loaded = True
                return self._current_value_data

        instance = LazyPlanningView()

        assert not instance._diagnosis_loaded
        assert not instance._predictions_loaded
        assert not instance._current_value_loaded

        # Load on first access
        diagnosis = instance.diagnosis
        predictions = instance.predictions
        current_value = instance.current_value

        assert instance._diagnosis_loaded
        assert instance._predictions_loaded
        assert instance._current_value_loaded
        assert diagnosis.causes == ["lazy_loaded"]
        assert len(predictions) == 1
        assert current_value["loaded"] is True

        assert isinstance(instance, PlanningView)

    def test_property_with_side_effects(self):
        """Test properties that have side effects."""

        class SideEffectView:
            def __init__(self):
                self.access_count = 0

            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return DiagnosisResult(causes=[f"access_{self.access_count}"])

            @property
            def predictions(self) -> list[PredictionResult]:
                self.access_count += 1
                return [PredictionResult(value=f"pred_{self.access_count}")]

            @property
            def current_value(self) -> Any:
                return self.access_count

        instance = SideEffectView()

        assert instance.access_count == 0

        # Access multiple times
        pred1 = instance.predictions
        pred2 = instance.predictions
        pred3 = instance.predictions

        assert instance.access_count == 3
        assert pred1[0].value == "pred_1"
        assert pred2[0].value == "pred_2"
        assert pred3[0].value == "pred_3"
        assert instance.current_value == 3

        assert isinstance(instance, PlanningView)


class TestPlanningViewIntegration:
    """Integration tests for PlanningView usage patterns."""

    def test_use_in_type_annotations(self):
        """Test that PlanningView can be used in type hints."""

        def analyze_planning(view: PlanningView) -> dict:
            """Analyze a planning view and return summary."""
            summary = {
                "has_diagnosis": view.diagnosis is not None,
                "num_predictions": len(view.predictions),
                "current_value_type": type(view.current_value).__name__,
            }

            if view.diagnosis:
                summary["diagnosis_confidence"] = view.diagnosis.confidence
                summary["num_causes"] = len(view.diagnosis.causes)

            if view.predictions:
                summary["first_horizon"] = view.predictions[0].horizon

            return summary

        # Create a compliant view
        class TestPlanningViewImpl:
            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return DiagnosisResult(causes=["test1", "test2"], confidence=0.8)

            @property
            def predictions(self) -> list[PredictionResult]:
                return [
                    PredictionResult(value=1, horizon=1),
                    PredictionResult(value=2, horizon=2),
                ]

            @property
            def current_value(self) -> Any:
                return 42

        view = TestPlanningViewImpl()
        result = analyze_planning(view)

        assert result["has_diagnosis"] is True
        assert result["num_predictions"] == 2
        assert result["current_value_type"] == "int"
        assert result["diagnosis_confidence"] == 0.8
        assert result["num_causes"] == 2
        assert result["first_horizon"] == 1

    def test_multiple_planning_views_comparison(self):
        """Test working with multiple planning views."""

        class SimplePlanningView:
            def __init__(self, name: str, diagnosis_conf: float = None):
                self.name = name
                self._diagnosis_conf = diagnosis_conf

            @property
            def diagnosis(self) -> DiagnosisResult | None:
                if self._diagnosis_conf is None:
                    return None
                return DiagnosisResult(
                    causes=[f"cause_{self.name}"], confidence=self._diagnosis_conf
                )

            @property
            def predictions(self) -> list[PredictionResult]:
                return [
                    PredictionResult(value=f"pred_{self.name}_1"),
                    PredictionResult(value=f"pred_{self.name}_2"),
                ]

            @property
            def current_value(self) -> Any:
                return f"value_{self.name}"

        # Create multiple views
        views = [
            SimplePlanningView("view1", 0.9),
            SimplePlanningView("view2", 0.7),
            SimplePlanningView("view3", None),  # No diagnosis
        ]

        # All should be PlanningView instances
        for view in views:
            assert isinstance(view, PlanningView)

        # Filter views with diagnosis
        views_with_diagnosis = [v for v in views if v.diagnosis is not None]
        assert len(views_with_diagnosis) == 2

        # Sort by diagnosis confidence
        sorted_views = sorted(
            views_with_diagnosis,
            key=lambda v: v.diagnosis.confidence if v.diagnosis else 0,
            reverse=True,
        )
        assert sorted_views[0].name == "view1"
        assert sorted_views[1].name == "view2"

    def test_planning_view_in_collections(self):
        """Test using PlanningView in collections."""

        class CollectionPlanningView:
            def __init__(self, id: int):
                self.id = id

            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return DiagnosisResult(causes=[f"id_{self.id}"])

            @property
            def predictions(self) -> list[PredictionResult]:
                return [PredictionResult(value=self.id)]

            @property
            def current_value(self) -> Any:
                return self.id

        # Create dictionary of views
        views_dict = {i: CollectionPlanningView(i) for i in range(5)}

        # Verify all are PlanningView instances
        for view in views_dict.values():
            assert isinstance(view, PlanningView)

        # Use in list comprehension
        predictions_sum = sum(view.predictions[0].value for view in views_dict.values())
        assert predictions_sum == sum(range(5))  # 0 + 1 + 2 + 3 + 4 = 10


class TestPlanningViewWithDiagnosisResultFeatures:
    """Test PlanningView specifically with DiagnosisResult features."""

    def test_diagnosis_result_immutability(self):
        """Test that DiagnosisResult is immutable (frozen dataclass)."""

        class TestView:
            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return DiagnosisResult(
                    causes=["cause1", "cause2"],
                    confidence=0.8,
                    metadata={"key": "value"},
                )

            @property
            def predictions(self) -> list[PredictionResult]:
                return []

            @property
            def current_value(self) -> Any:
                return None

        view = TestView()
        diagnosis = view.diagnosis

        # DiagnosisResult should be frozen
        with pytest.raises(FrozenInstanceError):
            diagnosis.confidence = 0.9

    def test_diagnosis_result_replace_method(self):
        """Test using replace() method on DiagnosisResult."""

        class TestView:
            def __init__(self):
                self._diagnosis = DiagnosisResult(causes=["initial"], confidence=0.5)

            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return self._diagnosis

            @property
            def predictions(self) -> list[PredictionResult]:
                return []

            @property
            def current_value(self) -> Any:
                return None

            def update_diagnosis(self):
                """Demonstrate updating diagnosis with replace()."""
                self._diagnosis = replace(
                    self._diagnosis, confidence=0.9, metadata={"updated": True}
                )

        view = TestView()
        original = view.diagnosis

        view.update_diagnosis()
        updated = view.diagnosis

        assert original != updated
        assert updated.confidence == 0.9
        assert updated.metadata["updated"] is True
        assert updated.causes == ["initial"]  # Unchanged


class TestPlanningViewWithPredictionResultFeatures:
    """Test PlanningView specifically with PredictionResult features."""

    def test_prediction_result_immutability(self):
        """Test that PredictionResult is immutable (frozen dataclass)."""

        class TestView:
            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return None

            @property
            def predictions(self) -> list[PredictionResult]:
                return [
                    PredictionResult(
                        value="test",
                        horizon=1,
                        confidence=0.8,
                        metadata={"key": "value"},
                    )
                ]

            @property
            def current_value(self) -> Any:
                return None

        view = TestView()
        prediction = view.predictions[0]

        # PredictionResult should be frozen
        with pytest.raises(FrozenInstanceError):
            prediction.value = "new_value"

        with pytest.raises(FrozenInstanceError):
            prediction.confidence = 0.9

    def test_prediction_result_dataclass_features(self):
        """Test PredictionResult dataclass features."""

        class TestView:
            @property
            def diagnosis(self) -> DiagnosisResult | None:
                return None

            @property
            def predictions(self) -> list[PredictionResult]:
                pred = PredictionResult(
                    value=42, horizon=3, confidence=0.75, metadata={"source": "model_a"}
                )

                # Test asdict method
                pred_dict = asdict(pred)
                assert pred_dict["value"] == 42
                assert pred_dict["confidence"] == 0.75

                # Test fields
                field_names = {f.name for f in fields(pred)}
                assert field_names == {"value", "horizon", "confidence", "metadata"}

                return [pred]

            @property
            def current_value(self) -> Any:
                return None

        view = TestView()
        predictions = view.predictions

        assert len(predictions) == 1
        assert predictions[0].value == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
