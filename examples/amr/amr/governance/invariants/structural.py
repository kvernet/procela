"""Structural probe invariant for Procela PoC."""

from itertools import cycle

import numpy as np

from procela import (
    Executive,
    InvariantPhase,
    InvariantViolation,
    SystemInvariant,
    VariableRecord,
    VariableSnapshot,
)

from ...mechanisms.registry import FamilyRegistry
from ...variables import error_colonized, experiment_status
from .status import ExperimentStatus


class StructuralProbeInvariant(SystemInvariant):
    """
    Runs controlled experiments by isolating one family at a time.

    Measures each family's standalone predictive performance.
    """

    def __init__(
        self,
        executive: Executive,
        registry: FamilyRegistry,
        probe_interval: int = 30,
        probe_duration: int = 10,
        evaluation_window: int = 10,
    ) -> None:
        """Structural probe invariant constructor."""
        self.executive = executive
        self.registry = registry
        self.probe_interval = probe_interval
        self.probe_duration = probe_duration
        self.evaluation_window = evaluation_window

        self.state = "monitoring"
        self.family_cycle = cycle(self.registry.families.keys())
        self.next_probe = probe_interval
        self.current_probe_family = None
        self.probe_start_step: int | None = None
        self.pre_error: float | None = None
        self.experiment_status: ExperimentStatus | None = None

        def check_probe_complete(step: int) -> None:
            """Call after each step to manage probe lifecycle."""
            if self.state == "experimenting" and self.probe_start_step:
                # Check if probe is complete
                if step - self.probe_start_step >= self.probe_duration:
                    _end_probe(step)

        def _end_probe(step: int) -> None:
            """End the current probe and restore all families."""
            exp_error = _get_recent_error()

            self.executive.logger.info(
                f"Step {step}: Probe complete. "
                f"{self.current_probe_family} isolated error: {exp_error:.3f}"
            )

            if self.experiment_status:
                self.experiment_status.success = bool(
                    exp_error < self.pre_error if self.pre_error else False
                )

            # Restore all families
            for _, family in self.registry.families.items():
                family.enable()

            # Schedule next probe
            self.state = "monitoring"
            self.next_probe = step + self.probe_interval
            self.current_probe_family = None

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
            current_step = snapshot.step
            # Check if probe is complete
            check_probe_complete(current_step)

            if self.state == "monitoring" and current_step >= self.next_probe:
                return False  # Time for probe

            return True

        def handle_violation(
            violation: InvariantViolation, snapshot: VariableSnapshot
        ) -> None:
            """Handle violation."""
            step = snapshot.step
            self.current_probe_family = next(self.family_cycle)

            self.executive.logger.info(
                f"Step {step}: Starting structural probe of "
                f"{self.current_probe_family} family."
            )

            self.state = "experimenting"
            self.probe_start_step = step

            # Save experiment status
            self.experiment_status = ExperimentStatus(
                start_step=step,
                end_step=step,
                success=False,
            )

            # Record pre-experiment errors
            self.pre_error = _get_recent_error()

            # Disable all other families
            for name, family in self.registry.families.items():
                if name == self.current_probe_family:
                    family.enable()
                else:
                    family.disable()

        super().__init__(
            name="StructuralProbeInvariant",
            condition=check_condition,
            on_violation=handle_violation,
            phase=InvariantPhase.PRE,
            message="",
        )
