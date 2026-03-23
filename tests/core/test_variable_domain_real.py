"""Test suite for RealDomain class."""

from procela.core.variable import RealDomain


class TestRealDomain:
    """Test cases for RealDomain class."""

    def test_initialization_with_no_bounds(self):
        """Test initialization without bounds."""
        domain = RealDomain()
        assert domain.min_value == -float("inf")
        assert domain.max_value == float("inf")
        assert domain.name == ""

    def test_initialization_with_name(self):
        """Test initialization with custom name."""
        domain = RealDomain(name="temperature")
        assert domain.name == "temperature"

    def test_validate_non_numeric_value(self):
        """Test validation of non-numeric values."""
        domain = RealDomain()
        assert domain.validate("string") is False
        assert domain.validate([1, 2, 3]) is False
        assert domain.validate({"key": "value"}) is False
        assert domain.validate(None) is False
        assert domain.validate(True) is True
        assert domain.validate(False) is True

    def test_validate_with_int_value(self):
        """Test validation with float and integer value."""
        domain = RealDomain()
        assert domain.validate(1) is True
        assert domain.validate(0.5) is True
        assert domain.validate(10.5) is True

    def test_explain_valid_value(self):
        """Test explanation for valid value."""
        domain = RealDomain()
        explanation = domain.explain(50)
        assert "Value 50 is valid in RealDomain" == explanation

    def test_explain_non_numeric_value(self):
        """Test explanation for non-numeric value."""
        domain = RealDomain()
        explanation = domain.explain("fifty")
        assert "Value fifty is not numeric" == explanation

    def test_edge_case_large_numbers(self):
        """Test edge case with very large numbers."""
        domain = RealDomain()
        assert domain.validate(1e99) is True
        assert domain.validate(-1e99) is True

    def test_edge_case_infinity_and_nan(self):
        """Test edge case with infinity and NaN."""
        domain = RealDomain()
        # These should return False as they are numeric but special
        assert domain.validate(float("inf")) is True
        assert domain.validate(float("-inf")) is True
        assert domain.validate(float("nan")) is False

    def test_string_representation(self):
        """Test string representation of domain."""
        domain = RealDomain(name="test")
        # Just ensure no error
        repr(domain)
        str(domain)

    def test_equality_not_implemented(self):
        """Test that equality is not specially implemented."""
        domain1 = RealDomain()
        domain2 = RealDomain()
        # Different objects should not be equal by default
        assert domain1 != domain2
