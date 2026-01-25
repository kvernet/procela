"""Test suite for CompositeDomain class."""

from typing import Any, Optional

from procela.core.assessment import StatisticsResult
from procela.core.variable import (
    CategoricalDomain,
    CompositeDomain,
    RangeDomain,
    ValueDomain,
)


# Mock domain for testing
class MockDomain(ValueDomain):
    """Mock domain for testing composite behavior."""

    def __init__(self, name: str = "", should_validate: bool = True):
        super().__init__(name)
        self.should_validate = should_validate
        self.validation_calls = []
        self.explanation_calls = []

    def validate(self, value: Any, context: Optional[dict] = None) -> bool:
        self.validation_calls.append((value, context))
        return self.should_validate

    def explain(self, value: Any, context: Optional[dict] = None) -> str:
        self.explanation_calls.append((value, context))
        return f"Explanation from {self.name}: value={value}"


class TestCompositeDomain:
    """Test cases for CompositeDomain class."""

    def test_initialization_with_empty_list(self):
        """Test initialization with empty subdomains list."""
        domain = CompositeDomain([])
        assert domain.subdomains == []
        assert domain.name == ""

    def test_initialization_with_single_domain(self):
        """Test initialization with single domain."""
        subdomain = RangeDomain(min_value=0)
        domain = CompositeDomain([subdomain], name="composite")
        assert len(domain.subdomains) == 1
        assert domain.subdomains[0] is subdomain
        assert domain.name == "composite"

    def test_initialization_with_multiple_domains(self):
        """Test initialization with multiple domains."""
        subdomain1 = RangeDomain(min_value=0)
        subdomain2 = CategoricalDomain(["a", "b"])
        domain = CompositeDomain([subdomain1, subdomain2])
        assert len(domain.subdomains) == 2
        assert domain.subdomains[0] is subdomain1
        assert domain.subdomains[1] is subdomain2

    def test_initialization_with_name(self):
        """Test initialization with custom name."""
        domain = CompositeDomain([], name="my_composite")
        assert domain.name == "my_composite"

    def test_validate_all_domains_pass(self):
        """Test validation when all sub-domains pass."""
        mock1 = MockDomain("mock1", should_validate=True)
        mock2 = MockDomain("mock2", should_validate=True)
        mock3 = MockDomain("mock3", should_validate=True)

        domain = CompositeDomain([mock1, mock2, mock3])
        result = domain.validate("test_value")

        assert result is True
        assert len(mock1.validation_calls) == 1
        assert len(mock2.validation_calls) == 1
        assert len(mock3.validation_calls) == 1
        assert mock1.validation_calls[0][0] == "test_value"
        assert mock2.validation_calls[0][0] == "test_value"
        assert mock3.validation_calls[0][0] == "test_value"

    def test_validate_first_domain_fails_short_circuit(self):
        """Test short-circuit evaluation when first domain fails."""
        mock1 = MockDomain("mock1", should_validate=False)
        mock2 = MockDomain("mock2", should_validate=True)  # Should not be called
        mock3 = MockDomain("mock3", should_validate=True)  # Should not be called

        domain = CompositeDomain([mock1, mock2, mock3])
        result = domain.validate("test_value")

        assert result is False
        assert len(mock1.validation_calls) == 1
        assert len(mock2.validation_calls) == 0  # Short-circuited
        assert len(mock3.validation_calls) == 0  # Short-circuited

    def test_validate_middle_domain_fails(self):
        """Test validation when middle domain fails."""
        mock1 = MockDomain("mock1", should_validate=True)
        mock2 = MockDomain("mock2", should_validate=False)
        mock3 = MockDomain("mock3", should_validate=True)  # Should not be called

        domain = CompositeDomain([mock1, mock2, mock3])
        result = domain.validate("test_value")

        assert result is False
        assert len(mock1.validation_calls) == 1
        assert len(mock2.validation_calls) == 1
        assert len(mock3.validation_calls) == 0  # Short-circuited

    def test_validate_all_domains_fail(self):
        """Test validation when all domains fail."""
        mock1 = MockDomain("mock1", should_validate=False)
        mock2 = MockDomain("mock2", should_validate=False)

        domain = CompositeDomain([mock1, mock2])
        result = domain.validate("test_value")

        assert result is False
        assert len(mock1.validation_calls) == 1
        assert len(mock2.validation_calls) == 0  # Short-circuited

    def test_validate_empty_composite(self):
        """Test validation with empty composite (always True)."""
        domain = CompositeDomain([])
        assert domain.validate("anything") is True
        assert domain.validate(123) is True
        assert domain.validate(None) is True
        assert domain.validate([1, 2, 3]) is True

    def test_validate_with_context_propagation(self):
        """Test that context is propagated to all sub-domains."""
        mock1 = MockDomain("mock1", should_validate=True)
        mock2 = MockDomain("mock2", should_validate=True)

        domain = CompositeDomain([mock1, mock2])
        context = {"param": "value"}
        result = domain.validate("test", context)

        assert result is True
        assert mock1.validation_calls[0][1] == context
        assert mock2.validation_calls[0][1] == context

    def test_explain_all_domains(self):
        """Test explanation combines all sub-domain explanations."""
        mock1 = MockDomain("mock1", should_validate=True)
        mock2 = MockDomain("mock2", should_validate=True)
        mock3 = MockDomain("mock3", should_validate=True)

        domain = CompositeDomain([mock1, mock2, mock3])
        explanation = domain.explain("test_value")

        assert "Explanation from mock1: value=test_value" in explanation
        assert "Explanation from mock2: value=test_value" in explanation
        assert "Explanation from mock3: value=test_value" in explanation
        assert " | " in explanation  # Contains separator

        # Check order is preserved
        parts = explanation.split(" | ")
        assert parts[0] == "Explanation from mock1: value=test_value"
        assert parts[1] == "Explanation from mock2: value=test_value"
        assert parts[2] == "Explanation from mock3: value=test_value"

    def test_explain_empty_composite(self):
        """Test explanation with empty composite (empty string)."""
        domain = CompositeDomain([])
        explanation = domain.explain("anything")
        assert explanation == ""

    def test_explain_single_domain(self):
        """Test explanation with single domain (no separator)."""
        mock = MockDomain("mock", should_validate=True)
        domain = CompositeDomain([mock])
        explanation = domain.explain("test")
        assert explanation == "Explanation from mock: value=test"
        assert " | " not in explanation

    def test_explain_with_context_propagation(self):
        """Test that context is propagated for explanations."""
        mock1 = MockDomain("mock1", should_validate=True)
        mock2 = MockDomain("mock2", should_validate=True)

        domain = CompositeDomain([mock1, mock2])
        context = {"param": "value"}
        _ = domain.explain("test", context)

        assert mock1.explanation_calls[0][1] == context
        assert mock2.explanation_calls[0][1] == context

    def test_real_world_composite(self):
        """Test real-world composite domain scenario."""
        # Create a domain for positive even numbers less than 100
        positive = RangeDomain(min_value=0)
        even = CategoricalDomain([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
        less_than_100 = RangeDomain(max_value=99)

        composite = CompositeDomain([positive, even, less_than_100])

        # Test valid cases
        assert composite.validate(0) is True
        assert composite.validate(10) is True
        assert composite.validate(20) is True

        # Test invalid cases
        assert composite.validate(-2) is False  # Not positive
        assert composite.validate(3) is False  # Not even
        assert composite.validate(100) is False  # Not less than 100

        # Test explanations
        explanation = composite.explain(3)
        assert "Value 3 is valid in RangeDomain" in explanation
        assert "Value 3 is not in allowed categories" in explanation
        assert " | " in explanation

    def test_nested_composite(self):
        """Test composite domain containing another composite."""
        inner1 = RangeDomain(min_value=0)
        inner2 = CategoricalDomain(["a", "b"])
        inner_composite = CompositeDomain([inner1, inner2])

        outer = RangeDomain(max_value=10)
        nested_composite = CompositeDomain([inner_composite, outer])

        # Test validation
        assert nested_composite.validate(5) is False  # 5 is not in ["a", "b"]
        assert nested_composite.validate("a") is False  # "a" is not numeric

        # Test explanation
        explanation = nested_composite.explain(5)
        assert " | " in explanation  # Should have separator

    def test_subdomain_list_reference_not_copy(self):
        """Test that subdomains list is stored by reference."""
        subdomains = [RangeDomain(min_value=0)]
        domain = CompositeDomain(subdomains)

        # Modify original list
        subdomains.append(RangeDomain(max_value=10))

        # Domain should see the modification
        assert len(domain.subdomains) == 2

    def test_type_annotations(self):
        """Test that type annotations are correct."""
        from typing import get_type_hints

        hints = get_type_hints(CompositeDomain.__init__)
        assert hints["subdomains"] == list[ValueDomain]
        assert hints["name"] is str

        hints = get_type_hints(CompositeDomain.validate)
        assert hints["value"] == Any
        assert hints["stats"] == Optional[StatisticsResult]
        assert hints["return"] is bool

        hints = get_type_hints(CompositeDomain.explain)
        assert hints["value"] == Any
        assert hints["stats"] == Optional[StatisticsResult]
        assert hints["return"] is str

    def test_string_representation(self):
        """Test string representation of domain."""
        subdomain = RangeDomain(min_value=0)
        domain = CompositeDomain([subdomain], name="test")
        # Just ensure no error
        repr(domain)
        str(domain)

    def test_explain_separator_consistency(self):
        """Test that separator is consistently applied."""
        mock1 = MockDomain("mock1")
        mock2 = MockDomain("mock2")
        mock3 = MockDomain("mock3")

        domain = CompositeDomain([mock1, mock2, mock3])
        explanation = domain.explain("test")

        # Count separators
        separator_count = explanation.count(" | ")
        assert separator_count == 2  # n-1 separators for n domains
