"""
Variable model abstraction for Procela.

This module defines the Variable class, which represents an active
semantic entity with identity, memory, and reasoning coordination.
It provides methods for recording observations, accessing history,
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
from typing import Any, Iterable, Sequence

from ...symbols.key import Key
from ...symbols.time import TimePoint
from ..action.policy import HighestConfidencePolicy, SelectionPolicy
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
from ..memory.variable.history import ReasoningHistory, VariableHistory
from ..memory.variable.record import VariableRecord
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
    Container for the epistemic state of a variable.

    This immutable data class holds the knowledge-related aspects of a
    variable's state, including historical statistics, anomaly detection
    results, and trend analysis results.

    Parameters
    ----------
    stats : HistoryStatistics
        Statistical analysis of the variable's historical data.
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


class Variable:
    """
    Active variable entity with memory and reasoning coordination.

    A Variable holds recorded observations and integrates with the memory
    and reasoning subsystems. It supports recording values with domain
    validation, retrieving history, generating reasoning views, and
    executing reasoning actions.

    Semantics Reference
    -------------------
    https://procela.org/docs/semantics/core/variable/variable.html

    Examples Reference
    ------------------
    https://procela.org/docs/examples/core/variable/variable.html
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
        policy: SelectionPolicy | None = None,
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

        Notes
        -----
        This constructor sets up memory and reasoning history containers.
        Semantic interpretation of configuration and role is external.
        """
        self.name = name
        self.domain = domain
        self.description = description
        self.units = units
        self.role = role
        self.config = config or {}
        self.seed = seed
        self._policy = policy or HighestConfidencePolicy()
        self._validators = validators

        from ..key_authority import KeyAuthority

        self._key = KeyAuthority.issue(self)
        self._history = VariableHistory(_config=self.config)
        self._reasoning_history = ReasoningHistory()
        self._candidates: list[VariableRecord] = []

    def key(self) -> Key:
        """
        Return the unique identity key for the variable.

        Returns
        -------
        Key
            A stable identity key assigned to this variable.
        """
        return self._key

    def record(
        self,
        value: Any,
        *,
        time: TimePoint | None = None,
        source: Key | None = None,
        confidence: float | None = None,
        explanation: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> VariableRecord:
        """
        Record a new observation for this variable.

        Parameters
        ----------
        value : Any
            Observed value for the variable.
        time : TimePoint | None, optional
            Temporal position of the observation.
        source : Key | None, optional
            Originating source identity.
        confidence : float | None, optional
            Confidence score for the observation.
        explanation : str | None, optional
            Optional human explanation.
        metadata : dict[str, Any] | None, optional
            Optional additional metadata.

        Returns
        -------
        VariableRecord
            Immutable record of the observation.

        Raises
        ------
        ValueError
            If the value does not satisfy the variable's domain.
        """
        history, _ = self.history()
        stats = history.stats().stats()
        if not self.domain.validate(value, stats):
            why = self.domain.explain(value, stats)
            raise ValueError(f"Value {value!r} violates domain: {why}")

        record = VariableRecord(
            value=value,
            time=time,
            source=source,
            confidence=confidence,
            explanation=explanation,
            metadata=metadata or {},
        )

        self._history = self._history.new(record)
        return record

    def history(self) -> tuple[VariableHistory, ReasoningHistory]:
        """
        Return the variable's history and associated reasoning history.

        Returns
        -------
        tuple[VariableHistory, ReasoningHistory]
            Immutable history of observed records and reasoning results.
        """
        return self._history, self._reasoning_history

    def values(self) -> Iterable[Any]:
        """
        Iterate over recorded values for this variable.

        Returns
        -------
        Iterable[Any]
            Sequence of values from recorded observations.
        """
        return (r.value for r in self.history()[0].get_records())

    @property
    def value(self) -> Any:
        """
        Get the last value of a variable.

        Returns
        -------
        Any
            The last value of the variable
        """
        return self._history.stats().last_value

    def __repr__(self) -> str:
        """
        Return a string representation of the variable.

        Returns
        -------
        str
            Concise string representation identifying the variable.
        """
        history, _ = self.history()
        return (
            f"Variable(key={self._key!r}, "
            f"name={self.name!r}, "
            f"units={self.units!r}, "
            f"role={self.role.name}, "
            f"stats={history.stats()})"
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
        stats = self.history()[0].stats()
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
            f"sources    : {len(stats.sources)}"
        )

    def epistemic(self) -> VariableEpistemic:
        """
        Return the epistemic state of the variable.

        This method computes and returns an epistemic representation derived
        from the variable's recorded observations and reasoning history.

        Returns
        -------
        VariableEpistemic
            Epistemic state associated with this variable.
        """
        history, _ = self.history()
        stats = history.stats().stats()
        anomaly = self._detect_anomaly()
        trend = self._analyze_trend()

        return VariableEpistemic(
            key=self.key(),
            reasoning=self._reasoning_history.latest(),
            stats=stats,
            anomaly=anomaly,
            trend=trend,
        )

    def add_candidate(self, candidate: VariableRecord) -> None:
        """
        Add candidate produced by some mechanims.

        Parameters
        ----------
        candidate : VariableRecord
            The candidate record produced by some mechanism.
        """
        self._candidates.append(candidate)

    def candidates(self) -> list[VariableRecord]:
        """
        Get all current candidates of the variable.

        Returns
        -------
        list[VariableRecord]
            The current candidates of the variable.
        """
        return self._candidates

    def commit(self, record: VariableRecord | None) -> None:
        """
        Commit a change to the variable.

        Parameters
        ----------
        record : VariableRecord
            The variable record to be commited.

        Notes
        -----
        The candidates list is cleared after a commit.
        """
        if record is None:
            return

        if not isinstance(record, VariableRecord):
            return

        history, _ = self.history()
        stats = history.stats().stats()
        if not self.domain.validate(record.value, stats):
            why = self.domain.explain(record.value, stats)
            raise ValueError(f"Value {record.value!r} violates domain: {why}")

        self._history = self._history.new(record)
        self.clear_candidates()

    def policy(self) -> SelectionPolicy:
        """
        Get the selection policy of the variable.

        Returns
        -------
        SelectionPolicy | None
            The selection policy of the variable.
        """
        return self._policy

    def validators(self) -> Iterable[ProposalValidator] | None:
        """
        Get the validators of the variable.

        Returns
        -------
        Iterable[ProposalValidator] | None
            The validators of the variable.
        """
        return self._validators

    def clear_candidates(self) -> None:
        """Clear the list of candidates."""
        self._candidates.clear()

    def reset(self) -> None:
        """
        Reset the complete epistemic state of the variable.

        This method clears all observation history, reasoning history, and pending
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
        - Observation and reasoning histories are fully reset.
        - All candidate proposals are cleared.

        Warnings
        --------
        This method must only be called between simulation runs.
        Calling reset during execution results in undefined behavior.
        """
        self._history.reset()
        self._reasoning_history.reset()
        self.clear_candidates()

    # -----------------------------
    # Epistemic reasoning
    # -----------------------------

    def explain(self, recent_reasoning: int = 3) -> str:
        """
        Return an explanation of the variable's current state.

        This method produces a structured explanation based on recorded
        observations, reasoning results, and associated metadata.

        Parameters
        ----------
        recent_reasoning : int
            The number of recent reasoning to be included, default is 3.

        Returns
        -------
        str
            Human-readable explanation of the variable state.
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
        if hasattr(self, "_reasoning_history") and self._reasoning_history:
            lines.append("Recent reasoning steps:")
            for res in self._reasoning_history.get_results()[-recent_reasoning:]:
                lines.append(self._explain_reasoning(res))

        return "\n".join(lines)

    # -----------------------------
    # Action reasoning
    # -----------------------------

    def detect_anomaly(self) -> AnomalyResult:
        """
        Detect anomaly for this variable and record reasoning result.

        Returns
        -------
        AnomalyResult
            Outcome of anomaly detection.
        """
        with Timer() as t:
            result = self._detect_anomaly()

        # record reasoning
        self._record_reasoning(
            ReasoningResult(
                task=ReasoningTask.ANOMALY_DETECTION,
                success=result.is_anomaly,
                result=result,
                confidence=None,
                explanation=None,
                metadata={},
                execution_time=t.elapsed,
            )
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
            result = self._analyze_trend()

        success = result is not None

        # record reasoning
        self._record_reasoning(
            ReasoningResult(
                task=ReasoningTask.TREND_ANALYSIS,
                success=success,
                result=result,
                confidence=None,
                explanation=None,
                metadata={},
                execution_time=t.elapsed,
            )
        )
        return result

    def resolve_conflict(
        self,
        candidates: Sequence[VariableRecord],
        policy: SelectionPolicy,
        validators: Iterable[ProposalValidator] | None = None,
    ) -> VariableRecord | None:
        """
        Resolve conflicting VariableRecords into a single authoritative record.

        Parameters
        ----------
        candidates : Sequence[VariableRecord]
            Competing records to resolve.
        policy : SelectionPolicy
            Policy used to choose among proposals.
        validators : Iterable[ProposalValidator] | None, optional
            Optional validators for proposals.

        Returns
        -------
        VariableRecord | None
            Resolved record if successful; otherwise None.
        """
        with Timer() as t:
            result, resolved = ConflictResolver().resolve(
                candidates=candidates, policy=policy, validators=validators
            )

            if resolved is None and result is not None:
                self._record_reasoning(result=result)
                return None

            if resolved is not None:
                if not self._record(resolved):
                    self._create_failed_reasoning_result(
                        task=ReasoningTask.CONFLICT_RESOLUTION,
                        confidence=resolved.confidence,
                        explanation="Resolved record failed domain validation.",
                    )
                    return None

        self._record_reasoning(
            ReasoningResult(
                task=ReasoningTask.CONFLICT_RESOLUTION,
                success=True,
                result=resolved,
                confidence=resolved.confidence if resolved is not None else None,
                explanation="Conflict resolved succesfully.",
                execution_time=t.elapsed,
            )
        )
        return resolved

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

        # Record reasoning
        self._record_reasoning(
            ReasoningResult(
                task=ReasoningTask.ACTION_PROPOSAL,
                success=bool(proposals),
                result=proposals,
                execution_time=t.elapsed,
            )
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
            result = self._predict(predictor, horizon=horizon)

        rr = ReasoningResult(
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

        self._record_reasoning(rr)
        return rr

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

        rr = ReasoningResult(
            task=ReasoningTask.CAUSAL_DIAGNOSIS,
            success=True,
            result=result,
            confidence=None,
            execution_time=t.elapsed,
        )

        self._record_reasoning(rr)
        return rr

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
            prediction = self._predict(predictor, horizon=horizon)

            class View:
                diagnosis = diagnosis_result
                predictions = [prediction]
                current_value = stats.value

            result = planningOperator.plan(View())

        rr = ReasoningResult(
            task=ReasoningTask.INTERVENTION_PLANNING,
            success=len(result.proposals) > 0,
            result=result,
            confidence=None,
            execution_time=t.elapsed,
        )

        self._record_reasoning(rr)
        return rr

    # -----------------------------
    # Private helpers
    # -----------------------------

    def _explain_reasoning(self, res: ReasoningResult) -> str:
        """
        Explain a reasoning result.

        Parameters
        ----------
        res : ReasoningResult
            The reasoning result to be explained.

        Returns
        -------
        str
            Human explanation of the reasoning result.
        """
        if res is None or not isinstance(res, ReasoningResult):
            return ""

        lines = []
        task_name = res.task.name.replace("_", " ").capitalize()
        lines.append(f"  - {task_name}")

        if res.task == ReasoningTask.ANOMALY_DETECTION and isinstance(
            res.result, AnomalyResult
        ):
            keys = (
                list(res.result.metadata.keys())
                if res.result.metadata is not None
                else []
            )
            lines.append(f"\tscore    : {res.result.score}")
            lines.append(f"\tthreshold: {res.result.threshold}")
            lines.append(f"\tmethod   : {res.result.method}")
            lines.append(f"\tmetadata : additional dict of {len(keys)} keys")
        elif res.task == ReasoningTask.TREND_ANALYSIS and isinstance(
            res.result, TrendResult
        ):
            lines.append(f"\tvalue    : {res.result.value}")
            lines.append(f"\tdirection: {res.result.direction}")
            lines.append(f"\tthreshold: {res.result.threshold}")
        elif res.task == ReasoningTask.VALUE_PREDICTION and isinstance(
            res.result, PredictionResult
        ):
            keys = (
                list(res.result.metadata.keys())
                if res.result.metadata is not None
                else []
            )
            lines.append(f"\tvalue     : {res.result.value}")
            lines.append(f"\thorizon   : {res.result.horizon}")
            lines.append(f"\tconfidence: {res.result.confidence}")
            lines.append(f"\tmetadata  : additional dict of {len(keys)} keys")
        elif res.task == ReasoningTask.CONFLICT_RESOLUTION and isinstance(
            res.result, VariableRecord
        ):
            from_keys = (
                res.result.metadata.get("resolved_from", [])
                if res.result.metadata is not None
                else []
            )
            policy = (
                res.result.metadata.get("policy", None)
                if res.result.metadata is not None
                else None
            )
            lines.append(f"\tvalue     : {res.result.value}")
            lines.append(f"\tconfidence: {res.result.confidence}")
            lines.append(f"\tsources   : {len(from_keys)}")
            lines.append(f"\tpolicy    : {policy}")
        elif res.task == ReasoningTask.ACTION_PROPOSAL and isinstance(res.result, list):
            for proposal in res.result:
                action_name = proposal.action.replace("_", " ").capitalize()
                lines.append(f"\tAction    : {action_name}")
        elif res.task == ReasoningTask.CAUSAL_DIAGNOSIS and isinstance(
            res.result, DiagnosisResult
        ):
            lines.append("\tCauses:")
            for cause in res.result.causes:
                lines.append(f"\t\t- {cause}")
            for key, value in res.result.metadata.items():
                key_text = key.replace("_", " ").capitalize()
                lines.append(f"\t{key_text:22}: {value}")
        if res.task == ReasoningTask.INTERVENTION_PLANNING and isinstance(
            res.result, PlanningResult
        ):
            for proposal in res.result.proposals:
                strategy = (
                    res.result.strategy.capitalize()
                    if res.result.strategy is not None
                    else None
                )
                lines.append(f"\tRationale: {proposal.rationale}")
                lines.append(f"\tEffect   : {proposal.effect.description}")
                lines.append(f"\tOutcome  : {proposal.effect.expected_outcome}")
                lines.append(f"\tStrategy : {strategy}")

        return "\n".join(lines)

    def _detect_anomaly(self, operator: AnomalyOperator | None = None) -> AnomalyResult:
        """
        Detect anomaly using operator or pre-configuration.

        Parameters
        ----------
        operator : AnomalyOperator | None
            The anomaly operator to be used to detect anomalies.

        Returns
        -------
        AnomalyResult
            The result of the detected anomaly.
        """
        if operator is not None and not isinstance(operator, AnomalyOperator):
            raise TypeError(
                f"`operator` should be a AnomalyOperator instance, got {operator}"
            )

        if operator is None:
            anomaly_cfg = self.config.get("anomaly", {})
            method = anomaly_cfg.get("method", "z-score")
            threshold = anomaly_cfg.get("threshold", 3.0)
            operator = AnomalyOperatorThreshold(method, threshold=threshold)

        history, _ = self.history()
        stats = history.stats().stats()

        return operator.detect(stats)

    def _analyze_trend(
        self, operator: TrendOperator | None = None
    ) -> TrendResult | None:
        """
        Analyze trend using operator or pre-configuration.

        Parameters
        ----------
        operator : TrendOperator | None
            The trend operator to be used to analyze trends if provided.

        Returns
        -------
        TrendResult | None
            The result of analyzed trend or None if no trend.
        """
        if not isinstance(self.domain, StatisticalDomain):
            return None

        history, _ = self.history()
        stats = history.stats().stats()

        if operator is None:
            trend = self.config.get("trend", {})
            absolute = trend.get("absolute", 0.3)
            std_factor = trend.get("std_factor", 1.0)
            threshold = self.domain.trend_threshold(
                stats, absolute=absolute, std_factor=std_factor
            )
            operator = TrendOperatorThreshold(threshold)

        return operator.analyze(stats=stats)

    def _predict(
        self,
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

        view = self.epistemic()

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

    def _create_failed_reasoning_result(
        self, task: ReasoningTask, confidence: float | None, explanation: str
    ) -> ReasoningResult:
        """
        Create failed reasoning result.

        Parameters
        ----------
        task : ReasoningTask
            The task of the reasoning.
        confidence : float | None
            The confidence of the reasoning if provided.
        explanation : str
            The explanation containing details of the failure.

        Returns
        -------
        ReasoningResult
            The result of the failed reasoning.
        """
        result = ReasoningResult(
            task=task,
            success=False,
            result=None,
            confidence=confidence,
            explanation=explanation,
        )
        self._record_reasoning(result)
        return result

    def _record(self, record: VariableRecord) -> bool:
        """
        Record a new observation for this variable.

        Parameters
        ----------
        record : VariableRecord
            The variable record.

        Returns
        -------
        bool
            True if the record is saved successfully, false otherwise.
        """
        history, _ = self.history()
        stats = history.stats().stats()
        if self.domain.validate(record.value, stats):
            self._history = self._history.new(record)
            return True
        return False

    def _record_reasoning(self, result: ReasoningResult) -> None:
        """
        Record a reasoning result.

        Parameters
        ----------
        result : ReasoningResult
            The reasoning result to record.
        """
        self._reasoning_history = self._reasoning_history.new(result=result)
