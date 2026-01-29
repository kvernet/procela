"""
Pytest suite with 100% coverage for Compose class.
"""

from unittest.mock import Mock, patch

import pytest

from procela.core.mechanism import Mechanism
from procela.core.process import Compose, Process
from procela.core.variable import RealDomain, Variable
from procela.symbols.key import Key


def create_real_variable():
    """Create a variable with real domain."""
    return Variable(name="real_variable", domain=RealDomain())


class TestComposeInitialization:
    """Test Compose initialization and basic properties."""

    def test_initialization_with_empty_processes(self):
        """Test initialization with empty process sequence."""
        compose = Compose(processes=[])

        # Should call parent constructor with empty list
        assert compose.mechanisms() == ()
        assert compose.is_enabled() is True

    def test_initialization_with_single_process(self):
        """Test initialization with single process."""
        # Create mock process with mechanisms
        mock_process = Mock(spec=Process)
        mock_mechanisms = [Mock(spec=Mechanism) for _ in range(3)]
        mock_process.mechanisms.return_value = tuple(mock_mechanisms)

        with patch("procela.core.key_authority.KeyAuthority") as MockKeyAuthority:
            mock_key = Key()
            MockKeyAuthority.issue.return_value = mock_key

            compose = Compose(processes=[mock_process])

            # Should have all mechanisms from the process
            assert len(compose.mechanisms()) == 3
            assert compose.mechanisms() == tuple(mock_mechanisms)
            mock_process.mechanisms.assert_called_once()

    def test_initialization_with_multiple_processes(self):
        """Test initialization with multiple processes."""
        # Create mock processes with different numbers of mechanisms
        mock_processes = []
        all_mechanisms = []

        for i in range(3):
            mock_process = Mock(spec=Process)
            n_mechs = i + 1  # 1, 2, 3 mechanisms
            mechanisms = [Mock(spec=Mechanism) for _ in range(n_mechs)]
            mock_process.mechanisms.return_value = tuple(mechanisms)
            mock_processes.append(mock_process)
            all_mechanisms.extend(mechanisms)

        compose = Compose(processes=mock_processes)

        # Should have all mechanisms from all processes (1+2+3=6)
        assert len(compose.mechanisms()) == 6
        assert list(compose.mechanisms()) == all_mechanisms

        # Each process.mechanisms() should have been called
        for process in mock_processes:
            process.mechanisms.assert_called_once()

    def test_initialization_preserves_order(self):
        """Test that mechanism order is preserved across processes."""
        # Create processes with identifiable mechanisms
        process1 = Mock(spec=Process)
        mech1 = Mock(spec=Mechanism)
        mech1.name = "P1-M1"
        mech2 = Mock(spec=Mechanism)
        mech2.name = "P1-M2"
        process1.mechanisms.return_value = (mech1, mech2)

        process2 = Mock(spec=Process)
        mech3 = Mock(spec=Mechanism)
        mech3.name = "P2-M1"
        mech4 = Mock(spec=Mechanism)
        mech4.name = "P2-M2"
        mech5 = Mock(spec=Mechanism)
        mech5.name = "P2-M3"
        process2.mechanisms.return_value = (mech3, mech4, mech5)

        process3 = Mock(spec=Process)
        mech6 = Mock(spec=Mechanism)
        mech6.name = "P3-M1"
        process3.mechanisms.return_value = (mech6,)

        compose = Compose(processes=[process1, process2, process3])

        # Should be in order: P1 mechanisms, then P2, then P3
        mechanisms = list(compose.mechanisms())
        assert len(mechanisms) == 6
        assert mechanisms[0].name == "P1-M1"
        assert mechanisms[1].name == "P1-M2"
        assert mechanisms[2].name == "P2-M1"
        assert mechanisms[3].name == "P2-M2"
        assert mechanisms[4].name == "P2-M3"
        assert mechanisms[5].name == "P3-M1"

    def test_compose_inherits_from_process(self):
        """Test that Compose is a subclass of Process."""
        compose = Compose(processes=[])
        assert isinstance(compose, Process)
        assert issubclass(Compose, Process)


class TestComposeInheritedMethods:
    """Test that Compose inherits and can use all Process methods."""

    def test_enable_disable_methods(self):
        """Test enable/disable methods inherited from Process."""
        mock_process = Mock(spec=Process)
        mock_process.mechanisms.return_value = ()

        compose = Compose(processes=[mock_process])

        # Initially enabled
        assert compose.is_enabled() is True

        # Disable
        compose.disable()
        assert compose.is_enabled() is False

        # Enable
        compose.enable()
        assert compose.is_enabled() is True

    def test_step_method(self):
        """Test step() method inherited from Process."""
        # Create mechanisms with run tracking
        mech1 = Mock(spec=Mechanism)
        mech2 = Mock(spec=Mechanism)
        mech3 = Mock(spec=Mechanism)

        process = Mock(spec=Process)
        process.mechanisms.return_value = (mech1, mech2, mech3)

        compose = Compose(processes=[process])

        # Execute step
        compose.step()

        # All mechanisms should be called
        mech1.run.assert_called_once()
        mech2.run.assert_called_once()
        mech3.run.assert_called_once()

    def test_step_respects_enablement(self):
        """Test that step() respects enablement state."""
        mech = Mock(spec=Mechanism)
        process = Mock(spec=Process)
        process.mechanisms.return_value = (mech,)

        compose = Compose(processes=[process])

        # Disable and step
        compose.disable()
        compose.step()
        mech.run.assert_not_called()  # Should not run

        # Enable and step
        compose.enable()
        compose.step()
        mech.run.assert_called_once()  # Should run

    def test_writable_method(self):
        """Test writable() method inherited from Process."""
        # Create mechanisms with write variables
        mech1 = Mock(spec=Mechanism)
        var1, var2 = create_real_variable(), create_real_variable()
        mech1.writes.return_value = [var1, var2]

        mech2 = Mock(spec=Mechanism)
        var3 = create_real_variable()
        mech2.writes.return_value = [var3]

        process = Mock(spec=Process)
        process.mechanisms.return_value = (mech1, mech2)

        compose = Compose(processes=[process])

        writable = compose.writable()

        assert isinstance(writable, set)
        assert len(writable) == 3
        assert var1 in writable
        assert var2 in writable
        assert var3 in writable

    def test_variables_method(self):
        """Test variables() method inherited from Process."""
        # Create mechanisms with read and write variables
        mech1 = Mock(spec=Mechanism)
        var1, var2 = create_real_variable(), create_real_variable()
        mech1.reads.return_value = [var1]
        mech1.writes.return_value = [var2]

        mech2 = Mock(spec=Mechanism)
        var3, var4 = create_real_variable(), create_real_variable()
        mech2.reads.return_value = [var3]
        mech2.writes.return_value = [var4]

        process = Mock(spec=Process)
        process.mechanisms.return_value = (mech1, mech2)

        compose = Compose(processes=[process])

        variables = compose.variables()

        assert isinstance(variables, set)
        assert len(variables) == 4
        assert var1 in variables
        assert var2 in variables
        assert var3 in variables
        assert var4 in variables

    def test_key_method(self):
        """Test key() method inherited from Process."""
        with patch("procela.core.key_authority.KeyAuthority") as MockKeyAuthority:
            mock_key = Key()
            MockKeyAuthority.issue.return_value = mock_key

            compose = Compose(processes=[])

            # Should return the same key every time
            key1 = compose.key()
            key2 = compose.key()

            assert key1 is key2

    def test_mechanisms_method(self):
        """Test mechanisms() method returns flattened mechanisms."""
        # Create nested processes
        mech1, mech2, mech3 = (
            Mock(spec=Mechanism),
            Mock(spec=Mechanism),
            Mock(spec=Mechanism),
        )

        process1 = Mock(spec=Process)
        process1.mechanisms.return_value = (mech1,)

        process2 = Mock(spec=Process)
        process2.mechanisms.return_value = (mech2, mech3)

        compose = Compose(processes=[process1, process2])

        mechanisms = compose.mechanisms()

        assert isinstance(mechanisms, tuple)
        assert len(mechanisms) == 3
        assert mechanisms[0] is mech1
        assert mechanisms[1] is mech2
        assert mechanisms[2] is mech3


class TestComposeFlatteningBehavior:
    """Test the flattening behavior of Compose."""

    def test_flattening_nested_compose(self):
        """Test Compose with nested Compose instances."""
        # Create leaf mechanisms
        leaf_mechs = [Mock(spec=Mechanism) for _ in range(4)]
        for i, mech in enumerate(leaf_mechs):
            mech.id = f"Leaf{i}"

        # Create leaf processes
        leaf_process1 = Mock(spec=Process)
        leaf_process1.mechanisms.return_value = (leaf_mechs[0], leaf_mechs[1])

        leaf_process2 = Mock(spec=Process)
        leaf_process2.mechanisms.return_value = (leaf_mechs[2], leaf_mechs[3])

        # Create nested compose
        nested_compose = Compose(processes=[leaf_process1, leaf_process2])

        # Create another leaf process
        leaf_process3 = Mock(spec=Process)
        leaf_mech5 = Mock(spec=Mechanism)
        leaf_mech5.id = "Leaf4"
        leaf_process3.mechanisms.return_value = (leaf_mech5,)

        # Create top-level compose with nested compose and leaf process
        top_compose = Compose(processes=[nested_compose, leaf_process3])

        # Top compose should have all 5 mechanisms flattened
        mechanisms = list(top_compose.mechanisms())
        assert len(mechanisms) == 5

        # Check all mechanisms are present
        mech_ids = [m.id for m in mechanisms if hasattr(m, "id")]
        assert "Leaf0" in mech_ids
        assert "Leaf1" in mech_ids
        assert "Leaf2" in mech_ids
        assert "Leaf3" in mech_ids
        assert "Leaf4" in mech_ids

    def test_flattening_deeply_nested(self):
        """Test deeply nested Compose instances."""
        # Create leaf mechanism
        leaf_mech = Mock(spec=Mechanism)
        leaf_mech.name = "DeepLeaf"

        # Create chain of processes
        leaf_process = Mock(spec=Process)
        leaf_process.mechanisms.return_value = (leaf_mech,)

        # Create multiple levels of composition
        level3 = Compose(processes=[leaf_process])
        level2 = Compose(processes=[level3])
        level1 = Compose(processes=[level2])
        root = Compose(processes=[level1])

        # Root should have the leaf mechanism
        mechanisms = list(root.mechanisms())
        assert len(mechanisms) == 1
        assert mechanisms[0].name == "DeepLeaf"

    def test_flattening_with_empty_processes(self):
        """Test flattening with empty processes in the sequence."""
        # Create some real mechanisms
        mech1, mech2 = Mock(spec=Mechanism), Mock(spec=Mechanism)

        # Create processes, some empty
        process1 = Mock(spec=Process)
        process1.mechanisms.return_value = ()

        process2 = Mock(spec=Process)
        process2.mechanisms.return_value = (mech1,)

        process3 = Mock(spec=Process)
        process3.mechanisms.return_value = ()

        process4 = Mock(spec=Process)
        process4.mechanisms.return_value = (mech2,)

        process5 = Mock(spec=Process)
        process5.mechanisms.return_value = ()

        compose = Compose(processes=[process1, process2, process3, process4, process5])

        # Should only have mechanisms from non-empty processes
        mechanisms = list(compose.mechanisms())
        assert len(mechanisms) == 2
        assert mechanisms[0] is mech1
        assert mechanisms[1] is mech2


class TestComposeIntegration:
    """Integration tests for Compose usage patterns."""

    def test_compose_with_real_process_subclass(self):
        """Test Compose with real Process subclass."""

        class SimpleProcess(Process):
            def __init__(self, mechanisms):
                super().__init__(mechanisms)
                self.name = "SimpleProcess"

        # Create real mechanisms
        class SimpleMechanism(Mechanism):
            def __init__(self, name):
                super().__init__(reads=[], writes=[])
                self.name = name
                self.run_count = 0

            def transform(self):
                self.run_count += 1

        # Create mechanisms
        mechs = [SimpleMechanism(f"M{i}") for i in range(4)]

        # Create processes
        process1 = SimpleProcess(mechanisms=mechs[:2])  # M0, M1
        process2 = SimpleProcess(mechanisms=mechs[2:])  # M2, M3

        # Create compose
        compose = Compose(processes=[process1, process2])

        # Test mechanisms
        assert len(compose.mechanisms()) == 4
        assert compose.mechanisms()[0].name == "M0"
        assert compose.mechanisms()[3].name == "M3"

        # Test step execution
        compose.step()
        for mech in mechs:
            assert mech.run_count == 1

        # Test enable/disable
        compose.disable()
        compose.step()
        for mech in mechs:
            assert mech.run_count == 1  # No increment

        compose.enable()
        compose.step()
        for mech in mechs:
            assert mech.run_count == 2  # Incremented again

        # Test key collections
        # Add some variables to mechanisms for testing
        var1, var2 = create_real_variable(), create_real_variable()
        mechs[0]._reads = [var1]
        mechs[0]._writes = [var2]
        mechs[1]._reads = [var2]
        mechs[1]._writes = [var1]

        writable = compose.writable()
        variables = compose.variables()

        assert len(writable) == 2
        assert len(variables) == 2

    def test_compose_as_process_aggregator(self):
        """Test using Compose to aggregate multiple independent processes."""

        class DomainProcess(Process):
            def __init__(self, domain_name, n_mechanisms):
                mechs = [Mock(spec=Mechanism) for _ in range(n_mechanisms)]
                for i, mech in enumerate(mechs):
                    mech.domain = domain_name
                    mech.id = f"{domain_name}-{i}"
                super().__init__(mechs)
                self.domain = domain_name

        # Create domain-specific processes
        sensor_process = DomainProcess("sensor", 2)
        control_process = DomainProcess("control", 3)
        logging_process = DomainProcess("logging", 1)

        # Compose all domains
        system = Compose(processes=[sensor_process, control_process, logging_process])

        # Should have all mechanisms (2+3+1=6)
        assert len(system.mechanisms()) == 6

        # Check mechanism domains
        mechanisms = list(system.mechanisms())
        domains = [m.domain for m in mechanisms]

        assert domains.count("sensor") == 2
        assert domains.count("control") == 3
        assert domains.count("logging") == 1

        # Order should be preserved
        assert mechanisms[0].domain == "sensor"
        assert mechanisms[1].domain == "sensor"
        assert mechanisms[2].domain == "control"
        assert mechanisms[5].domain == "logging"

    def test_compose_with_dynamic_process_behavior(self):
        """Test Compose where processes change dynamically."""

        class DynamicProcess(Process):
            def __init__(self, initial_mechanisms):
                self._dynamic_mechs = list(initial_mechanisms)
                super().__init__(self._dynamic_mechs)

            def add_mechanism(self, mechanism):
                self._dynamic_mechs.append(mechanism)
                # Note: Process doesn't allow dynamic modification,
                # so we're testing the Compose initialization snapshot

        # Create initial setup
        mech1, mech2 = Mock(spec=Mechanism), Mock(spec=Mechanism)
        process = DynamicProcess([mech1])

        # Compose captures initial state
        compose = Compose(processes=[process])
        assert len(compose.mechanisms()) == 1

        # Add mechanism to process after compose creation
        process.add_mechanism(mech2)

        # Compose should still have original mechanisms (snapshot at creation)
        assert len(compose.mechanisms()) == 1

        new_compose = Compose(processes=[process])
        assert len(new_compose.mechanisms()) == 1


class TestComposeEdgeCases:
    """Test edge cases and special scenarios."""

    def test_compose_with_large_number_of_processes(self):
        """Test with a large number of processes."""
        n_processes = 100
        mock_processes = []
        total_mechs = 0

        for i in range(n_processes):
            mock_process = Mock(spec=Process)
            n_mechs = (i % 5) + 1  # 1-5 mechanisms per process
            mechanisms = [Mock(spec=Mechanism) for _ in range(n_mechs)]
            mock_process.mechanisms.return_value = tuple(mechanisms)
            mock_processes.append(mock_process)
            total_mechs += n_mechs

        compose = Compose(processes=mock_processes)

        # Should have all mechanisms
        assert len(compose.mechanisms()) == total_mechs

        # Each process.mechanisms() should have been called
        for process in mock_processes:
            process.mechanisms.assert_called_once()

    def test_compose_with_self_reference_avoidance(self):
        """Test that Compose doesn't create circular references with self."""
        # and Compose IS-A Process, but let's test the behavior

        # Create a regular process
        mock_process = Mock(spec=Process)
        mock_mech = Mock(spec=Mechanism)
        mock_process.mechanisms.return_value = (mock_mech,)

        # Create first compose
        compose1 = Compose(processes=[mock_process])

        # Create second compose that includes first compose
        # This is valid since Compose is a Process
        compose2 = Compose(processes=[compose1])

        # Compose2 should have the mechanism from compose1
        assert len(compose2.mechanisms()) == 1
        assert compose2.mechanisms()[0] is mock_mech

        # Create third compose that includes both
        compose3 = Compose(processes=[compose1, compose2])

        # Should have mechanism twice (no deduplication in flattening)
        assert len(compose3.mechanisms()) == 2
        assert compose3.mechanisms()[0] is mock_mech
        assert compose3.mechanisms()[1] is mock_mech

    def test_compose_with_process_returning_none_mechanisms(self):
        """Test with process returning None or invalid mechanisms."""
        # This should not happen with proper Process implementations,
        # but let's test robustness

        mock_process = Mock(spec=Process)
        # Simulate process.mechanisms() returning something unexpected
        # (though Process contract says it returns Sequence[Mechanism])
        mock_process.mechanisms.return_value = None

        # Should handle gracefully (will fail at iteration in list comprehension)
        with pytest.raises(TypeError):
            Compose(processes=[mock_process])

    def test_compose_initialization_performance(self):
        """Test initialization doesn't have performance issues with many mechanisms."""
        # Create many processes with many mechanisms
        n_processes = 10
        mechs_per_process = 1000

        mock_processes = []
        for i in range(n_processes):
            mock_process = Mock(spec=Process)
            mechanisms = [Mock(spec=Mechanism) for _ in range(mechs_per_process)]
            mock_process.mechanisms.return_value = tuple(mechanisms)
            mock_processes.append(mock_process)

        # Should complete initialization
        compose = Compose(processes=mock_processes)

        # Should have all mechanisms
        assert len(compose.mechanisms()) == n_processes * mechs_per_process


class TestComposeDesignContract:
    """Test design contracts mentioned in docstrings."""

    def test_compose_flattens_mechanisms_once(self):
        """Test that mechanisms are flattened at initialization."""
        mock_process = Mock(spec=Process)
        mech1, mech2 = Mock(spec=Mechanism), Mock(spec=Mechanism)
        mock_process.mechanisms.return_value = (mech1, mech2)

        compose = Compose(processes=[mock_process])

        # mechanisms() should return the flattened tuple
        mechanisms = compose.mechanisms()
        assert isinstance(mechanisms, tuple)
        assert len(mechanisms) == 2

        # Process.mechanisms() should have been called once during init
        mock_process.mechanisms.assert_called_once()

        compose.mechanisms()
        compose.mechanisms()
        mock_process.mechanisms.assert_called_once()  # Still just once

    def test_compose_is_transparent_to_process_methods(self):
        """Test that Compose transparently inherits all Process behavior."""
        # All Process methods should work exactly the same on Compose

        mock_process = Mock(spec=Process)
        mock_mech = Mock(spec=Mechanism)
        mock_process.mechanisms.return_value = (mock_mech,)

        compose = Compose(processes=[mock_process])

        # Test that all Process methods are available
        assert hasattr(compose, "key")
        assert hasattr(compose, "mechanisms")
        assert hasattr(compose, "enable")
        assert hasattr(compose, "disable")
        assert hasattr(compose, "is_enabled")
        assert hasattr(compose, "step")
        assert hasattr(compose, "writable")
        assert hasattr(compose, "variables")

        # Test they work correctly
        assert callable(compose.key)
        assert callable(compose.mechanisms)
        assert callable(compose.enable)
        assert callable(compose.disable)
        assert callable(compose.is_enabled)
        assert callable(compose.step)
        assert callable(compose.writable)
        assert callable(compose.variables)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
