"""Experiment status for Procela PoC."""


class ExperimentStatus:
    """Experiment status."""

    def __init__(self, start_step: int, end_step: int, success: bool = False) -> None:
        """
        Experiment status constructor.

        Parameters
        ----------
        start_step : int
            The start step.
        end_step : int
            The end step.
        success : bool
            Whether the experiment succeeds or fails. Default is False.
        """
        self.start = start_step
        self.end = end_step
        self.success = success
