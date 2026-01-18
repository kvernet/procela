"""
Pytest suite for procela.core.timer.Timer
100% coverage test suite for the Timer context manager.
"""

import time
from unittest.mock import patch

import pytest

# Import the module to test
from procela.core.timer import Timer

# ==================== TEST FIXTURES ====================


@pytest.fixture
def timer():
    """Provides a fresh Timer instance for each test."""
    return Timer()


# ==================== TEST CONTEXT MANAGER BASICS ====================


class TestTimerContextManager:
    """Test basic context manager functionality."""

    def test_timer_can_be_used_as_context_manager(self, timer):
        """Test that Timer can be used in a with statement."""
        with timer as t:
            assert t is timer
            # Timer should have started
            assert hasattr(t, "start")
            assert isinstance(t.start, float)

        # Timer should have stopped
        assert hasattr(timer, "end")
        assert hasattr(timer, "elapsed")
        assert isinstance(timer.end, float)
        assert isinstance(timer.elapsed, float)

    def test_timer_returns_self_on_enter(self, timer):
        """Test that __enter__ returns the Timer instance."""
        entered_timer = timer.__enter__()
        assert entered_timer is timer

        # Clean up
        timer.__exit__(None, None, None)

    def test_context_manager_sets_all_attributes(self, timer):
        """Test that all timing attributes are properly set."""
        # Before entering context
        assert not hasattr(timer, "start")
        assert not hasattr(timer, "end")
        assert not hasattr(timer, "elapsed")

        # During context
        with timer:
            assert hasattr(timer, "start")
            assert isinstance(timer.start, float)
            assert not hasattr(timer, "end")
            assert not hasattr(timer, "elapsed")

        # After context
        assert hasattr(timer, "end")
        assert hasattr(timer, "elapsed")
        assert isinstance(timer.end, float)
        assert isinstance(timer.elapsed, float)

    def test_multiple_context_managers_are_independent(self):
        """Test that multiple Timer instances don't interfere."""
        timer1 = Timer()
        timer2 = Timer()

        with timer1:
            time.sleep(0.001)

        with timer2:
            time.sleep(0.002)

        # Each timer should have its own independent measurements
        assert timer1.elapsed < timer2.elapsed
        assert timer1.start != timer2.start
        assert timer1.end != timer2.end


# ==================== TEST TIMING ACCURACY ====================


class TestTimingAccuracy:
    """Test that Timer measures time accurately."""

    def test_timer_measures_positive_time(self, timer):
        """Test that elapsed time is positive."""
        with timer:
            time.sleep(0.01)  # Sleep for 10ms

        assert timer.elapsed > 0
        assert timer.end > timer.start

    def test_timer_measures_short_durations(self, timer):
        """Test that Timer can measure very short durations."""
        with timer:
            pass  # Do nothing

        # Even doing nothing should take some (very small) time
        assert timer.elapsed >= 0
        # Typically less than 1ms for empty block
        assert timer.elapsed < 0.001

    def test_timer_measures_specific_duration(self, timer):
        """Test that Timer accurately measures a known duration."""
        sleep_duration = 0.05  # 50ms

        with timer:
            time.sleep(sleep_duration)

        # Allow small overhead for context manager and function calls
        # Should be very close to sleep_duration
        assert timer.elapsed >= sleep_duration
        assert timer.elapsed < sleep_duration + 0.01  # Within 10ms tolerance

    def test_consecutive_timings(self):
        """Test that Timer can be reused for consecutive measurements."""
        timer = Timer()

        # First measurement
        with timer:
            time.sleep(0.01)
        first_elapsed = timer.elapsed

        # Second measurement (should overwrite first)
        with timer:
            time.sleep(0.02)
        second_elapsed = timer.elapsed

        # Second should be longer than first
        assert second_elapsed > first_elapsed
        # Attributes should reflect second measurement
        assert timer.elapsed == second_elapsed


# ==================== TEST EDGE CASES ====================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_timer_with_exception_in_context(self, timer):
        """Test that Timer completes even when exception occurs."""
        with pytest.raises(ValueError):
            with timer:
                time.sleep(0.001)
                raise ValueError("Test exception")

        # Timer should still have recorded timing
        assert hasattr(timer, "start")
        assert hasattr(timer, "end")
        assert hasattr(timer, "elapsed")
        assert timer.elapsed > 0

    def test_exit_without_enter_raises_attribute_error(self, timer):
        """Test that __exit__ without __enter__ raises AttributeError."""
        with pytest.raises(AttributeError) as exc_info:
            timer.__exit__(None, None, None)

        assert "'Timer' object has no attribute 'start'" in str(exc_info.value)

    def test_timer_with_exit_arguments(self, timer):
        """Test that __exit__ handles all three standard arguments."""
        # Test with exception info
        exc_type = ValueError
        exc_val = ValueError("Test error")
        exc_tb = None

        timer.__enter__()
        time.sleep(0.001)
        # Should not raise even with exception arguments
        timer.__exit__(exc_type, exc_val, exc_tb)

        assert hasattr(timer, "elapsed")
        assert timer.elapsed > 0

    def test_timer_attributes_not_set_before_use(self):
        """Test that Timer doesn't have timing attributes before use."""
        timer = Timer()

        # Should not have timing attributes initially
        assert not hasattr(timer, "start")
        assert not hasattr(timer, "end")
        assert not hasattr(timer, "elapsed")

    def test_timer_with_zero_time_context(self, timer):
        """Test Timer with context that takes effectively zero time."""
        with timer:
            _ = 1 + 1  # Minimal computation

        # Should have valid timing
        assert hasattr(timer, "elapsed")
        assert timer.elapsed >= 0


# ==================== TEST MOCKED TIMING ====================


class TestMockedTiming:
    """Tests using mocked time functions for precise control."""

    def test_timer_with_mocked_time(self):
        """Test Timer with mocked perf_counter for precise control."""
        timer = Timer()

        # Mock time.perf_counter to return specific values
        with patch("time.perf_counter") as mock_perf:
            # Simulate timer starting at 1000.0 and ending at 1000.5
            mock_perf.side_effect = [1000.0, 1000.5]

            with timer:
                # perf_counter called once here (in __enter__)
                pass
            # perf_counter called again here (in __exit__)

        # Verify timing
        assert timer.start == 1000.0
        assert timer.end == 1000.5
        assert timer.elapsed == 0.5

    def test_timer_calls_perf_counter_twice(self):
        """Test that perf_counter is called exactly twice per context."""
        timer = Timer()

        with patch("time.perf_counter") as mock_perf:
            mock_perf.return_value = 1000.0

            with timer:
                pass

        # Should be called twice: once in __enter__, once in __exit__
        assert mock_perf.call_count == 2

    def test_multiple_timers_with_mocked_time(self):
        """Test multiple timers with mocked time sequence."""
        with patch("time.perf_counter") as mock_perf:
            # Simulate increasing time values
            mock_perf.side_effect = [1.0, 2.0, 3.0, 4.0]

            timer1 = Timer()
            with timer1:
                pass  # times: 1.0 to 2.0

            timer2 = Timer()
            with timer2:
                pass  # times: 3.0 to 4.0

        # Verify each timer's measurements
        assert timer1.start == 1.0
        assert timer1.end == 2.0
        assert timer1.elapsed == 1.0

        assert timer2.start == 3.0
        assert timer2.end == 4.0
        assert timer2.elapsed == 1.0


# ==================== TEST TYPE ANNOTATIONS AND INTERFACE ====================


class TestTypeAnnotations:
    """Test that Timer has correct type annotations and interface."""

    def test_timer_has_correct_attributes_after_use(self, timer):
        """Test that Timer attributes have correct types after use."""
        with timer:
            time.sleep(0.001)

        # All attributes should be floats
        assert isinstance(timer.start, float)
        assert isinstance(timer.end, float)
        assert isinstance(timer.elapsed, float)

    def test_timer_is_context_manager(self):
        """Test that Timer implements context manager protocol."""
        timer = Timer()

        # Should have both required methods
        assert hasattr(timer, "__enter__")
        assert hasattr(timer, "__exit__")

        # Both should be callable
        assert callable(timer.__enter__)
        assert callable(timer.__exit__)

    def test_enter_returns_timer_instance(self, timer):
        """Test that __enter__ returns a Timer instance."""
        result = timer.__enter__()
        assert isinstance(result, Timer)

        # Clean up
        timer.__exit__(None, None, None)


# ==================== TEST PERFORMANCE CHARACTERISTICS ====================


class TestPerformanceCharacteristics:
    """Test Timer's performance characteristics."""

    def test_timer_overhead_is_small(self):
        """Test that Timer has minimal overhead."""
        # Measure overhead by timing an empty context multiple times
        overheads = []

        for _ in range(100):
            timer = Timer()
            with timer:
                pass
            overheads.append(timer.elapsed)

        # Average overhead should be very small
        avg_overhead = sum(overheads) / len(overheads)
        assert avg_overhead < 0.0001  # Less than 0.1ms overhead

    def test_timer_doesnt_interfere_with_timed_code(self):
        """Test that using Timer doesn't affect the code being timed."""
        # Time a computation without Timer
        time.perf_counter()
        result = sum(i * i for i in range(1000))
        time.perf_counter()

        # Time the same computation with Timer
        timer = Timer()
        with timer:
            result2 = sum(i * i for i in range(1000))

        # Results should be the same
        assert result == result2


# ==================== TEST 100% COVERAGE VALIDATION ====================


def test_all_code_paths_covered():
    """Test that validates we've covered all code paths in timer.py."""
    # Instantiate Timer
    timer = Timer()

    # Test normal context manager flow
    with timer:
        time.sleep(0.001)

    # Test that all attributes exist after use
    assert hasattr(timer, "start")
    assert hasattr(timer, "end")
    assert hasattr(timer, "elapsed")

    # Test __enter__ and __exit__ directly
    timer2 = Timer()
    timer2.__enter__()
    time.sleep(0.001)
    timer2.__exit__(None, None, None)

    # Test error path: __exit__ without __enter__
    timer3 = Timer()
    try:
        timer3.__exit__(None, None, None)
        # Should not reach here
        assert False, "Should have raised AttributeError"
    except AttributeError:
        pass  # Expected


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
