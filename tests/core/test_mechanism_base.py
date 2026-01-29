"""
Pytest suite with 100% coverage for Mechanism abstract class.
"""

import pytest

from procela.core.mechanism import Mechanism
from procela.core.variable import RealDomain, Variable
from procela.symbols.key import Key


class TestMechanismInitialization:
    """Test Mechanism initialization and basic properties."""

    def test_initialization_with_empty_sequences(self):
        """Test initialization with empty read/write sequences."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        mechanism = TestMechanism(reads=[], writes=[])

        assert isinstance(mechanism.key(), Key)
        assert mechanism.reads() == ()
        assert mechanism.writes() == ()
        assert mechanism.is_enabled() is True

    def test_initialization_with_single_keys(self):
        """Test initialization with single keys."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        read_key = Variable(name="v1", domain=RealDomain())
        write_key = Variable(name="v2", domain=RealDomain())

        mechanism = TestMechanism(reads=[read_key], writes=[write_key])

        assert mechanism.reads() == (read_key,)
        assert mechanism.writes() == (write_key,)
        assert len(mechanism.reads()) == 1
        assert len(mechanism.writes()) == 1

    def test_initialization_with_multiple_keys(self):
        """Test initialization with multiple keys."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        reads = [
            Variable(name="v1", domain=RealDomain()),
            Variable(name="v2", domain=RealDomain()),
            Variable(name="v3", domain=RealDomain()),
        ]
        writes = [
            Variable(name="v1", domain=RealDomain()),
            Variable(name="v2", domain=RealDomain()),
        ]

        mechanism = TestMechanism(reads=reads, writes=writes)

        assert mechanism.reads() == tuple(reads)
        assert mechanism.writes() == tuple(writes)
        assert len(mechanism.reads()) == 3
        assert len(mechanism.writes()) == 2

    def test_initialization_with_duplicate_keys(self):
        """Test initialization with duplicate keys in sequences."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        same = Variable(name="v1", domain=RealDomain())
        read_keys = [same, same, Variable(name="v1", domain=RealDomain())]
        write_keys = [same, Variable(name="v1", domain=RealDomain()), same]

        mechanism = TestMechanism(reads=read_keys, writes=write_keys)

        # Should preserve duplicates
        assert len(mechanism.reads()) == 3
        assert len(mechanism.writes()) == 3
        assert mechanism.reads().count(same) == 2
        assert mechanism.writes().count(same) == 2

    def test_key_uniqueness_per_instance(self):
        """Test that each mechanism instance gets a unique key."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        mechanism1 = TestMechanism(reads=[], writes=[])
        mechanism2 = TestMechanism(reads=[], writes=[])
        mechanism3 = TestMechanism(
            reads=[Variable(name="v1", domain=RealDomain())],
            writes=[
                Variable(name="v2", domain=RealDomain()),
            ],
        )

        # Each should have a unique key
        key1 = mechanism1.key()
        key2 = mechanism2.key()
        key3 = mechanism3.key()

        assert key1 != key2
        assert key1 != key3
        assert key2 != key3

    def test_initial_enabled_state(self):
        """Test that mechanisms are initially enabled."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        mechanism = TestMechanism(reads=[], writes=[])
        assert mechanism.is_enabled() is True

    def test_initial_that_raises(self):
        """Test that mechanisms raise errors."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        with pytest.raises(TypeError):
            TestMechanism(reads=2, writes=[])

        with pytest.raises(TypeError):
            TestMechanism(reads=[], writes=[24])


class TestMechanismEnableDisable:
    """Test enable/disable functionality."""

    def test_enable_method(self):
        """Test that enable() sets enabled to True."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        mechanism = TestMechanism(reads=[], writes=[])

        # Start enabled
        assert mechanism.is_enabled() is True

        # Disable then enable
        mechanism.disable()
        assert mechanism.is_enabled() is False

        mechanism.enable()
        assert mechanism.is_enabled() is True

    def test_disable_method(self):
        """Test that disable() sets enabled to False."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        mechanism = TestMechanism(reads=[], writes=[])

        # Start enabled
        assert mechanism.is_enabled() is True

        mechanism.disable()
        assert mechanism.is_enabled() is False

        # Multiple calls should keep it disabled
        mechanism.disable()
        mechanism.disable()
        assert mechanism.is_enabled() is False

    def test_enable_disable_cycle(self):
        """Test multiple enable/disable cycles."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        mechanism = TestMechanism(reads=[], writes=[])

        for i in range(5):
            mechanism.disable()
            assert mechanism.is_enabled() is False, f"Failed on disable cycle {i}"

            mechanism.enable()
            assert mechanism.is_enabled() is True, f"Failed on enable cycle {i}"


class TestMechanismRunMethod:
    """Test the run() method behavior."""

    def test_run_when_enabled_calls_transform(self):
        """Test that run() calls transform() when mechanism is enabled."""

        transform_called = []

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                transform_called.append(True)

        mechanism = TestMechanism(reads=[], writes=[])

        # Initially enabled
        assert mechanism.is_enabled() is True

        mechanism.run()
        assert len(transform_called) == 1

        # Run again
        mechanism.run()
        assert len(transform_called) == 2

    def test_run_when_disabled_skips_transform(self):
        """Test that run() does not call transform() when mechanism is disabled."""

        transform_called = []

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                transform_called.append(True)

        mechanism = TestMechanism(reads=[], writes=[])
        mechanism.disable()

        mechanism.run()
        assert len(transform_called) == 0

        # Multiple runs should still not call transform
        mechanism.run()
        mechanism.run()
        assert len(transform_called) == 0

    def test_run_enable_disable_pattern(self):
        """Test run behavior when enabling/disabling between runs."""

        transform_calls = []

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                transform_calls.append("called")

        mechanism = TestMechanism(reads=[], writes=[])

        # Enabled -> should call
        mechanism.run()
        assert len(transform_calls) == 1

        # Disable -> should not call
        mechanism.disable()
        mechanism.run()
        assert len(transform_calls) == 1

        # Enable -> should call again
        mechanism.enable()
        mechanism.run()
        assert len(transform_calls) == 2

        # Disable and run multiple times
        mechanism.disable()
        for _ in range(5):
            mechanism.run()
        assert len(transform_calls) == 2


class TestMechanismAbstractMethod:
    """Test that Mechanism requires transform() implementation."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that Mechanism cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            Mechanism(reads=[], writes=[])

    def test_concrete_subclass_must_implement_transform(self):
        """Test that concrete subclasses must implement transform()."""

        class IncompleteMechanism(Mechanism):
            # Missing transform() implementation
            pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteMechanism(reads=[], writes=[])

    def test_concrete_subclass_with_transform_can_be_instantiated(self):
        """Test that concrete subclass with transform() can be instantiated."""

        class ConcreteMechanism(Mechanism):
            def transform(self) -> None:
                print("Transforming")

        # Should not raise an error
        mechanism = ConcreteMechanism(reads=[], writes=[])
        assert isinstance(mechanism, Mechanism)
        assert isinstance(mechanism, ConcreteMechanism)


class TestMechanismTransformMethod:
    """Test transform() method implementations."""

    def test_transform_can_access_instance_variables(self):
        """Test that transform() can access mechanism state."""

        class StatefulMechanism(Mechanism):
            def __init__(self, reads, writes, multiplier):
                super().__init__(reads, writes)
                self.multiplier = multiplier
                self.result = 0

            def transform(self) -> None:
                # Access and modify instance state
                self.result = len(self.reads()) * self.multiplier

        mechanism = StatefulMechanism(
            reads=[
                Variable(name="v1", domain=RealDomain()),
                Variable(name="v2", domain=RealDomain()),
                Variable(name="v3", domain=RealDomain()),
            ],
            writes=[Variable(name="v1", domain=RealDomain())],
            multiplier=10,
        )

        mechanism.run()
        assert mechanism.result == 30  # 3 reads * 10

    def test_transform_can_be_empty(self):
        """Test that transform() can be empty (do nothing)."""

        class EmptyTransformMechanism(Mechanism):
            def transform(self) -> None:
                # Explicitly do nothing
                pass

        mechanism = EmptyTransformMechanism(reads=[], writes=[])

        # Should not raise any errors
        mechanism.run()
        mechanism.run()
        mechanism.run()

    def test_transform_can_raise_exceptions(self):
        """Test that transform() can raise exceptions."""

        class ExceptionMechanism(Mechanism):
            def transform(self) -> None:
                raise ValueError("Transform failed")

        mechanism = ExceptionMechanism(reads=[], writes=[])

        # Exception should propagate through run()
        with pytest.raises(ValueError, match="Transform failed"):
            mechanism.run()

        # Should still be enabled
        assert mechanism.is_enabled() is True


class TestMechanismImmutableProperties:
    """Test that key, reads, and writes are immutable after initialization."""

    def test_reads_immutable(self):
        """Test that reads() returns an immutable sequence."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        original = [
            Variable(name="v1", domain=RealDomain()),
            Variable(name="v2", domain=RealDomain()),
        ]
        mechanism = TestMechanism(reads=original, writes=[])

        reads_result = mechanism.reads()

        # Should be a tuple (immutable)
        assert isinstance(reads_result, tuple)

        # Attempting to modify should fail
        with pytest.raises(AttributeError):
            reads_result.append(Key())

        # Original list modification shouldn't affect mechanism
        original.append(Variable(name="v1", domain=RealDomain()))
        assert len(mechanism.reads()) == 2  # Still original length

    def test_writes_immutable(self):
        """Test that writes() returns an immutable sequence."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        original = [
            Variable(name="v1", domain=RealDomain()),
            Variable(name="v2", domain=RealDomain()),
            Variable(name="v3", domain=RealDomain()),
        ]
        mechanism = TestMechanism(reads=[], writes=original)

        writes_result = mechanism.writes()

        # Should be a tuple (immutable)
        assert isinstance(writes_result, tuple)

        # Verify content
        assert writes_result == tuple(original)

    def test_key_immutable(self):
        """Test that key() returns the same key always."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        mechanism = TestMechanism(reads=[], writes=[])

        key1 = mechanism.key()
        key2 = mechanism.key()
        key3 = mechanism.key()

        # Should return the same key every time
        assert key1 is key2
        assert key1 is key3
        assert key2 is key3


class TestMechanismEdgeCases:
    """Test edge cases and special scenarios."""

    def test_mechanism_with_same_read_write_keys(self):
        """Test mechanism that reads and writes the same keys."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        same = Variable(name="v1", domain=RealDomain())
        other = Variable(name="v2", domain=RealDomain())

        mechanism = TestMechanism(reads=[same, other], writes=[same, other])

        assert len(mechanism.reads()) == 2
        assert len(mechanism.writes()) == 2
        assert mechanism.reads() == mechanism.writes()

    def test_mechanism_with_empty_key_in_sequences(self):
        """Test behavior with potentially problematic key sequences."""
        # This test depends on Key() implementation
        # Assuming Key() always creates valid keys

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        keys = [Key() for _ in range(0)]  # Empty list
        mechanism = TestMechanism(reads=keys, writes=keys)

        assert mechanism.reads() == ()
        assert mechanism.writes() == ()

    def test_mechanism_inheritance_hierarchy(self):
        """Test Mechanism in an inheritance hierarchy."""

        class BaseMechanism(Mechanism):
            def transform(self) -> None:
                self.base_called = True

        class DerivedMechanism(BaseMechanism):
            def __init__(self, reads, writes, extra_param):
                super().__init__(reads, writes)
                self.extra_param = extra_param
                self.derived_called = False

            def transform(self) -> None:
                super().transform()
                self.derived_called = True

        mechanism = DerivedMechanism(
            reads=[
                Variable(name="v1", domain=RealDomain()),
            ],
            writes=[
                Variable(name="v2", domain=RealDomain()),
            ],
            extra_param="test",
        )

        mechanism.run()

        assert hasattr(mechanism, "base_called")
        assert mechanism.base_called is True
        assert mechanism.derived_called is True
        assert mechanism.extra_param == "test"


class TestMechanismIntegration:
    """Integration tests for Mechanism usage patterns."""

    def test_multiple_mechanisms_independence(self):
        """Test that multiple mechanisms operate independently."""

        class CounterMechanism(Mechanism):
            def __init__(self, reads, writes):
                super().__init__(reads, writes)
                self.run_count = 0

            def transform(self) -> None:
                self.run_count += 1

        # Create multiple independent mechanisms
        mechanisms = [CounterMechanism(reads=[], writes=[]) for _ in range(5)]

        # Run each mechanism
        for i, mechanism in enumerate(mechanisms):
            mechanism.run()
            assert mechanism.run_count == 1

        # Disable some, enable others
        mechanisms[0].disable()
        mechanisms[2].disable()

        # Run all again
        for mechanism in mechanisms:
            mechanism.run()

        # Check counts
        assert mechanisms[0].run_count == 1  # Disabled, no increment
        assert mechanisms[1].run_count == 2  # Enabled, incremented
        assert mechanisms[2].run_count == 1  # Disabled, no increment
        assert mechanisms[3].run_count == 2  # Enabled, incremented
        assert mechanisms[4].run_count == 2  # Enabled, incremented

    def test_mechanism_with_complex_state(self):
        """Test mechanism with complex internal state management."""

        class StateMachineMechanism(Mechanism):
            def __init__(self, reads, writes):
                super().__init__(reads, writes)
                self.state = "IDLE"
                self.transition_count = 0

            def transform(self) -> None:
                if self.state == "IDLE":
                    self.state = "PROCESSING"
                elif self.state == "PROCESSING":
                    self.state = "COMPLETE"
                elif self.state == "COMPLETE":
                    self.state = "IDLE"
                    self.transition_count += 1

            def reset(self):
                self.state = "IDLE"
                self.transition_count = 0

        mechanism = StateMachineMechanism(
            reads=[
                Variable(name="v1", domain=RealDomain()),
            ],
            writes=[
                Variable(name="v2", domain=RealDomain()),
            ],
        )

        # Initial state
        assert mechanism.state == "IDLE"
        assert mechanism.transition_count == 0

        # Run through state transitions
        mechanism.run()  # IDLE -> PROCESSING
        assert mechanism.state == "PROCESSING"

        mechanism.run()  # PROCESSING -> COMPLETE
        assert mechanism.state == "COMPLETE"

        mechanism.run()  # COMPLETE -> IDLE, increment count
        assert mechanism.state == "IDLE"
        assert mechanism.transition_count == 1

        # Disable and run - should not affect state
        mechanism.disable()
        mechanism.run()
        assert mechanism.state == "IDLE"  # Unchanged
        assert mechanism.transition_count == 1  # Unchanged

        # Enable and continue
        mechanism.enable()
        mechanism.run()  # IDLE -> PROCESSING
        assert mechanism.state == "PROCESSING"

    def test_mechanism_polymorphism(self):
        """Test polymorphism with different Mechanism implementations."""

        class AddMechanism(Mechanism):
            def __init__(self, reads, writes, value):
                super().__init__(reads, writes)
                self.value = value
                self.total = 0

            def transform(self) -> None:
                self.total += self.value

        class MultiplyMechanism(Mechanism):
            def __init__(self, reads, writes, factor):
                super().__init__(reads, writes)
                self.factor = factor
                self.total = 1

            def transform(self) -> None:
                self.total *= self.factor

        # Use polymorphically
        mechanisms = [
            AddMechanism(reads=[], writes=[], value=5),
            MultiplyMechanism(reads=[], writes=[], factor=2),
            AddMechanism(reads=[], writes=[], value=10),
        ]

        # Run all mechanisms
        for mechanism in mechanisms:
            mechanism.run()

        # Check results
        assert isinstance(mechanisms[0], AddMechanism)
        assert mechanisms[0].total == 5

        assert isinstance(mechanisms[1], MultiplyMechanism)
        assert mechanisms[1].total == 2

        assert isinstance(mechanisms[2], AddMechanism)
        assert mechanisms[2].total == 10

        # All should be Mechanism instances
        for mechanism in mechanisms:
            assert isinstance(mechanism, Mechanism)


class TestMechanismErrorConditions:
    """Test error conditions and validation."""

    def test_invalid_initialization_parameters(self):
        """Test initialization with invalid parameters."""

        class TestMechanism(Mechanism):
            def transform(self) -> None:
                pass

        # Test with None (should fail if type checking is strict)
        # This depends on whether the code has type checking
        # We'll test what happens with unexpected inputs

        # Test with non-sequence (should fail)
        with pytest.raises(TypeError):
            TestMechanism(reads="not_a_sequence", writes=[])

        with pytest.raises(TypeError):
            TestMechanism(reads=[], writes=123)

    def test_transform_method_access_control(self):
        """Test that transform should only access declared keys."""
        # This is a documentation/design test since we can't enforce it in tests

        class WellBehavedMechanism(Mechanism):
            def __init__(self, reads, writes):
                super().__init__(reads, writes)
                self.declared_reads = reads
                self.declared_writes = writes

            def transform(self) -> None:
                # Well-behaved: only accesses declared keys
                # In real implementation, this would access actual variables
                read_count = len(self.declared_reads)
                write_count = len(self.declared_writes)
                self.result = f"R{read_count}W{write_count}"

        mechanism = WellBehavedMechanism(
            reads=[
                Variable(name="v1", domain=RealDomain()),
                Variable(name="v2", domain=RealDomain()),
            ],
            writes=[
                Variable(name="v3", domain=RealDomain()),
            ],
        )

        mechanism.run()
        assert mechanism.result == "R2W1"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
