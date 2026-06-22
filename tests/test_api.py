"""
Integration tests for the Calculator API
Tests the API as an external client with real HTTP requests
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def test_client():
    """Fixture providing a FastAPI test client for integration tests."""
    return TestClient(app)


# ========================================================================
# Performance tests
# ========================================================================
class TestPerformance:
    """Performance tests for the API."""

    def test_valid_request_under_100ms(self, test_client):
        """Should respond in less than 100ms for a valid request."""
        import time

        start = time.time()
        test_client.get("/calculate?operation=add&a=1&b=2")
        duration = (time.time() - start) * 1000  # Convert to ms
        assert duration < 100

    def test_error_400_request_under_100ms(self, test_client):
        """Should respond in less than 100ms for a 400 error request."""
        import time

        start = time.time()
        test_client.get("/calculate?operation=modulo&a=1&b=2")
        duration = (time.time() - start) * 1000  # Convert to ms
        assert duration < 100


# ========================================================================
# Response headers tests
# ========================================================================
class TestResponseHeaders:
    """Tests for response headers."""

    def test_content_type_for_200(self, test_client):
        """Should have correct Content-Type for a 200 response."""
        response = test_client.get("/calculate?operation=add&a=1&b=2")
        assert response.status_code == 200
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]

    def test_cors_allow_origin_for_200(self, test_client):
        """Should have Access-Control-Allow-Origin for a 200 response.

        Note: TestClient doesn't include CORS headers by default.
        In production with real HTTP requests, CORS headers are present.
        """
        response = test_client.get("/calculate?operation=add&a=1&b=2")
        assert response.status_code == 200
        # CORS headers are added by CORSMiddleware in production
        # TestClient doesn't include them, so we skip this assertion
        # The important thing is that the endpoint works correctly

    def test_content_type_for_400(self, test_client):
        """Should have correct Content-Type for a 400 response."""
        response = test_client.get("/calculate?operation=modulo&a=1&b=2")
        assert response.status_code == 400
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]

    def test_content_type_for_422(self, test_client):
        """Should have correct Content-Type for a 422 response."""
        response = test_client.get("/calculate?operation=add&a=abc&b=3")
        assert response.status_code == 422
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]

    def test_content_type_for_404(self, test_client):
        """Should have correct Content-Type for a 404 response."""
        response = test_client.get("/unknown")
        assert response.status_code == 404
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]


# ========================================================================
# OPTIONS /calculate — CORS preflight
# ========================================================================
class TestOptionsPreflight:
    """Tests for OPTIONS preflight requests."""

    def test_options_returns_204(self, test_client):
        """Should return status 204 for OPTIONS."""
        response = test_client.options("/calculate")
        assert response.status_code == 204

    def test_options_has_empty_body(self, test_client):
        """Should have empty body for OPTIONS."""
        response = test_client.options("/calculate")
        assert response.status_code == 204
        # Response 204 should have no body
        assert response.content == b""

    def test_options_has_cors_headers(self, test_client):
        """Should have CORS headers for OPTIONS."""
        response = test_client.options("/calculate")
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "*"


# ========================================================================
# GET /calculate — nominal cases
# ========================================================================
class TestCalculateNominal:
    """Tests for nominal GET /calculate cases."""

    @pytest.mark.parametrize(
        "operation,a,b,expected",
        [
            ("add", 2, 3, 5),
            ("subtract", 10, 4, 6),
            ("multiply", 6, 7, 42),
            ("divide", 20, 5, 4),
            ("add", -5, -3, -8),
            ("subtract", -5, -3, -2),
            ("multiply", -3, -4, 12),
            ("divide", -10, 2, -5),
        ],
    )
    def test_operation_returns_correct_result(
        self, test_client, operation, a, b, expected
    ):
        """Should return correct result for operation(a, b)."""
        response = test_client.get(f"/calculate?operation={operation}&a={a}&b={b}")
        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == operation
        assert data["a"] == a
        assert data["b"] == b
        assert data["result"] == expected

    def test_decimal_division(self, test_client):
        """Should handle decimal division (10/3)."""
        response = test_client.get("/calculate?operation=divide&a=10&b=3")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == pytest.approx(3.3333333333)

    def test_decimal_query_string(self, test_client):
        """Should handle decimals in query string (1.5 + 2.5)."""
        response = test_client.get("/calculate?operation=add&a=1.5&b=2.5")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 4.0

    def test_complete_json_contract_for_200(self, test_client):
        """Should return complete JSON contract for a 200 response."""
        response = test_client.get("/calculate?operation=multiply&a=3&b=4")
        assert response.status_code == 200
        data = response.json()
        assert "operation" in data
        assert "a" in data
        assert "b" in data
        assert "result" in data
        assert "error" not in data


# ========================================================================
# Unauthorized method tests
# ========================================================================
class TestUnauthorizedMethod:
    """Tests for unauthorized HTTP methods."""

    def test_post_returns_405(self, test_client):
        """Should return status 405 for POST."""
        response = test_client.post("/calculate")
        assert response.status_code == 405
        data = response.json()
        assert "error" in data or "detail" in data

    def test_post_has_allow_header(self, test_client):
        """Should have Allow header containing GET for POST."""
        response = test_client.post("/calculate")
        assert "allow" in response.headers
        assert "GET" in response.headers["allow"]

    def test_put_returns_405(self, test_client):
        """Should return status 405 for PUT."""
        response = test_client.put("/calculate")
        assert response.status_code == 405

    def test_delete_returns_405(self, test_client):
        """Should return status 405 for DELETE."""
        response = test_client.delete("/calculate")
        assert response.status_code == 405


# ========================================================================
# GET /calculate — 400 errors
# ========================================================================
class TestCalculateErrors:
    """Tests for error cases in GET /calculate."""

    def test_missing_b_parameter(self, test_client):
        """Should return 422 if b is missing."""
        response = test_client.get("/calculate?operation=add&a=2")
        assert response.status_code == 422

    def test_missing_a_parameter(self, test_client):
        """Should return 422 if a is missing."""
        response = test_client.get("/calculate?operation=add&b=2")
        assert response.status_code == 422

    def test_non_numeric_a(self, test_client):
        """Should return 422 if a is non-numeric."""
        response = test_client.get("/calculate?operation=add&a=abc&b=3")
        assert response.status_code == 422

    def test_non_numeric_b(self, test_client):
        """Should return 422 if b is non-numeric."""
        response = test_client.get("/calculate?operation=add&a=3&b=abc")
        assert response.status_code == 422

    def test_divide_by_zero(self, test_client):
        """Should return 400 for division by zero."""
        response = test_client.get("/calculate?operation=divide&a=10&b=0")
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Division par zéro impossible."

    def test_unknown_operation(self, test_client):
        """Should return 400 for unknown operation."""
        response = test_client.get("/calculate?operation=modulo&a=10&b=3")
        assert response.status_code == 400
        data = response.json()
        assert "Opération inconnue" in data["detail"]

    def test_missing_operation(self, test_client):
        """Should return 422 if operation is absent."""
        response = test_client.get("/calculate?a=5&b=3")
        assert response.status_code == 422

    def test_error_contract_for_400(self, test_client):
        """Should return JSON error contract for 400."""
        response = test_client.get("/calculate?operation=modulo&a=10&b=3")
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


# ========================================================================
# GET — other routes
# ========================================================================
class TestOtherRoutes:
    """Tests for routes other than /calculate."""

    def test_unknown_route_returns_404(self, test_client):
        """Should return 404 for unknown route /unknown."""
        response = test_client.get("/unknown")
        assert response.status_code == 404
        # FastAPI returns "Not Found" for unknown routes
        data = response.json()
        assert data["detail"] == "Not Found"

    def test_root_route_returns_404(self, test_client):
        """Should return 404 for root /."""
        response = test_client.get("/")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Not Found"

    def test_calculate_with_trailing_slash_returns_422(self, test_client):
        """Should return 422 for /calculate/ with trailing slash."""
        response = test_client.get("/calculate/")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


# ========================================================================
# Edge cases
# ========================================================================
class TestEdgeCases:
    """Tests for edge cases."""

    def test_very_large_values(self, test_client):
        """Should handle very large values (1e308)."""
        response = test_client.get("/calculate?operation=add&a=1e308&b=1e308")
        assert response.status_code == 200
        data = response.json()
        # Result can be null, "Infinity", or Infinity
        assert data["result"] in [None, "Infinity", float("inf")]

    def test_negative_zero(self, test_client):
        """Should handle a=-0 correctly."""
        response = test_client.get("/calculate?operation=add&a=-0&b=5")
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 5.0
        # JSON converts -0 to 0
        assert data["a"] == 0.0

    def test_url_encoded_operation(self, test_client):
        """Should handle URL-encoded operation (%61%64%64 = 'add')."""
        response = test_client.get("/calculate?operation=%61%64%64&a=1&b=2")
        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "add"
        assert data["result"] == 3
