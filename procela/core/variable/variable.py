"""
Variable model with memory and reasoning abstraction in Procela.

This module defines the Variable class, which represents an active
semantic entity with identity, memory, and reasoning coordination.
It provides methods for recording observations, accessing memory,
and invoking reasoning tasks such as anomaly detection, trend
analysis, conflict resolution, action proposal, and prediction.

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/variable/variable.html

Examples Reference
------------------
https://procela.org/docs/examples/core/variable/variable.html
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from ...symbols.key import Key
from ..action.policy import HighestConfidencePolicy, ResolutionPolicy
from ..action.proposal import ActionProposal
from ..action.proposer import ActionProposer
from ..action.resolver import ConflictResolver
from ..action.validator import ProposalValidator
from ..assessment.anomaly import AnomalyResult
from ..assessment.diagnosis import DiagnosisResult
from ..assessment.planning import PlanningResult
from ..assessment.prediction import PredictionResult
from ..assessment.reasoning import ReasoningResult
from ..assessment.statistics import StatisticsResult
from ..assessment.task import ReasoningTask
from ..assessment.trend import TrendResult
from ..memory.base import VariableMemory
from ..memory.candidate import CandidateRecord
from ..memory.record import VariableRecord
from ..memory.statistics import MemoryStatistics
from ..reasoning.anomaly.operator import AnomalyOperator, AnomalyOperatorThreshold
from ..reasoning.diagnosis.operator import (
    DiagnosisOperator,
    DiagnosisOperatorThreshold,
    TrendOperator,
    TrendOperatorThreshold,
)
from ..reasoning.planning.operator import PlanningOperator
from ..reasoning.prediction.base import Predictor
from ..reasoning.prediction.last import LastPredictor
from ..timer import Timer
from .domain.statistical import StatisticalDomain
from .domain.value import ValueDomain
from .role import VariableRole


@dataclass(frozen=True)
class VariableEpistemic:
    """
    Container for the epistemic projection of a variable.

    This immutable data class holds the knowledge-related aspects of a
    variable's projection, including last reasoning result, memory statistics,
    anomaly detection results, and trend analysis results.

    Parameters
    ----------
    key : Key
        The unique identity of the variable epistemics.
    reasoning : ReasoningResult | None
        The most recent reasoning result of the variable.
    stats : StatisticsResult
        Statistical analysis of the variable's memory.
    anomaly : AnomalyResult | None
        Anomaly detection results.
    trend : TrendResult | None
        Trend analysis results.
    """

    key: Key
    reasoning: ReasoningResult | None
    stats: StatisticsResult
    anomaly: AnomalyResult | None
    trend: TrendResult | None

    def __post_init__(self) -> None:
        """
        Validate a variable epistemic view after initialization.

        Performs type checking on the attributes and generates
        a unique key for the instance.

        Raises
        ------
        TypeError
            If `reasoning` is not a ReasoningResult or None.
            If `stats` is not a StatisticsResult.
            If `anomaly` is not an AnomalyResult or None.
            If `trend` is not a TrendResult or None.
        """
        if not isinstance(self.key, Key):
            raise TypeError(f"`key` should be a Key, got {type(self.key)}")

        if not isinstance(self.reasoning, ReasoningResult | None):
            raise TypeError(
                f"`reasoning` should be a ReasoningResult or None, "
                f"got {type(self.reasoning)}"
            )

        if not isinstance(self.stats, StatisticsResult):
            raise TypeError(
                f"`stats` should be a StatisticsResult, " f"got {type(self.stats)}"
            )

        if not isinstance(self.anomaly, AnomalyResult | None):
            raise TypeError(
                f"`anomaly` should be a AnomalyResult or None, "
                f"got {type(self.anomaly)}"
            )

        if not isinstance(self.trend, TrendResult | None):
            raise TypeError(
                f"`trend` should be a TrendResult or None, " f"got {type(self.trend)}"
            )


class Variable:
    """
    Active variable entity with memory and reasoning coordination.

    A Variable holds recorded observations and integrates with the memory
    and reasoning subsystems. It supports recording values with domain
    validation, retrieving memory, generating reasoning views, and
    executing reasoning actions.
    """

    def __init__(
        self,
        name: str,
        domain: ValueDomain,
        description: str = "",
        units: str | None = None,
        role: VariableRole = VariableRole.ENDOGENOUS,
        config: dict[str, Any] | None = None,
        seed: int | None = None,
        policy: ResolutionPolicy | None = None,
        validators: Iterable[ProposalValidator] | None = None,
    ):
        """
        Instantiate a variable with identity and configuration.

        Parameters
        ----------
        name : str
            The variable's unique name.
        domain : ValueDomain
            Domain used to validate recorded values.
        description : str, optional
            Human-readable description.
        units : str | None, optional
            Units of the variable's values.
        role : VariableRole, optional
            Role of the variable within the model.
        config : dict[str, Any] | None, optional
            Variable configuration for reasoning and domain.
        seed : int | None, optional
            Seed for reproducible internal behavior.
        policy : ResolutionPolicy | None
            The resolution policy used to resolve conflicts between hypotheses.
            Default is None.
        validators : Iterable[ProposalValidator] | None
            The iterable ProposalValidators to filter hypotheses before resolution.

        Notes
        -----
        This constructor sets up memory and reasoning containers.
        Semantic interpretation of configuration and role is external.
        """
        self.name = name
        self.domain = domain
        self.description = description
        self.units = units
        self.role = role
        self.config = config or {}
        self.seed = seed
        self.policy = policy or HighestConfidencePolicy()
        self.validators = validators

        from ..key_authority import KeyAuthority

        self._key = KeyAuthority.issue(self)

        # Used during commits
        self.hypotheses: list[CandidateRecord] = []
        self.conclusion: VariableRecord | None = None
        self.reasoning: ReasoningResult | None = None

        self.memory: VariableMemory | None = None
        self.stats = MemoryStatistics()

    def key(self) -> Key:
        """
        Return the unique identity key for the variable.

        Returns
        -------
        Key
            The unique identity key assigned to this variable.
        """
        return self._key

    def init(self, record: VariableRecord) -> None:
        """
        Initialize a variable with a record.

        Parameters
        ----------
        record : VariableRecord
            The record to be initialized the variable with.
        """
        if not self.validate(record):
            why = self.domain.explain(record)
            raise ValueError(
                "The variable initialization fails "
                f"domain violation constraint: {why}"
            )
        self.memory = None
        self.clear_candidates()
        self.stats = MemoryStatistics.empty()
        self.hypotheses.append(CandidateRecord(record=record))
        self.conclusion = record
        self.reasoning = ReasoningResult.empty()
        self.commit()

    @property
    def value(self) -> Any:
        """
        Get the last value of a variable.

        Returns
        -------
        Any
            The last value of the variable
        """
        return self.stats.last_value

    def has_records(self) -> bool:
        """
        Detect whether the variable already has records.

        Returns
        -------
        bool
            Whether the variable has records or not.
        """
        return self.stats.count > 0

    def validate(self, record: VariableRecord | None) -> bool:
        """
        Validate a record against this variable's domain.

        Parameters
        ----------
        record : VariableRecord
            The variable record to validate.

        Returns
        -------
        bool
            True if the record is valid w.r.t the domain, false otherwise.

        Notes
        -----
            The method always returns True when the record is None.
        """
        if record is None:
            return True

        stats = self.stats.result()
        return self.domain.validate(record.value, stats)

    def records(self) -> Iterable[VariableRecord | None]:
        """
        Iterate over resolved records for this variable.

        Returns
        -------
        Iterable[VariableRecord]
            Sequence of records from resolved observations.
        """
        if self.memory is None:
            return iter(())
        return (record for _, record, _ in self.memory.iter())

    def add_candidate(self, record: VariableRecord) -> None:
        """
        Add candidate produced by some mechanims.

        Parameters
        ----------
        record : VariableRecord
            The candidate record produced by some mechanism.
        """
        self.hypotheses.append(CandidateRecord(record))

    def candidates(self, exclude: Key | None = None) -> list[CandidateRecord]:
        """
        Get all current candidates of the variable by excluding a specific one.

        Parameters
        ----------
        exclude : Key | None
            The key to be excluded from candidates. Default is None.

        Returns
        -------
        list[CandidateRecord]
            The candidates of the variable excluded the identified one.
        """
        if exclude is None:
            return self.hypotheses

        return [
            candidate
            for candidate in self.hypotheses
            if candidate.record is not None and candidate.record.source != exclude
        ]

    def commit(
        self,
        include_hypotheses: bool = True,
        include_conclusion: bool = True,
        include_reasonning: bool = True,
    ) -> None:
        """
        Commit a change to the variable's memory.

        Parameters
        ----------
        include_hypotheses : bool
            If proposed candidates should be included in the commit.
        include_conclusion : bool
            If resolved candidate should be included in the commit.
        include_reasonning : bool
            If reasonning result should be included in the commit.

        Notes
        -----
        Only last change is committed.
        """
        if include_hypotheses:
            if not isinstance(self.hypotheses, list):
                raise TypeError(
                    f"`hypotheses` should be a list, got {type(self.hypotheses)}"
                )
            for i, hypothesis in enumerate(self.hypotheses):
                if not isinstance(hypothesis, CandidateRecord):
                    raise TypeError(
                        f"`hypothesis` at index {i} should be a CandidateRecord, "
                        f"got {hypothesis}"
                    )

        if include_conclusion:
            if not isinstance(self.conclusion, VariableRecord | None):
                raise TypeError(
                    f"`conclusion` should be a VariableRecord or None, "
                    f"got {self.conclusion}"
                )

            if not self.validate(self.conclusion):
                if self.reasoning is not None:
                    self.reasoning = ReasoningResult.failed_result(
                        self.reasoning.task,
                        confidence=self.reasoning.confidence,
                        explanation="Variable domain violation",
                    )

        if include_reasonning:
            if not isinstance(self.reasoning, ReasoningResult | None):
                raise TypeError(
                    f"reasoning result should be a ReasoningResult or None, "
                    f"got {self.reasoning}"
                )

        anomaly_cfg = self.config.get("anomaly", {})
        alpha = anomaly_cfg.get("alpha", 0.3)

        if self.memory is None:
            self.memory = VariableMemory(
                hypotheses=tuple(self.hypotheses) if include_hypotheses else (),
                conclusion=self.conclusion if include_conclusion else None,
                reasoning=self.reasoning if include_reasonning else None,
                config=self.config,
                previous=None,
            )
            self.stats = MemoryStatistics.empty().update(
                record=self.conclusion,
                alpha=alpha,
            )
        else:
            self.memory = self.memory.new(
                hypotheses=tuple(self.hypotheses) if include_hypotheses else (),
                conclusion=self.conclusion if include_conclusion else None,
                reasoning=self.reasoning if include_reasonning else None,
            )
            self.stats = self.stats.update(
                record=self.conclusion,
                alpha=alpha,
            )

    def clear_candidates(self) -> None:
        """Clear the list of candidates."""
        self.hypotheses.clear()
        self.conclusion = None
        self.reasoning = None

    def reset(self) -> None:
        """
        Reset the complete epistemic memory of the variable.

        This method clears all records in the memory, and pending
        candidate records while preserving the variable identity, key,
        configuration, domain, and policies.

        Calling this method defines a boundary between simulation worlds. The
        variable remains the same conceptual entity, but all accumulated knowledge
        and inferred state are discarded.

        This operation is required for scenario exploration, counterfactual
        evaluation, and optimization workflows.

        Notes
        -----
        - Variable identity and configuration are preserved.
        - Observation and reasoning are fully reset.
        - All pending candidates are cleared.

        Warnings
        --------
        This method must only be called between simulation runs.
        Calling reset during execution results in undefined behavior.
        """
        self.memory = None
        self.clear_candidates()
        self.stats = MemoryStatistics.empty()

    def __repr__(self) -> str:
        """
        Return a string representation of the variable.

        Returns
        -------
        str
            Concise string representation identifying the variable.
        """
        stats = self.stats
        return (
            f"Variable(key={self._key!r}, "
            f"name={self.name!r}, "
            f"units={self.units!r}, "
            f"role={self.role.name}, "
            f"stats={stats})"
        )

    def summary(self) -> str:
        """
        Return a textual summary of the variable state.

        The summary includes basic metadata, value counts, and aggregate
        statistics (mean, std, min, max, confidence, EWMA, sources).

        Returns
        -------
        str
            Human-readable summary string.
        """
        stats = self.stats
        return (
            "===== Variable summary =====\n"
            f"name       : {self.name}\n"
            f"description: {self.description}\n"
            f"units      : {self.units}\n"
            f"role       : {self.role.name}\n"
            f"config keys: {list(self.config.keys())}\n"
            f"seed       : {self.seed}\n"
            f"count      : {stats.count}\n"
            f"mean       : {stats.mean()}\n"
            f"std        : {stats.std()}\n"
            f"min        : {stats.min}\n"
            f"max        : {stats.max}\n"
            f"confidence : {stats.confidence()}\n"
            f"ewma       : {stats.ewma}\n"
            f"sources: {len(stats.sources)}"
        )

    def epistemic(self) -> VariableEpistemic:
        """
        Return the epistemic projection of the variable.

        This method computes and returns an epistemic representation derived
        from the variable's recorded observations and reasoning result.

        Returns
        -------
        VariableEpistemic
            Epistemic projection associated with this variable.
        """
        reasoning: ReasoningResult | None = None

        if self.memory is not None:
            _, _, reasoning = self.memory.latest()

        stats = self.stats.result()
        anomaly = self._detect_anomaly(stats)
        trend = self._analyze_trend(stats)

        return VariableEpistemic(
            key=self.key(),
            reasoning=reasoning,
            stats=stats,
            anomaly=anomaly,
            trend=trend,
        )

    # -----------------------------
    # Epistemic reasoning
    # -----------------------------

    def explain(self, recent_reasoning: int = 3) -> str:
        """
        Return an explanation of the variable's evolution.

        This method produces a structured explanation based on recorded
        observations, reasoning results, and associated metadata.

        Parameters
        ----------
        recent_reasoning : int
            The number of recent reasoning to be included, default is 3.

        Returns
        -------
        str
            Human-readable explanation of the variable's evolution.
        """
        epistemic = self.epistemic()
        stats = epistemic.stats
        anomaly = epistemic.anomaly
        trend = epistemic.trend

        mean, std = stats.mean, stats.std
        confidence = stats.confidence

        lines = [
            f"Variable '{self.name}' ({self.role.name})",
            f"Description: {self.description or 'N/A'}",
            f"Units: {self.units or 'N/A'}",
            f"Latest value: {stats.value} " f"(confidence: {confidence})",
            f"Observed {stats.count} records "
            f"(min={stats.min}, max={stats.max}, "
            f"mean={mean}, std={std})",
        ]

        # Anomaly summary
        if anomaly is not None and anomaly.is_anomaly:
            lines.append(
                f"Anomaly detected! score={anomaly.score}, "
                f"threshold={anomaly.threshold}, method={anomaly.method}"
            )
        else:
            lines.append("No anomaly detected.")

        # Trend summary
        if trend is not None:
            lines.append(
                f"Trend: {trend.direction.upper()} (delta={trend.value:.3f}, "
                f"threshold={trend.threshold})"
            )
        else:
            lines.append("Trend: N/A")

        # Optional reasoning summary (last 3 actions)
        lines.append("Recent reasoning steps:")
        if self.memory is not None:
            for _, _, res in self.memory.records()[-recent_reasoning:]:
                lines.append(self._explain_reasoning(res))

        return "\n".join(lines)

    # -----------------------------
    # Action reasoning
    # -----------------------------

    def detect_anomaly(self) -> AnomalyResult:
        """
        Detect anomaly for this variable.

        Returns
        -------
        AnomalyResult
            Outcome of anomaly detection.
        """
        with Timer() as t:
            stats = self.stats.result()
            result = self._detect_anomaly(stats)

        # Ephemeral reasoning
        self.reasoning = ReasoningResult(
            task=ReasoningTask.ANOMALY_DETECTION,
            success=result.is_anomaly,
            result=result,
            confidence=None,
            explanation=None,
            metadata={},
            execution_time=t.elapsed,
        )

        return result

    def analyze_trend(self) -> TrendResult | None:
        """
        Analyze trend for this variable and record reasoning result.

        Returns
        -------
        TrendResult | None
            Trend result if available, otherwise None.
        """
        with Timer() as t:
            stats = self.stats.result()
            result = self._analyze_trend(stats)

        success = result is not None

        # Ephemeral reasoning
        self.reasoning = ReasoningResult(
            task=ReasoningTask.TREND_ANALYSIS,
            success=success,
            result=result,
            confidence=None,
            explanation=None,
            metadata={},
            execution_time=t.elapsed,
        )

        return result

    def resolve_conflict(self) -> VariableRecord | None:
        """
        Resolve competing candidates into a single authoritative record.

        Returns
        -------
        VariableRecord | None
            The resolved record.
        """
        self.conclusion, self.reasoning = ConflictResolver().resolve(
            candidates=self.hypotheses,
            policy=self.policy,
            validators=self.validators,
        )

        if not self.validate(self.conclusion):
            self.reasoning = ReasoningResult.failed_result(
                task=ReasoningTask.CONFLICT_RESOLUTION,
                confidence=(
                    self.conclusion.confidence if self.conclusion is not None else None
                ),
                explanation="Resolved record failed domain validation.",
            )

        return self.conclusion

    def propose_actions(self) -> list[ActionProposal]:
        """
        Generate action proposals and record the corresponding reasoning result.

        Returns
        -------
        list[ActionProposal]
            List of proposed actions.
        """
        with Timer() as t:
            view = self.epistemic()
            proposals = ActionProposer().propose(view=view)

        # Ephemeral reasoning
        self.reasoning = ReasoningResult(
            task=ReasoningTask.ACTION_PROPOSAL,
            success=bool(proposals),
            result=proposals,
            execution_time=t.elapsed,
        )

        return proposals

    def predict(
        self,
        predictor: Predictor | None = None,
        *,
        horizon: int | None = None,
    ) -> ReasoningResult:
        """
        Predict future variable value and record reasoning result.

        Parameters
        ----------
        predictor : Predictor | None, optional
            Predictor strategy to apply.
        horizon : int | None, optional
            Prediction horizon.

        Returns
        -------
        ReasoningResult
            Reasoning result containing prediction details.
        """
        if predictor is not None and not isinstance(predictor, Predictor):
            raise TypeError(
                f"`predictor` should be a Predictor instance, got {predictor}"
            )

        predictor = predictor or LastPredictor()

        with Timer() as t:
            view = self.epistemic()
            result = self._predict(view, predictor, horizon=horizon)

        # Ephemeral reasoning
        self.reasoning = ReasoningResult(
            task=ReasoningTask.VALUE_PREDICTION,
            success=result is not None,
            result=result,
            confidence=None,  # explicitly undefined for now
            explanation=None,
            metadata={
                "predictor": predictor.__class__.__name__,
                "horizon": horizon,
            },
            execution_time=t.elapsed,
        )
        return self.reasoning

    def diagnose_causes(
        self, operator: DiagnosisOperator | None = None
    ) -> ReasoningResult:
        """
        Diagnose causes of observed behavior and record the reasoning result.

        Parameters
        ----------
        operator : DiagnosisOperator | None, optional
            Strategy for diagnosis evaluation.

        Returns
        -------
        ReasoningResult
            Reasoning result with diagnosis output.
        """
        if operator is not None and not isinstance(operator, DiagnosisOperator):
            raise TypeError(
                f"`operator` should be a DiagnosisOperator instance, got {operator}"
            )

        with Timer() as t:
            result = self._diagnose_causes(operator)

        # Ephemeral reasoning
        self.reasoning = ReasoningResult(
            task=ReasoningTask.CAUSAL_DIAGNOSIS,
            success=True,
            result=result,
            confidence=None,
            execution_time=t.elapsed,
        )

        return self.reasoning

    def plan_intervention(
        self,
        planningOperator: PlanningOperator | None = None,
        diagnosisOperator: DiagnosisOperator | None = None,
        predictor: Predictor | None = None,
        *,
        horizon: int | None = None,
    ) -> ReasoningResult:
        """
        Plan interventions for this variable and record the reasoning result.

        Parameters
        ----------
        planningOperator : PlanningOperator | None, optional
            Operator for planning strategy.
        diagnosisOperator : DiagnosisOperator | None, optional
            Operator for diagnosis strategy.
        predictor : Predictor | None, optional
            Predictor for prediction strategy.
        horizon : int | None, optional
            Prediction horizon.

        Returns
        -------
        ReasoningResult
            Reasoning result containing the intervention plan.
        """
        with Timer() as t:
            if planningOperator is not None and not isinstance(
                planningOperator, PlanningOperator
            ):
                raise TypeError(
                    "`planningOperator` should be a PlanningOperator, "
                    f"got {planningOperator}"
                )

            if diagnosisOperator is not None and not isinstance(
                diagnosisOperator, DiagnosisOperator
            ):
                raise TypeError(
                    "`diagnosisOperator` should be a DiagnosisOperator, "
                    f"got {planningOperator}"
                )

            if predictor is not None and not isinstance(predictor, Predictor):
                raise TypeError(
                    f"`predictor` should be a Predictor instance, got {predictor}"
                )

            predictor = predictor or LastPredictor()

            if planningOperator is None:
                planning_cfg = self.config.get("planning", {})
                name = planning_cfg.get("name", "preventive")
                kwargs = planning_cfg.get("kwargs", {})
                planningOperator = PlanningOperator(name=name, **kwargs)

            # Define the planning view
            epistemic = self.epistemic()
            stats = epistemic.stats
            diagnosis_result = self._diagnose_causes(diagnosisOperator)
            prediction = self._predict(epistemic, predictor, horizon=horizon)

            class View:
                diagnosis = diagnosis_result
                predictions = [prediction]
                current_value = stats.value

            result = planningOperator.plan(View())

        # Ephemeral reasoning
        self.reasoning = ReasoningResult(
            task=ReasoningTask.INTERVENTION_PLANNING,
            success=len(result.proposals) > 0,
            result=result,
            confidence=None,
            execution_time=t.elapsed,
        )

        return self.reasoning

    def _detect_anomaly(
        self,
        stats: StatisticsResult,
        operator: AnomalyOperator | None = None,
    ) -> AnomalyResult:
        """
        Detect anomaly using operator or pre-configuration.

        Parameters
        ----------
        stats : StatisticsResult
            The statistics result to be used to detect anomalies.
        operator : AnomalyOperator | None
            The anomaly operator to be used to detect anomalies.

        Returns
        -------
        AnomalyResult
            The result of the detected anomaly.
        """
        if not isinstance(stats, StatisticsResult):
            raise TypeError(f"`stats` should be a StatisticsResult, got {type(stats)}")

        if operator is not None and not isinstance(operator, AnomalyOperator):
            raise TypeError(
                f"`operator` should be a AnomalyOperator instance, got {operator}"
            )

        if operator is None:
            anomaly_cfg = self.config.get("anomaly", {})
            method = anomaly_cfg.get("method", "z-score")
            threshold = anomaly_cfg.get("threshold", 3.0)
            operator = AnomalyOperatorThreshold(method, threshold=threshold)

        return operator.detect(stats)

    def _analyze_trend(
        self, stats: StatisticsResult, operator: TrendOperator | None = None
    ) -> TrendResult | None:
        """
        Analyze trend using operator or pre-configuration.

        Parameters
        ----------
        stats : StatisticsResult
            The statistics result to be used to analyze trend.
        operator : TrendOperator | None
            The trend operator to be used to analyze trends if provided.

        Returns
        -------
        TrendResult | None
            The result of analyzed trend or None if no trend.
        """
        if not isinstance(stats, StatisticsResult):
            raise TypeError(f"`stats` should be a StatisticsResult, got {type(stats)}")

        if not isinstance(operator, TrendOperator | None):
            raise TypeError(
                "`operator` should be a TrendOperator or None, " f"got {type(operator)}"
            )

        if not isinstance(self.domain, StatisticalDomain):
            return None

        if operator is None:
            trend = self.config.get("trend", {})
            absolute = trend.get("absolute", 0.3)
            std_factor = trend.get("std_factor", 1.0)
            threshold = self.domain.trend_threshold(
                stats, absolute=absolute, std_factor=std_factor
            )
            operator = TrendOperatorThreshold(threshold)

        return operator.analyze(stats=stats)

    # -----------------------------
    # Private helpers
    # -----------------------------

    def _explain_reasoning(self, result: ReasoningResult | None) -> str:
        """
        Explain a reasoning result.

        Parameters
        ----------
        result : ReasoningResult
            The reasoning result to be explained.

        Returns
        -------
        str
            Human explanation of the reasoning result.
        """
        if result is None or not isinstance(result, ReasoningResult):
            return ""

        lines = []
        task_name = result.task.name.replace("_", " ").capitalize()
        lines.append(f"  - {task_name}")

        if result.task == ReasoningTask.ANOMALY_DETECTION and isinstance(
            result.result, AnomalyResult
        ):
            keys = (
                list(result.result.metadata.keys())
                if result.result.metadata is not None
                else []
            )
            lines.append(f"\tanomaly  : {result.result.is_anomaly}")
            lines.append(f"\tscore    : {result.result.score}")
            lines.append(f"\tthreshold: {result.result.threshold}")
            lines.append(f"\tmethod   : {result.result.method}")
            lines.append(f"\tmetadata : additional dict of {len(keys)} keys")
        elif result.task == ReasoningTask.TREND_ANALYSIS and isinstance(
            result.result, TrendResult
        ):
            lines.append(f"\tvalue    : {result.result.value}")
            lines.append(f"\tdirection: {result.result.direction}")
            lines.append(f"\tthreshold: {result.result.threshold}")
        elif result.task == ReasoningTask.VALUE_PREDICTION and isinstance(
            result.result, PredictionResult
        ):
            keys = (
                list(result.result.metadata.keys())
                if result.result.metadata is not None
                else []
            )
            lines.append(f"\tvalue     : {result.result.value}")
            lines.append(f"\thorizon   : {result.result.horizon}")
            lines.append(f"\tconfidence: {result.result.confidence}")
            lines.append(f"\tmetadata  : additional dict of {len(keys)} keys")
        elif result.task == ReasoningTask.CONFLICT_RESOLUTION and isinstance(
            result.result, VariableRecord
        ):
            from_keys = (
                result.result.metadata.get("resolved_from", [])
                if result.result.metadata is not None
                else []
            )
            policy = (
                result.result.metadata.get("policy", None)
                if result.result.metadata is not None
                else None
            )
            lines.append(f"\tvalue     : {result.result.value}")
            lines.append(f"\tconfidence: {result.result.confidence}")
            lines.append(f"\tsources   : {len(from_keys)}")
            lines.append(f"\tpolicy    : {policy}")
        elif result.task == ReasoningTask.ACTION_PROPOSAL and isinstance(
            result.result, list
        ):
            for proposal in result.result:
                action_name = proposal.action.replace("_", " ").capitalize()
                lines.append(f"\tAction    : {action_name}")
        elif result.task == ReasoningTask.CAUSAL_DIAGNOSIS and isinstance(
            result.result, DiagnosisResult
        ):
            lines.append("\tCauses:")
            for cause in result.result.causes:
                lines.append(f"\t\t- {cause}")
            for key, value in result.result.metadata.items():
                key_text = key.replace("_", " ").capitalize()
                lines.append(f"\t{key_text:22}: {value}")
        if result.task == ReasoningTask.INTERVENTION_PLANNING and isinstance(
            result.result, PlanningResult
        ):
            for proposal in result.result.proposals:
                strategy = (
                    result.result.strategy.capitalize()
                    if result.result.strategy is not None
                    else None
                )
                lines.append(f"\tRationale: {proposal.rationale}")
                lines.append(f"\tEffect   : {proposal.effect.description}")
                lines.append(f"\tOutcome  : {proposal.effect.expected_outcome}")
                lines.append(f"\tStrategy : {strategy}")

        return "\n".join(lines)

    def _predict(
        self,
        view: VariableEpistemic,
        predictor: Predictor | None = None,
        *,
        horizon: int | None = None,
    ) -> PredictionResult:
        """
        Predict future variable value using predictor or pre-configuration.

        Parameters
        ----------
        predictor : Predictor | None
            The predictor to be used to make predictions.
        horizon : int | None
            The horizon for the prediction.

        Returns
        -------
        PredictionResult
            The predicted result.
        """
        if predictor is not None and not isinstance(predictor, Predictor):
            raise TypeError(
                f"`predictor` should be a Predictor instance, got {predictor}"
            )

        predictor = predictor or LastPredictor()
        return predictor.predict(view=view, horizon=horizon)

    def _diagnose_causes(
        self, operator: DiagnosisOperator | None = None
    ) -> DiagnosisResult:
        """
        Diagnose causes using operator or pre-configuration.

        Parameters
        ----------
        operator : DiagnosisOperator | None
            The operator to be used to diagnose causes if provided.

        Returns
        -------
        DiagnosisResult
            The diagnosis result.
        """
        if operator is not None and not isinstance(operator, DiagnosisOperator):
            raise TypeError(
                f"`operator` should be a DiagnosisOperator instance, got {operator}"
            )

        if operator is None:
            diagnosis_cfg = self.config.get("diagnosis", {})
            name = diagnosis_cfg.get("name", "anomaly")
            kwargs = diagnosis_cfg.get("kwargs", {})
            operator = DiagnosisOperatorThreshold(name=name, **kwargs)

        view = self.epistemic()

        return operator.diagnose(view=view)

    def _record_to_proposal(self, record: VariableRecord) -> ActionProposal:
        """
        Convert a VariableRecord into an ActionProposal.

        Parameters
        ----------
        record : VariableRecord
            The record of the variable to be saved.

        Returns
        -------
        ActionProposal
            The action proposal result.
        """
        return ActionProposal(
            value=record.value,
            confidence=record.confidence or 0.0,
            source=record.source,
            metadata={
                "record_key": record.key(),
                "time": record.time,
            },
        )
