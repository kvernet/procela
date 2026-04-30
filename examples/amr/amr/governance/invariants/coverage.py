"""Coverage decay invariant for Procela PoC."""

import numpy as np

from procela import (
    Executive,
    InvariantPhase,
    InvariantViolation,
    SystemInvariant,
    VariableRecord,
    VariableSnapshot,
)

from ...mechanisms.family import MechanismFamily
from ...mechanisms.registry import FamilyRegistry
from ...variables import error_colonized, experiment_status
from .status import ExperimentStatus


class CoverageDecayInvariant(SystemInvariant):
    """
    Detects when a family's coverage falls below threshold.

    Temporarily disables the family to test if predictions improve.
    """

    def __init__(
        self,
        executive: Executive,
        registry: FamilyRegistry,
        coverage_threshold: float = 0.7,
        decay_duration: int = 5,
        experiment_duration: int = 10,
        evaluation_window: int = 10,
    ) -> None:
        """
        Coverage decay invariant constructor.

        Parameters
        ----------
        executive : Executive
            The executive.
        registry : FamilyRegistry
            The family registry.
        coverage_threshold : float
            The coverage threshold. Default is 0.7.
        decay_duration : float
            The decay duration. Default is 5.
        experiment_duration : int
            The experiment duration. Default is 10.
        evaluation_window : int
            The evaluation window. Default is 10.
        """
        self.executive = executive
        self.registry = registry
        self.coverage_threshold = coverage_threshold
        self.decay_duration = decay_duration
        self.experiment_duration = experiment_duration
        self.evaluation_window = evaluation_window

        self.state = "monitoring"
        self.decay_counts = {name: 0 for name in registry.families.keys()}
        self.decaying_family: MechanismFamily | None = None
        self.experiment_start_step: int | None = None
        self.pre_error: float | None = None
        self.experiment_status: ExperimentStatus | None = None

        def _check_experiment(step: int) -> None:
            """
            Call after each step to manage experiment lifecycle.

            Parameters
            ----------
            step : int
                The current simulation step.
            """
            if self.state == "experimenting" and self.experiment_start_step is not None:
                if step - self.experiment_start_step >= self.experiment_duration:
                    _evaluate_experiment(step)

        def _evaluate_experiment(step: int) -> None:
            """
            Compare performance during experiment vs baseline.

            Parameters
            ----------
            step : int
                The current simulation step.
            """
            exp_error = _get_recent_error()

            if self.pre_error and exp_error < self.pre_error:
                if self.decaying_family:
                    self.executive.logger.info(
                        f"Step {step}: Experiment SUCCESSFUL. Keeping "
                        f"{self.decaying_family.name} disabled."
                        f"\n\texp. mean error ({exp_error:.3f}) < "
                        f"pre mean error: ({self.pre_error:.3f})"
                    )
                if self.experiment_status:
                    self.experiment_status.success = True
            else:
                if self.decaying_family:
                    self.executive.logger.info(
                        f"Step {step}: Experiment FAILED. Restoring "
                        f"{self.decaying_family.name}."
                        f"\n\texp. mean error ({exp_error:.3f}) >= "
                        f"pre mean error: ({self.pre_error:.3f})"
                    )
                    self.decaying_family.enable()
                if self.experiment_status:
                    self.experiment_status.success = False

            self.state = "monitoring"

            # Save experiment status
            if self.experiment_status:
                self.experiment_status.end = step
            metadata = {}
            if self.experiment_status:
                metadata = {
                    "start": self.experiment_status.start,
                    "end": self.experiment_status.end,
                    "success": self.experiment_status.success,
                }
            experiment_status.set(
                VariableRecord(value=0.0, confidence=1.0, metadata=metadata)
            )

        def _get_recent_error() -> float:
            """
            Get mean of the recent prediction errors.

            Returns
            -------
            float
                The reccent error.
            """
            errors = [
                c.value
                for _, c, _, _ in error_colonized.recent(self.evaluation_window)
                if c is not None and c.value is not None
            ]

            return float(np.mean(errors))

        def check_condition(snapshot: VariableSnapshot) -> bool:
            """
            Check condition.

            Parameters
            ----------
            snapshot : VariableSnapshot
                The variable snapshot.

            Returns
            -------
            bool
                Whether violation occured or not.
            """
            # Check the experiment lifecycle
            _check_experiment(snapshot.step)

            if self.state != "monitoring":
                return True

            # Check each family's coverage
            for name, family in self.registry.families.items():
                cov = family.coverage.value
                if cov is None:
                    continue

                if cov < self.coverage_threshold:
                    self.decay_counts[name] += 1
                    if self.decay_counts[name] >= self.decay_duration:
                        self.decaying_family = family
                        return False  # Violation
                else:
                    self.decay_counts[name] = 0

            return True

        def handle_violation(
            violation: InvariantViolation, snapshot: VariableSnapshot
        ) -> None:
            """
            Handle violation.

            Parameters
            ----------
            violation : InvariantViolation
                The invariant violation.
            snapshot : VariableSnapshot
                The variable snapshot.
            """
            step = snapshot.step
            if self.decaying_family:
                self.executive.logger.info(
                    f"Step {step}: Coverage decay detected for "
                    f"{self.decaying_family.name}. Starting experiment."
                )

            self.state = "experimenting"
            self.experiment_start_step = step

            # Save experiment status
            self.experiment_status = ExperimentStatus(
                start_step=step,
                end_step=step,
                success=False,
            )

            # Record pre-experiment mean error
            self.pre_error = _get_recent_error()

            # Disable the decaying family
            if self.decaying_family:
                self.decaying_family.disable()

        super().__init__(
            name="CoverageDecayInvariant",
            condition=check_condition,
            on_violation=handle_violation,
            phase=InvariantPhase.POST,
            message="",
        )
