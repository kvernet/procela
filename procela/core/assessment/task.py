"""
Enumeration of reasoning tasks.

Defines the canonical reasoning tasks used by Procela's assessment
framework, including monitoring, analytical, predictive, diagnostic,
and decision/action tasks.

Examples
--------
>>> from procela import ReasoningTask
>>>
>>> print(ReasoningTask.ANOMALY_DETECTION)
Anomaly Detection
>>> for task in ReasoningTask:
...     print(task.name, task.value)
NONE 1
ANOMALY_DETECTION 2
CONSTRAINT_CHECKING 3
TREND_ANALYSIS 4
PATTERN_RECOGNITION 5
SENSITIVITY_ANALYSIS 6
VALUE_PREDICTION 7
UNCERTAINTY_QUANTIFICATION 8
ACTION_PROPOSAL 9
CONFLICT_RESOLUTION 10
INTERVENTION_PLANNING 11
CAUSAL_DIAGNOSIS 12

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/assessment/task.html

Examples Reference
------------------
https://procela.org/docs/examples/core/assessment/task.html
"""

from __future__ import annotations

from enum import Enum, auto


class ReasoningTask(Enum):
    """
    Canonical reasoning tasks in the Procela framework.

    Each enum member represents a discrete type of reasoning task,
    grouped by category (monitoring, analytical, predictive, decision/action,
    diagnostic).

    Examples
    --------
    >>> from procela import ReasoningTask
    >>>
    >>> print(ReasoningTask.ANOMALY_DETECTION)
    Anomaly Detection
    >>> for task in ReasoningTask:
    ...     print(task.name, task.value)
    NONE 1
    ANOMALY_DETECTION 2
    CONSTRAINT_CHECKING 3
    TREND_ANALYSIS 4
    PATTERN_RECOGNITION 5
    SENSITIVITY_ANALYSIS 6
    VALUE_PREDICTION 7
    UNCERTAINTY_QUANTIFICATION 8
    ACTION_PROPOSAL 9
    CONFLICT_RESOLUTION 10
    INTERVENTION_PLANNING 11
    CAUSAL_DIAGNOSIS 12
    """

    # No reasoning. Useful in resetting memory.
    NONE = auto()

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
        """
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
        """
        return _DESCRIPTIONS[self]


_DESCRIPTIONS = {
    ReasoningTask.NONE: ("No reasoning. Useful in resetting memory."),
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
