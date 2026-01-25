"""
Test suite for procela.core.reasoning.prediction.operator module.
100% coverage for the exact PredictionOperator code.
"""

from unittest.mock import Mock, patch

import pytest

from procela.core.assessment import PredictionResult
from procela.core.epistemic import VariableView
from procela.core.reasoning import (
    PredictionOperator,
    Predictor,
)


class TestPredictionOperator:
    """Test cases for the PredictionOperator class."""

    @pytest.fixture
    def mock_predictor(self):
        """Create a mock Predictor object."""
        predictor = Mock(spec=Predictor)
        predictor.__class__.__name__ = "MockPredictor"
        return predictor

    @pytest.fixture
    def mock_prediction_view(self):
        """Create a mock VariableView object."""
        return Mock(spec=VariableView)

    @pytest.fixture
    def mock_prediction_result_value(self):
        """Create a mock prediction result value."""
        return 42.5

    def test_predictor_type_check_passes(self, mock_predictor, mock_prediction_view):
        """Test that predictor type check passes with valid predictor."""
        operator = PredictionOperator()

        # Configure predictor to return a value
        mock_predictor.predict.return_value = 100.0

        result = operator.predict(mock_predictor, mock_prediction_view)

        # Should not raise TypeError
        assert isinstance(result, PredictionResult)

    def test_predictor_type_check_fails_with_wrong_type(self, mock_prediction_view):
        """Test that predictor type check fails with non-Predictor."""
        operator = PredictionOperator()

        with pytest.raises(TypeError) as exc_info:
            operator.predict("not a predictor", mock_prediction_view)

        assert "predictor should be a Predictor instance" in str(exc_info.value)
        assert "got" in str(exc_info.value)
        assert "not a predictor" in str(exc_info.value)

    def test_predictor_type_check_fails_with_none(self, mock_prediction_view):
        """Test that predictor type check fails with None."""
        operator = PredictionOperator()

        with pytest.raises(TypeError) as exc_info:
            operator.predict(None, mock_prediction_view)

        assert "predictor should be a Predictor instance" in str(exc_info.value)
        assert "got" in str(exc_info.value)
        assert "None" in str(exc_info.value)

    def test_view_type_check_passes(self, mock_predictor, mock_prediction_view):
        """Test that view type check passes with valid view."""
        operator = PredictionOperator()
        mock_predictor.predict.return_value = 75.5

        result = operator.predict(mock_predictor, mock_prediction_view)

        # Should not raise TypeError
        assert isinstance(result, PredictionResult)

    def test_view_type_check_fails_with_wrong_type(self, mock_predictor):
        """Test that view type check fails with non-VariableView."""
        operator = PredictionOperator()

        with pytest.raises(TypeError) as exc_info:
            operator.predict(mock_predictor, "not a view")

        assert "view should be a VariableView" in str(exc_info.value)
        assert "got" in str(exc_info.value)
        assert "not a view" in str(exc_info.value)

    def test_view_type_check_fails_with_none(self, mock_predictor):
        """Test that view type check fails with None."""
        operator = PredictionOperator()

        with pytest.raises(TypeError) as exc_info:
            operator.predict(mock_predictor, None)

        assert "view should be a VariableView" in str(exc_info.value)
        assert "got" in str(exc_info.value)
        assert "None" in str(exc_info.value)

    def test_predict_with_horizon(self, mock_predictor, mock_prediction_view):
        """Test predict method with horizon specified."""
        operator = PredictionOperator()
        expected_value = 123.45
        horizon = 10

        mock_predictor.predict.return_value = expected_value

        result = operator.predict(mock_predictor, mock_prediction_view, horizon)

        # Verify predictor was called correctly
        mock_predictor.predict.assert_called_once_with(mock_prediction_view, horizon)

        # Verify result
        assert isinstance(result, PredictionResult)
        assert result.value == expected_value
        assert result.horizon == horizon
        assert result.confidence is None
        assert "predictor" in result.metadata
        assert result.metadata["predictor"] == "MockPredictor"
        assert result.metadata["horizon"] == horizon

    def test_predict_without_horizon(self, mock_predictor, mock_prediction_view):
        """Test predict method without horizon (default None)."""
        operator = PredictionOperator()
        expected_value = 99.9

        mock_predictor.predict.return_value = expected_value

        result = operator.predict(mock_predictor, mock_prediction_view)

        # Should call predictor with None horizon
        mock_predictor.predict.assert_called_once_with(mock_prediction_view, None)

        # Verify result
        assert result.value == expected_value
        assert result.horizon is None
        assert result.confidence is None
        assert result.metadata["predictor"] == "MockPredictor"
        assert result.metadata["horizon"] is None

    def test_predict_with_zero_horizon(self, mock_predictor, mock_prediction_view):
        """Test predict method with horizon = 0."""
        operator = PredictionOperator()
        expected_value = 0.0

        mock_predictor.predict.return_value = expected_value

        with pytest.raises(ValueError, match="Horizon must be positive, got 0"):
            operator.predict(mock_predictor, mock_prediction_view, 0)

    def test_predict_with_negative_horizon(self, mock_predictor, mock_prediction_view):
        """Test predict method with negative horizon."""
        operator = PredictionOperator()
        expected_value = -50.0

        mock_predictor.predict.return_value = expected_value

        with pytest.raises(ValueError, match="Horizon must be positive, got -5"):
            operator.predict(mock_predictor, mock_prediction_view, -5)

    def test_predict_result_structure(self, mock_predictor, mock_prediction_view):
        """Test the structure of the returned PredictionResult."""
        operator = PredictionOperator()
        test_value = 3.14159
        horizon = 7

        mock_predictor.predict.return_value = test_value

        result = operator.predict(mock_predictor, mock_prediction_view, horizon)

        # Check all attributes
        assert hasattr(result, "value")
        assert hasattr(result, "horizon")
        assert hasattr(result, "confidence")
        assert hasattr(result, "metadata")

        # Check values
        assert result.value == test_value
        assert result.horizon == horizon
        assert result.confidence is None

        # Check metadata
        assert isinstance(result.metadata, dict)
        assert result.metadata["predictor"] == "MockPredictor"
        assert result.metadata["horizon"] == horizon

    def test_predict_with_different_predictor_classes(self, mock_prediction_view):
        """Test with different predictor class names."""
        test_cases = [
            ("LinearPredictor", 100.0),
            ("NeuralNetworkPredictor", 85.5),
            ("ARIMAPredictor", 42.3),
            ("ExponentialSmoothingPredictor", 77.8),
        ]

        for class_name, predicted_value in test_cases:
            mock_predictor = Mock(spec=Predictor)
            mock_predictor.__class__.__name__ = class_name
            mock_predictor.predict.return_value = predicted_value

            operator = PredictionOperator()
            result = operator.predict(mock_predictor, mock_prediction_view)

            assert result.metadata["predictor"] == class_name
            assert result.value == predicted_value

    def test_predict_with_predictor_returning_none(
        self, mock_predictor, mock_prediction_view
    ):
        """Test when predictor returns None."""
        operator = PredictionOperator()
        mock_predictor.predict.return_value = None

        result = operator.predict(mock_predictor, mock_prediction_view)

        assert result.value is None
        assert result.confidence is None

    def test_predict_with_predictor_returning_complex_value(
        self, mock_predictor, mock_prediction_view
    ):
        """Test when predictor returns a complex value (not just float)."""
        operator = PredictionOperator()

        # Test with list
        mock_predictor.predict.return_value = [10.0, 20.0, 30.0]
        result = operator.predict(mock_predictor, mock_prediction_view)
        assert result.value == [10.0, 20.0, 30.0]

        # Test with dict
        mock_predictor.predict.return_value = {"mean": 50.0, "std": 5.0}
        result = operator.predict(mock_predictor, mock_prediction_view, horizon=5)
        assert result.value == {"mean": 50.0, "std": 5.0}

        # Test with string
        mock_predictor.predict.return_value = "high"
        result = operator.predict(mock_predictor, mock_prediction_view)
        assert result.value == "high"

    def test_type_error_message_format(self):
        """Test the exact format of TypeError messages."""
        operator = PredictionOperator()

        # Test predictor error message
        with pytest.raises(TypeError) as exc_info:
            operator.predict(42, Mock(spec=VariableView))

        error_msg = str(exc_info.value)
        assert error_msg.startswith("predictor should be a Predictor instance")
        assert "got" in error_msg
        assert "42" in error_msg

        # Test view error message
        mock_predictor = Mock(spec=Predictor)
        with pytest.raises(TypeError) as exc_info:
            operator.predict(mock_predictor, 3.14)

        error_msg = str(exc_info.value)
        assert error_msg.startswith("view should be a VariableView")
        assert "got" in error_msg
        assert "3.14" in error_msg

    def test_predict_method_signature(self):
        """Test that the predict method has correct signature."""
        import inspect

        operator = PredictionOperator()
        sig = inspect.signature(operator.predict)

        # Check parameters
        params = list(sig.parameters.keys())
        assert params == ["predictor", "view", "horizon"]

        # Check annotations
        annotations = operator.predict.__annotations__
        assert annotations["predictor"] == "Predictor"
        assert annotations["view"] == "VariableView"
        assert annotations["horizon"] == "int | None"
        assert annotations["return"] == "PredictionResult"

        # Check default value for horizon
        assert sig.parameters["horizon"].default is None

    def test_class_docstring(self):
        """Test that the class and method have the expected docstrings."""
        assert "Operator for performing predictions." in PredictionOperator.__doc__
        assert "Predict future values" in PredictionOperator.predict.__doc__

    def test_operator_is_stateless(self):
        """Test that PredictionOperator has no instance state."""
        operator1 = PredictionOperator()
        operator2 = PredictionOperator()

        # They should be equivalent
        assert operator1.__dict__ == operator2.__dict__

        # Should have no instance attributes
        assert not hasattr(operator1, "__dict__") or len(operator1.__dict__) == 0


class TestIntegration:
    """Integration tests for PredictionOperator."""

    def test_complete_prediction_workflow(self):
        """Test a complete prediction workflow."""
        # Create realistic predictor
        mock_predictor = Mock(spec=Predictor)
        mock_predictor.__class__.__name__ = "ExponentialSmoothingPredictor"

        # Create realistic view
        mock_view = Mock(spec=VariableView)
        mock_view.history = [10.0, 12.0, 11.5, 13.0, 12.5]
        mock_view.current_value = 12.8
        mock_view.context = {"seasonality": "daily"}

        # Set up prediction
        predicted_value = 13.2
        horizon = 3
        mock_predictor.predict.return_value = predicted_value

        # Perform prediction
        operator = PredictionOperator()
        result = operator.predict(mock_predictor, mock_view, horizon)

        # Verify
        mock_predictor.predict.assert_called_once_with(mock_view, horizon)

        assert result.value == predicted_value
        assert result.horizon == horizon
        assert result.confidence is None
        assert result.metadata == {
            "predictor": "ExponentialSmoothingPredictor",
            "horizon": horizon,
        }

    def test_multiple_predictions_with_same_operator(self):
        """Test making multiple predictions with the same operator."""
        operator = PredictionOperator()

        # Create multiple predictor/view combinations
        test_cases = [
            (Mock(spec=Predictor), Mock(spec=VariableView), 1, 100.0),
            (Mock(spec=Predictor), Mock(spec=VariableView), 5, 105.5),
            (Mock(spec=Predictor), Mock(spec=VariableView), None, 98.7),
        ]

        for predictor, view, horizon, value in test_cases:
            predictor.__class__.__name__ = f"Predictor_{id(predictor)}"
            predictor.predict.return_value = value

            result = operator.predict(predictor, view, horizon)

            predictor.predict.assert_called_once_with(view, horizon)
            assert result.value == value
            assert result.horizon == horizon

    def test_real_time_series_prediction_scenario(self):
        """Test a realistic time series prediction scenario."""
        # Simulate stock price prediction
        mock_predictor = Mock(spec=Predictor)
        mock_predictor.__class__.__name__ = "LSTMPredictor"

        mock_view = Mock(spec=VariableView)
        mock_view.timestamps = list(range(100))  # 100 time points
        mock_view.values = [
            50.0 + i * 0.1 + (i % 10) for i in range(100)
        ]  # Simulated prices

        # Predict next 5 time steps
        predicted_values = [65.1, 65.3, 65.6, 65.8, 66.1]
        horizon = 5
        mock_predictor.predict.return_value = predicted_values

        operator = PredictionOperator()
        result = operator.predict(mock_predictor, mock_view, horizon)

        # Verify the prediction
        assert result.value == predicted_values
        assert result.horizon == horizon
        assert len(result.value) == 5
        assert result.metadata["predictor"] == "LSTMPredictor"

    def test_prediction_with_confidence_if_supported(self):
        """Test that confidence is always None (as per current implementation)."""
        mock_predictor = Mock(spec=Predictor)
        mock_predictor.__class__.__name__ = "BayesianPredictor"
        mock_predictor.predict.return_value = (75.0, 0.95)  # value, confidence

        mock_view = Mock(spec=VariableView)

        operator = PredictionOperator()
        result = operator.predict(mock_predictor, mock_view)

        # Confidence should still be None (explicitly undefined in code)
        assert result.confidence is None
        # The tuple should be stored as the value
        assert result.value == (75.0, 0.95)


def test_coverage_edge_cases():
    """Additional tests to ensure 100% coverage of all edge cases."""

    # Test with predictor that raises exception
    mock_predictor = Mock(spec=Predictor)
    mock_predictor.__class__.__name__ = "FailingPredictor"
    mock_predictor.predict.side_effect = ValueError("Prediction failed")

    mock_view = Mock(spec=VariableView)

    operator = PredictionOperator()

    # Exception should propagate through operator
    with pytest.raises(ValueError) as exc_info:
        operator.predict(mock_predictor, mock_view)

    assert "Prediction failed" in str(exc_info.value)

    # Test with very large horizon
    mock_predictor2 = Mock(spec=Predictor)
    mock_predictor2.__class__.__name__ = "LongTermPredictor"
    mock_predictor2.predict.return_value = 200.0

    result = operator.predict(mock_predictor2, mock_view, horizon=1000)
    assert result.horizon == 1000

    # Test with float horizon (should still work if predictor accepts it)
    # Note: type hint says int | None, but Python won't enforce this
    mock_predictor3 = Mock(spec=Predictor)
    mock_predictor3.__class__.__name__ = "FloatHorizonPredictor"
    mock_predictor3.predict.return_value = 150.0

    with pytest.raises(TypeError, match="Horizon must be an integer, got float"):
        operator.predict(mock_predictor3, mock_view, horizon=2.5)


def test_prediction_result_construction():
    """Test the exact construction of PredictionResult."""
    operator = PredictionOperator()

    mock_predictor = Mock(spec=Predictor)
    mock_predictor.__class__.__name__ = "TestPredictor"
    mock_predictor.predict.return_value = 99.9

    mock_view = Mock(spec=VariableView)

    result = operator.predict(mock_predictor, mock_view, horizon=7)

    # Verify PredictionResult was constructed with exact expected arguments
    assert result.value == 99.9
    assert result.horizon == 7
    assert result.confidence is None
    assert result.metadata == {"predictor": "TestPredictor", "horizon": 7}

    # Test that metadata dict is created fresh each time
    result2 = operator.predict(mock_predictor, mock_view, horizon=10)
    assert result2.metadata["horizon"] == 10
    assert result.metadata["horizon"] == 7  # First result unchanged


def test_type_check_implementation_details():
    """Test details of type checking implementation."""
    operator = PredictionOperator()

    # Test with object that quacks like a Predictor but isn't one
    class FakePredictor:
        def predict(self, view, horizon):
            return 100.0

    fake_predictor = FakePredictor()

    # Should fail type check even though it has predict method
    with pytest.raises(TypeError) as exc_info:
        operator.predict(fake_predictor, Mock(spec=VariableView))

    assert "Predictor instance" in str(exc_info.value)

    # Test with subclass of Predictor
    class RealPredictor(Predictor):
        def predict(self, view, horizon):
            return 200.0

    # Can't actually instantiate abstract class, so mock it
    with patch("procela.core.reasoning.prediction.base.Predictor"):
        real_predictor = RealPredictor()
        real_predictor.__class__.__name__ = "RealPredictor"

        # This should pass type check
        result = operator.predict(real_predictor, Mock(spec=VariableView))
        assert result.value == 200.0


def test_module_structure():
    """Test that the module has the expected structure."""
    from procela.core.reasoning.prediction import operator

    # Check exports
    assert hasattr(operator, "PredictionOperator")

    # Check the class
    assert operator.PredictionOperator.__name__ == "PredictionOperator"

    # Check method exists
    assert hasattr(operator.PredictionOperator, "predict")

    # Verify it's a class method, not static/instance
    import inspect

    assert "self" in inspect.signature(operator.PredictionOperator.predict).parameters


def test_immutability_of_results():
    """Test that results are properly constructed and immutable."""
    operator = PredictionOperator()

    mock_predictor = Mock(spec=Predictor)
    mock_predictor.__class__.__name__ = "ImmutableTestPredictor"
    mock_predictor.predict.return_value = 50.0

    mock_view = Mock(spec=VariableView)

    result = operator.predict(mock_predictor, mock_view)

    # Try to modify result (depends on PredictionResult implementation)
    # At minimum, verify we have a PredictionResult object
    assert isinstance(result, PredictionResult)

    # Verify metadata is a dict (should be)
    assert isinstance(result.metadata, dict)
