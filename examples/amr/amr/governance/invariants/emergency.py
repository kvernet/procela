"""No active families invariant for Procela PoC."""

from procela import (
    Executive,
    InvariantPhase,
    InvariantViolation,
    SystemInvariant,
    VariableSnapshot,
)

from ...mechanisms.registry import FamilyRegistry


class NoActiveFamiliesInvariant(SystemInvariant):
    """No active families invariant."""

    def __init__(
        self,
        executive: Executive,
        registry: FamilyRegistry,
    ) -> None:
        """No active families invariant constructor."""
        self.executive = executive
        self.registry = registry

        def check_condition(snapshot: VariableSnapshot) -> bool:
            """Check condition."""
            active_count = sum(
                1
                for f in self.registry.families.values()
                if any(m.is_enabled() for m in f.mechanisms)
            )
            return not (active_count == 0)

        def handle_violation(
            violation: InvariantViolation, snapshot: VariableSnapshot
        ) -> None:
            """Handle violation."""
            for family in self.registry.families.values():
                family.enable()
                self.executive.logger.warning(
                    f"Step {snapshot.step}:EMERGENCY: "
                    "No active families detected — restored all"
                )

        super().__init__(
            name="NoActiveFamiliesInvariant",
            condition=check_condition,
            on_violation=handle_violation,
            phase=InvariantPhase.POST,
            message="",
        )
