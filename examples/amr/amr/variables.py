"""Variables for Procela PoC."""

from procela import (
    KeyAuthority,
    RangeDomain,
    RealDomain,
    Variable,
    VariableRecord,
    WeightedConfidencePolicy,
)

NO_SOURCE_KEY = KeyAuthority.issue(owner=None)

# Observable measurements
colonized = Variable(
    name="colonized",
    domain=RangeDomain(0.0, 100.0),
    description="Number of colonized patients",
    units="patients",
    policy=None,
)

antibiotic_usage = Variable(
    name="antibiotic_usage",
    domain=RangeDomain(0.0, 50.0),
    description="Antibiotic defined daily doses",
    units="DDD",
    policy=None,
)

environmental_load = Variable(
    name="environmental_load",
    domain=RangeDomain(0.0, 100.0),
    description="Environmental contamination index",
    units="index",
    policy=None,
)

# Intervention variable (where policies compete)
intervention_code = Variable(
    name="intervention_code",
    domain=RangeDomain(0.0, 3.0),
    description="Current intervention (0=none, 1=isolation, 2=cleaning, 3=stewardship)",
    units="code",
    policy=WeightedConfidencePolicy(),
)

# Predictions with intervention
predicted_colonized = Variable(
    name="predicted_colonized",
    domain=RangeDomain(0.0, 100.0),
    description="Predicted colonized patients next step with intervention",
    units="patients",
    policy=WeightedConfidencePolicy(),
)

# Predictions without intervention
baseline_colonized = Variable(
    name="baseline_colonized",
    domain=RangeDomain(0.0, 100.0),
    description="Predicted colonized patients next step without intervention",
    units="patients",
    policy=WeightedConfidencePolicy(),
)

# Regime
regime = Variable(
    name="regime",
    domain=RangeDomain(0.0, 2.0),
    description="True regime (0=selection, 1=environment, 2=contact)",
    units="code",
    policy=None,
)

# Prediction errors
error_colonized = Variable(
    name="error_colonized",
    domain=RealDomain(),
    description="Predicted colonized patients error",
    units="patients",
    policy=None,
)

# Prediction without intervention errors
error_baseline_colonized = Variable(
    name="error_baseline_colonized",
    domain=RealDomain(),
    description="Predicted colonized patients error without intervention",
    units="patients",
    policy=None,
)

# Experiment status
experiment_status = Variable(
    name="experiment_status",
    domain=RangeDomain(0.0, 1.0),  # dummy domain
    description="Records experiment status and metadata",
    policy=None,
)

# For conveniance
ALL_VARIABLES = [
    colonized,
    antibiotic_usage,
    environmental_load,
    intervention_code,
    predicted_colonized,
    baseline_colonized,
    regime,
    error_colonized,
    error_baseline_colonized,
]


# Initialize variables
def init_variables() -> None:
    """Initialize variables."""
    colonized.init(VariableRecord(value=10.0, confidence=1.0, source=NO_SOURCE_KEY))
    antibiotic_usage.init(
        VariableRecord(value=20.0, confidence=1.0, source=NO_SOURCE_KEY)
    )
    environmental_load.init(
        VariableRecord(value=10.0, confidence=1.0, source=NO_SOURCE_KEY)
    )
    intervention_code.init(
        VariableRecord(value=0.0, confidence=1.0, source=NO_SOURCE_KEY)
    )
    regime.set(VariableRecord(value=0.0, confidence=1.0, source=NO_SOURCE_KEY))


# Reset all variables
def reset_variables() -> None:
    """
    Rset all the variables.

    Useful across different experiments and in the context of a Monte Carlo study.
    """
    for var in ALL_VARIABLES:
        var.reset()

    experiment_status.reset()

    intervention_code.policy = WeightedConfidencePolicy()
    predicted_colonized.policy = WeightedConfidencePolicy()
    baseline_colonized.policy = WeightedConfidencePolicy()
