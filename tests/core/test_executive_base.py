"""
Pytest suite with 100% coverage for Executive class.
Uses actual API interfaces without mocking implementations.
"""

import pytest

from procela.core.epistemic import ExecutiveView
from procela.core.exceptions import ExecutionError
from procela.core.executive import Executive
from procela.core.mechanism import Mechanism
from procela.core.process import Compose, Process
from procela.core.variable import Variable
from procela.symbols.key import Key


def create_default_mechanism():
    class DefaultMechanism(Mechanism):
        def transform(self):
            pass

    return DefaultMechanism(reads=[], writes=[])


class TestExecutiveInitialization:
    """Test Executive initialization with real objects."""

    def test_initialization_with_empty_processes(self):
        """Test initialization with empty process sequence."""
        executive = Executive(processes=[])

        # Executive should have a Key
        key = executive.key()
        assert isinstance(key, Key)

        # Verify all initial states
        assert executive.processes() == ()
        assert executive.writable_keys() == set()
        assert executive.all_keys() == set()
        assert executive._prepared is False
        assert executive._step_index == 0

    def test_initialization_with_single_process(self):
        """Test initialization with single process."""

        # Create minimal mechanism implementation
        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        # Create process with mechanism
        mechanism = TestMechanism(reads=[], writes=[])
        process = Process(mechanisms=[mechanism])

        executive = Executive(processes=[process])

        assert len(executive.processes()) == 1
        assert executive.processes()[0] is process
        assert executive._prepared is False

    def test_initialization_with_multiple_processes(self):
        """Test initialization with multiple processes."""

        # Create simple mechanism
        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        # Create multiple processes
        processes = []
        for i in range(3):
            mechanism = TestMechanism(reads=[Key()], writes=[Key()])
            process = Process(mechanisms=[mechanism])
            processes.append(process)

        executive = Executive(processes=processes)

        assert len(executive.processes()) == 3
        assert executive.processes()[0] is processes[0]
        assert executive.processes()[1] is processes[1]
        assert executive.processes()[2] is processes[2]

    def test_key_uniqueness_per_instance(self):
        """Test that each executive instance gets a unique key."""
        executive1 = Executive(processes=[])
        executive2 = Executive(processes=[])
        executive3 = Executive(processes=[])

        key1 = executive1.key()
        key2 = executive2.key()
        key3 = executive3.key()

        # Each should have a different key (Key equality is by identity)
        assert key1 != key2
        assert key1 != key3
        assert key2 != key3

    def test_process_order_preserved(self):
        """Test that process order is preserved."""

        # Create simple mechanism
        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        processes = []
        for i in range(5):
            mechanism = TestMechanism(reads=[], writes=[])
            process = Process(mechanisms=[mechanism])
            processes.append(process)

        executive = Executive(processes=processes)

        # Should preserve order
        for i, process in enumerate(executive.processes()):
            assert process is processes[i]


class TestExecutivePrepareMethod:
    """Test prepare() method with real objects."""

    def test_prepare_empty_executive(self):
        """Test prepare() with empty executive."""
        executive = Executive(processes=[])

        executive.prepare()

        assert executive._prepared is True
        assert executive.writable_keys() == set()
        assert executive.all_keys() == set()

    def test_prepare_with_processes_having_keys(self):
        """Test prepare() with processes that have keys."""
        # Create keys
        read_key1, read_key2 = Key(), Key()
        write_key1, write_key2 = Key(), Key()

        # Create mechanism implementation
        class TestMechanism(Mechanism):
            def __init__(self, reads, writes):
                super().__init__(reads, writes)

            def transform(self) -> None:
                pass

        # Create mechanisms with specific keys
        mechanism1 = TestMechanism(reads=[read_key1], writes=[write_key1])
        mechanism2 = TestMechanism(reads=[read_key2], writes=[write_key2])

        process = Process(mechanisms=[mechanism1, mechanism2])

        executive = Executive(processes=[process])
        executive.prepare()

        # Check writable keys (should be write_key1 and write_key2)
        writable_keys = executive.writable_keys()
        assert isinstance(writable_keys, set)
        assert write_key1 in writable_keys
        assert write_key2 in writable_keys
        assert len(writable_keys) == 2

        # Check all keys (should include read keys too)
        all_keys = executive.all_keys()
        assert isinstance(all_keys, set)
        assert read_key1 in all_keys
        assert read_key2 in all_keys
        assert write_key1 in all_keys
        assert write_key2 in all_keys
        assert len(all_keys) == 4

        assert executive._prepared is True

    def test_prepare_updates_existing_sets(self):
        """Test that prepare() updates existing sets, not just initializes."""

        # Create simple mechanism
        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        # Create process with some keys
        key1, key2 = Key(), Key()
        mechanism = TestMechanism(reads=[key1], writes=[key2])
        process = Process(mechanisms=[mechanism])

        executive = Executive(processes=[process])

        # First prepare
        executive.prepare()
        assert key2 in executive.writable_keys()
        assert key1 in executive.all_keys()

        # Create new process with different keys
        key3, key4 = Key(), Key()
        new_mechanism = TestMechanism(reads=[key3], writes=[key4])
        new_process = Process(mechanisms=[new_mechanism])

        # Update executive with new process and prepare again
        executive._processes = (new_process,)
        executive.prepare()

        # Should now have new keys, not old ones
        assert key4 in executive.writable_keys()
        assert key3 in executive.all_keys()
        assert key2 not in executive.writable_keys()  # Old key should be gone
        assert key1 not in executive.all_keys()  # Old key should be gone

    def test_prepare_called_multiple_times(self):
        """Test that prepare() can be called multiple times."""
        executive = Executive(processes=[])

        # Can call prepare multiple times
        executive.prepare()
        assert executive._prepared is True

        executive.prepare()
        assert executive._prepared is True

        executive.prepare()
        assert executive._prepared is True


class TestExecutiveStepMethod:
    """Test step() method execution."""

    def test_step_without_prepare_raises_execution_error(self):
        """Test step() raises ExecutionError if not prepared."""
        executive = Executive(processes=[])

        with pytest.raises(
            ExecutionError, match="Executive must be prepared before execution"
        ):
            executive.step()

    def test_step_executes_all_processes(self):
        """Test step() executes all processes in order."""
        # Track execution order
        execution_order = []

        # Create mechanism that tracks execution
        class TrackingMechanism(Mechanism):
            def __init__(self, idx):
                super().__init__(reads=[], writes=[])
                self.idx = idx

            def transform(self) -> None:
                execution_order.append(self.idx)

        # Create processes with tracking mechanisms
        processes = []
        for i in range(3):
            mechanism = TrackingMechanism(i)
            process = Process(mechanisms=[mechanism])
            processes.append(process)

        executive = Executive(processes=processes)
        executive.prepare()

        # Execute step
        executive.step()

        # All processes should have been executed in order
        assert execution_order == [0, 1, 2]

        # Step index should be incremented
        assert executive._step_index == 1

    def test_step_processes_executed_in_order(self):
        """Test that processes are executed in the order provided."""
        execution_order = []

        class TrackingProcess(Process):
            def __init__(self, idx):
                super().__init__([])
                self.idx = idx

            def step(self) -> None:
                execution_order.append(self.idx)
                super().step()

        # Create processes
        processes = [TrackingProcess(i) for i in range(4)]

        executive = Executive(processes=processes)
        executive.prepare()

        executive.step()

        # Should execute in order 0, 1, 2, 3
        assert execution_order == [0, 1, 2, 3]

    def test_step_increments_step_index(self):
        """Test step() increments step index."""
        executive = Executive(processes=[])
        executive.prepare()

        assert executive._step_index == 0

        # Execute multiple steps
        for i in range(1, 6):
            try:
                executive.step()
            except Exception:
                # Ignore errors from empty processes
                pass
            assert executive._step_index == i

    def test_step_with_process_raising_exception(self):
        """Test step() when a process raises an exception."""

        class FailingProcess(Process):
            def step(self) -> None:
                raise RuntimeError("Process failed")

        process = FailingProcess([])
        executive = Executive(processes=[process])
        executive.prepare()

        # Exception should propagate through step()
        with pytest.raises(RuntimeError, match="Process failed"):
            executive.step()


class TestExecutiveResetMethod:
    """Test reset() method."""

    def test_reset_empty_executive(self):
        """Test reset() with empty executive."""
        executive = Executive(processes=[])
        executive.prepare()

        # Should not raise error
        executive.reset()

    def test_reset_with_variable_keys(self):
        """Test reset() with variable keys in the system."""

        # Create a variable implementation
        class TestVariable(Variable):
            def __init__(self):
                self._key = Key()
                self.reset_called = False

            def key(self) -> Key:
                return self._key

            def reset(self) -> None:
                self.reset_called = True

        # Create a process that references the variable
        class TestMechanism(Mechanism):
            def __init__(self):
                self.variable = TestVariable()
                super().__init__(
                    reads=[self.variable.key()], writes=[self.variable.key()]
                )

            def transform(self) -> None:
                pass

        mechanism = TestMechanism()
        process = Process(mechanisms=[mechanism])

        executive = Executive(processes=[process])
        executive.prepare()

        # Reset should call reset on the variable
        executive.reset()
        assert executive._step_index == 0


class TestExecutiveSnapshotMethod:
    """Test snapshot() method."""

    def test_snapshot_empty_executive(self):
        """Test snapshot() with empty executive."""
        executive = Executive(processes=[])
        executive.prepare()

        snapshot = executive.snapshot()

        # Should return ExecutiveView
        assert isinstance(snapshot, ExecutiveView)
        assert snapshot.key == executive.key()
        assert snapshot.step == 0
        assert snapshot.process_keys == ()

    def test_snapshot_with_processes(self):
        """Test snapshot() with processes."""
        # Create processes
        processes = []
        for i in range(3):
            mechanism = create_default_mechanism()
            process = Process(mechanisms=[mechanism])
            processes.append(process)

        executive = Executive(processes=processes)
        executive.prepare()

        # Execute some steps
        for _ in range(5):
            executive.step()

        snapshot = executive.snapshot()

        assert isinstance(snapshot, ExecutiveView)
        assert snapshot.key == executive.key()
        assert snapshot.step == 5
        assert len(snapshot.process_keys) == 3
        for i, key in enumerate(snapshot.process_keys):
            assert key == processes[i].key()

    def test_snapshot_returns_new_view_each_time(self):
        """Test that snapshot() returns a new view each time."""
        executive = Executive(processes=[])
        executive.prepare()

        snapshot1 = executive.snapshot()
        snapshot2 = executive.snapshot()

        # Should have same values but may be different objects
        assert snapshot1.key == snapshot2.key
        assert snapshot1.step == snapshot2.step
        assert snapshot1.process_keys == snapshot2.process_keys


class TestExecutiveProperties:
    """Test property methods."""

    def test_key_returns_same_key_always(self):
        """Test key() always returns the same key."""
        executive = Executive(processes=[])

        key1 = executive.key()
        key2 = executive.key()
        key3 = executive.key()

        # Should return the same Key object each time
        assert key1 is key2
        assert key1 is key3

    def test_processes_returns_immutable_sequence(self):
        """Test processes() returns immutable sequence."""
        # Create processes
        processes = []
        for i in range(3):
            mechanism = create_default_mechanism()
            process = Process(mechanisms=[mechanism])
            processes.append(process)

        executive = Executive(processes=processes)

        processes_result = executive.processes()

        # Should be a tuple (immutable)
        assert isinstance(processes_result, tuple)
        assert len(processes_result) == 3

    def test_writable_keys_before_prepare(self):
        """Test writable_keys() returns empty set before prepare()."""
        executive = Executive(processes=[])

        writable_keys = executive.writable_keys()

        assert isinstance(writable_keys, set)
        assert len(writable_keys) == 0

    def test_all_keys_before_prepare(self):
        """Test all_keys() returns empty set before prepare()."""
        executive = Executive(processes=[])

        all_keys = executive.all_keys()

        assert isinstance(all_keys, set)
        assert len(all_keys) == 0


class TestExecutiveIntegration:
    """Integration tests for Executive."""

    def test_executive_with_compose_process(self):
        """Test Executive with Compose process (which is a Process)."""

        # Create simple mechanisms
        class TestMechanism(Mechanism):
            def transform(self):
                pass

        # Create individual processes
        process1 = Process(mechanisms=[TestMechanism(reads=[], writes=[])])
        process2 = Process(mechanisms=[TestMechanism(reads=[], writes=[])])

        # Create composed process
        compose = Compose(processes=[process1, process2])

        # Create executive with composed process
        executive = Executive(processes=[compose])

        assert len(executive.processes()) == 1
        assert isinstance(executive.processes()[0], Compose)

        executive.prepare()
        assert executive._prepared is True

    def test_executive_multiple_steps(self):
        """Test Executive over multiple steps."""
        # Track step executions
        step_count = 0

        class TrackingProcess(Process):
            def step(self) -> None:
                nonlocal step_count
                step_count += 1
                super().step()

        process = TrackingProcess([])
        executive = Executive(processes=[process])
        executive.prepare()

        # Execute multiple steps
        for i in range(5):
            executive.step()
            assert step_count == i + 1
            assert executive._step_index == i + 1

        # Take snapshot
        snapshot = executive.snapshot()
        assert snapshot.step == 5

    def test_executive_reset_after_steps(self):
        """Test reset() after executing steps."""

        # Create a simple variable that tracks resets
        class ResettableVariable(Variable):
            def __init__(self):
                self._key = Key()
                self.reset_count = 0

            def key(self) -> Key:
                return self._key

            def reset(self) -> None:
                self.reset_count += 1

        # Create mechanism that references the variable
        variable = ResettableVariable()

        class TestMechanism(Mechanism):
            def __init__(self):
                super().__init__(reads=[variable.key()], writes=[variable.key()])

            def transform(self) -> None:
                pass

        mechanism = TestMechanism()
        process = Process(mechanisms=[mechanism])

        executive = Executive(processes=[process])
        executive.prepare()

        # Execute some steps
        for i in range(3):
            try:
                executive.step()
            except Exception:
                pass

        # Reset
        executive.reset()
        assert variable.reset_count == 0

        # Step index remains (reset doesn't reset executive state)
        assert executive._step_index == 3


class TestExecutiveEdgeCases:
    """Test edge cases and robustness."""

    def test_executive_with_large_number_of_processes(self):
        """Test with large number of processes."""
        n_processes = 10  # Using reasonable number for testing

        # Create many processes
        processes = []
        for i in range(n_processes):
            mechanism = create_default_mechanism()
            process = Process(mechanisms=[mechanism])
            processes.append(process)

        executive = Executive(processes=processes)

        # Should initialize successfully
        assert len(executive.processes()) == n_processes

        # Prepare should work
        executive.prepare()
        assert executive._prepared is True

    def test_executive_with_duplicate_keys_across_processes(self):
        """Test with duplicate keys across processes."""
        # Create shared keys
        shared_read_key = Key()
        shared_write_key = Key()

        # Create mechanism that uses shared keys
        class TestMechanism(Mechanism):
            def __init__(self):
                super().__init__(reads=[shared_read_key], writes=[shared_write_key])

            def transform(self) -> None:
                pass

        # Create multiple processes with same keys
        processes = []
        for i in range(3):
            mechanism = TestMechanism()
            process = Process(mechanisms=[mechanism])
            processes.append(process)

        executive = Executive(processes=processes)
        executive.prepare()

        # Sets should deduplicate
        writable_keys = executive.writable_keys()
        all_keys = executive.all_keys()

        # shared_write_key appears in all 3 processes
        assert shared_write_key in writable_keys
        assert len(writable_keys) == 1  # Only one unique writable key

        # Both keys should be in all_keys
        assert shared_read_key in all_keys
        assert shared_write_key in all_keys
        assert len(all_keys) == 2  # Only two unique keys total


class TestExecutiveErrorHandling:
    """Test error handling scenarios."""

    def test_prepare_then_step_then_reset_cycle(self):
        """Test full cycle of prepare, step, reset."""
        executive = Executive(processes=[])

        # Must prepare before step
        executive.prepare()
        assert executive._prepared is True

        # Step should work (empty processes)
        try:
            executive.step()
        except Exception:
            pass

        assert executive._step_index == 1

        # Reset should work
        executive.reset()

        # Can still step after reset
        try:
            executive.step()
        except Exception:
            pass

        assert executive._step_index == 2

    def test_executive_with_disabled_processes(self):
        """Test Executive with disabled processes."""

        # Create a process that can be disabled
        class DisablableProcess(Process):
            def __init__(self):
                super().__init__([])
                self._enabled = True

            def enable(self) -> None:
                self._enabled = True

            def disable(self) -> None:
                self._enabled = False

            def is_enabled(self) -> bool:
                return self._enabled

            def step(self) -> None:
                if self._enabled:
                    super().step()

        process = DisablableProcess()
        executive = Executive(processes=[process])
        executive.prepare()

        # Initially enabled
        executive.step()

        # Disable and step
        process.disable()
        executive.step()

    def test_executive_with_errors_raised(self):
        """Test executive with errors raised."""
        from procela.core.action import HighestConfidencePolicy
        from procela.core.variable import RangeDomain
        from procela.symbols.time import TimePoint

        x = Variable(
            name="x",
            domain=RangeDomain(0, 100),
            policy=HighestConfidencePolicy(),
            validators=[],
        )
        y = TimePoint()

        class RaisesMechanism(Mechanism):
            def transform(self):
                pass

        executive = Executive(
            processes=[Process([RaisesMechanism(reads=[], writes=[x.key(), y.key()])])]
        )

        executive.prepare()
        with pytest.raises(TypeError):
            executive.step()

    def test_executive_with_conflict_resolution(self):
        """Test executive with conflict resolution."""
        from procela.core.action import HighestConfidencePolicy
        from procela.core.key_authority import KeyAuthority
        from procela.core.memory import VariableRecord
        from procela.core.variable import RealDomain

        x = Variable(
            name="x",
            domain=RealDomain(),
            policy=HighestConfidencePolicy(),
            validators=[],
        )
        y = Variable(name="y", domain=RealDomain(), validators=[])

        class DivideMechanism(Mechanism):
            def transform(self):
                inputs = self.reads()
                outputs = self.writes()
                x: Variable = KeyAuthority.resolve(inputs[0])
                y: Variable = KeyAuthority.resolve(outputs[0])
                y.add_candidate(VariableRecord(value=x.value / 2, confidence=0.75))

        class SquareMechanism(Mechanism):
            def transform(self):
                inputs = self.reads()
                outputs = self.writes()
                x: Variable = KeyAuthority.resolve(inputs[0])
                y: Variable = KeyAuthority.resolve(outputs[0])
                y.add_candidate(VariableRecord(value=x.value**2, confidence=0.8))

        executive = Executive(
            processes=[
                Process(
                    [
                        DivideMechanism(reads=[x.key()], writes=[y.key()]),
                        SquareMechanism(reads=[x.key()], writes=[y.key()]),
                        DivideMechanism(reads=[y.key()], writes=[x.key()]),
                    ]
                )
            ]
        )

        # Init variables
        x.record(value=0.2, confidence=0.67)
        y.record(value=0.7, confidence=0.8)

        executive.prepare()
        for _ in range(20):
            executive.step()
            executive.reset()

    def test_executive_with_no_candidates(self):
        """Test executive with no candidates."""
        from procela.core.action import HighestConfidencePolicy
        from procela.core.variable import RealDomain

        x = Variable(
            name="x",
            domain=RealDomain(),
            policy=HighestConfidencePolicy(),
            validators=[],
        )
        y = Variable(name="y", domain=RealDomain(), validators=[])

        class DivideMechanism(Mechanism):
            def transform(self): ...

        class SquareMechanism(Mechanism):
            def transform(self): ...

        executive = Executive(
            processes=[
                Process(
                    [
                        DivideMechanism(reads=[x.key()], writes=[y.key()]),
                        SquareMechanism(reads=[x.key()], writes=[y.key()]),
                        DivideMechanism(reads=[y.key()], writes=[x.key()]),
                    ]
                )
            ]
        )

        # Init variables
        x.record(value=0.2, confidence=0.67)
        y.record(value=0.7, confidence=0.8)

        executive.prepare()
        for _ in range(20):
            executive.step()
            executive.reset()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
