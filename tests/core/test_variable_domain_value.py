"""Test suite for ValueDomain abstract base class."""

from typing import Any, Optional

import pytest

from procela.core.memory import MemoryStatistics
from procela.core.variable import ValueDomain


# Concrete implementation for testing
class ConcreteDomain(ValueDomain):
    """Concrete implementation for testing abstract methods."""

    def validate(self, value: Any, context: Optional[dict] = None) -> bool:
        """Always returns True for testing."""
        return True

    def explain(self, value: Any, context: Optional[dict] = None) -> str:
        """Returns a fixed explanation."""
        return f"Test explanation for {value}"


class TestValueDomain:
    """Test cases for ValueDomain abstract base class."""

    def test_abstract_class_cannot_be_instantiated(self):
        """Test that ValueDomain cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ValueDomain("test")

    def test_concrete_implementation_can_be_instantiated(self):
        """Test that concrete subclass can be instantiated."""
        domain = ConcreteDomain("test_domain")
        assert domain.name == "test_domain"

    def test_default_name_is_empty_string(self):
        """Test that default name is empty string."""
        domain = ConcreteDomain()
        assert domain.name == ""

    def test_name_initialization(self):
        """Test that name is properly initialized."""
        test_name = "my_domain"
        domain = ConcreteDomain(test_name)
        assert domain.name == test_name

    def test_validate_abstract_method(self):
        """Test that validate method is abstract."""
        domain = ConcreteDomain()
        # Should not raise NotImplementedError
        result = domain.validate("test_value")
        assert result is True

    def test_explain_abstract_method(self):
        """Test that explain method is abstract."""
        domain = ConcreteDomain()
        # Should not raise NotImplementedError
        result = domain.explain("test_value")
        assert "test_value" in result

    def test_validate_with_context(self):
        """Test validate method with context parameter."""
        domain = ConcreteDomain()
        context = {"param": "value"}
        result = domain.validate("test", context)
        assert result is True

    def test_explain_with_context(self):
        """Test explain method with context parameter."""
        domain = ConcreteDomain()
        context = {"param": "value"}
        result = domain.explain("test", context)
        assert "test" in result

    def test_trend_threshold(self):
        """Test trend threshold."""
        domain = ConcreteDomain()
        stats = MemoryStatistics.empty()
        res = domain.trend_threshold(stats=stats)
        assert res is None

    def test_method_signatures(self):
        """Test that methods have correct signatures."""
        import inspect

        # Check validate signature
        validate_sig = inspect.signature(ConcreteDomain.validate)
        assert "value" in validate_sig.parameters
        assert "context" in validate_sig.parameters
        assert validate_sig.parameters["context"].default is None

        # Check explain signature
        explain_sig = inspect.signature(ConcreteDomain.explain)
        assert "value" in explain_sig.parameters
        assert "context" in explain_sig.parameters
        assert explain_sig.parameters["context"].default is None
