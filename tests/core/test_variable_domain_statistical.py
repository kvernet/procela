"""Test suite for StatisticalDomain class."""

from typing import Any

import pytest

from procela.core.assessment import StatisticsResult
from procela.core.variable import HistoryStatistics, StatisticalDomain
from procela.symbols import Key


class TestStatisticalDomain:
    """Test cases for StatisticalDomain class."""

    def build_history_statistics(
        self,
        count: int = 1,
        sum: float | None = None,
        sumsq: float | None = None,
        min: float | None = None,
        max: float | None = None,
        last_value: float | None = None,
        confidence_sum: float | None = None,
        ewma: float | None = None,
        sources: frozenset[Key] = frozenset(),
    ):
        return HistoryStatistics(
            count=count,
            sum=sum,
            sumsq=sumsq,
            min=min,
            max=max,
            last_value=last_value,
            confidence_sum=confidence_sum,
            ewma=ewma,
            sources=sources,
        )

    def test_initialization_default_parameters(self):
        """Test initialization with default parameters."""
        domain = StatisticalDomain()
        assert domain.k == 3.0
        assert domain.name == ""

    def test_initialization_with_custom_k(self):
        """Test initialization with custom k value."""
        domain = StatisticalDomain(k=2.5)
        assert domain.k == 2.5
        assert domain.name == ""

    def test_initialization_with_name(self):
        """Test initialization with custom name."""
        domain = StatisticalDomain(name="quality_domain")
        assert domain.k == 3.0
        assert domain.name == "quality_domain"

    def test_initialization_with_all_parameters(self):
        """Test initialization with all parameters."""
        domain = StatisticalDomain(k=2.0, name="two_sigma")
        assert domain.k == 2.0
        assert domain.name == "two_sigma"

    def test_initialization_with_zero_k(self):
        """Test initialization with k=0."""
        domain = StatisticalDomain(k=0.0)
        assert domain.k == 0.0

    def test_initialization_with_negative_k_raises_error(self):
        """Test that negative k raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            StatisticalDomain(k=-1.0)
        assert "k must be non-negative, got -1.0" in str(exc_info.value)

    def test_initialization_with_non_numeric_k_raises_error(self):
        """Test that non numeric k raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            StatisticalDomain(k="not_a_number")
        assert "k must be numeric, got not_a_number" in str(exc_info.value)

    def test_validate_with_complete_stats_inside_bounds(self):
        """Test validation with complete stats, value inside bounds."""
        domain = StatisticalDomain(k=2.0)
        stats = self.build_history_statistics(count=2, sum=200.0, sumsq=20200.0)
        assert domain.validate(95, stats.stats()) is True
        assert domain.validate(105, stats.stats()) is True
        assert domain.validate(80, stats.stats()) is True  # Lower bound inclusive
        assert domain.validate(120, stats.stats()) is True  # Upper bound inclusive

    def test_validate_with_complete_stats_outside_bounds(self):
        """Test validation with complete stats, value outside bounds."""
        domain = StatisticalDomain(k=2.0)
        stats = self.build_history_statistics(count=2, sum=200.0, sumsq=20200.0)
        assert domain.validate(79, stats.stats()) is False  # Below lower bound
        assert domain.validate(121, stats.stats()) is False  # Above upper bound

    def test_validate_without_stats(self):
        """Test validation without stats (should pass) for numeric values."""
        domain = StatisticalDomain(k=2.0)
        assert domain.validate(999) is True
        assert domain.validate("anything") is False
        assert domain.validate(None) is False

    def test_validate_with_none_stats(self):
        """Test validation with None stats."""
        domain = StatisticalDomain(k=2.0)
        assert domain.validate(50, None) is True

    def test_validate_with_incomplete_stats_missing_mean(self):
        """Test validation with stats missing mean."""
        domain = StatisticalDomain(k=2.0)
        # Missing mean
        stats = self.build_history_statistics(sumsq=10.0)
        assert domain.validate(50, stats.stats()) is True

    def test_validate_with_incomplete_stats_missing_std(self):
        """Test validation with stats missing std."""
        domain = StatisticalDomain(k=2.0)
        # Missing std
        stats = self.build_history_statistics(
            sum=100.0,
        )
        assert domain.validate(50, stats.stats()) is True

    def test_validate_with_empty_stats(self):
        """Test validation with empty stats dict."""
        domain = StatisticalDomain(k=2.0)
        assert domain.validate(50, {}) is True

    def test_validate_with_different_k_values(self):
        """Test validation with different k values."""
        stats = self.build_history_statistics(count=2, sum=200.0, sumsq=20200.0)

        # k=1.0: bounds 90-110
        domain1 = StatisticalDomain(k=1.0)
        assert domain1.validate(95, stats.stats()) is True
        assert domain1.validate(85, stats.stats()) is False

        # k=2.0: bounds 80-120
        domain2 = StatisticalDomain(k=2.0)
        assert domain2.validate(85, stats.stats()) is True
        assert domain2.validate(75, stats.stats()) is False

        # k=3.0: bounds 70-130
        domain3 = StatisticalDomain(k=3.0)
        assert domain3.validate(75, stats.stats()) is True
        assert domain3.validate(65, stats.stats()) is False

    def test_validate_non_numeric_value_raises_error(self):
        """Test that non-numeric value raises TypeError during comparison."""
        domain = StatisticalDomain(k=2.0)
        stats = self.build_history_statistics(sum=100.0, sumsq=10.0)

        assert not domain.validate("not_a_number", stats.stats())

    def test_validate_with_zero_std(self):
        """Test validation with zero standard deviation."""
        domain = StatisticalDomain(k=2.0)
        stats = self.build_history_statistics(count=2, sum=100.0, sumsq=5000.0)
        assert domain.validate(50, stats.stats()) is True
        assert domain.validate(50.0, stats.stats()) is True
        assert domain.validate(51, stats.stats()) is False
        assert domain.validate(49, stats.stats()) is False

    def test_explain_with_complete_stats(self):
        """Test explanation with complete stats."""
        domain = StatisticalDomain(k=2.0)
        stats = self.build_history_statistics(count=2, sum=200.0, sumsq=20200.0)

        explanation = domain.explain(95, stats.stats())
        assert "Value 95 is within [80.0, 120.0]." == explanation

        # Different value, same bounds
        explanation2 = domain.explain(125, stats.stats())
        assert "Value 125 is not within [80.0, 120.0]." == explanation2

    def test_explain_without_stats(self):
        """Test explanation without stats."""
        domain = StatisticalDomain(k=2.0)
        explanation = domain.explain(50)
        assert explanation == "Insufficient history for statistical validation."

    def test_explain_with_none_stats(self):
        """Test explanation with None stats."""
        domain = StatisticalDomain(k=2.0)
        explanation = domain.explain(50, None)
        assert explanation == "Insufficient history for statistical validation."

    def test_explain_with_incomplete_stats(self):
        """Test explanation with stats missing mean."""
        domain = StatisticalDomain(k=2.0)
        stats = self.build_history_statistics(count=1, sum=2.0, sumsq=10.0)
        explanation = domain.explain(50, stats.stats())
        assert explanation == "Insufficient history for statistical validation."

    def test_explain_with_incomplete_stats_missing_std(self):
        """Test explanation with stats missing std."""
        domain = StatisticalDomain(k=2.0)
        stats = self.build_history_statistics(
            sum=100.0,
        )
        explanation = domain.explain(50, stats.stats())
        assert explanation == "Insufficient history for statistical validation."

    def test_explain_with_empty_stats(self):
        """Test explanation with empty stats dict."""
        domain = StatisticalDomain(k=2.0)
        explanation = domain.explain(50, {})
        assert explanation == "Insufficient history for statistical validation."

    def test_explain_with_different_k_values(self):
        """Test explanation with different k values."""
        stats = self.build_history_statistics(count=2, sum=200.0, sumsq=20200.0)

        domain1 = StatisticalDomain(k=1.0)
        exp1 = domain1.explain(95, stats.stats())
        assert exp1 == "Value 95 is within [90.0, 110.0]."

        domain2 = StatisticalDomain(k=2.0)
        exp2 = domain2.explain(95, stats.stats())
        assert exp2 == "Value 95 is within [80.0, 120.0]."

        domain3 = StatisticalDomain(k=3.0)
        exp3 = domain3.explain(95, stats.stats())
        assert exp3 == "Value 95 is within [70.0, 130.0]."

    def test_explain_with_k_zero(self):
        """Test explanation with k=0."""
        domain = StatisticalDomain(k=0.0)
        stats = self.build_history_statistics(count=2, sum=100.0, sumsq=5000.0)
        explanation = domain.explain(50, stats.stats())
        assert explanation == "Value 50 is within [50.0, 50.0]."

    def test_explain_with_zero_std(self):
        """Test explanation with zero standard deviation."""
        domain = StatisticalDomain(k=2.0)
        stats = self.build_history_statistics(count=2, sum=100.0, sumsq=5000.0)
        explanation = domain.explain(50, stats.stats())
        assert explanation == "Value 50 is within [50.0, 50.0]."

    def test_explain_with_float_precision(self):
        """Test explanation with floating point precision."""
        domain = StatisticalDomain(k=1.5)
        stats = self.build_history_statistics(count=3, sum=150.5, sumsq=20987.5)
        explanation = domain.explain(52.0, stats.stats())

        assert "Value 52.0 is within" in explanation

    def test_explain_with_negative_mean(self):
        """Test explanation with negative mean."""
        domain = StatisticalDomain(k=2.0)
        stats = self.build_history_statistics(count=2, sum=-200.0, sumsq=40020.0)
        explanation = domain.explain(-95, stats.stats())
        assert "Value -95 is within" in explanation

    def test_explain_with_non_numeric(self):
        """Test explanation with non numeric values."""
        domain = StatisticalDomain(k=2.0)
        stats = self.build_history_statistics(sum=-100.0, sumsq=10.0)
        explanation = domain.explain("not_a_number", stats)
        assert explanation == "Value must be numeric."

    def test_trend_threshold(self):
        """Test trend threshold."""
        domain = StatisticalDomain(k=2.0)
        stats = self.build_history_statistics(count=25, sum=4750.0, sumsq=902900.0)
        with pytest.raises(ValueError, match="Provide either absolute or std_factor."):
            domain.trend_threshold(stats=stats.stats(), absolute=None, std_factor=None)

        res = domain.trend_threshold(
            stats=stats.stats(), absolute=0.58, std_factor=None
        )
        assert res == 0.58

        res = domain.trend_threshold(stats=stats.stats(), absolute=None, std_factor=1.0)
        assert res == 4.0

        stats = self.build_history_statistics(sum=4750.0, sumsq=902900.0)
        res = domain.trend_threshold(stats=stats.stats(), absolute=None, std_factor=1.0)
        assert res is None

    def test_type_annotations(self):
        """Test that type annotations are correct."""
        from typing import get_type_hints

        hints = get_type_hints(StatisticalDomain.__init__)
        assert hints["k"] is float
        assert hints["name"] is str

        hints = get_type_hints(StatisticalDomain.validate)
        assert hints["value"] == Any
        assert hints["stats"] == StatisticsResult | None
        assert hints["return"] is bool

        hints = get_type_hints(StatisticalDomain.explain)
        assert hints["value"] == Any
        assert hints["stats"] == StatisticsResult | None
        assert hints["return"] is str

    def test_string_representation(self):
        """Test string representation of domain."""
        domain = StatisticalDomain(k=2.5, name="test")
        # Just ensure no error
        repr(domain)
        str(domain)

    def test_edge_case_nan_in_stats(self):
        """Test edge case with NaN in stats."""
        domain = StatisticalDomain(k=2.0)

        # NaN in sum
        stats1 = HistoryStatistics(
            3,
            float("nan"),
            409,
            None,
            None,
            None,
            1.0,
            None,
            frozenset(),
        )
        # Comparison with NaN always returns False
        assert domain.validate(50, stats1.stats()) is False

        # NaN in sumsq
        stats2 = HistoryStatistics(
            3, 300, float("nan"), None, None, None, 1.0, None, frozenset()
        )
        assert domain.validate(50, stats2.stats()) is False

    def test_edge_case_infinity_in_stats(self):
        """Test edge case with infinity in stats."""
        domain = StatisticalDomain(k=2.0)

        # Infinity in sum
        stats1 = HistoryStatistics(
            3,
            float("inf"),
            float("inf"),
            None,
            None,
            None,
            1.0,
            None,
            frozenset(),
        )
        assert domain.validate(float("inf"), stats1.stats()) is False

        # Infinity in sumsq
        stats2 = HistoryStatistics(
            3, 39, float("inf"), None, None, None, 1.0, None, frozenset()
        )
        assert domain.validate(50, stats2.stats()) is True
        assert domain.validate(float("inf"), stats2.stats()) is True
        assert domain.validate(float("-inf"), stats2.stats()) is True
