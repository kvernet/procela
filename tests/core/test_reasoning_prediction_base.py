"""
Pytest Suite for procela.core.reasoning.prediction.base.

Aims for 100% coverage of the abstract base class `Predictor`.
Tests focus on the class definition, the abstract method contract,
and the behavior of concrete implementations.
"""

from abc import ABC
from unittest.mock import Mock, create_autospec

import pytest

from procela.core.assessment import PredictionResult
from procela.core.reasoning import Predictor
from procela.core.variable import VariableEpistemic


class TestPredictorAbstractBaseClass:
    """Test the abstract nature and definition of the Predictor class."""

    def test_predictor_is_abstract(self) -> None:
        """Verify that Predictor is an abstract class and cannot be instantiated."""
        # The Predictor class should be subclass of ABC
        assert issubclass(Predictor, ABC)

        # Attempting to instantiate the abstract class should raise TypeError
        with pytest.raises(TypeError) as exc_info:
            # This will fail because `predict` is an abstract method
            Predictor()  # type: ignore
        # Check the error message mentions the abstract method
        assert "abstract" in str(exc_info.value).lower()
        assert "predict" in str(exc_info.value).lower()

    def test_predict_method_is_abstract(self) -> None:
        """Verify the `predict` method is marked as abstract."""
        # Check that 'predict' is in the list of abstract methods
        # __abstractmethods__ is a frozenset defined by the ABC meta
        assert "predict" in Predictor.__abstractmethods__

    def test_predict_method_signature(self) -> None:
        """Verify the `predict` method has the correct signature."""
        # Inspect the method's annotations
        predict_method = Predictor.predict
        # Verify parameter names
        import inspect

        sig = inspect.signature(predict_method)
        params = list(sig.parameters.keys())
        assert params == ["self", "view", "horizon"]
        # Verify default value for 'horizon' is None
        assert sig.parameters["horizon"].default is None
        # Verify return annotation is 'Any'
        assert sig.return_annotation is PredictionResult


class TestConcretePredictorImplementation:
    """
    Test the behavior of a concrete implementation of the Predictor.

    These tests ensure that any subclass properly implements the interface
    and handles the contract defined by the base class.
    """

    @pytest.fixture
    def mock_prediction_view(self) -> Mock:
        """Provide a mock VariableEpistemic for testing."""
        return create_autospec(VariableEpistemic, instance=True)

    @pytest.fixture
    def concrete_predictor(self) -> type[Predictor]:
        """Define a minimal, valid concrete predictor class for testing."""

        class ConcreteTestPredictor(Predictor):
            """A concrete implementation of Predictor for unit tests."""

            def predict(
                self, view: VariableEpistemic, horizon: int | None = None
            ) -> list[float]:
                """
                Simple test implementation.
                Returns a list of zeros of length `horizon` or 1.
                """
                if horizon is None:
                    horizon = 1
                if horizon < 0:
                    raise ValueError("Horizon cannot be negative.")
                if not isinstance(view, VariableEpistemic):
                    raise TypeError("view must be a VariableEpistemic")
                return [0.0] * horizon

        return ConcreteTestPredictor

    def test_concrete_class_can_be_instantiated(
        self, concrete_predictor: type[Predictor]
    ) -> None:
        """A concrete subclass that implements `predict` can be instantiated."""
        instance = concrete_predictor()
        assert isinstance(instance, Predictor)
        assert isinstance(instance, concrete_predictor)

    def test_concrete_predictor_method_call(
        self, concrete_predictor: type[Predictor], mock_prediction_view: Mock
    ) -> None:
        """The implemented `predict` method can be called with correct arguments."""
        predictor_instance = concrete_predictor()
        result = predictor_instance.predict(mock_prediction_view, horizon=3)

        # Verify the result matches our simple implementation
        assert result == [0.0, 0.0, 0.0]
        # Verify the mock view was passed through
        # (Our mock doesn't get used in the simple logic, but it was accepted)

    def test_concrete_predictor_default_horizon(
        self, concrete_predictor: type[Predictor], mock_prediction_view: Mock
    ) -> None:
        """The `predict` method works with the default horizon (None)."""
        predictor_instance = concrete_predictor()
        result = predictor_instance.predict(mock_prediction_view)
        # Our test implementation defaults horizon to 1 when None
        assert result == [0.0]

    def test_concrete_predictor_invalid_view_type(
        self, concrete_predictor: type[Predictor]
    ) -> None:
        """The concrete implementation can enforce type checking on the view."""
        predictor_instance = concrete_predictor()
        with pytest.raises(TypeError) as exc_info:
            predictor_instance.predict(view="not a view object")  # type: ignore
        assert "must be a VariableEpistemic" in str(exc_info.value)

    def test_concrete_predictor_invalid_horizon(
        self, concrete_predictor: type[Predictor], mock_prediction_view: Mock
    ) -> None:
        """The concrete implementation can validate the horizon parameter."""
        predictor_instance = concrete_predictor()
        with pytest.raises(ValueError) as exc_info:
            predictor_instance.predict(mock_prediction_view, horizon=-5)
        assert "cannot be negative" in str(exc_info.value)


class TestPredictorSubclassContract:
    """
    Tests to ensure subclasses adhere to the Liskov Substitution Principle.
    """

    def test_missing_predict_implementation_raises_error(self) -> None:
        """A subclass that does NOT implement `predict` remains abstract."""

        # Define a subclass that does NOT implement the abstract method
        class IncompletePredictor(Predictor):
            """This class does not implement 'predict' and should be abstract."""

            pass

        # This class should still be considered abstract
        assert "predict" in IncompletePredictor.__abstractmethods__
        # And should not be instantiable
        with pytest.raises(TypeError) as exc_info:
            IncompletePredictor()  # type: ignore
        assert "abstract" in str(exc_info.value).lower()


# This block ensures 100% coverage by directly executing the module's code.
def test_module_execution_for_coverage() -> None:
    """
    Directly import and execute the base module to ensure all top-level code runs.

    This test guarantees coverage of the module's import statements and any
    top-level code that might exist (though the provided base.py has none
    besides class definition).
    """
    # Simply importing the module executes its top-level code.
    # We've already done this at the top of the file, but this test makes it explicit.
    import procela.core.reasoning.prediction.base as prediction_base

    assert prediction_base.Predictor is not None
    # Verify the module's docstring is present (non-empty)
    assert prediction_base.__doc__ is not None
    assert len(prediction_base.__doc__) > 0


# Optional: To run tests directly from the file
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
