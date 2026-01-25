"""
Pytest suite with 100% coverage for MechanismTemplate abstract class.
"""

from typing import Sequence

import pytest

from procela.core.mechanism import MechanismTemplate
from procela.symbols.key import Key


class TestMechanismTemplateAbstractMethods:
    """Test that MechanismTemplate requires abstract method implementations."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that MechanismTemplate cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            MechanismTemplate()

    def test_incomplete_subclass_missing_reads(self):
        """Test subclass missing reads() implementation."""

        class IncompleteTemplate(MechanismTemplate):
            # Missing reads()

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteTemplate()

    def test_incomplete_subclass_missing_writes(self):
        """Test subclass missing writes() implementation."""

        class IncompleteTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return []

            # Missing writes()

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteTemplate()

    def test_incomplete_subclass_missing_transform(self):
        """Test subclass missing transform() implementation."""

        class IncompleteTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return []

            def writes(self) -> Sequence[Key]:
                return []

            # Missing transform()

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteTemplate()

    def test_complete_subclass_can_be_instantiated(self):
        """Test that complete subclass can be instantiated."""

        class CompleteTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return []

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                pass

        # Should not raise an error
        template = CompleteTemplate()
        assert isinstance(template, MechanismTemplate)
        assert isinstance(template, CompleteTemplate)


class TestMechanismTemplateReadsMethod:
    """Test reads() method implementations."""

    def test_reads_empty_sequence(self):
        """Test reads() returning empty sequence."""

        class EmptyReadsTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return []

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                pass

        template = EmptyReadsTemplate()
        result = template.reads()

        assert isinstance(result, Sequence)
        assert len(result) == 0

    def test_reads_single_key(self):
        """Test reads() returning single key."""

        class SingleReadTemplate(MechanismTemplate):
            def __init__(self):
                self._read_key = Key()

            def reads(self) -> Sequence[Key]:
                return [self._read_key]

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                pass

        template = SingleReadTemplate()
        result = template.reads()

        assert isinstance(result, Sequence)
        assert len(result) == 1
        assert isinstance(result[0], Key)

    def test_reads_multiple_keys(self):
        """Test reads() returning multiple keys."""

        class MultiReadTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return [Key(), Key(), Key()]

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                pass

        template = MultiReadTemplate()
        result = template.reads()

        assert isinstance(result, Sequence)
        assert len(result) == 3
        assert all(isinstance(k, Key) for k in result)

    def test_reads_duplicate_keys(self):
        """Test reads() returning duplicate keys."""

        class DuplicateReadTemplate(MechanismTemplate):
            def __init__(self):
                self._key = Key()

            def reads(self) -> Sequence[Key]:
                # Return same key multiple times
                return [self._key, self._key, self._key]

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                pass

        template = DuplicateReadTemplate()
        result = template.reads()

        assert len(result) == 3
        assert result[0] is result[1]
        assert result[1] is result[2]

    def test_reads_dynamic_result(self):
        """Test reads() with dynamic return value."""

        class DynamicReadTemplate(MechanismTemplate):
            def __init__(self):
                self.read_keys = []

            def reads(self) -> Sequence[Key]:
                return list(self.read_keys)  # Return current state

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                pass

        template = DynamicReadTemplate()

        # Initially empty
        assert len(template.reads()) == 0

        # Add keys
        template.read_keys.append(Key())
        assert len(template.reads()) == 1

        template.read_keys.append(Key())
        template.read_keys.append(Key())
        assert len(template.reads()) == 3

        # Clear
        template.read_keys.clear()
        assert len(template.reads()) == 0


class TestMechanismTemplateWritesMethod:
    """Test writes() method implementations."""

    def test_writes_empty_sequence(self):
        """Test writes() returning empty sequence."""

        class EmptyWritesTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return []

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                pass

        template = EmptyWritesTemplate()
        result = template.writes()

        assert isinstance(result, Sequence)
        assert len(result) == 0

    def test_writes_single_key(self):
        """Test writes() returning single key."""

        class SingleWriteTemplate(MechanismTemplate):
            def __init__(self):
                self._write_key = Key()

            def reads(self) -> Sequence[Key]:
                return []

            def writes(self) -> Sequence[Key]:
                return [self._write_key]

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                pass

        template = SingleWriteTemplate()
        result = template.writes()

        assert isinstance(result, Sequence)
        assert len(result) == 1
        assert isinstance(result[0], Key)

    def test_writes_multiple_keys(self):
        """Test writes() returning multiple keys."""

        class MultiWriteTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return []

            def writes(self) -> Sequence[Key]:
                return [Key(), Key(), Key(), Key()]

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                pass

        template = MultiWriteTemplate()
        result = template.writes()

        assert isinstance(result, Sequence)
        assert len(result) == 4
        assert all(isinstance(k, Key) for k in result)

    def test_writes_different_from_reads(self):
        """Test writes() returning different keys than reads()."""

        class SeparateKeysTemplate(MechanismTemplate):
            def __init__(self):
                self._read_key = Key()
                self._write_key = Key()

            def reads(self) -> Sequence[Key]:
                return [self._read_key]

            def writes(self) -> Sequence[Key]:
                return [self._write_key]

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                pass

        template = SeparateKeysTemplate()

        reads = template.reads()
        writes = template.writes()

        assert len(reads) == 1
        assert len(writes) == 1
        assert reads[0] != writes[0]

    def test_writes_same_as_reads(self):
        """Test writes() returning same keys as reads()."""

        class SameKeysTemplate(MechanismTemplate):
            def __init__(self):
                self._shared_key = Key()

            def reads(self) -> Sequence[Key]:
                return [self._shared_key]

            def writes(self) -> Sequence[Key]:
                return [self._shared_key]

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                pass

        template = SameKeysTemplate()

        reads = template.reads()
        writes = template.writes()

        assert reads[0] is writes[0]  # Same object


class TestMechanismTemplateTransformMethod:
    """Test transform() method implementations."""

    def test_transform_with_empty_parameters(self):
        """Test transform() with empty input and output lists."""

        transform_called_with = []

        class EmptyTransformTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return []

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                transform_called_with.append((inputs, outputs))

        template = EmptyTransformTemplate()

        template.transform([], [])

        assert len(transform_called_with) == 1
        inputs, outputs = transform_called_with[0]
        assert inputs == []
        assert outputs == []

    def test_transform_with_inputs_only(self):
        """Test transform() with inputs but no outputs."""

        transform_called_with = []

        class InputOnlyTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return [Key(), Key()]

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                transform_called_with.append((inputs, outputs))

        template = InputOnlyTemplate()
        input_keys = [Key(), Key()]

        template.transform(input_keys, [])

        assert len(transform_called_with) == 1
        inputs, outputs = transform_called_with[0]
        assert inputs == input_keys
        assert outputs == []

    def test_transform_with_outputs_only(self):
        """Test transform() with outputs but no inputs."""

        transform_called_with = []

        class OutputOnlyTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return []

            def writes(self) -> Sequence[Key]:
                return [Key(), Key(), Key()]

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                transform_called_with.append((inputs, outputs))

        template = OutputOnlyTemplate()
        output_keys = [Key(), Key(), Key()]

        template.transform([], output_keys)

        assert len(transform_called_with) == 1
        inputs, outputs = transform_called_with[0]
        assert inputs == []
        assert outputs == output_keys

    def test_transform_with_both_inputs_and_outputs(self):
        """Test transform() with both inputs and outputs."""

        transform_called_with = []

        class FullTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return [Key()]

            def writes(self) -> Sequence[Key]:
                return [Key()]

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                transform_called_with.append((inputs, outputs))

        template = FullTemplate()
        input_keys = [Key(), Key()]
        output_keys = [Key(), Key(), Key()]

        template.transform(input_keys, output_keys)

        assert len(transform_called_with) == 1
        inputs, outputs = transform_called_with[0]
        assert inputs == input_keys
        assert outputs == output_keys

    def test_transform_accessing_instance_state(self):
        """Test transform() accessing and modifying instance state."""

        class StatefulTemplate(MechanismTemplate):
            def __init__(self):
                self.call_count = 0
                self.last_inputs = None
                self.last_outputs = None

            def reads(self) -> Sequence[Key]:
                return []

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                self.call_count += 1
                self.last_inputs = inputs.copy()  # Store copy
                self.last_outputs = outputs.copy()  # Store copy

        template = StatefulTemplate()
        input_keys = [Key(), Key()]
        output_keys = [Key()]

        # First call
        template.transform(input_keys, output_keys)

        assert template.call_count == 1
        assert template.last_inputs == input_keys
        assert template.last_outputs == output_keys

        # Second call with different parameters
        new_inputs = [Key()]
        new_outputs = [Key(), Key()]

        template.transform(new_inputs, new_outputs)

        assert template.call_count == 2
        assert template.last_inputs == new_inputs
        assert template.last_outputs == new_outputs

    def test_transform_raising_exceptions(self):
        """Test transform() that raises exceptions."""

        class ExceptionTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return []

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                raise ValueError("Transform failed unexpectedly")

        template = ExceptionTemplate()

        with pytest.raises(ValueError, match="Transform failed unexpectedly"):
            template.transform([], [])

    def test_transform_with_side_effects(self):
        """Test transform() with side effects (simulating Variable.add_candidate())."""

        class MockVariable:
            def __init__(self, key):
                self.key = key
                self.candidates = []

            def add_candidate(self, value):
                self.candidates.append(value)

        class ProposalTemplate(MechanismTemplate):
            def __init__(self):
                self.variables = {}

            def reads(self) -> Sequence[Key]:
                return []

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                # Simulate adding candidates to output variables
                # (as mentioned in docstring)
                for output_key in outputs:
                    # In real implementation, would call Variable.add_candidate()
                    # Here we simulate it
                    if output_key not in self.variables:
                        self.variables[output_key] = MockVariable(output_key)
                    self.variables[output_key].add_candidate(
                        f"proposal_for_{output_key}"
                    )

        template = ProposalTemplate()
        output_keys = [Key(), Key()]

        template.transform([], output_keys)

        # Check that candidates were added
        for output_key in output_keys:
            assert output_key in template.variables
            var = template.variables[output_key]
            assert len(var.candidates) == 1
            assert f"proposal_for_{output_key}" in var.candidates[0]


class TestMechanismTemplateIntegration:
    """Integration tests for MechanismTemplate usage patterns."""

    def test_template_with_dynamic_key_generation(self):
        """Test template that generates keys dynamically."""

        class DynamicKeyTemplate(MechanismTemplate):
            def __init__(self, prefix: str):
                self.prefix = prefix
                self.generated_keys = []

            def reads(self) -> Sequence[Key]:
                key = Key()
                self.generated_keys.append(key)
                return [key]

            def writes(self) -> Sequence[Key]:
                key = Key()
                self.generated_keys.append(key)
                return [key]

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                # Process with generated keys
                self.processed_inputs = len(inputs)
                self.processed_outputs = len(outputs)

        template1 = DynamicKeyTemplate("template1")
        template2 = DynamicKeyTemplate("template2")

        # Each template should generate its own keys
        reads1 = template1.reads()
        writes1 = template1.writes()

        reads2 = template2.reads()
        writes2 = template2.writes()

        # Keys should be different between templates
        assert reads1 != reads2
        assert writes1 != writes2

        # Test transform
        template1.transform([Key()], [Key(), Key()])
        assert template1.processed_inputs == 1
        assert template1.processed_outputs == 2

    def test_template_chaining_simulation(self):
        """Simulate chaining templates together."""

        class SourceTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return []

            def writes(self) -> Sequence[Key]:
                return [Key()]  # Output key

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                # Source generates data
                self.generated_data = "source_data"

        class ProcessorTemplate(MechanismTemplate):
            def __init__(self, source_key):
                self.source_key = source_key

            def reads(self) -> Sequence[Key]:
                return [self.source_key]  # Read from source

            def writes(self) -> Sequence[Key]:
                return [Key()]  # Output key

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                # Process data from source
                self.processed = f"processed_{len(inputs)}"

        class SinkTemplate(MechanismTemplate):
            def __init__(self, processor_key):
                self.processor_key = processor_key

            def reads(self) -> Sequence[Key]:
                return [self.processor_key]  # Read from processor

            def writes(self) -> Sequence[Key]:
                return []  # No outputs (sink)

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                # Consume data
                self.consumed = f"consumed_{len(inputs)}"

        # Create chain
        source = SourceTemplate()
        source_output_key = source.writes()[0]

        processor = ProcessorTemplate(source_output_key)
        processor_output_key = processor.writes()[0]

        sink = SinkTemplate(processor_output_key)

        # Execute chain (simplified - in reality would coordinate)
        source.transform([], [source_output_key])
        processor.transform([source_output_key], [processor_output_key])
        sink.transform([processor_output_key], [])

        assert source.generated_data == "source_data"
        assert processor.processed == "processed_1"
        assert sink.consumed == "consumed_1"


class TestMechanismTemplateEdgeCases:
    """Test edge cases and special scenarios."""

    def test_template_with_large_number_of_keys(self):
        """Test with a large number of keys."""

        class LargeTemplate(MechanismTemplate):
            def __init__(self, n_reads: int, n_writes: int):
                self.n_reads = n_reads
                self.n_writes = n_writes

            def reads(self) -> Sequence[Key]:
                return [Key() for _ in range(self.n_reads)]

            def writes(self) -> Sequence[Key]:
                return [Key() for _ in range(self.n_writes)]

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                self.input_count = len(inputs)
                self.output_count = len(outputs)

        # Test with various sizes
        for n_reads, n_writes in [(0, 0), (10, 5), (100, 50), (1, 100)]:
            template = LargeTemplate(n_reads, n_writes)

            reads = template.reads()
            writes = template.writes()

            assert len(reads) == n_reads
            assert len(writes) == n_writes

            # Test transform with matching number of inputs/outputs
            input_keys = [Key() for _ in range(n_reads)]
            output_keys = [Key() for _ in range(n_writes)]

            template.transform(input_keys, output_keys)
            assert template.input_count == n_reads
            assert template.output_count == n_writes

    def test_template_with_none_or_invalid_keys(self):
        """Test behavior with potentially invalid keys."""
        # This depends on Key() implementation
        # Assuming Key() always creates valid keys

        class SimpleTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return [Key()]

            def writes(self) -> Sequence[Key]:
                return [Key()]

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                # Should handle whatever keys are passed
                self.received_inputs = inputs
                self.received_outputs = outputs

        template = SimpleTemplate()

        # Pass keys that weren't declared (should still work)
        undeclared_key = Key()
        template.transform([undeclared_key], [undeclared_key])

        assert template.received_inputs == [undeclared_key]
        assert template.received_outputs == [undeclared_key]

    def test_template_inheritance_hierarchy(self):
        """Test template in an inheritance hierarchy."""

        class BaseTemplate(MechanismTemplate):
            def reads(self) -> Sequence[Key]:
                return [Key()]

            def writes(self) -> Sequence[Key]:
                return [Key()]

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                self.base_called = True

        class DerivedTemplate(BaseTemplate):
            def __init__(self, extra_param):
                self.extra_param = extra_param
                self.derived_called = False

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                super().transform(inputs, outputs)
                self.derived_called = True
                self.processed_param = self.extra_param.upper()

        template = DerivedTemplate("test")

        # Should have all methods
        assert len(template.reads()) == 1
        assert len(template.writes()) == 1

        # Execute transform
        template.transform([Key()], [Key()])

        assert template.base_called is True
        assert template.derived_called is True
        assert template.processed_param == "TEST"
        assert template.extra_param == "test"

    def test_template_as_factory_pattern(self):
        """Test using template as a factory for creating mechanisms."""
        # This is a conceptual test showing how MechanismTemplate
        # might be used to create Mechanism instances

        class MechanismFactoryTemplate(MechanismTemplate):
            def __init__(self):
                self.created_mechanisms = []

            def reads(self) -> Sequence[Key]:
                return [Key()]

            def writes(self) -> Sequence[Key]:
                return [Key(), Key()]

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                # In a real implementation, this might create Mechanism instances
                # based on the inputs and outputs
                self.last_inputs = inputs
                self.last_outputs = outputs

                # Simulate creating a mechanism
                mechanism_info = {
                    "inputs": inputs,
                    "outputs": outputs,
                    "timestamp": "2024-01-01",
                }
                self.created_mechanisms.append(mechanism_info)

        factory = MechanismFactoryTemplate()

        # Multiple transformations
        for i in range(3):
            input_keys = [Key() for _ in range(i + 1)]
            output_keys = [Key() for _ in range(i + 2)]

            factory.transform(input_keys, output_keys)

        assert len(factory.created_mechanisms) == 3
        assert len(factory.created_mechanisms[0]["inputs"]) == 1
        assert len(factory.created_mechanisms[2]["outputs"]) == 4


class TestMechanismTemplateDesignContract:
    """Test design contracts mentioned in docstrings."""

    def test_transform_should_not_commit_state_directly(self):
        """Test that transform() doesn't commit state (conceptual test)."""
        # This is a documentation/design test
        # We can't enforce it in tests, but we can document the intent

        class WellBehavedTemplate(MechanismTemplate):
            def __init__(self):
                self.proposals_made = []

            def reads(self) -> Sequence[Key]:
                return []

            def writes(self) -> Sequence[Key]:
                return []

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                # Well-behaved: only creates proposals, doesn't commit
                for output_key in outputs:
                    # Simulate creating a proposal without committing
                    proposal = {
                        "key": output_key,
                        "value": "proposed_value",
                        "method": "template_transform",
                    }
                    self.proposals_made.append(proposal)
                # Note: doesn't actually modify any variable state

        template = WellBehavedTemplate()
        output_keys = [Key(), Key()]

        template.transform([], output_keys)

        assert len(template.proposals_made) == 2
        assert template.proposals_made[0]["method"] == "template_transform"

    def test_reads_writes_declare_all_possible_keys(self):
        """Test that reads()/writes() declare all possible keys (conceptual)."""

        class DeclarativeTemplate(MechanismTemplate):
            def __init__(self):
                # Declare all keys that might be used
                self.all_read_keys = [Key(), Key()]
                self.all_write_keys = [Key()]

            def reads(self) -> Sequence[Key]:
                # Return all keys that COULD be read
                return list(self.all_read_keys)

            def writes(self) -> Sequence[Key]:
                # Return all keys that COULD be written
                return list(self.all_write_keys)

            def transform(self, inputs: list[Key], outputs: list[Key]) -> None:
                # Should only use keys from declared sets
                # (This would be enforced in a real system)
                self.used_inputs = [k for k in inputs if k in self.all_read_keys]
                self.used_outputs = [k for k in outputs if k in self.all_write_keys]

        template = DeclarativeTemplate()

        # Use subset of declared keys
        some_read_keys = [template.all_read_keys[0]]
        some_write_keys = [template.all_write_keys[0]]

        template.transform(some_read_keys, some_write_keys)

        assert template.used_inputs == some_read_keys
        assert template.used_outputs == some_write_keys


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
