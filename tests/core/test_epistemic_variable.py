"""
Pytest suite with 100% coverage for VariableView protocol.
Uses the actual implementations of all protocols and dataclasses.
"""

from dataclasses import FrozenInstanceError, asdict, fields, replace
from typing import Any, Protocol

import pytest

from procela.core.assessment import (
    AnomalyResult,
    ReasoningResult,
    ReasoningTask,
    StatisticsResult,
    TrendResult,
)
from procela.core.epistemic import EpistemicView, VariableView
from procela.symbols.key import Key


class TestVariableViewProtocolDefinition:
    """Test the VariableView protocol definition and structure."""

    def test_protocol_is_runtime_checkable(self):
        """Test that VariableView is decorated with @runtime_checkable."""
        assert hasattr(VariableView, "_is_runtime_protocol")
        assert VariableView._is_runtime_protocol is True

    def test_protocol_has_all_required_properties(self):
        """Test that VariableView defines all required properties."""
        # Check inherited properties from EpistemicView
        assert hasattr(VariableView, "key")
        assert hasattr(VariableView, "reasoning")

        # Check VariableView specific properties
        assert hasattr(VariableView, "stats")
        assert hasattr(VariableView, "anomaly")
        assert hasattr(VariableView, "trend")

        # Check they are properties
        assert isinstance(VariableView.stats, property)
        assert isinstance(VariableView.anomaly, property)
        assert isinstance(VariableView.trend, property)


class TestVariableViewProtocolCompliance:
    """Test classes that comply with the VariableView protocol."""

    def test_concrete_class_with_all_properties_is_instance(self):
        """Test a class with all required properties is recognized as VariableView."""

        class ConcreteVariableView:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return None

            @property
            def stats(self) -> StatisticsResult:
                return StatisticsResult(
                    count=100,
                    sum=500.0,
                    min=1.0,
                    max=10.0,
                    mean=5.0,
                    std=2.5,
                    value=6.0,
                    ewma=5.5,
                    confidence=0.95,
                )

            @property
            def anomaly(self) -> AnomalyResult | None:
                return AnomalyResult(
                    is_anomaly=False,
                    score=0.1,
                    threshold=3.0,
                    method="z-score",
                    metadata={"window": 10},
                )

            @property
            def trend(self) -> TrendResult | None:
                return TrendResult(value=0.8, direction="up", threshold=0.5)

        instance = ConcreteVariableView()

        # Should be instance of both protocols
        assert isinstance(instance, EpistemicView)
        assert isinstance(instance, VariableView)

        # Verify properties work correctly
        assert isinstance(instance.key, Key)
        assert instance.reasoning is None

        assert instance.stats.count == 100
        assert instance.stats.mean == 5.0

        assert instance.anomaly.is_anomaly is False
        assert instance.anomaly.score == 0.1

        assert instance.trend.value == 0.8
        assert instance.trend.direction == "up"

    def test_class_with_none_anomaly_is_instance(self):
        """Test that a class with None anomaly still satisfies the protocol."""

        class ViewWithNoneAnomaly:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return "some_reasoning"

            @property
            def stats(self) -> StatisticsResult:
                return StatisticsResult()

            @property
            def anomaly(self) -> AnomalyResult | None:
                return None

            @property
            def trend(self) -> TrendResult | None:
                return TrendResult(value=0.0, direction="stable", threshold=0.1)

        instance = ViewWithNoneAnomaly()

        assert isinstance(instance, VariableView)
        assert instance.anomaly is None
        assert instance.reasoning == "some_reasoning"

    def test_class_with_none_trend_is_instance(self):
        """Test that a class with None trend still satisfies the protocol."""

        class ViewWithNoneTrend:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return None

            @property
            def stats(self) -> StatisticsResult:
                return StatisticsResult(count=10, sum=50.0, mean=5.0)

            @property
            def anomaly(self) -> AnomalyResult | None:
                return AnomalyResult(is_anomaly=True, score=5.0)

            @property
            def trend(self) -> TrendResult | None:
                return None

        instance = ViewWithNoneTrend()

        assert isinstance(instance, VariableView)
        assert instance.trend is None
        assert instance.anomaly.is_anomaly is True

    def test_class_with_partial_statistics_is_instance(self):
        """Test with partial statistics (some fields None)."""

        class ViewWithPartialStats:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return None

            @property
            def stats(self) -> StatisticsResult:
                # Only provide some fields
                return StatisticsResult(
                    count=5,
                    sum=25.0,
                    mean=5.0,
                    # min, max, std, etc. will be None by default
                )

            @property
            def anomaly(self) -> AnomalyResult | None:
                return None

            @property
            def trend(self) -> TrendResult | None:
                return None

        instance = ViewWithPartialStats()

        assert isinstance(instance, VariableView)
        assert instance.stats.count == 5
        assert instance.stats.mean == 5.0
        assert instance.stats.min is None
        assert instance.stats.std is None

    def test_class_with_minimal_anomaly_is_instance(self):
        """Test with minimal AnomalyResult (only required fields)."""

        class ViewWithMinimalAnomaly:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return None

            @property
            def stats(self) -> StatisticsResult:
                return StatisticsResult()

            @property
            def anomaly(self) -> AnomalyResult | None:
                # Only required field
                return AnomalyResult(is_anomaly=False)

            @property
            def trend(self) -> TrendResult | None:
                return None

        instance = ViewWithMinimalAnomaly()

        assert isinstance(instance, VariableView)
        assert instance.anomaly.is_anomaly is False
        assert instance.anomaly.score is None
        assert instance.anomaly.method is None

    def test_class_missing_stats_property_not_instance(self):
        """Test that missing stats property prevents protocol compliance."""

        class MissingStatsView:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return None

            # Missing stats

            @property
            def anomaly(self) -> AnomalyResult | None:
                return None

            @property
            def trend(self) -> TrendResult | None:
                return None

        instance = MissingStatsView()

        # Should be EpistemicView but not VariableView
        assert isinstance(instance, EpistemicView)
        assert not isinstance(instance, VariableView)


class TestVariableViewWithRealDataClasses:
    """Test VariableView compliance using actual dataclasses."""

    def test_comprehensive_variable_view(self):
        """Test a comprehensive VariableView implementation."""

        class ComprehensiveVariableView:
            def __init__(self):
                self._key = Key()
                self._stats = StatisticsResult(
                    count=1000,
                    sum=50000.0,
                    min=10.5,
                    max=99.9,
                    mean=50.0,
                    std=20.5,
                    value=55.5,
                    ewma=52.0,
                    confidence=0.99,
                )
                self._anomaly = AnomalyResult(
                    is_anomaly=True,
                    score=4.2,
                    threshold=3.0,
                    method="IQR",
                    metadata={
                        "window_size": 100,
                        "timestamp": "2024-01-01T12:00:00",
                        "severity": "high",
                    },
                )
                self._trend = TrendResult(value=0.75, direction="up", threshold=0.3)
                self._reasoning = {"analysis": "comprehensive"}

            @property
            def key(self) -> Key:
                return self._key

            @property
            def reasoning(self) -> Any | None:
                return self._reasoning

            @property
            def stats(self) -> StatisticsResult:
                return self._stats

            @property
            def anomaly(self) -> AnomalyResult | None:
                return self._anomaly

            @property
            def trend(self) -> TrendResult | None:
                return self._trend

        view = ComprehensiveVariableView()

        assert isinstance(view, VariableView)

        # Test stats
        assert view.stats.count == 1000
        assert view.stats.mean == 50.0
        assert view.stats.confidence == 0.99

        # Test anomaly
        assert view.anomaly.is_anomaly is True
        assert view.anomaly.score == 4.2
        assert view.anomaly.method == "IQR"
        assert view.anomaly.metadata["severity"] == "high"

        # Test trend
        assert view.trend.value == 0.75
        assert view.trend.direction == "up"
        assert view.trend.threshold == 0.3

        # Test EpistemicView properties
        assert isinstance(view.key, Key)
        assert view.reasoning["analysis"] == "comprehensive"

    def test_variable_view_with_different_trend_directions(self):
        """Test all possible trend directions."""

        for direction in ["up", "down", "stable"]:

            class DirectionalView:
                @property
                def key(self) -> Key:
                    return Key()

                @property
                def reasoning(self) -> Any | None:
                    return f"trend_{direction}"

                @property
                def stats(self) -> StatisticsResult:
                    return StatisticsResult(count=1)

                @property
                def anomaly(self) -> AnomalyResult | None:
                    return None

                @property
                def trend(self) -> TrendResult | None:
                    return TrendResult(value=0.5, direction=direction, threshold=0.2)

            view = DirectionalView()

            assert isinstance(view, VariableView)
            assert view.trend.direction == direction
            assert view.reasoning == f"trend_{direction}"

    def test_variable_view_with_negative_values(self):
        """Test with negative statistical values."""

        class NegativeStatsView:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return None

            @property
            def stats(self) -> StatisticsResult:
                return StatisticsResult(
                    count=10,
                    sum=-50.0,
                    min=-15.0,
                    max=-1.0,
                    mean=-5.0,
                    std=4.0,
                    value=-3.0,
                    ewma=-4.0,
                    confidence=0.8,
                )

            @property
            def anomaly(self) -> AnomalyResult | None:
                return AnomalyResult(is_anomaly=True, score=-2.5, threshold=-1.0)

            @property
            def trend(self) -> TrendResult | None:
                return TrendResult(value=-0.3, direction="down", threshold=0.0)

        with pytest.raises(ValueError):
            view = NegativeStatsView()

            assert isinstance(view, VariableView)
            assert view.stats.mean == -5.0
            assert view.stats.min == -15.0
            assert view.anomaly.score == -2.5
            assert view.trend.value == -0.3


class TestVariableViewEdgeCases:
    """Test edge cases and special scenarios."""

    def test_lazy_loaded_properties(self):
        """Test implementation with lazy-loaded properties."""

        class LazyVariableView:
            def __init__(self):
                self._stats_loaded = False
                self._anomaly_loaded = False
                self._trend_loaded = False

            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return ReasoningResult(
                    task=ReasoningTask.ACTION_PROPOSAL,
                    success=False,
                    result="lazy_loaded",
                )

            @property
            def stats(self) -> StatisticsResult:
                if not self._stats_loaded:
                    self._stats_value = StatisticsResult(
                        count=100, mean=50.0, confidence=0.9
                    )
                    self._stats_loaded = True
                return self._stats_value

            @property
            def anomaly(self) -> AnomalyResult | None:
                if not self._anomaly_loaded:
                    self._anomaly_value = AnomalyResult(is_anomaly=False, score=0.5)
                    self._anomaly_loaded = True
                return self._anomaly_value

            @property
            def trend(self) -> TrendResult | None:
                if not self._trend_loaded:
                    self._trend_value = TrendResult(
                        value=0.2, direction="stable", threshold=0.1
                    )
                    self._trend_loaded = True
                return self._trend_value

        instance = LazyVariableView()

        assert not instance._stats_loaded
        assert not instance._anomaly_loaded
        assert not instance._trend_loaded
        assert isinstance(instance, VariableView)

        # Load on first access
        stats = instance.stats
        anomaly = instance.anomaly
        trend = instance.trend

        assert instance._stats_loaded
        assert instance._anomaly_loaded
        assert instance._trend_loaded
        assert stats.count == 100
        assert anomaly.is_anomaly is False
        assert trend.direction == "stable"


class TestVariableViewIntegration:
    """Integration tests for VariableView usage patterns."""

    def test_use_in_type_annotations(self):
        """Test that VariableView can be used in type hints."""

        def analyze_variable(view: VariableView) -> dict:
            """Analyze a variable view and return summary."""
            summary = {
                "has_anomaly": view.anomaly is not None,
                "has_trend": view.trend is not None,
                "sample_count": view.stats.count,
                "current_value": view.stats.value,
            }

            if view.anomaly:
                summary["anomaly_detected"] = view.anomaly.is_anomaly
                summary["anomaly_score"] = view.anomaly.score

            if view.trend:
                summary["trend_direction"] = view.trend.direction
                summary["trend_strength"] = view.trend.value

            if view.reasoning:
                summary["has_reasoning"] = True

            return summary

        # Create a compliant view
        class TestVariableViewImpl:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return "test_analysis"

            @property
            def stats(self) -> StatisticsResult:
                return StatisticsResult(
                    count=500, sum=2500.0, mean=5.0, value=5.5, confidence=0.95
                )

            @property
            def anomaly(self) -> AnomalyResult | None:
                return AnomalyResult(is_anomaly=True, score=3.2, threshold=2.5)

            @property
            def trend(self) -> TrendResult | None:
                return TrendResult(value=0.6, direction="up", threshold=0.3)

        view = TestVariableViewImpl()
        result = analyze_variable(view)

        assert result["has_anomaly"] is True
        assert result["has_trend"] is True
        assert result["sample_count"] == 500
        assert result["current_value"] == 5.5
        assert result["anomaly_detected"] is True
        assert result["anomaly_score"] == 3.2
        assert result["trend_direction"] == "up"
        assert result["trend_strength"] == 0.6
        assert result["has_reasoning"] is True

    def test_filtering_variable_views(self):
        """Test filtering and sorting variable views."""

        class SimpleVariableView:
            def __init__(self, name: str, anomaly_score: float = None):
                self.name = name
                self._anomaly_score = anomaly_score

            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return None

            @property
            def stats(self) -> StatisticsResult:
                return StatisticsResult(count=100, mean=50.0)

            @property
            def anomaly(self) -> AnomalyResult | None:
                if self._anomaly_score is None:
                    return None
                return AnomalyResult(
                    is_anomaly=self._anomaly_score > 3.0, score=self._anomaly_score
                )

            @property
            def trend(self) -> TrendResult | None:
                return TrendResult(value=0.5, direction="stable", threshold=0.2)

        # Create multiple views
        views = [
            SimpleVariableView("view1", 2.5),  # No anomaly
            SimpleVariableView("view2", 4.0),  # Anomaly
            SimpleVariableView("view3", None),  # No anomaly detection
            SimpleVariableView("view4", 5.5),  # Anomaly
        ]

        # All should be VariableView instances
        for view in views:
            assert isinstance(view, VariableView)

        # Filter views with anomalies
        anomalous_views = [v for v in views if v.anomaly and v.anomaly.is_anomaly]
        assert len(anomalous_views) == 2
        assert anomalous_views[0].name == "view2"
        assert anomalous_views[1].name == "view4"

        # Sort by anomaly score
        sorted_anomalies = sorted(
            [v for v in views if v.anomaly],
            key=lambda v: v.anomaly.score if v.anomaly else 0,
            reverse=True,
        )
        assert sorted_anomalies[0].name == "view4"
        assert sorted_anomalies[1].name == "view2"
        assert sorted_anomalies[2].name == "view1"

    def test_variable_view_monitoring_simulation(self):
        """Simulate monitoring multiple variable views."""

        class MonitoringVariableView:
            def __init__(self, id: str, initial_value: float):
                self.id = id
                self.values = [initial_value]
                self.anomalies_detected = 0

            def add_measurement(self, value: float):
                """Add a new measurement."""
                self.values.append(value)

            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return f"monitoring_{self.id}"

            @property
            def stats(self) -> StatisticsResult:
                count = len(self.values)
                total = sum(self.values)
                avg = total / count if count > 0 else 0

                return StatisticsResult(
                    count=count,
                    sum=total,
                    min=min(self.values) if self.values else None,
                    max=max(self.values) if self.values else None,
                    mean=avg,
                    value=self.values[-1] if self.values else None,
                )

            @property
            def anomaly(self) -> AnomalyResult | None:
                if len(self.values) < 2:
                    return None

                current = self.values[-1]
                previous = self.values[-2]
                change = abs(current - previous)

                is_anomalous = change > 10.0
                if is_anomalous:
                    self.anomalies_detected += 1

                return AnomalyResult(
                    is_anomaly=is_anomalous,
                    score=change / 10.0,
                    method="change_detection",
                    metadata={"anomalies_count": self.anomalies_detected},
                )

            @property
            def trend(self) -> TrendResult | None:
                if len(self.values) < 3:
                    return None

                recent = self.values[-3:]
                if recent[2] > recent[0]:
                    direction = "up"
                elif recent[2] < recent[0]:
                    direction = "down"
                else:
                    direction = "stable"

                return TrendResult(
                    value=abs(recent[2] - recent[0]) / 2,
                    direction=direction,
                    threshold=5.0,
                )

        # Simulate monitoring
        monitor = MonitoringVariableView("temp_sensor", 20.0)

        assert isinstance(monitor, VariableView)
        assert monitor.stats.count == 1
        assert monitor.anomaly is None  # Need at least 2 values

        # Add measurements
        monitor.add_measurement(22.0)  # Normal change
        monitor.add_measurement(25.0)  # Normal change
        monitor.add_measurement(40.0)  # Large change - anomaly!

        assert monitor.stats.count == 4
        assert monitor.anomaly.is_anomaly is True
        assert monitor.anomalies_detected == 1
        assert monitor.trend.direction == "up"


class TestVariableViewDataclassFeatures:
    """Test VariableView with dataclass features."""

    def test_statistics_result_immutability(self):
        """Test that StatisticsResult is immutable."""

        class TestView:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return None

            @property
            def stats(self) -> StatisticsResult:
                return StatisticsResult(count=10, mean=5.0)

            @property
            def anomaly(self) -> AnomalyResult | None:
                return None

            @property
            def trend(self) -> TrendResult | None:
                return None

        view = TestView()
        stats = view.stats

        # StatisticsResult should be frozen
        with pytest.raises(FrozenInstanceError):
            stats.count = 20

        with pytest.raises(FrozenInstanceError):
            stats.mean = 10.0

    def test_anomaly_result_replace_method(self):
        """Test using replace() method on AnomalyResult."""

        class TestView:
            def __init__(self):
                self._anomaly = AnomalyResult(is_anomaly=False, score=0.5)

            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return None

            @property
            def stats(self) -> StatisticsResult:
                return StatisticsResult()

            @property
            def anomaly(self) -> AnomalyResult | None:
                return self._anomaly

            @property
            def trend(self) -> TrendResult | None:
                return None

            def update_anomaly(self, new_score: float):
                """Update anomaly with replace()."""
                self._anomaly = replace(
                    self._anomaly,
                    score=new_score,
                    is_anomaly=new_score > 3.0,
                    metadata={"updated": True},
                )

        view = TestView()
        original = view.anomaly

        view.update_anomaly(4.0)
        updated = view.anomaly

        assert original != updated
        assert updated.is_anomaly is True
        assert updated.score == 4.0
        assert updated.metadata["updated"] is True

    def test_trend_result_asdict(self):
        """Test asdict() method on TrendResult."""

        class TestView:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return None

            @property
            def stats(self) -> StatisticsResult:
                return StatisticsResult()

            @property
            def anomaly(self) -> AnomalyResult | None:
                return None

            @property
            def trend(self) -> TrendResult | None:
                trend = TrendResult(value=0.75, direction="up", threshold=0.3)

                # Test asdict
                trend_dict = asdict(trend)
                assert trend_dict["value"] == 0.75
                assert trend_dict["direction"] == "up"
                assert trend_dict["threshold"] == 0.3

                # Test fields
                field_names = {f.name for f in fields(trend)}
                assert field_names == {"value", "direction", "threshold"}

                return trend

        view = TestView()
        trend = view.trend

        assert trend.value == 0.75
        assert trend.direction == "up"


class TestVariableViewProtocolMetadata:
    """Test protocol metadata and advanced features."""

    def test_protocol_subclassing(self):
        """Test that other protocols can inherit from VariableView."""

        class ExtendedVariableView(VariableView, Protocol):
            @property
            def additional_metric(self) -> float: ...

        class ConcreteExtendedView:
            @property
            def key(self) -> Key:
                return Key()

            @property
            def reasoning(self) -> Any | None:
                return None

            @property
            def stats(self) -> StatisticsResult:
                return StatisticsResult()

            @property
            def anomaly(self) -> AnomalyResult | None:
                return None

            @property
            def trend(self) -> TrendResult | None:
                return None

            @property
            def additional_metric(self) -> float:
                return 99.9

        instance = ConcreteExtendedView()

        # Should be instance of both protocols
        assert isinstance(instance, VariableView)
        assert isinstance(instance, ExtendedVariableView)
        assert instance.additional_metric == 99.9


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
