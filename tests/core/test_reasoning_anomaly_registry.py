"""
Pytest module for procela.core.reasoning.anomaly.registry.

Tests the anomaly detector registry with 100% coverage.
"""

from unittest.mock import Mock

import pytest

from procela.core.reasoning import (
    _ANOMALY_DETECTORS,
    AnomalyDetector,
    EWMADetector,
    ZScoreDetector,
    available_detectors,
    clear_detector_registry,
    get_detector,
    get_detectors,
    has_detector,
    register_detector,
    unregister_detector,
)


class TestRegistryInitialState:
    """Tests for the registry's initial state."""

    def test_initial_registry_contents(self) -> None:
        """Test that registry starts with expected detectors."""
        detectors = get_detectors()

        assert isinstance(detectors, dict)
        assert len(detectors) == 2
        assert "ewma" in detectors
        assert "z-score" in detectors
        assert detectors["ewma"] is EWMADetector
        assert detectors["z-score"] is ZScoreDetector

    def test_initial_methods_list(self) -> None:
        """Test available_detectors returns correct initial set."""
        methods = available_detectors()

        assert isinstance(methods, set)
        assert len(methods) == 2
        assert "ewma" in methods
        assert "z-score" in methods


class TestGetDetector:
    """Tests for the get_detector function."""

    def test_get_existing_detector_default_args(self) -> None:
        """Test getting a detector with default arguments."""
        detector = get_detector("z-score")

        assert isinstance(detector, ZScoreDetector)
        assert detector.name == "ZScoreDetector"
        assert detector.threshold == 3.0  # Default value

    def test_get_existing_detector_custom_args(self) -> None:
        """Test getting a detector with custom arguments."""
        detector = get_detector("z-score", threshold=2.5)

        assert isinstance(detector, ZScoreDetector)
        assert detector.threshold == 2.5

    def test_get_ewma_detector(self) -> None:
        """Test getting the EWMA detector."""
        detector = get_detector("ewma")

        assert isinstance(detector, EWMADetector)
        assert detector.name == "EWMADetector"
        assert detector.threshold == 3.0  # Default value

    def test_get_nonexistent_detector(self) -> None:
        """Test getting a detector that doesn't exist raises KeyError."""
        with pytest.raises(KeyError) as exc_info:
            get_detector("nonexistent")

        error_msg = str(exc_info.value)
        assert "Anomaly detector 'nonexistent' not found" in error_msg
        assert "Available detectors:" in error_msg
        assert "ewma" in error_msg
        assert "z-score" in error_msg

    def test_get_detector_invalid_arguments(self) -> None:
        """Test getting a detector with invalid arguments raises TypeError."""
        # ZScoreDetector expects numeric threshold, not string
        with pytest.raises(TypeError) as exc_info:
            get_detector("z-score", threshold="invalid")

        error_msg = str(exc_info.value)
        assert "Failed to instantiate detector 'z-score'" in error_msg


class TestRegisterDetector:
    """Tests for the register_detector function."""

    def test_register_new_detector(self) -> None:
        """Test registering a new detector."""

        # Define a mock detector class
        class MockDetector(AnomalyDetector):
            name = "MockDetector"

            def __init__(self, param=1.0):
                self.param = param

            def detect(self, stats):
                pass

        # Register it
        register_detector("mock", MockDetector)

        # Verify it was registered
        assert "mock" in _ANOMALY_DETECTORS
        assert _ANOMALY_DETECTORS["mock"] is MockDetector

        # Can instantiate it
        detector = get_detector("mock", param=2.0)
        assert isinstance(detector, MockDetector)
        assert detector.param == 2.0

        # Clean up
        unregister_detector("mock")

    def test_register_duplicate_name(self) -> None:
        """Test registering with duplicate name raises ValueError."""

        class AnotherDetector(AnomalyDetector):
            name = "AnotherDetector"

            def detect(self, stats):
                pass

        # First registration should work
        register_detector("another", AnotherDetector)

        # Second registration should fail
        with pytest.raises(ValueError) as exc_info:
            register_detector("another", AnotherDetector)

        assert "already registered" in str(exc_info.value)

        # Clean up
        unregister_detector("another")

    def test_register_non_anomalydetector(self) -> None:
        """Test registering non-AnomalyDetector class raises TypeError."""

        class NotADetector:
            pass

        with pytest.raises(TypeError) as exc_info:
            register_detector("invalid", NotADetector)  # type: ignore

        error_msg = str(exc_info.value)
        assert "must be a subclass of AnomalyDetector" in error_msg

    def test_register_non_class(self) -> None:
        """Test registering something that's not a class raises TypeError."""
        not_a_class = "I'm a string, not a class"

        with pytest.raises(TypeError) as exc_info:
            register_detector("invalid", not_a_class)  # type: ignore

        error_msg = str(exc_info.value)
        assert "must be a class" in error_msg


class TestUnregisterDetector:
    """Tests for the unregister_detector function."""

    def test_unregister_existing_detector(self) -> None:
        """Test unregistering an existing detector."""

        # First register a test detector
        class TestDetector(AnomalyDetector):
            name = "TestDetector"

            def detect(self, stats):
                pass

        register_detector("test", TestDetector)
        assert "test" in _ANOMALY_DETECTORS

        # Unregister it
        detector_class = unregister_detector("test")

        # Verify return value and state
        assert detector_class is TestDetector
        assert "test" not in _ANOMALY_DETECTORS

    def test_unregister_nonexistent_detector(self) -> None:
        """Test unregistering a non-existent detector raises KeyError."""
        with pytest.raises(KeyError) as exc_info:
            unregister_detector("nonexistent")

        error_msg = str(exc_info.value)
        assert "not found in registry" in error_msg
        assert "Available detectors:" in error_msg

    def test_unregister_and_reregister(self) -> None:
        """Test unregistering and then reregistering a detector."""

        class TestDetector(AnomalyDetector):
            name = "TestDetector"

            def detect(self, stats):
                pass

        # Register, unregister, then reregister
        register_detector("test", TestDetector)
        assert "test" in _ANOMALY_DETECTORS

        unregister_detector("test")
        assert "test" not in _ANOMALY_DETECTORS

        # Should be able to register again
        register_detector("test", TestDetector)
        assert "test" in _ANOMALY_DETECTORS

        # Clean up
        unregister_detector("test")


class TestGetRegisteredDetectors:
    """Tests for the get_detectors function."""

    def test_returns_copy_not_reference(self) -> None:
        """Test that get_detectors returns a copy."""
        original = get_detectors()

        # Modify the copy
        original["extra"] = "not a detector"

        # Original registry should not be affected
        assert "extra" not in _ANOMALY_DETECTORS
        assert "extra" not in get_detectors()

    def test_contents_after_modification(self) -> None:
        """Test returned dictionary reflects registry state."""
        # Get initial state
        initial = get_detectors()
        initial_count = len(initial)

        # Add a detector
        class TempDetector(AnomalyDetector):
            name = "TempDetector"

            def detect(self, stats):
                pass

        register_detector("temp", TempDetector)

        # Get new state
        updated = get_detectors()

        # Should have one more item
        assert len(updated) == initial_count + 1
        assert "temp" in updated
        assert updated["temp"] is TempDetector

        # Clean up
        unregister_detector("temp")


class TestAnomalyDetectorMethods:
    """Tests for the available_detectors function."""

    def test_returns_set(self) -> None:
        """Test that it returns a set."""
        methods = available_detectors()
        assert isinstance(methods, set)

    def test_set_contents(self) -> None:
        """Test that the set contains the right names."""
        methods = available_detectors()

        # Should contain at least the default detectors
        assert "ewma" in methods
        assert "z-score" in methods

    def test_set_updates_with_registry(self) -> None:
        """Test that the set updates when registry changes."""
        # Get initial set
        initial = available_detectors()

        # Add a detector
        class TempDetector(AnomalyDetector):
            name = "TempDetector"

            def detect(self, stats):
                pass

        register_detector("temp", TempDetector)

        # Get updated set
        updated = available_detectors()

        # Should have the new detector
        assert "temp" in updated
        assert len(updated) == len(initial) + 1

        # Clean up
        unregister_detector("temp")


class TestClearRegistry:
    """Tests for the clear_detector_registry function."""

    def test_clears_all_detectors(self) -> None:
        """Test that clear_detector_registry removes all detectors."""
        # Ensure registry has content
        assert len(_ANOMALY_DETECTORS) > 0

        # Clear it
        clear_detector_registry()

        # Should be empty
        assert len(_ANOMALY_DETECTORS) == 0
        assert len(available_detectors()) == 0

        # Restore default state for other tests
        # (In a real test suite, this would be in a fixture)
        _ANOMALY_DETECTORS.update(
            {
                "ewma": EWMADetector,
                "z-score": ZScoreDetector,
            }
        )


class TestHasDetector:
    """Tests for the has_detector function."""

    def test_has_existing_detector(self) -> None:
        """Test has_detector returns True for existing detectors."""
        assert has_detector("ewma") is True
        assert has_detector("z-score") is True

    def test_has_nonexistent_detector(self) -> None:
        """Test has_detector returns False for non-existent detectors."""
        assert has_detector("nonexistent") is False

    def test_has_detector_after_registration(self) -> None:
        """Test has_detector reflects registration changes."""

        class TempDetector(AnomalyDetector):
            name = "TempDetector"

            def detect(self, stats):
                pass

        # Initially should not have it
        assert not has_detector("temp")

        # Register it
        register_detector("temp", TempDetector)

        # Now should have it
        assert has_detector("temp")

        # Unregister it
        unregister_detector("temp")

        # Should no longer have it
        assert not has_detector("temp")


class TestRegistryIntegration:
    """Integration tests for the registry module."""

    def test_full_workflow(self) -> None:
        """Test complete workflow: register, get, use, unregister."""

        # Define a custom detector
        class CustomDetector(AnomalyDetector):
            name = "CustomDetector"

            def __init__(self, multiplier=1.0):
                self.multiplier = multiplier

            def detect(self, stats):
                from procela.core.assessment import AnomalyResult

                return AnomalyResult(is_anomaly=False)

        # 1. Register the detector
        register_detector("custom", CustomDetector)
        assert has_detector("custom")

        # 2. Get an instance
        detector = get_detector("custom", multiplier=2.0)
        assert isinstance(detector, CustomDetector)
        assert detector.multiplier == 2.0
        assert detector.name == "CustomDetector"

        # 3. Use it (simplified)
        mock_stats = Mock()
        result = detector.detect(mock_stats)
        assert result.is_anomaly is False

        # 4. Check it's in the methods list
        methods = available_detectors()
        assert "custom" in methods

        # 5. Get registry copy
        registry = get_detectors()
        assert registry["custom"] is CustomDetector

        # 6. Unregister it
        unregistered = unregister_detector("custom")
        assert unregistered is CustomDetector
        assert not has_detector("custom")

    def test_registry_isolation(self) -> None:
        """Test that registry modifications don't affect other tests."""
        # This test assumes other tests might modify the registry
        # We'll verify the core detectors are always present
        assert has_detector("ewma")
        assert has_detector("z-score")

        core_detectors = get_detectors()
        assert "ewma" in core_detectors
        assert "z-score" in core_detectors
        assert core_detectors["ewma"] is EWMADetector
        assert core_detectors["z-score"] is ZScoreDetector


def test_module_import() -> None:
    """Test that the module can be imported correctly."""
    from procela.core.reasoning.anomaly.registry import (
        available_detectors,
        clear_detector_registry,
        get_detector,
        get_detectors,
        has_detector,
        register_detector,
        unregister_detector,
    )

    # Verify all exports exist
    assert callable(get_detector)
    assert callable(register_detector)
    assert callable(unregister_detector)
    assert callable(get_detectors)
    assert callable(available_detectors)
    assert callable(clear_detector_registry)
    assert callable(has_detector)


if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=procela.core.reasoning.anomaly.registry",
            "--cov-report=term-missing",
        ]
    )
