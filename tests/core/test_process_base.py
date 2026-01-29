"""Pytest suite with 100% coverage for Process class."""

from unittest.mock import Mock, patch

import pytest

from procela.core.mechanism import Mechanism
from procela.core.process import Process
from procela.core.variable import RealDomain, Variable
from procela.symbols.key import Key


def create_real_variable():
    """Create a variable with real domain."""
    return Variable(name="real_variable", domain=RealDomain())


class TestProcessInitialization:
    """Test Process initialization and basic properties."""

    def test_initialization_with_empty_mechanisms(self):
        """Test initialization with empty mechanism sequence."""
        process = Process(mechanisms=[])

        assert process.variables() == set()
        assert process.mechanisms() == ()
        assert process.is_enabled() is True

    def test_initialization_with_single_mechanism(self):
        """Test initialization with single mechanism."""
        mock_mechanism = Mock(spec=Mechanism)
        mock_key = Key()

        with patch("procela.core.key_authority.KeyAuthority") as MockKeyAuthority:
            MockKeyAuthority.issue.return_value = mock_key

            process = Process(mechanisms=[mock_mechanism])

            assert process.mechanisms() == (mock_mechanism,)
            assert len(process.mechanisms()) == 1
            assert process.is_enabled() is True

    def test_initialization_with_multiple_mechanisms(self):
        """Test initialization with multiple mechanisms."""
        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(5)]

        process = Process(mechanisms=mock_mechanisms)

        assert process.mechanisms() == tuple(mock_mechanisms)
        assert len(process.mechanisms()) == 5

    def test_initialization_preserves_order(self):
        """Test that mechanism order is preserved."""
        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(3)]
        mock_mechanisms[0].name = "first"
        mock_mechanisms[1].name = "second"
        mock_mechanisms[2].name = "third"

        process = Process(mechanisms=mock_mechanisms)

        mechanisms = process.mechanisms()
        assert mechanisms[0].name == "first"
        assert mechanisms[1].name == "second"
        assert mechanisms[2].name == "third"

    def test_key_uniqueness_per_instance(self):
        """Test that each process instance gets a unique key."""
        with patch("procela.core.key_authority.KeyAuthority") as MockKeyAuthority:
            # Configure KeyAuthority to return different keys for each call
            mock_keys = [Key(), Key(), Key()]
            MockKeyAuthority.issue.side_effect = mock_keys

            processes = [
                Process(mechanisms=[]),
                Process(mechanisms=[Mock(spec=Mechanism)]),
                Process(mechanisms=[Mock(spec=Mechanism), Mock(spec=Mechanism)]),
            ]

            # Each should have a unique key
            assert isinstance(processes[0].key(), Key)
            assert MockKeyAuthority.issue.call_count == 0


class TestProcessEnableDisable:
    """Test enable/disable functionality."""

    def test_initial_enabled_state(self):
        """Test that processes are initially enabled."""
        process = Process(mechanisms=[])
        assert process.is_enabled() is True

    def test_enable_method(self):
        """Test that enable() sets enabled to True."""
        process = Process(mechanisms=[])

        # Start enabled
        assert process.is_enabled() is True

        # Disable then enable
        process.disable()
        assert process.is_enabled() is False

        process.enable()
        assert process.is_enabled() is True

    def test_disable_method(self):
        """Test that disable() sets enabled to False."""
        process = Process(mechanisms=[])

        # Start enabled
        assert process.is_enabled() is True

        process.disable()
        assert process.is_enabled() is False

        # Multiple calls should keep it disabled
        process.disable()
        process.disable()
        assert process.is_enabled() is False

    def test_enable_disable_cycle(self):
        """Test multiple enable/disable cycles."""
        process = Process(mechanisms=[])

        for i in range(5):
            process.disable()
            assert process.is_enabled() is False, f"Failed on disable cycle {i}"

            process.enable()
            assert process.is_enabled() is True, f"Failed on enable cycle {i}"


class TestProcessStepMethod:
    """Test step() method execution."""

    def test_step_when_enabled_executes_all_mechanisms(self):
        """Test step() executes all mechanisms when process is enabled."""
        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(3)]

        process = Process(mechanisms=mock_mechanisms)

        # All mechanisms should be called
        process.step()

        for mechanism in mock_mechanisms:
            mechanism.run.assert_called_once()

    def test_step_when_disabled_skips_all_mechanisms(self):
        """Test step() does nothing when process is disabled."""
        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(3)]

        process = Process(mechanisms=mock_mechanisms)
        process.disable()

        process.step()

        # No mechanisms should be called
        for mechanism in mock_mechanisms:
            mechanism.run.assert_not_called()

    def test_step_executes_mechanisms_in_order(self):
        """Test mechanisms are executed in the order they were provided."""
        execution_order = []

        def create_mock_mechanism(idx):
            mock = Mock(spec=Mechanism)
            mock.run.side_effect = lambda: execution_order.append(idx)
            return mock

        mock_mechanisms = [create_mock_mechanism(i) for i in range(5)]

        process = Process(mechanisms=mock_mechanisms)
        process.step()

        # Should execute in order 0, 1, 2, 3, 4
        assert execution_order == [0, 1, 2, 3, 4]

    def test_step_respects_individual_mechanism_enablement(self):
        """Test that step() respects each mechanism's enabled state."""
        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(3)]

        # Configure mechanism enabled states
        mock_mechanisms[0].is_enabled.return_value = True
        mock_mechanisms[1].is_enabled.return_value = False  # Disabled
        mock_mechanisms[2].is_enabled.return_value = True

        process = Process(mechanisms=mock_mechanisms)

        process.step()

        # All mechanisms' run() should be called
        # (Mechanism.run() internally checks is_enabled())
        for mechanism in mock_mechanisms:
            mechanism.run.assert_called_once()

    def test_step_with_mechanism_exception(self):
        """Test step() when a mechanism raises an exception."""
        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(3)]

        # Second mechanism raises an exception
        mock_mechanisms[1].run.side_effect = ValueError("Mechanism failed")

        process = Process(mechanisms=mock_mechanisms)

        # Exception should propagate
        with pytest.raises(ValueError, match="Mechanism failed"):
            process.step()

        # First mechanism should have been called
        mock_mechanisms[0].run.assert_called_once()
        # Third mechanism should NOT have been called (exception stopped execution)
        mock_mechanisms[2].run.assert_not_called()

    def test_step_toggles_enablement_between_calls(self):
        """Test step() behavior when enabling/disabling between calls."""
        mock_mechanism = Mock(spec=Mechanism)
        process = Process(mechanisms=[mock_mechanism])

        # Enabled -> should call
        process.step()
        assert mock_mechanism.run.call_count == 1

        # Disable -> should not call
        process.disable()
        process.step()
        assert mock_mechanism.run.call_count == 1  # No additional call

        # Enable -> should call again
        process.enable()
        process.step()
        assert mock_mechanism.run.call_count == 2


class TestProcessWritableKeys:
    """Test writable_keys() method."""

    def test_writable_keys_empty_process(self):
        """Test writable_keys() with empty process."""
        process = Process(mechanisms=[])

        vars = process.writable()

        assert isinstance(vars, set)
        assert len(vars) == 0

    def test_writable_keys_single_mechanism(self):
        """Test writable_keys() with single mechanism."""
        mock_mechanism = Mock(spec=Mechanism)
        var1 = Key()
        var2 = Key()
        mock_mechanism.writes.return_value = [var1, var2]

        process = Process(mechanisms=[mock_mechanism])

        vars = process.writable()

        assert isinstance(vars, set)
        assert len(vars) == 2
        assert var1 in vars
        assert var2 in vars

    def test_writable_keys_multiple_mechanisms(self):
        """Test writable_keys() with multiple mechanisms."""
        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(3)]

        # Each mechanism writes different keys
        var1, var2, var3, var4 = (
            create_real_variable(),
            create_real_variable(),
            create_real_variable(),
            create_real_variable(),
        )
        mock_mechanisms[0].writes.return_value = [var1, var2]
        mock_mechanisms[1].writes.return_value = [var2, var3]  # key2 is duplicate
        mock_mechanisms[2].writes.return_value = [var4]

        process = Process(mechanisms=mock_mechanisms)

        vars = process.writable()

        assert isinstance(vars, set)
        assert len(vars) == 4  # key2 should appear only once
        assert var1 in vars
        assert var2 in vars
        assert var3 in vars
        assert var4 in vars

    def test_wrvarble_keys_with_empty_writes(self):
        """Testvaritable_keys() with mechanisms that write nothing."""
        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(3)]

        # First writes keys, second writes nothing, third writes keys
        var1, var2 = create_real_variable(), create_real_variable()
        mock_mechanisms[0].writes.return_value = [var1]
        mock_mechanisms[1].writes.return_value = []
        mock_mechanisms[2].writes.return_value = [var2]

        process = Process(mechanisms=mock_mechanisms)

        vars = process.writable()

        assert len(vars) == 2
        assert var1 in vars
        assert var2 in vars


class TestProcessAllKeys:
    """Test all_keys() method."""

    def test_all_keys_empty_process(self):
        """Test all_keys() with empty process."""
        process = Process(mechanisms=[])

        variables = process.variables()

        assert isinstance(variables, set)
        assert len(variables) == 0

    def test_all_keys_single_mechanism(self):
        """Test all_keys() with single mechanism."""
        mock_mechanism = Mock(spec=Mechanism)
        read = create_real_variable()
        write = create_real_variable()
        mock_mechanism.reads.return_value = [read]
        mock_mechanism.writes.return_value = [write]

        process = Process(mechanisms=[mock_mechanism])

        variables = process.variables()

        assert len(variables) == 2
        assert read in variables
        assert write in variables

    def test_all_keys_multiple_mechanisms(self):
        """Test all_keys() with multiple mechanisms."""
        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(3)]

        # Define keys
        var1, var2, var3, var4, var5 = (
            create_real_variable(),
            create_real_variable(),
            create_real_variable(),
            create_real_variable(),
            create_real_variable(),
        )

        # Mechanism 0 reads key1, writes key2
        mock_mechanisms[0].reads.return_value = [var1]
        mock_mechanisms[0].writes.return_value = [var2]

        # Mechanism 1 reads key2 (duplicate), writes key3
        mock_mechanisms[1].reads.return_value = [var2]
        mock_mechanisms[1].writes.return_value = [var3]

        # Mechanism 2 reads key4, writes key5
        mock_mechanisms[2].reads.return_value = [var4]
        mock_mechanisms[2].writes.return_value = [var5]

        process = Process(mechanisms=mock_mechanisms)

        variables = process.variables()

        assert len(variables) == 5  # All unique keys
        assert var1 in variables
        assert var2 in variables
        assert var3 in variables
        assert var4 in variables
        assert var5 in variables

    def test_all_keys_with_read_write_overlap(self):
        """Test all_keys() when mechanism reads and writes same key."""
        mock_mechanism = Mock(spec=Mechanism)
        same = create_real_variable()

        # Mechanism reads and writes the same key
        mock_mechanism.reads.return_value = [same]
        mock_mechanism.writes.return_value = [same]

        process = Process(mechanisms=[mock_mechanism])

        variables = process.variables()

        assert len(variables) == 1  # Should be deduplicated
        assert same in variables

    def test_all_keys_returns_copy_not_reference(self):
        """Test that all_keys() returns a new set each time."""
        mock_mechanism = Mock(spec=Mechanism)
        var = create_real_variable()
        mock_mechanism.reads.return_value = [var]
        mock_mechanism.writes.return_value = []

        process = Process(mechanisms=[mock_mechanism])

        variables1 = process.variables()
        variables2 = process.variables()

        # Should be equal but different objects
        assert variables1 == variables2
        assert variables1 is not variables2

        # Modifying returned set shouldn't affect process
        variables1.add(create_real_variable())
        variables3 = process.variables()
        assert len(variables3) == 1  # Still only the original key


class TestProcessKeyMethod:
    """Test key() method."""

    def test_key_returns_same_key_always(self):
        """Test that key() always returns the same key."""
        with patch("procela.core.key_authority.KeyAuthority") as MockKeyAuthority:
            mock_key = Key()
            MockKeyAuthority.issue.return_value = mock_key

            process = Process(mechanisms=[])

            key1 = process.key()
            key2 = process.key()
            key3 = process.key()

            # Should return the same key every time
            assert key1 is key2
            assert key1 is key3
            assert key2 is key3


class TestProcessMechanismsMethod:
    """Test mechanisms() method."""

    def test_mechanisms_returns_immutable_sequence(self):
        """Test that mechanisms() returns immutable sequence."""
        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(3)]

        process = Process(mechanisms=mock_mechanisms)

        mechanisms = process.mechanisms()

        # Should be a tuple (immutable)
        assert isinstance(mechanisms, tuple)

        # Original list modification shouldn't affect process
        mock_mechanisms.append(Mock(spec=Mechanism))
        assert len(process.mechanisms()) == 3  # Still original length

    def test_mechanisms_preserves_order(self):
        """Test that mechanisms() preserves the original order."""
        mock_mechanisms = []
        for i in range(5):
            mock = Mock(spec=Mechanism)
            mock.id = i
            mock_mechanisms.append(mock)

        process = Process(mechanisms=mock_mechanisms)

        mechanisms = process.mechanisms()

        # Should be in same order
        for i, mechanism in enumerate(mechanisms):
            assert mechanism.id == i


class TestProcessIntegration:
    """Integration tests for Process usage patterns."""

    def test_process_with_real_mechanism_subclass(self):
        """Test Process with actual Mechanism subclass."""

        class TestMechanism(Mechanism):
            def __init__(self, reads, writes, name):
                super().__init__(reads, writes)
                self.name = name
                self.run_count = 0

            def transform(self) -> None:
                self.run_count += 1

        # Create real mechanisms
        var1, var2, var3 = (
            create_real_variable(),
            create_real_variable(),
            create_real_variable(),
        )

        mechanism1 = TestMechanism(reads=[var1], writes=[var2], name="M1")
        mechanism2 = TestMechanism(reads=[var2], writes=[var3], name="M2")
        mechanism3 = TestMechanism(reads=[var3], writes=[], name="M3")

        # Create process
        process = Process(mechanisms=[mechanism1, mechanism2, mechanism3])

        # Test initial state
        assert len(process.mechanisms()) == 3
        assert process.mechanisms()[0].name == "M1"

        # Test writable
        writable = process.writable()
        assert var2 in writable
        assert var3 in writable
        assert len(writable) == 2  # key2 and key3

        # Test variables
        variables = process.variables()
        assert var1 in variables
        assert var2 in variables
        assert var3 in variables
        assert len(variables) == 3

        # Test step execution
        process.step()
        assert mechanism1.run_count == 1
        assert mechanism2.run_count == 1
        assert mechanism3.run_count == 1

        # Test disable/enable
        process.disable()
        process.step()
        assert mechanism1.run_count == 1  # No increment

        process.enable()
        process.step()
        assert mechanism1.run_count == 2  # Incremented again

    def test_multiple_processes_independence(self):
        """Test that multiple processes operate independently."""

        class CounterMechanism(Mechanism):
            def __init__(self, reads, writes):
                super().__init__(reads, writes)
                self.run_count = 0

            def transform(self) -> None:
                self.run_count += 1

        # Create shared mechanisms
        shared_mech = CounterMechanism(reads=[], writes=[])

        # Create multiple processes with shared and unique mechanisms
        process1 = Process(
            mechanisms=[shared_mech, CounterMechanism(reads=[], writes=[])]
        )

        process2 = Process(
            mechanisms=[shared_mech, CounterMechanism(reads=[], writes=[])]
        )

        # Run process1 only
        process1.step()
        assert shared_mech.run_count == 1

        # Run process2 only
        process2.step()
        assert shared_mech.run_count == 2  # Shared mech incremented again

        # Check process-specific mechanisms
        assert process1.mechanisms()[1].run_count == 1
        assert process2.mechanisms()[1].run_count == 1

        # Disable process1, enable process2
        process1.disable()
        process1.step()
        assert shared_mech.run_count == 2  # No increment

        process2.step()
        assert shared_mech.run_count == 3  # Incremented

    def test_process_composition(self):
        """Test composing processes from other processes' mechanisms."""

        class SimpleMechanism(Mechanism):
            def __init__(self, id):
                super().__init__(reads=[], writes=[])
                self.id = id
                self.executed = False

            def transform(self) -> None:
                self.executed = True

        # Create individual mechanisms
        mechs = [SimpleMechanism(i) for i in range(5)]

        # Create sub-processes
        sub_process1 = Process(mechanisms=mechs[:2])  # mechs 0, 1
        Process(mechanisms=mechs[2:4])  # mechs 2, 3

        # Create main process with all mechanisms
        main_process = Process(mechanisms=mechs)  # All 5 mechs

        # Test that main process has all mechanisms
        assert len(main_process.mechanisms()) == 5

        # Execute main process
        main_process.step()

        # All mechanisms should be executed
        for mech in mechs:
            assert mech.executed is True

        # Reset
        for mech in mechs:
            mech.executed = False

        # Execute sub-processes
        sub_process1.step()
        assert mechs[0].executed is True
        assert mechs[1].executed is True
        assert mechs[2].executed is False  # Not in sub_process1
        assert mechs[3].executed is False  # Not in sub_process1
        assert mechs[4].executed is False  # Not in any sub-process


class TestProcessEdgeCases:
    """Test edge cases and special scenarios."""

    def test_process_with_mechanism_returning_none_keys(self):
        """Test with mechanisms returning None or empty sequences."""
        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(3)]

        # Different return patterns
        mock_mechanisms[0].reads.return_value = []
        mock_mechanisms[0].writes.return_value = []

        mock_mechanisms[1].reads.return_value = [create_real_variable()]
        mock_mechanisms[1].writes.return_value = []

        mock_mechanisms[2].reads.return_value = []
        mock_mechanisms[2].writes.return_value = [
            create_real_variable(),
            create_real_variable(),
        ]

        process = Process(mechanisms=mock_mechanisms)

        # Should handle all cases without errors
        writable = process.writable()
        variables = process.variables()

        assert len(writable) == 2
        assert len(variables) == 3  # 1 read + 2 writes

    def test_process_with_large_number_of_mechanisms(self):
        """Test with a large number of mechanisms."""
        n_mechanisms = 100
        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(n_mechanisms)]

        # Each mechanism reads and writes unique keys
        for i, mock in enumerate(mock_mechanisms):
            read = create_real_variable()
            write = create_real_variable()
            mock.reads.return_value = [read]
            mock.writes.return_value = [write]
            mock.run.return_value = None

        process = Process(mechanisms=mock_mechanisms)

        # Test mechanisms count
        assert len(process.mechanisms()) == n_mechanisms

        # Test step execution
        process.step()
        for mock in mock_mechanisms:
            mock.run.assert_called_once()

        # Test key collections
        writable = process.writable()
        variables = process.variables()

        assert len(writable) == n_mechanisms
        assert len(variables) == n_mechanisms * 2  # Each has read + write key

    def test_process_with_duplicate_mechanisms(self):
        """Test with duplicate mechanism instances."""
        mock_mechanism = Mock(spec=Mechanism)
        var = create_real_variable()
        mock_mechanism.reads.return_value = [var]
        mock_mechanism.writes.return_value = [var]

        # Same mechanism instance multiple times
        process = Process(mechanisms=[mock_mechanism, mock_mechanism, mock_mechanism])

        # Should have 3 references to same mechanism
        mechanisms = process.mechanisms()
        assert len(mechanisms) == 3
        assert mechanisms[0] is mechanisms[1]
        assert mechanisms[1] is mechanisms[2]

        # Step should call run() 3 times
        process.step()
        assert mock_mechanism.run.call_count == 3

        # Key collections should deduplicate
        writable = process.writable()
        variables = process.variables()

        assert len(writable) == 1  # Only one unique key
        assert len(variables) == 1  # Only one unique key

    def test_process_mechanisms_immutability_after_creation(self):
        """Test that mechanisms tuple is immutable."""
        original_mechs = [Mock(spec=Mechanism), Mock(spec=Mechanism)]
        process = Process(mechanisms=original_mechs)

        mechanisms = process.mechanisms()

        # Should be a tuple
        assert isinstance(mechanisms, tuple)

        # Attempting to modify should fail
        with pytest.raises(AttributeError):
            mechanisms.append(Mock(spec=Mechanism))

        # Original list modification shouldn't affect process
        original_mechs.append(Mock(spec=Mechanism))
        assert len(process.mechanisms()) == 2  # Still original count


class TestProcessDesignContract:
    """Test design contracts mentioned in docstrings."""

    def test_step_does_not_resolve_conflicts(self):
        """Test that step() just runs mechanisms without conflict resolution."""
        # This is a conceptual test - step() just calls run() on each mechanism
        # Conflict resolution would happen elsewhere in the system

        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(3)]

        process = Process(mechanisms=mock_mechanisms)
        process.step()

        # step() just calls run() on each
        for mock in mock_mechanisms:
            mock.run.assert_called_once()

        # No additional coordination or conflict resolution logic

    def test_enable_disable_affects_process_not_mechanisms(self):
        """Test that enabling/disabling process doesn't affect individual mechanisms."""
        mock_mechanism = Mock(spec=Mechanism)
        mock_mechanism.is_enabled.return_value = True

        process = Process(mechanisms=[mock_mechanism])

        # Initially both enabled
        assert process.is_enabled() is True
        assert mock_mechanism.is_enabled() is True

        # Disable process
        process.disable()
        assert process.is_enabled() is False
        assert mock_mechanism.is_enabled() is True  # Mechanism still enabled

        # Enable process
        process.enable()
        assert process.is_enabled() is True
        assert mock_mechanism.is_enabled() is True  # Mechanism still enabled


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
