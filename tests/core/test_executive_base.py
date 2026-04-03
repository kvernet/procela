"""Minimal pytest suite for Executive class with 100% coverage."""

from unittest.mock import Mock, create_autospec

import numpy as np
import pytest

from procela.core.exceptions import ExecutionError
from procela.core.executive import Executive
from procela.core.invariant import (
    InvariantCategory,
    InvariantPhase,
    InvariantSeverity,
    InvariantViolation,
    InvariantViolationCritical,
    InvariantViolationFatal,
    InvariantViolationInfo,
    InvariantViolationWarning,
    SystemInvariant,
    VariableSnapshot,
)
from procela.core.logger import setup_logging
from procela.core.mechanism import Mechanism
from procela.core.memory import VariableRecord
from procela.core.policy import HighestConfidencePolicy, WeightedConfidencePolicy
from procela.core.process import Process
from procela.core.variable import RangeDomain, Variable
from procela.symbols.key import Key


class TestExecutive:
    """Test suite for the Executive class."""

    def test_initialization(self):
        """Test Executive.__init__ with default and custom parameters."""
        # Test with defaults
        exec_default = Executive()
        assert exec_default._processes == []
        assert exec_default._mechanisms == []
        assert exec_default._prepared is True

        # Test with provided processes and mechanisms
        mock_process = create_autospec(Process)
        mock_mechanism = create_autospec(Mechanism)
        exec_with_args = Executive(
            processes=[mock_process], mechanisms=[mock_mechanism]
        )
        assert exec_with_args._processes == [mock_process]
        assert exec_with_args._mechanisms == [mock_mechanism]
        assert exec_with_args._prepared is True

    def test_add_and_remove_process(self):
        """Test add_process and remove_process methods."""
        executive = Executive()
        mock_process = create_autospec(Process)

        # Test add_process
        executive.add_process(mock_process)
        assert mock_process in executive._processes
        assert executive._prepared is True

        # Test remove_process
        executive.remove_process(mock_process)
        assert mock_process not in executive._processes
        assert executive._prepared is True

    def test_add_and_remove_mechanism(self):
        """Test add_mechanism and remove_mechanism methods."""
        executive = Executive()
        mock_mechanism = create_autospec(Mechanism)

        # Test add_mechanism
        executive.add_mechanism(mock_mechanism)
        assert mock_mechanism in executive._mechanisms
        assert executive._prepared is True

        # Test remove_mechanism
        executive.remove_mechanism(mock_mechanism)
        assert mock_mechanism not in executive._mechanisms
        assert executive._prepared is True

    def test_set_logger(self):
        """Test set logger."""
        executive = Executive()
        logger = setup_logging(
            name="procela",
            console=False,
        )
        executive.set_logger(logger)
        assert executive.logger == logger

    def test_prepare_method(self):
        """Test the prepare method collects variables correctly."""
        # Create mocks
        mock_process = create_autospec(Process)
        mock_mechanism = create_autospec(Mechanism)
        mock_var1 = create_autospec(Variable)
        mock_var2 = create_autospec(Variable)
        mock_var3 = create_autospec(Variable)

        # Configure mocks
        mock_process.writable.return_value = [mock_var1]
        mock_process.variables.return_value = [mock_var1, mock_var2]
        mock_mechanism.writes.return_value = [mock_var2]
        mock_mechanism.reads.return_value = [mock_var3]

        # Create executive and test
        executive = Executive(processes=[mock_process], mechanisms=[mock_mechanism])

        executive._prepared = False
        executive._writable = {mock_var3}
        executive._variables = {mock_var3}

        executive.prepare()

        assert executive._prepared is True
        assert executive._writable == {mock_var1, mock_var2}
        assert executive._variables == {mock_var1, mock_var2, mock_var3}

    def test_step_method_normal_flow(self):
        """Test the step method with normal execution flow."""
        # Create comprehensive mocks
        mock_process = create_autospec(Process)
        mock_mechanism = create_autospec(Mechanism)
        mock_variable = create_autospec(Variable)
        mock_key = create_autospec(Key)
        mock_record = Mock()

        # Configure mocks
        mock_variable.key.return_value = mock_key
        mock_variable.resolve_conflict.return_value = (mock_record, [mock_record])
        mock_record.source = mock_key

        # Create executive
        executive = Executive(processes=[mock_process], mechanisms=[mock_mechanism])
        executive._writable = {mock_variable}
        executive._step_index = 0

        # Execute step
        executive.step()

        # Verify calls
        mock_process.step.assert_called_once()
        mock_mechanism.run.assert_called_once()
        mock_variable.resolve_conflict.assert_called_once()
        mock_variable.commit.assert_called_once_with()
        mock_variable.clear_hypotheses.assert_called_once()

        # Verify trace was updated
        assert executive._step_index == 1

    def test_step_method_no_candidates(self):
        """Test step method when variables have no candidates."""
        # Create mocks
        mock_process = create_autospec(Process)
        mock_mechanism = create_autospec(Mechanism)
        mock_variable = create_autospec(Variable)

        # Create executive
        executive = Executive(processes=[mock_process], mechanisms=[mock_mechanism])
        executive._writable = {mock_variable}

        # Execute step
        executive.step()

        # Verify variable wasn't resolved
        mock_variable.resolve_conflict.assert_called()

    def test_step_method_not_prepared(self):
        """Test step method when not prepared."""
        executive = Executive()
        executive._prepared = False

        with pytest.raises(ExecutionError, match="Executive must be prepared"):
            executive.step()

    def test_step_method_invalid_variable(self):
        """Test step method handles non-Variable in writable set."""
        # Create executive with non-Variable in writable
        executive = Executive(processes=[], mechanisms=[])
        executive._writable = {None}  # Invalid value

        with pytest.raises(
            TypeError, match="Expected `Variable`, got <class 'NoneType'>"
        ):
            executive.step()

        executive._writable = {Key()}  # Invalid value

        # Should raise error
        with pytest.raises(
            TypeError,
            match="Expected `Variable`, got <class 'procela.symbols.key.Key'>",
        ):
            executive.step()

    def test_run_method(self):
        """Test the run method with all phases."""
        # Create executive with mock invariant
        executive = Executive()

        # Mock invariant that passes check
        mock_invariant = create_autospec(SystemInvariant)
        mock_invariant.phase = InvariantPhase.PRE
        executive._invariants = [mock_invariant]

        # Mock step to count calls
        step_count = 0
        original_step = executive.step

        def mock_step():
            nonlocal step_count
            step_count += 1

        executive.step = mock_step

        # Mock _check_invariants to track calls
        check_calls = []
        original_check = executive._check_invariants

        def mock_check(phase):
            check_calls.append(phase)

        executive._check_invariants = mock_check

        # Test run with callback
        callback_calls = []

        def pre_step(exec, i):
            callback_calls.append((exec, i))

        def post_step(exec, i):
            pass

        executive.run(steps=3, pre_step=pre_step, post_step=post_step)

        # Verify results
        assert step_count == 3
        assert len(check_calls) == 0
        assert len(callback_calls) == 3
        for i, (exec, step_num) in enumerate(callback_calls):
            assert exec is executive
            assert step_num == i

        # Restore original methods
        executive.step = original_step
        executive._check_invariants = original_check

    def test_run_method_not_prepared(self):
        """Test run method raises error when not prepared."""
        executive = Executive()
        executive._prepared = False

        with pytest.raises(ExecutionError, match="Executive must be prepared"):
            executive.run(steps=1)

    def test_key_method(self):
        """Test the key method returns correct key."""
        executive = Executive()
        key = executive.key()

        assert isinstance(key, Key)
        assert key == executive._key

    def test_processes_method(self):
        """Test processes method returns correct sequence."""
        mock_process = create_autospec(Process)
        executive = Executive(processes=[mock_process])

        processes = executive.processes()
        assert processes == [mock_process]

    def test_mechanisms_method(self):
        """Test mechanisms method returns correct sequence."""
        mock_mechanism = create_autospec(Mechanism)
        executive = Executive(mechanisms=[mock_mechanism])

        mechanisms = executive.mechanisms()
        assert mechanisms == [mock_mechanism]

    def test_writable_method(self):
        """Test writable method returns correct set."""
        mock_variable = create_autospec(Variable)
        executive = Executive()
        executive._writable = {mock_variable}

        writable = executive.writable()
        assert writable == {mock_variable}

    def test_variables_method(self):
        """Test variables method returns correct set."""
        mock_variable = create_autospec(Variable)
        executive = Executive()
        executive._variables = {mock_variable}

        variables = executive.variables()
        assert variables == {mock_variable}

    def test_reset_method(self):
        """Test reset method resets all variables."""
        # Create mock variables
        mock_var1 = create_autospec(Variable)
        mock_var2 = create_autospec(Variable)

        # Create executive with variables
        executive = Executive()
        executive._variables = {mock_var1, mock_var2}
        executive._step_index = 5

        # Execute reset
        executive.reset()

        # Verify all variables were reset
        mock_var1.reset.assert_called_once()
        mock_var2.reset.assert_called_once()
        assert executive._step_index == 0

    def test_snapshot_method(self):
        """Test snapshot method creates VariableSnapshot."""
        # Create mock variable with epistemic view
        mock_variable = create_autospec(Variable)
        mock_view = Mock()
        mock_variable.epistemic.return_value = mock_view

        # Create executive
        executive = Executive()
        executive._variables = {mock_variable}

        # Get snapshot
        snapshot = executive.snapshot()

        # Verify snapshot was created
        assert isinstance(snapshot, VariableSnapshot)
        mock_variable.epistemic.assert_called_once()

    def test_add_invariant_method(self):
        """Test add_invariant method."""
        executive = Executive()
        mock_invariant = create_autospec(SystemInvariant)

        executive.add_invariant(mock_invariant)

        assert executive._invariants == [mock_invariant]

    def test_remove_invariant_method(self):
        """Test remove_invariant method."""
        executive = Executive()
        mock_invariant = create_autospec(SystemInvariant)

        executive.add_invariant(mock_invariant)

        executive.remove_invariant(mock_invariant)
        executive.step()

        assert executive._invariants == []

    def test_safe_mode_method(self):
        """Test safe_mode method (currently not implemented)."""
        executive = Executive()
        mock_invariant = create_autospec(SystemInvariant)

        # Should not raise (method exists but doesn't do anything)
        executive.safe_mode(mock_invariant)

    def test_abort_method(self):
        """Test abort method raises InvariantViolationFatal."""
        executive = Executive()

        # Create invariant with required attributes
        mock_invariant = Mock(spec=SystemInvariant)
        mock_invariant.name = "TestViolation"
        mock_invariant.message = "Test message"
        mock_invariant.category = InvariantCategory.CONSISTENCY
        mock_invariant.phase = InvariantPhase.RUNTIME

        # Verify abort raises the expected exception
        with pytest.raises(InvariantViolationFatal) as exc_info:
            executive.abort(mock_invariant)

        assert exc_info.value.name == "TestViolation"

    def test_check_invariants_method(self):
        """Test _check_invariants method with different violation types."""
        # Test 1: No invariants
        executive = Executive()
        executive._check_invariants(InvariantPhase.PRE)
        # Should return without error

        # Test 2: Invariant with different phase (should be skipped)
        executive = Executive()
        mock_invariant = create_autospec(SystemInvariant)
        mock_invariant.phase = InvariantPhase.POST  # Different from PRE
        executive._invariants = [mock_invariant]

        executive._check_invariants(InvariantPhase.PRE)
        mock_invariant.check.assert_not_called()

        # Test 3: InvariantViolationInfo (should be caught and ignored)
        executive = Executive()
        mock_invariant = create_autospec(SystemInvariant)
        mock_invariant.phase = InvariantPhase.RUNTIME
        mock_invariant.check.side_effect = InvariantViolationInfo(
            "Test", "Info", category=Mock(), phase=InvariantPhase.RUNTIME
        )
        executive._invariants = [mock_invariant]

        executive._check_invariants(InvariantPhase.RUNTIME)

        executive = Executive()
        mock_invariant = create_autospec(SystemInvariant)
        mock_invariant.phase = InvariantPhase.RUNTIME
        mock_invariant.check.side_effect = InvariantViolationWarning(
            "Test", "Warning", category=Mock(), phase=InvariantPhase.RUNTIME
        )
        executive._invariants = [mock_invariant]

        executive._check_invariants(InvariantPhase.RUNTIME)
        # Should not raise

        # Test 5: InvariantViolationCritical (should call safe_mode)
        executive = Executive()
        mock_invariant = create_autospec(SystemInvariant)
        mock_invariant.phase = InvariantPhase.RUNTIME
        mock_invariant.check.side_effect = InvariantViolationCritical(
            "Test", "Critical", category=Mock(), phase=InvariantPhase.RUNTIME
        )
        executive._invariants = [mock_invariant]

        # Mock safe_mode to track calls
        safe_mode_called = []
        original_safe_mode = executive.safe_mode
        executive.safe_mode = lambda inv: safe_mode_called.append(inv)

        executive._check_invariants(InvariantPhase.RUNTIME)
        assert len(safe_mode_called) == 1
        assert safe_mode_called[0] is mock_invariant

        executive.safe_mode = original_safe_mode

        # Test 6: InvariantViolationFatal (should call abort)
        executive = Executive()
        mock_invariant = create_autospec(SystemInvariant)
        mock_invariant.phase = InvariantPhase.RUNTIME
        mock_invariant.check.side_effect = InvariantViolationFatal(
            "Test", "Fatal", category=Mock(), phase=InvariantPhase.RUNTIME
        )
        executive._invariants = [mock_invariant]

        # Mock abort to track calls
        abort_called = []
        original_abort = executive.abort
        executive.abort = lambda inv: abort_called.append(inv)

        executive._check_invariants(InvariantPhase.RUNTIME)
        assert len(abort_called) == 1
        assert abort_called[0] is mock_invariant

        executive.abort = original_abort

    def test_check_invariants_generic_exception(self):
        """Test _check_invariants with generic InvariantViolation."""
        executive = Executive()
        mock_invariant = create_autospec(SystemInvariant)
        mock_invariant.phase = InvariantPhase.RUNTIME
        mock_invariant.name = "Test"
        mock_invariant.message = "Generic violation"
        mock_invariant.category = InvariantCategory.CONSISTENCY
        mock_invariant.severity = InvariantSeverity.CRITICAL

        # Create a generic InvariantViolation (not one of the specific subclasses)
        generic_violation = InvariantViolation(
            name="Test",
            message="Generic violation",
            category=InvariantCategory.CONSISTENCY,
            severity=InvariantSeverity.CRITICAL,
            phase=InvariantPhase.RUNTIME,
        )
        mock_invariant.check.side_effect = generic_violation

        executive._invariants = [mock_invariant]

        # Should re-raise the generic InvariantViolation
        with pytest.raises(InvariantViolation) as exc_info:
            executive._check_invariants(InvariantPhase.RUNTIME)

        assert exc_info.value.severity is InvariantSeverity.CRITICAL

    def test_check_invariants_other_exception(self):
        """Test _check_invariants with non-InvariantViolation exception."""
        executive = Executive()
        mock_invariant = create_autospec(SystemInvariant)
        mock_invariant.phase = InvariantPhase.RUNTIME
        mock_invariant.check.side_effect = ValueError("Some other error")

        executive._invariants = [mock_invariant]

        # Should re-raise as generic Exception
        with pytest.raises(ExecutionError):
            executive._check_invariants(InvariantPhase.RUNTIME)

    def test_random_generation(self):
        "Test random generation"
        rng = np.random.default_rng(42)
        exec = Executive()
        exec.set_rng(rng=rng)
        assert exec.step_index() == 0
        assert abs(exec.random() - 0.773956048) < 1e-6

    def test_get_and_set_rng_state(self):
        """Test get and set rng_state."""
        import random

        for rng in [None, np.random.default_rng(), random.Random()]:
            exec = Executive(rng=rng)

            state = exec.get_rng_state()
            u = exec.random()

            for _ in range(37):
                exec.random()

            exec.set_rng_state(state)

            assert exec.random() == u

    def test_create_and_restore_checkpoint(self):
        """Test create and restore checkpoint."""
        X = Variable("X", RangeDomain(0, 100), policy=WeightedConfidencePolicy())

        class MyMechanism(Mechanism):
            def __init__(
                self,
                executive: Executive,
                name: str,
                value: float = 0,
                delta: float = 0.05,
            ):
                super().__init__(reads=[X], writes=[X])
                self.executive = executive
                self.name = name
                self.value = value
                self.delta = delta

            def transform(self):
                self.writes()[0].add_hypothesis(
                    VariableRecord(value=self.value, confidence=self.executive.random())
                )
                self.value += self.delta

            def create_checkpoint(self):
                print(f"Mechanism {self.name} has created a checkpoint.")
                return self.value

            def restore_checkpoint(self, checkpoint):
                print(f"Mechanism {self.name} has restored a checkpoint.")
                self.value = checkpoint

        import numpy

        rng = numpy.random.default_rng(1)
        executive = Executive(rng=rng)
        mechanisms = [
            MyMechanism(executive=executive, name="Mech1", value=0.0, delta=0.05),
            MyMechanism(executive=executive, name="Mech2", value=1.0, delta=-0.05),
            MyMechanism(executive=executive, name="Mech3", value=2.0, delta=0.01),
        ]
        for mech in mechanisms:
            executive.add_mechanism(mech)

        class MyInvariant(SystemInvariant):
            def __init__(self) -> None:
                self.threshold = 0.5

                def check(snapshot: VariableSnapshot) -> bool:
                    return False  # Always violated to force event

                def handle(
                    invariant: InvariantViolation, snapshot: VariableSnapshot
                ) -> None:
                    self.threshold *= 0.95

                super().__init__(
                    "MyInvariant",
                    condition=check,
                    on_violation=handle,
                    phase=InvariantPhase.RUNTIME,
                    message="",
                )

            def create_checkpoint(self):
                return 0.5

            def restore_checkpoint(self, checkpoint):
                self.threshold = checkpoint

        executive.add_invariant(MyInvariant())

        def pre_step(executive: Executive, step: int):
            if step == 20:
                checkpoint = executive.create_checkpoint()

                # Run experiment
                X.policy = HighestConfidencePolicy()
                executive.run_experiment(steps=15)

                # Experiment failed
                executive.restore_checkpoint(checkpoint)

        executive.run(steps=100, pre_step=pre_step)

        assert X.stats.count == 100
        assert abs(executive._invariants[0].threshold - 0.5 * 0.95**79) < 1e-3
