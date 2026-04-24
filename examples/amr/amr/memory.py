"""Memory visualizer for Procela PoC."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import pandas as pd

from procela import (
    HypothesisRecord,
    HypothesisState,
    Key,
    KeyAuthority,
    Mechanism,
    ReasoningTask,
    Variable,
    VariableRecord,
)


@dataclass
class MemoryHypothesis:
    """Represents a single hypothesis from the variable memory."""

    mechanism: str | None
    value: Any
    confidence: float
    metadata: dict[str, Any]
    status: str


@dataclass
class MemoryConclusion:
    """Represents the resolved conclusion from the variable memory."""

    value: Any
    confidence: float
    policy: str | None
    considered_hypotheses: int = 0
    valid_hypotheses: int = 0


@dataclass
class MemoryRecord:
    """Complete record of all activity for a variable at one step."""

    step: int
    hypotheses: list[MemoryHypothesis]
    conclusion: MemoryConclusion | None
    pre_value: Any
    post_value: Any
    delta: float | None


class MemoryVisualizer:
    """
    Memory visualizer that utilizes variable.memory.

    This module provides complete mechanistic transparency for regulatory compliance.
    """

    def __init__(self, variables: list[Variable]) -> None:
        """
        Memory visualizer constructor.

        Parameters
        ----------
        variables : list[Variable]
            The list of variables to visualize.
        """
        self.variables = variables
        # self.audit_database = {}  # In production, would be a real database
        # self.cache = {}

    def get_history(
        self,
        variable: Variable,
        start_step: int = 0,
        end_step: int | None = None,
        source: Key | None = None,
        task: ReasoningTask | None = None,
        success: bool | None = None,
    ) -> list[MemoryRecord]:
        """
        Complete history of a variable's entire decision memory.

        Uses variable.memory.iter() to get ALL proposals and conclusions.

        Parameters
        ----------
        variable : Variable
            The variable to get history from.
            It should be included in writable variables of the executive.
        start_step : int
            The executive step to start from. Default is 0.
        end_step : int | None
            The optional executive step to end to. Default is None.
            When it is None, it means all up to the end.
        source : Key | None
            A optional source key.
        task : ReasoningTask | None
            A optonal reasoning task.
        success : bool | None
            Succeed or failed reasoning result.

        Returns
        -------
        list[MemoryRecord]
            The list to the record from the variable memories.
        """
        history: list[MemoryRecord] = []

        if variable.memory is None:
            return history

        count = variable.stats.count

        # Backward iter
        for step, (hypotheses, conclusion, reasoning) in enumerate(
            variable.memory.iter(source=source, task=task, success=success)
        ):
            if step == 0:
                candidates, resolved, _ = hypotheses, conclusion, reasoning
                continue

            if end_step and count - step > end_step:
                continue
            if count - step < start_step:
                break

            pre_value = conclusion.value if conclusion is not None else None
            post_value = resolved.value if resolved is not None else None
            delta = (
                post_value - pre_value
                if post_value is not None and pre_value is not None
                else None
            )
            history.append(
                MemoryRecord(
                    step=count - step,
                    hypotheses=self._extract_hypotheses(candidates),
                    conclusion=self._extract_conclusion(resolved, candidates),
                    pre_value=pre_value,
                    post_value=post_value,
                    delta=delta,
                )
            )
            candidates, resolved, _ = hypotheses, conclusion, reasoning

        history.reverse()
        return history

    def to_dataframe(
        self,
        start_step: int = 0,
        end_step: int | None = None,
        source: Key | None = None,
        task: ReasoningTask | None = None,
        success: bool | None = None,
    ) -> pd.DataFrame:
        """
        Get a DataFrame containing all relevant details from the executive.

        Parameters
        ----------
        start_step : int
            The executive step to start from. Default is 0.
        end_step : int | None
            The optional executive step to end to. Default is None.
            When it is None, it means all up to the end.
        source : Key | None
            A optional source key.
        task : ReasoningTask | None
            A optonal reasoning task.
        success : bool | None
            Succeed or failed reasoning result.

        Returns
        -------
        pd.DataFrame
            The DataFrame containing relevant details of the executive.
        """
        data = []

        for variable in self.variables:
            history = self.get_history(
                variable, start_step, end_step, source, task, success
            )
            for hist in history:
                data.append(
                    {
                        "name": variable.name,
                        "step": hist.step,
                        "value": hist.conclusion.value if hist.conclusion else None,
                        "confidence": (
                            hist.conclusion.confidence if hist.conclusion else None
                        ),
                        "policy": hist.conclusion.policy if hist.conclusion else None,
                        "considered_hypotheses": (
                            hist.conclusion.considered_hypotheses
                            if hist.conclusion
                            else None
                        ),
                        "valid_hypotheses": (
                            hist.conclusion.valid_hypotheses
                            if hist.conclusion
                            else None
                        ),
                        "pre_step_value": hist.pre_value,
                        "post_step_value": hist.post_value,
                        "delta_step_value": hist.delta,
                        **self._hypotheses_to_dict(hist.hypotheses),
                    }
                )

        return pd.DataFrame(data)

    def _extract_hypotheses(
        self, hypotheses: tuple[HypothesisRecord, ...]
    ) -> list[MemoryHypothesis]:
        """
        Extract the variable hypotheses details.

        Parameters
        ----------
        hypotheses : tuple[HypothesisRecord, ...]
            The hypotheses of a variable.

        Returns
        -------
        list[MemoryHypothesis]
            The list of hypotheses details.

        Notes
        -----
            Candidate record that is None is skipped.
        """
        proposals: list[MemoryHypothesis] = []

        if not hypotheses:
            return proposals

        for hypothesis in hypotheses:
            record = hypothesis.record
            if record is None:
                continue

            mech = KeyAuthority.resolve(key=record.source)
            if not isinstance(mech, Mechanism | None):
                continue

            proposals.append(
                MemoryHypothesis(
                    mechanism=mech.name if mech is not None else None,
                    value=record.value,
                    confidence=(
                        record.confidence if record.confidence is not None else 0.0
                    ),
                    metadata=record.metadata,
                    status=hypothesis.state.name,
                )
            )

        return proposals

    def _extract_conclusion(
        self,
        conclusion: VariableRecord | None,
        hypotheses: tuple[HypothesisRecord, ...],
    ) -> MemoryConclusion | None:
        """
        Extract the variable conclusion details.

        Parameters
        ----------
        conclusion : VariableRecord
            The conclusion details of a variable.
        hypotheses : tuple[HypothesisRecord, ...]
            The hypotheses of a variable.

        Returns
        -------
        MemoryConclusion | None
            The details from a variable conclusion record.
        """
        if conclusion is None:
            return None

        policy = KeyAuthority.resolve(conclusion.source)

        return MemoryConclusion(
            value=conclusion.value,
            confidence=(
                conclusion.confidence if conclusion.confidence is not None else 0.0
            ),
            policy=(
                policy.name if policy is not None and hasattr(policy, "name") else None
            ),
            considered_hypotheses=len(hypotheses),
            valid_hypotheses=len(
                [
                    hypothesis
                    for hypothesis in hypotheses
                    if hypothesis.state == HypothesisState.VALIDATED
                ]
            ),
        )

    def _hypotheses_to_dict(self, hypotheses: list[MemoryHypothesis]) -> dict[str, Any]:
        """
        Convert a list of MemoryHypothesis objects to a dictionary representation.

        Parameters
        ----------
        hypotheses : list[MemoryHypothesis]
            The list of hypotheses to transform into dict.

        Returns
        -------
        dict[str, Any]
            The dictionary from the the hypotheses.
        """
        result: dict[str, Any] = {}

        if not hypotheses:
            return result

        # Group hypotheses by source mechanism
        mechanism_hypotheses = defaultdict(list)

        for hyp in hypotheses:
            mechanism_hypotheses[hyp.mechanism].append(hyp)

        # Track total candidates across all mechanisms
        total_candidates = 0

        # For each mechanism, create indexed columns
        for mech_name, mech_hypotheses in mechanism_hypotheses.items():
            # Process each candidate from this mechanism
            for cand_index, hyp in enumerate(mech_hypotheses):
                # Create unique identifiers for this candidate
                candidate_id = f"{mech_name}_{cand_index}"

                # Value and confidence for this specific candidate
                result[f"cand_{candidate_id}_val"] = hyp.value
                result[f"cand_{candidate_id}_conf"] = hyp.confidence

                # Source mechanism information
                result[f"cand_{candidate_id}_mech"] = mech_name

                # Candidate status
                result[f"cand_{candidate_id}_status"] = hyp.status

                # Add metadata if available
                if hyp.metadata and isinstance(hyp.metadata, dict):
                    for key, value in hyp.metadata.items():
                        # Convert metadata to string for storage, handle special cases
                        if isinstance(value, (int, float, str, bool)):
                            result[f"cand_{candidate_id}_meta_{key}"] = value
                        else:
                            result[f"cand_{candidate_id}_meta_{key}"] = str(value)

                total_candidates += 1

            # Also create summary columns for the mechanism
            if mech_hypotheses:
                # Average value and confidence for this mechanism's candidates
                avg_value = sum(h.value for h in mech_hypotheses) / len(mech_hypotheses)
                avg_confidence = sum(h.confidence for h in mech_hypotheses) / len(
                    mech_hypotheses
                )

                result[f"mech_{mech_name}_avg_val"] = avg_value
                result[f"mech_{mech_name}_avg_conf"] = avg_confidence
                result[f"mech_{mech_name}_count"] = len(mech_hypotheses)

        # Add overall statistics
        result["total_candidates"] = total_candidates
        result["unique_mechanisms"] = len(mechanism_hypotheses)

        # Show the mechanism with the highest confidence candidate
        if hypotheses:
            # Find the candidate with highest confidence
            best_hyp = max(hypotheses, key=lambda h: h.confidence)

            result["mech"] = best_hyp.mechanism
            result["mech_val"] = best_hyp.value
            result["mech_conf"] = best_hyp.confidence

        return result
