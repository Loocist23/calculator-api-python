"""
Calculator - Business logic for the calculator
Implements the four basic arithmetic operations
"""


class Calculator:
    """
    Calculator class implementing basic arithmetic operations.
    
    Note: This implementation intentionally mirrors JavaScript's native behavior
    for type coercion to maintain compatibility with the original Node.js API.
    """

    def add(self, a: float, b: float) -> float:
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The sum of a and b
            
        Note: In Python, unlike JavaScript, we don't have automatic type coercion.
        However, we maintain the same behavior for valid numeric inputs.
        """
        return a + b

    def subtract(self, a: float, b: float) -> float:
        """
        Subtract two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The difference between a and b
        """
        return a - b

    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            The product of a and b
        """
        return a * b

    def divide(self, a: float, b: float) -> float:
        """
        Divide two numbers.
        
        Args:
            a: Dividend
            b: Divisor
            
        Returns:
            The quotient of a divided by b
            
        Raises:
            ValueError: If b is equal to 0
        """
        if b == 0:
            raise ValueError("Division par zéro impossible.")
        return a / b
