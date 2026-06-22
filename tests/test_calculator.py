"""
Unit tests for the Calculator class
Tests the business logic in isolation (without HTTP)
"""

import math

import pytest

from src.calculator import Calculator


@pytest.fixture
def calculator():
    """Fixture providing a Calculator instance for unit tests."""
    return Calculator()


# ========================================================================
# Tests for addition
# ========================================================================
class TestAdd:
    """Tests for the add method."""

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (2, 3, 5),
            (-5, -3, -8),
            (-5, 3, -2),
            (7, 0, 7),
            (0.1, 0.2, pytest.approx(0.3)),
        ],
    )
    def test_add_returns_correct_result(self, calculator, a, b, expected):
        """Should return a + b = expected."""
        assert calculator.add(a, b) == expected

    def test_add_with_null_coercion(self, calculator):
        """In Python, None + int raises TypeError, unlike JS."""
        with pytest.raises(TypeError):
            calculator.add(None, 2)


# ========================================================================
# Tests for subtraction
# ========================================================================
class TestSubtract:
    """Tests for the subtract method."""

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (10, 4, 6),
            (3, 10, -7),
            (5, 0, 5),
            (-5, -3, -2),
            (0.3, 0.1, pytest.approx(0.2)),
        ],
    )
    def test_subtract_returns_correct_result(self, calculator, a, b, expected):
        """Should return a - b = expected."""
        assert calculator.subtract(a, b) == expected

    def test_subtract_with_undefined_coercion(self, calculator):
        """In Python, None - int raises TypeError."""
        with pytest.raises(TypeError):
            calculator.subtract(None, 5)


# ========================================================================
# Tests for multiplication
# ========================================================================
class TestMultiply:
    """Tests for the multiply method."""

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (6, 7, 42),
            (0, 999, 0),
            (-3, -4, 12),
            (3, -4, -12),
            (0.1, 0.2, pytest.approx(0.02)),
        ],
    )
    def test_multiply_returns_correct_result(self, calculator, a, b, expected):
        """Should return a * b = expected."""
        assert calculator.multiply(a, b) == expected

    def test_multiply_with_string_coercion(self, calculator):
        """In Python, string * int repeats the string (unlike JS which returns NaN)."""
        # In Python, "abc" * 3 = "abcabcabc"
        # In JavaScript, "abc" * 3 = NaN
        result = calculator.multiply("abc", 3)
        assert result == "abcabcabc"

    def test_multiply_with_nan(self, calculator):
        """Multiplying NaN with a number returns NaN."""
        result = calculator.multiply(float("nan"), 5)
        assert math.isnan(result)


# ========================================================================
# Tests for division
# ========================================================================
class TestDivide:
    """Tests for the divide method."""

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (20, 5, 4),
            (0, 5, 0),
            (-10, -2, 5),
            (-7, 2, -3.5),
            (10, 3, pytest.approx(3.3333333333)),
        ],
    )
    def test_divide_returns_correct_result(self, calculator, a, b, expected):
        """Should return a / b ≈ expected."""
        assert calculator.divide(a, b) == expected

    def test_divide_by_zero_raises_error(self, calculator):
        """Should raise ValueError for division by zero."""
        with pytest.raises(ValueError, match="Division par zéro impossible."):
            calculator.divide(10, 0)

    def test_divide_zero_by_zero_raises_error(self, calculator):
        """Should raise ValueError for division of zero by zero."""
        with pytest.raises(ValueError, match="Division par zéro impossible."):
            calculator.divide(0, 0)

    def test_divide_nan_by_number(self, calculator):
        """Dividing NaN by a number returns NaN."""
        result = calculator.divide(float("nan"), 5)
        assert math.isnan(result)


# ========================================================================
# Type coercion behavior tests (documentation of Python behavior)
# ========================================================================
class TestTypeCoercion:
    """Tests documenting type coercion behavior differences between JS and Python."""

    def test_add_string_concatenation(self, calculator):
        """In Python, adding strings concatenates them (like JS)."""
        result = calculator.add("5", "3")
        assert result == "53"

    def test_add_null_type_error(self, calculator):
        """In Python, None + number raises TypeError."""
        with pytest.raises(TypeError):
            calculator.add(None, 2)

    def test_subtract_undefined_type_error(self, calculator):
        """In Python, None - number raises TypeError."""
        with pytest.raises(TypeError):
            calculator.subtract(None, 5)

    def test_multiply_string_type_error(self, calculator):
        """In Python, string * int repeats the string (unlike JS which returns NaN)."""
        # In Python, "abc" * 3 = "abcabcabc"
        # In JavaScript, "abc" * 3 = NaN
        result = calculator.multiply("abc", 3)
        assert result == "abcabcabc"

    def test_divide_nan_propagation(self, calculator):
        """NaN in division propagates."""
        result = calculator.divide(float("nan"), 5)
        assert math.isnan(result)


# ========================================================================
# Edge cases
# ========================================================================
class TestEdgeCases:
    """Tests for edge cases and special values."""

    def test_very_large_values(self, calculator):
        """Should handle very large values."""
        large = 1e308
        result = calculator.add(large, large)
        assert math.isinf(result)

    def test_negative_zero(self, calculator):
        """Should handle -0 correctly."""
        assert calculator.add(-0.0, 5) == 5.0

    def test_add_floating_point_precision(self, calculator):
        """JavaScript/Python have floating point precision issues with 0.1 + 0.2."""
        result = calculator.add(0.1, 0.2)
        assert result == pytest.approx(0.3)

    def test_subtract_floating_point_precision(self, calculator):
        """Test subtraction with floating point precision."""
        result = calculator.subtract(0.3, 0.1)
        assert result == pytest.approx(0.2)

    def test_multiply_floating_point_precision(self, calculator):
        """Test multiplication with floating point precision."""
        result = calculator.multiply(0.1, 0.2)
        assert result == pytest.approx(0.02)

    def test_divide_floating_point_precision(self, calculator):
        """Test division with floating point precision."""
        result = calculator.divide(0.3, 0.1)
        assert result == pytest.approx(3.0)
