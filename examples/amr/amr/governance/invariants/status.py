"""Experiment status for Procela PoC."""


class ExperimentStatus:
    """Experiment status."""

    def __init__(self, start_step: int, end_step: int, success: bool = False) -> None:
        """Experiment status constructor."""
        self.start = start_step
        self.end = end_step
        self.success = success
