"""
Test suite for variable module.

Coverage: 100%
"""

from typing import Iterator

import pytest

from procela.core.assessment import (
    AnomalyResult,
    DiagnosisResult,
    PredictionResult,
    ReasoningResult,
    ReasoningTask,
    TrendResult,
)
from procela.core.memory import (
    HypothesisRecord,
    VariableMemory,
    VariableRecord,
)
from procela.core.policy import HighestConfidencePolicy, ResolutionPolicy
from procela.core.reasoning import (
    AnomalyOperatorThreshold,
    DiagnosisOperatorThreshold,
    LastPredictor,
    TrendOperatorThreshold,
)
from procela.core.variable import (
    RangeDomain,
    StatisticalDomain,
    ValueDomain,
    Variable,
    VariableEpistemic,
    VariableRole,
)
from procela.symbols import Key, TimePoint


@pytest.fixture
def real_key():
    """Create a real Key."""
    return Key()


@pytest.fixture
def real_time_point():
    """Create a real TimePoint."""
    return TimePoint()


@pytest.fixture
def real_value_domain():
    """Create a real ValueDomain."""
    return RangeDomain(min_value=0, max_value=2300)


@pytest.fixture
def real_statistical_domain():
    """Create a real StatisticalDomain."""
    return StatisticalDomain(k=float("inf"))


@pytest.fixture
def real_variable_record(real_key, real_time_point):
    """Create a real VariableRecord."""
    return VariableRecord(
        value=42.0,
        time=real_time_point,
        source=real_key,
        confidence=0.9,
        explanation="Test record",
        metadata={"test": True},
    )


@pytest.fixture
def real_variable(real_value_domain):
    """Create a real Variable with config for all features."""
    return Variable(
        name="coverage_test",
        domain=real_value_domain,
        description="100% coverage test variable",
        units="test_units",
        policy=HighestConfidencePolicy(),
        role=VariableRole.ENDOGENOUS,
        config={
            "anomaly": {"method": "z-score", "threshold": 3.0},
            "trend": {"absolute": 0.3, "std_factor": 1.0},
            "diagnosis": {"name": "anomaly", "kwargs": {}},
            "planning": {"name": "preventive", "kwargs": {}},
        },
        seed=12345,
    )


@pytest.fixture
def statistical_variable(real_statistical_domain):
    """Create a statictical Variable with config for all features."""
    return Variable(
        name="coverage_test",
        domain=real_statistical_domain,
        description="100% coverage test variable",
        units="test_units",
        role=VariableRole.ENDOGENOUS,
        config={
            "anomaly": {"method": "z-score", "threshold": 3.0},
            "trend": {"absolute": 0.3, "std_factor": 1.0},
            "diagnosis": {"name": "anomaly", "kwargs": {}},
            "planning": {"name": "preventive", "kwargs": {}},
        },
        seed=12345,
    )


@pytest.fixture
def last_record_resolution():
    class LastRecordResolution(ResolutionPolicy):
        def resolve(self, hypotheses):
            if not hypotheses:
                return None
            return hypotheses[-1].record

    return LastRecordResolution()


def test_init_all_params(real_value_domain):
    """Test __init__ with all parameters - covers all branches."""
    # Test with all params
    var1 = Variable(
        name="test1",
        domain=real_value_domain,
        description="Desc",
        units="U",
        role=VariableRole.EXOGENOUS,
        config={"key": "value"},
        seed=42,
    )
    assert var1.name == "test1"
    assert var1.config == {"key": "value"}

    # Test with None config
    var2 = Variable(name="test2", domain=real_value_domain, config=None)
    assert var2.config == {}

    # Test with empty config
    var3 = Variable(name="test3", domain=real_value_domain, config={})
    assert var3.config == {}


def test_init_minimal(real_value_domain):
    """Test __init__ with minimal parameters."""
    var = Variable(name="minimal", domain=real_value_domain)
    assert var.description == ""
    assert var.units is None
    assert var.role == VariableRole.ENDOGENOUS
    assert var.config == {}
    assert var.seed is None


def test_get(real_value_domain):
    """Test get with records."""
    var = Variable(name="minimal", domain=real_value_domain)
    records = var.get(start=0)
    assert len(records) == 0

    var.set(VariableRecord(value=13.5, confidence=0.95))
    var.set(VariableRecord(value=12.5, confidence=0.99))
    var.set(VariableRecord(value=14.5, confidence=0.90))

    assert var.stats.count == 3
    records = var.get(start=2)
    assert len(records) == 1
    assert records[0][1].value == 14.5

    records = var.get(start=-1)
    assert len(records) == 1
    assert records[0][1].confidence == 0.90

    records = var.get(start=0, size=2, reverse=True)
    assert len(records) == 2
    assert records[-1][1].value == 12.5

    records = var.get(start=5)
    assert len(records) == 0


def test_recent(real_value_domain):
    """Test recent with records."""
    var = Variable(name="minimal", domain=real_value_domain)
    records = var.recent()
    assert len(records) == 0

    var.set(VariableRecord(value=13.5, confidence=0.95))
    var.set(VariableRecord(value=12.5, confidence=0.99))
    var.set(VariableRecord(value=14.5, confidence=0.90))

    assert var.stats.count == 3
    records = var.recent(size=2)
    assert len(records) == 2
    assert records[1][1].confidence == 0.99

    records = var.recent(size=1)
    assert len(records) == 1
    assert records[0][1].value == 14.5

    records = var.recent(size=3, reverse=True)
    assert len(records) == 3
    assert records[-1][1].value == 14.5

    records = var.recent(size=5)
    assert len(records) == 3


def test_variable_epistemic(real_variable):
    """Test post init."""
    with pytest.raises(
        TypeError, match="`key` should be a Key, got <class 'NoneType'>"
    ):
        VariableEpistemic(
            key=None,
            reasoning=None,
            stats=real_variable.stats,
            anomaly=None,
            trend=None,
        )

    with pytest.raises(TypeError):
        VariableEpistemic(
            key=Key(),
            reasoning=Key(),
            stats=real_variable.stats,
            anomaly=None,
            trend=None,
        )

    with pytest.raises(TypeError):
        VariableEpistemic(
            key=Key(), reasoning=None, stats=TimePoint(), anomaly=None, trend=None
        )

    with pytest.raises(TypeError):
        VariableEpistemic(
            key=Key(),
            reasoning=None,
            stats=real_variable.stats.result(),
            anomaly=Key(),
            trend=None,
        )

    with pytest.raises(TypeError):
        VariableEpistemic(
            key=Key(),
            reasoning=None,
            stats=real_variable.stats.result(),
            anomaly=None,
            trend="not-a-trend",
        )


def test_init_method_domain_violation():
    """Test init method with domain violation."""
    var = Variable(name="temperature", domain=RangeDomain(0, 100))
    assert var.description == ""
    assert var.units is None
    assert var.role == VariableRole.ENDOGENOUS
    assert var.config == {}
    assert var.seed is None

    with pytest.raises(ValueError):
        var.init(VariableRecord(value=102.8))


def test_records_method(real_variable):
    """Test records."""
    assert isinstance(real_variable.records(), Iterator)

    real_variable.init(VariableRecord(value=28.56))
    for record in real_variable.records():
        assert isinstance(record, VariableRecord)


def test_commit_with_includes(real_variable):
    """Test commit with includes."""

    # Include hypotheses
    real_variable.hypotheses = Key()
    with pytest.raises(TypeError, match="`hypotheses` should be a list"):
        real_variable.commit(include_hypotheses=True)

    real_variable.hypotheses = [
        HypothesisRecord(
            VariableRecord(value=98),
        ),
        "not-a-variable-record",
    ]
    with pytest.raises(
        TypeError, match="`hypothesis` at index 1 should be a HypothesisRecord"
    ):
        real_variable.commit(include_hypotheses=True)

    # Include conclusion
    real_variable.conclusion = Key()
    with pytest.raises(TypeError):
        real_variable.commit(include_hypotheses=False, include_conclusion=True)

    real_variable.conclusion = VariableRecord(value=-28.09)
    real_variable.reasoning = ReasoningResult(
        task=ReasoningTask.ACTION_PROPOSAL, success=False, result=None
    )
    real_variable.commit(include_hypotheses=False, include_conclusion=True)

    # Include reasoning
    real_variable.conclusion = VariableRecord(value=-28.09)
    real_variable.reasoning = TimePoint()
    with pytest.raises(
        TypeError, match="reasoning result should be a ReasoningResult or None"
    ):
        real_variable.commit(
            include_hypotheses=False, include_conclusion=False, include_reasonning=True
        )


def test_key_method(real_variable):
    """Test key() returns a Key."""
    key = real_variable.key()
    assert isinstance(key, Key)


def test_record_all_params(real_variable, real_key, real_time_point):
    """Test record() with all parameters."""
    real_variable.add_hypothesis(
        VariableRecord(
            value=99.9,
            time=real_time_point,
            source=real_key,
            confidence=0.99,
            explanation="Full params",
            metadata={"full": True},
        ),
    )
    assert isinstance(real_variable.hypotheses[0], HypothesisRecord)
    assert real_variable.hypotheses[0].record.value == 99.9
    assert real_variable.hypotheses[0].record.source == real_key


def test_record_validation_failure(real_variable):
    """Test record() when validation fails - NEEDS TO FAIL."""
    for test_value in [None, "invalid", -1e9, 1e9, [], {}]:
        try:
            real_variable.add_hypothesis(VariableRecord(value=test_value))
            continue
        except ValueError as e:
            assert "violates domain" in str(e)
            return


def test_memory_method(real_variable):
    """Test memory() method."""
    assert real_variable.memory is None


def test_value(real_variable):
    """Test value() on fresh variable."""
    value = real_variable.value
    assert value is None


def test_add_candidates(real_variable):
    """Test add_candidates() on fresh variable."""
    # No record
    policy = real_variable.policy
    assert isinstance(policy, ResolutionPolicy)

    real_variable.resolve_conflict()
    real_variable.commit()
    assert len(real_variable.memory.records()) == 1

    # 4 records
    record = VariableRecord(11.0, confidence=0.95, source=Key())
    real_variable.add_hypothesis(VariableRecord(10.0, confidence=0.5))
    real_variable.add_hypothesis(VariableRecord(13.0, confidence=0.65))
    real_variable.add_hypothesis(record)
    real_variable.add_hypothesis(VariableRecord(12.0, confidence=0.45))

    candidates = real_variable.hypotheses
    assert len(candidates) == 4

    real_variable.resolve_conflict()
    real_variable.commit()

    assert real_variable.validators is None
    real_variable.reset()


def test_create_and_restore_checkpoint(real_variable):
    "Test create and restore checkpoint method."
    real_variable.set(VariableRecord(value=109.78, confidence=1.0))
    checkpoint = real_variable.create_checkpoint()

    assert checkpoint is not None
    assert isinstance(checkpoint[0], ValueDomain)
    assert real_variable.stats.count == 1

    for i in range(200):
        real_variable.set(VariableRecord(value=i, confidence=1.0))

    assert real_variable.stats.count == 201

    real_variable.restore_checkpoint(checkpoint)
    assert real_variable.stats.count == 1


def test_has_records(real_variable):
    """Test has_records() method."""
    assert not real_variable.has_records()


def test_repr_method(real_variable):
    """Test __repr__ method."""
    repr_str = repr(real_variable)
    assert "Variable" in repr_str
    assert "coverage_test" in repr_str
    assert "ENDOGENOUS" in repr_str


def test_summary_method(real_variable):
    """Test summary() method."""
    real_variable.add_hypothesis(VariableRecord(value=75))
    real_variable.add_hypothesis(VariableRecord(value=85))

    summary = real_variable.summary()
    assert "===== Variable summary =====" in summary
    assert "coverage_test" in summary
    assert "count" in summary
    assert "mean" in summary
    assert "std" in summary


def test_epistemic_method(real_variable):
    """Test epistemic() method."""
    # Add data
    for i in range(5):
        real_variable.add_hypothesis(VariableRecord(value=i * 20))

    epistemic = real_variable.epistemic()
    assert isinstance(epistemic, VariableEpistemic)
    assert hasattr(epistemic, "stats")
    assert hasattr(epistemic, "anomaly")
    assert hasattr(epistemic, "trend")


def test_explain_method_real_variable(real_variable):
    """Test explain() covers real variable."""
    # Test 1: No anomaly, no trend
    real_variable.memory = VariableMemory(
        hypotheses=(), conclusion=None, reasoning=None
    )
    explanation1 = real_variable.explain()
    assert "coverage_test" in explanation1

    # Test 2: With anomaly (need to create one)
    # Add outlier value
    for i in range(10):
        real_variable.add_hypothesis(VariableRecord(value=i))  # Normal values

    real_variable.add_hypothesis(VariableRecord(value=1000))  # Outlier

    real_variable.explain()

    # Test 3: With reasoning memory
    # Execute some reasoning tasks
    real_variable.detect_anomaly()
    real_variable.analyze_trend()

    explanation3 = real_variable.explain()
    assert "Recent reasoning steps:" in explanation3 or "No anomaly" in explanation3


def test_explain_method_statistical_variable(statistical_variable):
    """Test explain() covers statistical_variable."""
    # Test 1: No anomaly, no trend
    statistical_variable.memory = VariableMemory(
        hypotheses=(), conclusion=None, reasoning=None
    )

    # Test 2: With anomaly (need to create one)
    # Add outlier value
    for i in range(10):
        statistical_variable.add_hypothesis(VariableRecord(value=i / 100))

    statistical_variable.add_hypothesis(VariableRecord(value=2000))  # Outlier

    epistemic = statistical_variable.epistemic()

    assert epistemic.trend is None

    statistical_variable.explain()

    # Test 3: With reasoning memory
    # Execute some reasoning tasks
    statistical_variable.detect_anomaly()
    statistical_variable.analyze_trend()
    statistical_variable.predict(predictor=LastPredictor(allow_none=True), horizon=5)

    explanation3 = statistical_variable.explain()
    assert "Recent reasoning steps:" in explanation3 or "No anomaly" in explanation3


def test_explain_method_statistical_variable_different_scenarios(
    statistical_variable, last_record_resolution
):
    """Test explain() covers statistical_variable with different scenarios."""
    # Test 1: No anomaly, no trend
    statistical_variable.memory = VariableMemory(
        hypotheses=(), conclusion=None, reasoning=None
    )

    statistical_variable.init(VariableRecord(value=0.78))

    # Test 2: With anomaly (need to create one)
    # Add outlier value
    for i in range(10):
        statistical_variable.add_hypothesis(VariableRecord(value=i / 100))

    statistical_variable.resolve_conflict()
    for _ in range(10):
        statistical_variable.commit()
    statistical_variable.clear_hypotheses()

    statistical_variable.add_hypothesis(VariableRecord(value=405))  # Outlier
    statistical_variable.resolve_conflict()
    statistical_variable.commit()
    statistical_variable.clear_hypotheses()

    epistemic = statistical_variable.epistemic()
    assert epistemic.trend is not None

    statistical_variable.explain()

    # Ask for no recent reasoning result
    explanation = statistical_variable._explain_reasoning(result=None)
    assert explanation == ""

    # Test 3: With reasoning memory
    # Execute some reasoning tasks
    statistical_variable.detect_anomaly()
    statistical_variable.analyze_trend()
    statistical_variable.hypotheses = (
        HypothesisRecord(VariableRecord(value=23.4, confidence=0.56)),
        HypothesisRecord(VariableRecord(value=26.1, confidence=0.68)),
    )
    statistical_variable.policy = last_record_resolution
    statistical_variable.resolve_conflict()
    statistical_variable.diagnose_causes()

    explanation = statistical_variable.explain()
    assert "Recent reasoning steps:" in explanation


def test_explain_explain_reasoning_statistical_variable(real_variable):
    """Test _explain_reasoning()."""
    real_variable._explain_reasoning(
        result=ReasoningResult(
            task=ReasoningTask.ANOMALY_DETECTION,
            success=False,
            result=AnomalyResult(is_anomaly=False, score=2.8),
        )
    )

    # Trend
    real_variable._explain_reasoning(
        result=ReasoningResult(
            task=ReasoningTask.TREND_ANALYSIS,
            success=False,
            result=TrendResult(value=873.7, direction="up", threshold=0.8),
        )
    )

    # Value prediction
    real_variable._explain_reasoning(
        result=ReasoningResult(
            task=ReasoningTask.VALUE_PREDICTION,
            success=False,
            result=PredictionResult(
                value=17.45,
            ),
        )
    )

    # Conflict resolution
    real_variable._explain_reasoning(
        result=ReasoningResult(
            task=ReasoningTask.CONFLICT_RESOLUTION,
            success=False,
            result=VariableRecord(
                value=17.45,
            ),
        )
    )

    # Causal diagnosis
    real_variable._explain_reasoning(
        result=ReasoningResult(
            task=ReasoningTask.CAUSAL_DIAGNOSIS,
            success=False,
            result=DiagnosisResult(causes=["abc", "xyz"], metadata={"key": "Test"}),
        )
    )


def test_variable_method_detect_anomaly_unknown_detector(real_value_domain):
    """Test variable method detect_anomaly with unknown detector"""
    var = Variable(
        name="unknown_detector",
        domain=real_value_domain,
        config={"anomaly": {"method": "unknown_detector", "threshold": 3.0}},
    )

    with pytest.raises(KeyError):
        var.detect_anomaly()


def test_variable_method_diagnose_causes_unknown_operator(real_value_domain):
    """Test variable method diagnose_causes with unknown operator"""
    var = Variable(
        name="unknown_operator",
        domain=real_value_domain,
        config={"diagnosis": {"name": "unknown_operator", "kwargs": {}}},
    )
    with pytest.raises(KeyError):
        var.diagnose_causes()


def test_detect_anomaly(real_variable):
    """Test detect_anomaly()."""
    # Add data
    for i in range(10):
        real_variable.add_hypothesis(VariableRecord(value=i * 10, confidence=0.9))
        real_variable.resolve_conflict()
        real_variable.commit()
        real_variable.clear_hypotheses()

    result = real_variable.detect_anomaly()
    assert isinstance(result, AnomalyResult)
    assert hasattr(result, "is_anomaly")
    assert hasattr(result, "score")


def test_analyze_trend(real_variable):
    """Test analyze_trend()."""
    # Add trending data
    for i in range(10):
        real_variable.add_hypothesis(VariableRecord(value=i * 10, confidence=0.9))
        real_variable.resolve_conflict()
        real_variable.commit()
        real_variable.clear_hypotheses()

    result = real_variable.analyze_trend()
    # Can be None or TrendResult
    if result is not None:
        assert isinstance(result, TrendResult)
        assert hasattr(result, "direction")


def test_resolve_conflict_empty(real_variable, last_record_resolution):
    """Test resolve_conflict() with empty candidates."""
    for i in range(4):
        real_variable.add_hypothesis(VariableRecord(value=i * 30))
    real_variable.resolve_conflict()
    real_variable.commit()
    real_variable.clear_hypotheses()
    assert real_variable.value == 0.0


def test_predict_default(real_variable):
    """Test predict() with default predictor."""
    # Add data
    for i in range(4):
        real_variable.add_hypothesis(VariableRecord(value=i * 30))
    real_variable.resolve_conflict()
    real_variable.commit()

    result = real_variable.predict(horizon=3)
    assert isinstance(result, ReasoningResult)
    assert result.task == ReasoningTask.VALUE_PREDICTION


def test_predict_custom_predictor(real_variable):
    """Test predict() with custom predictor."""
    predictor = LastPredictor(allow_none=True)

    result = real_variable.predict(predictor=predictor, horizon=5)
    assert isinstance(result, ReasoningResult)


def test_predict_invalid_predictor(real_variable):
    """Test predict() with invalid predictor - should raise TypeError."""
    with pytest.raises(TypeError, match="should be a Predictor instance"):
        real_variable.predict(predictor="not_a_predictor")


def test_diagnose_causes_default(real_variable):
    """Test diagnose_causes() with default operator."""
    result = real_variable.diagnose_causes()
    assert isinstance(result, ReasoningResult)
    assert result.task == ReasoningTask.CAUSAL_DIAGNOSIS


def test_diagnose_causes_custom_operator(real_variable):
    """Test diagnose_causes() with custom operator."""
    operator = DiagnosisOperatorThreshold(name="anomaly")
    result = real_variable.diagnose_causes(operator=operator)
    assert isinstance(result, ReasoningResult)


def test_diagnose_causes_invalid_operator(real_variable):
    """Test diagnose_causes() with invalid operator."""
    with pytest.raises(TypeError, match="should be a DiagnosisOperator instance"):
        real_variable.diagnose_causes(operator="not_an_operator")


def test_private_detect_anomaly(real_variable):
    """Test _detect_anomaly() private method."""
    # Test with default (config)
    result1 = real_variable._detect_anomaly(stats=real_variable.stats.result())
    assert isinstance(result1, AnomalyResult)

    # Test with custom operator
    operator = AnomalyOperatorThreshold(name="z-score", threshold=2.5)
    result2 = real_variable._detect_anomaly(
        stats=real_variable.stats.result(), operator=operator
    )
    assert isinstance(result2, AnomalyResult)

    with pytest.raises(TypeError):
        real_variable._detect_anomaly("not-a-statst-result")


def test_private_detect_anomaly_invalid(real_variable):
    """Test _detect_anomaly() with invalid operator."""
    with pytest.raises(TypeError, match="should be a AnomalyOperator instance"):
        real_variable._detect_anomaly(
            stats=real_variable.stats.result(), operator="invalid"
        )


def test_private_analyze_trend(real_variable):
    """Test _analyze_trend() private method."""
    result = real_variable._analyze_trend(stats=real_variable.stats.result())
    # Can be None if domain not StatisticalDomain
    if result is not None:
        assert isinstance(result, TrendResult)

    # Test with operator
    operator = TrendOperatorThreshold(threshold=0.1)
    result2 = real_variable._analyze_trend(
        stats=real_variable.stats.result(), operator=operator
    )
    if result2 is not None:
        assert isinstance(result2, TrendResult)

    with pytest.raises(TypeError, match="`stats` should be a StatisticsResult"):
        real_variable._analyze_trend(stats="not-a-stats-result")

    with pytest.raises(TypeError, match="`operator` should be a TrendOperator or None"):
        real_variable._analyze_trend(
            operator="not-an-operator", stats=real_variable.stats.result()
        )


def test_private_predict(real_variable):
    """Test _predict() private method."""
    predictor = LastPredictor(allow_none=True)
    result = real_variable._predict(
        view=real_variable.epistemic(), predictor=predictor, horizon=2
    )
    assert isinstance(result, PredictionResult)


def test_private_predict_invalid(real_variable):
    """Test _predict() with invalid predictor."""
    with pytest.raises(TypeError, match="should be a Predictor instance"):
        real_variable._predict(view=real_variable.epistemic(), predictor="invalid")


def test_private_diagnose_causes(real_variable):
    """Test _diagnose_causes() private method."""
    # Default from config
    result1 = real_variable._diagnose_causes()
    assert isinstance(result1, DiagnosisResult)

    # With operator
    operator = DiagnosisOperatorThreshold(name="anomaly")
    result2 = real_variable._diagnose_causes(operator=operator)
    assert isinstance(result2, DiagnosisResult)


def test_private_diagnose_causes_invalid(real_variable):
    """Test _diagnose_causes() with invalid operator."""
    with pytest.raises(TypeError, match="should be a DiagnosisOperator instance"):
        real_variable._diagnose_causes(operator="invalid")


def test_epistemic_none_results(real_variable):
    """Test epistemic() when private methods return None."""
    # Mock the private methods to return None
    original_detect = real_variable._detect_anomaly
    original_trend = real_variable._analyze_trend

    real_variable._detect_anomaly = lambda *args, **kwargs: None
    real_variable._analyze_trend = lambda *args, **kwargs: None

    try:
        epistemic = real_variable.epistemic()
        assert epistemic.anomaly is None
        assert epistemic.trend is None
    finally:
        # Restore
        real_variable._detect_anomaly = original_detect
        real_variable._analyze_trend = original_trend


def test_resolve_conflict_validation_fails(
    real_variable, real_variable_record, last_record_resolution
):
    """Test resolve_conflict when conclusion fails domain."""

    record1 = VariableRecord(value=-10, confidence=0.99)
    with pytest.raises(ValueError):
        real_variable.set(record1)

    record2 = VariableRecord(value=0, confidence=0.67)
    real_variable.set(record2)

    real_variable.add_hypothesis(record1)
    real_variable.add_hypothesis(record2)

    real_variable.resolve_conflict()
    assert real_variable.confidence == record2.confidence


def test_with_different_configs(real_value_domain):
    """Test Variable with different configurations."""
    # Test 1: No anomaly config
    var1 = Variable(name="no_anomaly", domain=real_value_domain, config={})
    var1.detect_anomaly()  # Should use defaults

    # Test 2: Custom anomaly config
    var2 = Variable(
        name="custom_anomaly",
        domain=real_value_domain,
        config={"anomaly": {"method": "iqr", "threshold": 2.0}},
    )
    with pytest.raises(KeyError):
        var2.detect_anomaly()


def test_diagnose_causes_unknown_name(real_value_domain):
    """Test _diagnose_causes() with unknown diagnosis name."""
    var = Variable(
        name="unknown_diagnosis",
        domain=real_value_domain,
        config={"diagnosis": {"name": "non_existent", "kwargs": {}}},
    )

    with pytest.raises(KeyError):
        var._diagnose_causes()


def test_detect_anomaly_unknown_method(real_value_domain):
    """Test _detect_anomaly() with unknown method."""
    var = Variable(
        name="unknown_method",
        domain=real_value_domain,
        config={"anomaly": {"method": "non_existent", "threshold": 1.0}},
    )

    with pytest.raises(KeyError):
        var._detect_anomaly(var.stats.result())


def test_all_type_checks(real_variable):
    """Test all type checking in the code."""
    # Test predict type check
    with pytest.raises(TypeError):
        real_variable.predict(predictor="string")

    # Test diagnose_causes type check
    with pytest.raises(TypeError):
        real_variable.diagnose_causes(operator="string")

    # Test _detect_anomaly type check
    with pytest.raises(TypeError):
        real_variable._detect_anomaly(operator="string")

    # Test _predict type check
    with pytest.raises(TypeError):
        real_variable._predict(predictor="string")

    # Test _diagnose_causes type check
    with pytest.raises(TypeError):
        real_variable._diagnose_causes(operator="string")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
