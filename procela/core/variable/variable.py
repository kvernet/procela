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

Examples
--------
https://procela.org/docs/examples/core/variable/variable.html
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

from ...symbols.key import Key
from ...symbols.time import TimePoint
from ..action.policy import SelectionPolicy
from ..action.proposal import ActionProposal
from ..action.proposer import ActionProposer
from ..action.resolver import ConflictResolver
from ..action.validator import ProposalValidator
from ..memory.variable.epistemic import VariableEpistemic
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
from ..reasoning.result import (
    AnomalyResult,
    DiagnosisResult,
    PredictionResult,
    ReasoningResult,
    TrendResult,
)
from ..reasoning.task import ReasoningTask
from ..timer import Timer
from .domain.statistical import StatisticalDomain
from .domain.value import ValueDomain
from .role import VariableRole


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

    Examples
    --------
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

        from ..key_authority import KeyAuthority

        self._key = KeyAuthority.issue(self)
        self._history = VariableHistory(_config=self.config)
        self._reasoning_history = ReasoningHistory()

    def key(self) -> Key:
        """
        Return the unique identity key for the variable.

        Returns
        -------
        Key
            A stable identity key assigned to this variable.

        Notes
        -----
        Variable identity semantics are defined externally.
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

        Notes
        -----
        Domain checks are applied mechanically. Semantic interpretation of
        why a value is valid or not is defined externally.
        """
        history, _ = self.history()
        stats = history.stats()
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

        Notes
        -----
        This method provides access to stored histories only.
        Semantic interpretation of history contents is external.
        """
        return self._history, self._reasoning_history

    def values(self) -> Iterable[Any]:
        """
        Iterate over recorded values for this variable.

        Returns
        -------
        Iterable[Any]
            Sequence of values from recorded observations.

        Notes
        -----
        This iterator exposes values only; interpretation is external.
        """
        return (r.value for r in self.history()[0].get_records())

    def __repr__(self) -> str:
        """
        Return a string representation of the variable.

        Returns
        -------
        str
            Concise string representation identifying the variable.

        Notes
        -----
        This representation is intended for debugging and logging purposes.
        Semantic interpretation of the representation is defined externally.
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

        Notes
        -----
        This is a convenience representation. Semantic interpretation of
        statistics and summary content is defined externally.
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

        Notes
        -----
        This method performs computational aggregation only. Semantic meaning
        of the epistemic state is defined externally.
        """
        history, _ = self.history()
        stats = history.stats()
        anomaly = self._detect_anomaly()
        trend = self._analyze_trend()

        return VariableEpistemic(
            stats=stats,
            anomaly=anomaly,
            trend=trend,
        )

    # -----------------------------
    # Epistemic reasoning
    # -----------------------------

    def explain(self) -> str:
        """
        Return an explanation of the variable's current state.

        This method produces a structured explanation based on recorded
        observations, reasoning results, and associated metadata.

        Returns
        -------
        str
            Human-readable explanation of the variable state.

        Notes
        -----
        This explanation is generated mechanically from available data.
        Semantic interpretation of explanations is defined externally.
        """
        epistemic = self.epistemic()
        stats = epistemic.stats
        anomaly = epistemic.anomaly
        trend = epistemic.trend

        mean, std = stats.mean(), stats.std()
        confidence = stats.confidence()

        lines = [
            f"Variable '{self.name}' ({self.role.name})",
            f"Description: {self.description or 'N/A'}",
            f"Units: {self.units or 'N/A'}",
            f"Latest value: {stats.last_value} " f"(confidence: {confidence})",
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
            for res in self._reasoning_history.get_results()[-3:]:
                task_name = res.task.name.replace("_", " ").capitalize()
                if isinstance(res.result, list):
                    summary = f"{len(res.result)} items"
                else:
                    summary = str(res.result)
                lines.append(f"  - {task_name}: {summary}")

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

        Notes
        -----
        This method executes computation and records a reasoning result.
        Semantic interpretation of anomaly detection is defined externally.
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

        Notes
        -----
        This method records a reasoning result. Semantic interpretation of
        trend results is defined externally.
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

        Notes
        -----
        This method executes conflict resolution and records a reasoning result.
        Semantic interpretation is defined externally.
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

        Notes
        -----
        Semantic interpretation of proposals is defined externally.
        """
        with Timer() as t:
            epistemic = self.epistemic()
            view = epistemic.get_proposal_view()
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

        Notes
        -----
        This method records the reasoning result. Semantic interpretation of
        predicted values is defined externally.
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

        Notes
        -----
        Semantic interpretation of diagnosis output is defined externally.
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

        Notes
        -----
        This method executes planning computation and records a reasoning result.
        Semantic interpretation of plans is defined externally.
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
                current_value = stats.last_value

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

    def _detect_anomaly(self, operator: AnomalyOperator | None = None) -> AnomalyResult:
        """Detect anomaly using operator or pre-configuration."""
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
        stats = history.stats()

        return operator.detect(stats)

    def _analyze_trend(
        self, operator: TrendOperator | None = None
    ) -> TrendResult | None:
        """Analyze trend using operator or pre-configuration.."""
        if not isinstance(self.domain, StatisticalDomain):
            return None

        history, _ = self.history()
        stats = history.stats()

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
        """Predict future variable value using predictor or pre-configuration.."""
        if predictor is not None and not isinstance(predictor, Predictor):
            raise TypeError(
                f"`predictor` should be a Predictor instance, got {predictor}"
            )

        predictor = predictor or LastPredictor()

        epistemic = self.epistemic()
        view = epistemic.get_prediction_view()

        return predictor.predict(view=view, horizon=horizon)

    def _diagnose_causes(
        self, operator: DiagnosisOperator | None = None
    ) -> DiagnosisResult:
        """Diagnose causes using operator or pre-configuration.."""
        if operator is not None and not isinstance(operator, DiagnosisOperator):
            raise TypeError(
                f"`operator` should be a DiagnosisOperator instance, got {operator}"
            )

        if operator is None:
            diagnosis_cfg = self.config.get("diagnosis", {})
            name = diagnosis_cfg.get("name", "anomaly")
            kwargs = diagnosis_cfg.get("kwargs", {})
            operator = DiagnosisOperatorThreshold(name=name, **kwargs)

        # Diagnosis view from variable epistemic
        epistemic = self.epistemic()
        view = epistemic.get_diagnosis_view()

        return operator.diagnose(view=view)

    def _record_to_proposal(self, record: VariableRecord) -> ActionProposal:
        """Convert a VariableRecord into an ActionProposal."""
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
        """Create failed reasoning result."""
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
        """Record a new observation for this variable."""
        history, _ = self.history()
        stats = history.stats()
        if self.domain.validate(record.value, stats):
            self._history = self._history.new(record)
            return True
        return False

    def _record_reasoning(self, result: ReasoningResult) -> None:
        """Record a reasoning result."""
        self._reasoning_history = self._reasoning_history.new(result=result)
