"""
Task module for the Procela framework.

This module defines the ReasoningTask enumeration, which categorizes the
different types of intelligent reasoning operations that active variables
in Procela can perform. Each task represents a distinct cognitive capability
within the framework's mechanistic modeling and active reasoning engine.
"""

from __future__ import annotations

from enum import Enum, auto


class ReasoningTask(Enum):
    """
    Enumeration of reasoning capabilities for active intelligent variables.

    In Procela, variables are not passive data containers but active reasoning
    entities. Each variable can perform multiple reasoning tasks to understand
    its state, predict future behavior, diagnose causes, and propose actions, etc.
    These tasks form the core cognitive repertoire of the framework's
    decentralized intelligence.

    The tasks are organized into several conceptual groups:

    1. **Monitoring & Detection Tasks**: ANOMALY_DETECTION, CONSTRAINT_CHECKING
    2. **Analytical Tasks**: TREND_ANALYSIS, PATTERN_RECOGNITION, SENSITIVITY_ANALYSIS
    3. **Predictive Tasks**: VALUE_PREDICTION, UNCERTAINTY_QUANTIFICATION
    4. **Decision & Action Tasks**: ACTION_PROPOSAL, CONFLICT_RESOLUTION,
                                    INTERVENTION_PLANNING
    5. **Diagnostic Tasks**: CAUSAL_DIAGNOSIS

    Each task corresponds to a specific type of reasoning that variables
    can perform, contributing to the system's overall ability to
    model, simulate, and optimize real-world processes with guaranteed
    feedback-loop consistency.

    Attributes
    ----------
    ANOMALY_DETECTION : ReasoningTask
        Identifies deviations from expected behavior or statistical norms.
        Example use: Detecting sensor malfunctions or unexpected state changes.

    CONFLICT_RESOLUTION : ReasoningTask
        Resolves contradictions between competing producers, proposals,
        or system goals. Example use: Choosing between conflicting values
        proposed by different mechanisms.

    ACTION_PROPOSAL : ReasoningTask
        Generates suggested actions to achieve system objectives or
        correct identified issues. Example use: Proposing parameter
        adjustments to maintain system stability.

    VALUE_PREDICTION : ReasoningTask
        Forecasts future values based on current state and historical trends.
        Example use: Predicting temperature evolution in a thermal system.

    CAUSAL_DIAGNOSIS : ReasoningTask
        Identifies root causes of observed effects or system behaviors.
        Example use: Determining why a pressure reading is outside
        acceptable bounds.

    UNCERTAINTY_QUANTIFICATION : ReasoningTask
        Assesses and quantifies the uncertainty associated with predictions,
        measurements, or model parameters. Example use: Estimating confidence
        intervals for forecasted values.

    CONSTRAINT_CHECKING : ReasoningTask
        Verifies that system states and proposed actions satisfy all
        operational constraints. Example use: Ensuring proposed control
        actions don't violate safety limits.

    TREND_ANALYSIS : ReasoningTask
        Analyzes temporal patterns and directional changes in system variables.
        Example use: Identifying accelerating degradation in equipment
        performance.

    PATTERN_RECOGNITION : ReasoningTask
        Identifies recurring structures or sequences in system behavior.
        Example use: Recognizing cyclic load patterns in energy systems.

    SENSITIVITY_ANALYSIS : ReasoningTask
        Evaluates how changes in inputs or parameters affect system outputs.
        Example use: Determining which control parameters have the greatest
        impact on system stability.

    INTERVENTION_PLANNING : ReasoningTask
        Develops coordinated sequences of actions to achieve complex objectives.
        Example use: Creating a multi-step maintenance procedure to address
        identified system issues.

    Examples
    --------
    >>> from procela.core.reasoning import ReasoningTask
    >>> # Accessing task values
    >>> task = ReasoningTask.ANOMALY_DETECTION
    >>> task.name
    'ANOMALY_DETECTION'
    >>> task.value  # auto() generates automatic values
    1
    >>> # Iterating through all tasks
    >>> for task in ReasoningTask:
    ...     print(f"{task.name}: {task.value}")
    ANOMALY_DETECTION: 1
    CONSTRAINT_CHECKING: 2
    TREND_ANALYSIS: 3
    # ... etc.
    >>> # Membership testing
    >>> "ANOMALY_DETECTION" in ReasoningTask.__members__
    True
    >>> ReasoningTask.CONSTRAINT_CHECKING in ReasoningTask
    True
    """

    # Monitoring & Detection Tasks
    ANOMALY_DETECTION = auto()
    CONSTRAINT_CHECKING = auto()

    # Analytical Tasks
    TREND_ANALYSIS = auto()
    PATTERN_RECOGNITION = auto()
    SENSITIVITY_ANALYSIS = auto()

    # Predictive Tasks
    VALUE_PREDICTION = auto()
    UNCERTAINTY_QUANTIFICATION = auto()

    # Decision & Action Tasks
    ACTION_PROPOSAL = auto()
    CONFLICT_RESOLUTION = auto()
    INTERVENTION_PLANNING = auto()

    # Diagnostic Tasks
    CAUSAL_DIAGNOSIS = auto()

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the reasoning task.

        Overrides the default Enum string representation to provide more
        readable output, converting the enum name to a more natural format.

        Returns
        -------
        str
            A formatted string representation of the task with underscores
            replaced by spaces and proper capitalization.

        Examples
        --------
        >>> task = ReasoningTask.ANOMALY_DETECTION
        >>> str(task)
        'Anomaly Detection'
        >>> task = ReasoningTask.CAUSAL_DIAGNOSIS
        >>> str(task)
        'Causal Diagnosis'
        """
        # Convert from UPPER_CASE to Title Case With Spaces
        return self.name.replace("_", " ").title()

    def description(self) -> str:
        """
        Return a detailed description of what this reasoning task entails.

        Provides human-readable explanations of each reasoning task's purpose
        and typical applications within the Procela framework.

        Returns
        -------
        str
            A descriptive explanation of the reasoning task.

        Examples
        --------
        >>> task = ReasoningTask.ANOMALY_DETECTION
        >>> task.description()
        'Identifies deviations from expected behavior or statistical norms.'
        """
        return _DESCRIPTIONS[self]


_DESCRIPTIONS = {
    ReasoningTask.ANOMALY_DETECTION: (
        "Identifies deviations from expected behavior or statistical norms."
    ),
    ReasoningTask.CONFLICT_RESOLUTION: (
        "Resolves contradictions between competing constraints or proposals."
    ),
    ReasoningTask.ACTION_PROPOSAL: (
        "Generates suggested actions to achieve system objectives."
    ),
    ReasoningTask.VALUE_PREDICTION: (
        "Forecasts future values based on current state and historical trends."
    ),
    ReasoningTask.CAUSAL_DIAGNOSIS: (
        "Identifies root causes of observed effects or system behaviors."
    ),
    ReasoningTask.UNCERTAINTY_QUANTIFICATION: (
        "Assesses and quantifies uncertainty in predictions and measurements."
    ),
    ReasoningTask.CONSTRAINT_CHECKING: (
        "Verifies that system states satisfy all operational constraints."
    ),
    ReasoningTask.TREND_ANALYSIS: (
        "Analyzes temporal patterns and directional changes in variables."
    ),
    ReasoningTask.PATTERN_RECOGNITION: (
        "Identifies recurring structures or sequences in system behavior."
    ),
    ReasoningTask.SENSITIVITY_ANALYSIS: (
        "Evaluates how changes in inputs affect system outputs."
    ),
    ReasoningTask.INTERVENTION_PLANNING: (
        "Develops coordinated sequences of actions to achieve complex objectives."
    ),
}
