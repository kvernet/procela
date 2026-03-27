"""Policy fragility invariant for Procela PoC."""

import numpy as np

from procela import (
    Executive,
    HighestConfidencePolicy,
    InvariantPhase,
    InvariantViolation,
    SystemInvariant,
    VariableRecord,
    VariableSnapshot,
)

from ...mechanisms.registry import FamilyRegistry
from ...variables import (
    error_colonized,
    experiment_status,
    intervention_code,
)
from .status import ExperimentStatus


class PolicyFragilityInvariant(SystemInvariant):
    """
    Detects high disagreement in intervention recommendations.

    This invariant runs experiments to test whether policy switching improves outcomes.

    States:
    - monitoring: watching for fragility
    - experimenting: trying new policy
    """

    def __init__(
        self,
        executive: Executive,
        registry: FamilyRegistry,
        fragility_threshold: float = 1.0,
        error_threshold: float = 0.6,
        experiment_duration: int = 10,
        evaluation_window: int = 10,
    ) -> None:
        """Policy fragility invariant constructor."""
        self.executive = executive
        self.registry = registry
        self.fragility_threshold = fragility_threshold
        self.error_threshold = error_threshold
        self.experiment_duration = experiment_duration
        self.evaluation_window = evaluation_window

        self.pre_experiment_policy = intervention_code.policy
        self.state = "monitoring"
        self.experiment_start_step: int | None = None
        self.pre_error: float | None = None
        self.experiment_status: ExperimentStatus | None = None

        def _check_experiment(step: int) -> None:
            """Call after each step to manage experiment lifecycle."""
            if self.state == "experimenting" and self.experiment_start_step:
                if step - self.experiment_start_step >= self.experiment_duration:
                    _evaluate_experiment(step)

        def _evaluate_experiment(step: int) -> None:
            """Compare performance during experiment vs baseline."""
            exp_error = _get_recent_error()

            if self.pre_error and exp_error < self.pre_error:
                self.executive.logger.info(
                    f"Step {step}: Experiment SUCCESSFUL. Keeping new policy."
                    f"\n\texp. mean error ({exp_error:.3f}) < "
                    f"pre. mean error: ({self.pre_error:.3f})"
                )
                if self.experiment_status:
                    self.experiment_status.success = True
            else:
                self.executive.logger.info(
                    f"Step {step}: Experiment FAILED. Restoring previous policy."
                    f"\n\texp. mean error ({exp_error:.3f}) >= "
                    f"pre mean error: ({self.pre_error:.3f})"
                )
                intervention_code.policy = self.pre_experiment_policy
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
                VariableRecord(
                    value=0.0,
                    confidence=1.0,
                    metadata=metadata,
                )
            )

        def _get_recent_error() -> float:
            """Get mean of the recent prediction errors."""
            errors = [
                c.value
                for _, c, _ in error_colonized.recent(self.evaluation_window)
                if c is not None and c.value is not None
            ]

            return float(np.mean(errors))

        def check_condition(snapshot: VariableSnapshot) -> bool:
            """Check condition."""
            # Check the experiment lifecycle
            _check_experiment(snapshot.step)

            if self.state != "monitoring":
                return True  # Already experimenting, don't trigger again

            # Policy distance as fragility metric
            fragility = registry.policy_fragility.value

            # Reccent error
            recent_error = error_colonized.value

            if fragility is None or recent_error is None:
                return True

            # Trigger when both thresholds exceeded
            return not (
                fragility > self.fragility_threshold
                and recent_error > self.error_threshold
            )

        def handle_violation(
            violation: InvariantViolation, snapshot: VariableSnapshot
        ) -> None:
            """Handle violation."""
            step = snapshot.step

            if self.state == "monitoring":
                self.executive.logger.info(
                    f"Step {step}: High fragility detected. Starting experiment."
                )
                self.state = "experimenting"
                self.experiment_start_step = step

                # Save experiment status
                self.experiment_status = ExperimentStatus(
                    start_step=step,
                    end_step=step,
                    success=False,
                )

                # Record pre-experiment errors
                self.pre_error = _get_recent_error()

                # Switch policy
                intervention_code.policy = HighestConfidencePolicy()

        super().__init__(
            name="PolicyFragilityInvariant",
            condition=check_condition,
            on_violation=handle_violation,
            phase=InvariantPhase.RUNTIME,
            message="",
        )
