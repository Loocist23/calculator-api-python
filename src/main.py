"""
Server - FastAPI server for the Calculator API
Uses FastAPI framework with Uvicorn
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from .calculator import Calculator

# Create FastAPI app
app = FastAPI(title="Calculator API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Create calculator instance
calculator = Calculator()

# Valid operations
VALID_OPERATIONS = {"add", "subtract", "multiply", "divide"}


@app.get("/calculate")
async def calculate(
    operation: str = Query(
        ..., description="Operation to perform: add, subtract, multiply, divide"
    ),
    a: float = Query(..., description="First operand"),
    b: float = Query(..., description="Second operand"),
):
    """
    Perform a calculation operation.

    This endpoint performs basic arithmetic operations (add, subtract, multiply, divide)
    on two numbers provided as query parameters.

    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First operand (numeric)
        b: Second operand (numeric)

    Returns:
        JSON object with operation, operands, and result

    Raises:
        HTTPException 400: If operation is unknown or division by zero
    """
    # Validate operation
    if operation not in VALID_OPERATIONS:
        raise HTTPException(
            status_code=400,
            detail="Opération inconnue. Utiliser : add, subtract, multiply, divide",
        )

    # Execute operation
    try:
        if operation == "add":
            result = calculator.add(a, b)
        elif operation == "subtract":
            result = calculator.subtract(a, b)
        elif operation == "multiply":
            result = calculator.multiply(a, b)
        elif operation == "divide":
            result = calculator.divide(a, b)
        else:
            # This should never be reached due to validation above
            raise HTTPException(status_code=400, detail="Opération inconnue")

        # Handle special float values
        if isinstance(result, float):
            # Check for infinity
            if result == float("inf") or result == float("-inf"):
                result = "Infinity" if result == float("inf") else "-Infinity"
            # Check for NaN
            elif result != result:  # NaN check
                result = None

        return {"operation": operation, "a": a, "b": b, "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.options("/calculate")
async def calculate_options():
    """
    Handle OPTIONS request for CORS preflight.
    Returns 204 No Content with appropriate CORS headers.
    """
    return Response(
        status_code=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    )


# For use in tests - export the request handler logic
def request_handler_logic(request: Request):
    """
    Logic for handling requests, extracted for testing purposes.
    This mimics the structure of the original Node.js requestHandler.
    """
    if request.method == "OPTIONS":
        return JSONResponse(
            status_code=204,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )

    if request.method != "GET":
        return JSONResponse(
            status_code=405,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
                "Allow": "GET, OPTIONS",
            },
            content={"error": "Méthode non autorisée. Utiliser GET."},
        )

    # This would be handled by FastAPI's routing
    # For testing purposes, we return a placeholder
    return JSONResponse(
        status_code=404,
        headers={"Content-Type": "application/json; charset=utf-8"},
        content={"error": "Route introuvable."},
    )


# Export for tests
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
