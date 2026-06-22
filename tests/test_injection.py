"""
Security tests - Injection and vulnerabilities
Tests the API's resistance to injection attacks
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from urllib.parse import quote


@pytest.fixture
def test_client():
    """Fixture providing a FastAPI test client for integration tests."""
    return TestClient(app)


# ========================================================================
# Injection in operation parameter
# ========================================================================
class TestOperationInjection:
    """Tests for injection attacks in the 'operation' parameter."""

    def test_javascript_injection_via_operation(self, test_client):
        """Should reject JavaScript code injection via operation."""
        malicious_op = "add;console.log('hacked')"
        response = test_client.get(f"/calculate?operation={malicious_op}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_template_literals_injection(self, test_client):
        """Should reject template literals injection."""
        malicious_op = "${require('fs').readFileSync('/etc/passwd')}"
        response = test_client.get(f"/calculate?operation={malicious_op}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_constructor_injection(self, test_client):
        """Should reject constructor injection."""
        response = test_client.get("/calculate?operation=constructor&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_proto_injection(self, test_client):
        """Should reject __proto__ injection."""
        response = test_client.get("/calculate?operation=__proto__&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_prototype_injection(self, test_client):
        """Should reject prototype injection."""
        response = test_client.get("/calculate?operation=prototype&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_semicolon_injection(self, test_client):
        """Should reject injection with semicolon."""
        response = test_client.get("/calculate?operation=add;alert(1)&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_parentheses_injection(self, test_client):
        """Should reject injection with parentheses."""
        response = test_client.get("/calculate?operation=add()&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_braces_injection(self, test_client):
        """Should reject injection with braces."""
        response = test_client.get("/calculate?operation={0}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_eval_injection(self, test_client):
        """Should reject eval injection."""
        response = test_client.get("/calculate?operation=eval&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_function_injection(self, test_client):
        """Should reject Function injection."""
        response = test_client.get("/calculate?operation=Function&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_uppercase_operation(self, test_client):
        """Should reject uppercase operations."""
        response = test_client.get("/calculate?operation=ADD&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_operation_with_spaces(self, test_client):
        """Should reject operations with spaces."""
        response = test_client.get(f"/calculate?operation={quote(' add ')}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_empty_operation(self, test_client):
        """Should reject empty operation."""
        response = test_client.get("/calculate?operation=&a=1&b=2")
        # Empty string is a valid string but not in VALID_OPERATIONS, so returns 400
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]


# ========================================================================
# Injection in a and b parameters
# ========================================================================
class TestParamInjection:
    """Tests for injection attacks in the 'a' and 'b' parameters."""

    def test_javascript_injection_in_a(self, test_client):
        """Should reject JavaScript code injection in a."""
        malicious_a = "1;console.log('hacked')"
        response = test_client.get(f"/calculate?operation=add&a={malicious_a}&b=2")
        # FastAPI returns 422 for invalid float
        assert response.status_code == 422

    def test_javascript_injection_in_b(self, test_client):
        """Should reject JavaScript code injection in b."""
        malicious_b = "2;alert(1)"
        response = test_client.get(f"/calculate?operation=add&a=1&b={malicious_b}")
        assert response.status_code == 422

    def test_alphabetic_in_a(self, test_client):
        """Should reject alphabetic characters in a."""
        response = test_client.get("/calculate?operation=add&a=abc123&b=2")
        assert response.status_code == 422

    def test_special_chars_in_b(self, test_client):
        """Should reject special characters in b."""
        response = test_client.get(f"/calculate?operation=add&a=1&b={quote('2#3')}")
        assert response.status_code == 422

    def test_spaces_in_a(self, test_client):
        """Should reject spaces in a."""
        response = test_client.get(f"/calculate?operation=add&a={quote(' 1 2 ')}&b=2")
        assert response.status_code == 422

    def test_parentheses_in_a(self, test_client):
        """Should reject parentheses in a."""
        response = test_client.get("/calculate?operation=add&a=%281%2B2%29&b=2")
        assert response.status_code == 422

    def test_unicode_fullwidth_in_a(self, test_client):
        """Should reject Unicode full-width characters in a."""
        response = test_client.get(f"/calculate?operation=add&a={quote('\uFF11\uFF12\uFF13')}&b=2")
        assert response.status_code == 422

    def test_null_byte_in_a(self, test_client):
        """Should reject null byte in a."""
        response = test_client.get(f"/calculate?operation=add&a={quote('1\x00')}&b=2")
        assert response.status_code == 422

    def test_html_tags_in_a(self, test_client):
        """Should reject HTML tags in a."""
        response = test_client.get("/calculate?operation=add&a=<script>alert(1)</script>&b=2")
        assert response.status_code == 422

    def test_quotes_in_a(self, test_client):
        """Should reject quotes in a."""
        response = test_client.get('/calculate?operation=add&a="123"&b=2')
        assert response.status_code == 422

    def test_apostrophes_in_a(self, test_client):
        """Should reject apostrophes in a."""
        response = test_client.get("/calculate?operation=add&a='123'&b=2")
        assert response.status_code == 422

    def test_backticks_in_a(self, test_client):
        """Should reject backticks in a."""
        response = test_client.get("/calculate?operation=add&a=`123`&b=2")
        assert response.status_code == 422


# ========================================================================
# DoS with very long strings
# ========================================================================
class TestLongStringAttacks:
    """Tests for DoS attacks with very long strings."""

    @pytest.fixture
    def long_string(self):
        """Create a very long string for testing."""
        return 'a' * 10000

    def test_long_operation(self, test_client, long_string):
        """Should reject operation with very long string."""
        response = test_client.get(f"/calculate?operation={long_string}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_long_a(self, test_client, long_string):
        """Should reject a with very long string."""
        response = test_client.get(f"/calculate?operation=add&a={long_string}&b=2")
        assert response.status_code == 422

    def test_long_b(self, test_client, long_string):
        """Should reject b with very long string."""
        response = test_client.get(f"/calculate?operation=add&a=1&b={long_string}")
        assert response.status_code == 422

    def test_large_valid_number(self, test_client):
        """Should handle very large but valid numbers."""
        large_number = '9' * 50
        response = test_client.get(f"/calculate?operation=add&a={large_number}&b=1")
        assert response.status_code == 200
        data = response.json()
        assert "result" in data


# ========================================================================
# Unicode and encoding attacks
# ========================================================================
class TestUnicodeAttacks:
    """Tests for Unicode and encoding attacks."""

    def test_zero_width_space_in_operation(self, test_client):
        """Should reject operation with zero-width space."""
        response = test_client.get(f"/calculate?operation={quote('add\u200B')}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_zero_width_space_in_add(self, test_client):
        """Should reject operation with zero-width space in middle."""
        response = test_client.get(f"/calculate?operation={quote('a\u200Bd\u200Bd')}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_control_characters_in_a(self, test_client):
        """Should reject control characters in a."""
        response = test_client.get(f"/calculate?operation=add&a={quote('1\u0000')}&b=2")
        assert response.status_code == 422

    def test_newline_in_operation(self, test_client):
        """Should reject newline in operation."""
        response = test_client.get(f"/calculate?operation={quote('add\n')}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_carriage_return_in_operation(self, test_client):
        """Should reject carriage return in operation."""
        response = test_client.get(f"/calculate?operation={quote('add\r')}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_tabulation_in_operation(self, test_client):
        """Should reject tabulation in operation."""
        response = test_client.get(f"/calculate?operation={quote('add\t')}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]


# ========================================================================
# SQL injection (even though there's no database)
# ========================================================================
class TestSQLInjection:
    """Tests for SQL injection payloads."""

    def test_sql_injection_in_operation(self, test_client):
        """Should reject SQL injection in operation."""
        payload = "add'; DROP TABLE users;--"
        response = test_client.get(f"/calculate?operation={quote(payload)}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_sql_injection_in_a(self, test_client):
        """Should reject SQL injection in a."""
        payload = "1 OR 1=1"
        response = test_client.get(f"/calculate?operation=add&a={quote(payload)}&b=2")
        assert response.status_code == 422

    def test_sql_union_injection(self, test_client):
        """Should reject SQL UNION injection."""
        payload = "UNION SELECT"
        response = test_client.get(f"/calculate?operation={quote(payload)}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_sql_comment_injection(self, test_client):
        """Should reject SQL comment injection."""
        response = test_client.get("/calculate?operation=add/*&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]


# ========================================================================
# XSS attacks
# ========================================================================
class TestXSSAttacks:
    """Tests for XSS (Cross-Site Scripting) attacks."""

    def test_xss_in_operation(self, test_client):
        """Should reject XSS in operation."""
        response = test_client.get("/calculate?operation=<script>alert(1)</script>&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_xss_img_tag_in_operation(self, test_client):
        """Should reject XSS with img tag in operation."""
        payload = '<img src=x onerror=alert(1)>'
        response = test_client.get(f"/calculate?operation={quote(payload)}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_xss_in_a(self, test_client):
        """Should reject XSS in a."""
        response = test_client.get("/calculate?operation=add&a=<script>alert(1)</script>&b=2")
        assert response.status_code == 422

    def test_javascript_url_in_operation(self, test_client):
        """Should reject javascript: URL in operation."""
        response = test_client.get("/calculate?operation=javascript:alert(1)&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_onerror_in_operation(self, test_client):
        """Should reject onerror in operation."""
        payload = 'add onerror=alert(1)'
        response = test_client.get(f"/calculate?operation={quote(payload)}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_template_injection_in_operation(self, test_client):
        """Should reject template injection in operation."""
        response = test_client.get("/calculate?operation=add${alert(1)}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]


# ========================================================================
# Prototype pollution
# ========================================================================
class TestPrototypePollution:
    """Tests for prototype pollution attacks."""

    def test_proto_in_operation(self, test_client):
        """Should reject __proto__ in operation."""
        response = test_client.get("/calculate?operation=__proto__&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_constructor_prototype_in_operation(self, test_client):
        """Should reject constructor.prototype in operation."""
        response = test_client.get("/calculate?operation=constructor.prototype&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_proto_in_a(self, test_client):
        """Should reject __proto__ in a."""
        response = test_client.get("/calculate?operation=add&a=__proto__&b=2")
        assert response.status_code == 422


# ========================================================================
# Path traversal
# ========================================================================
class TestPathTraversal:
    """Tests for path traversal attacks."""

    def test_path_traversal_in_operation(self, test_client):
        """Should reject path traversal in operation."""
        response = test_client.get("/calculate?operation=../../../etc/passwd&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_path_traversal_in_a(self, test_client):
        """Should reject path traversal in a."""
        response = test_client.get("/calculate?operation=add&a=../../../etc/passwd&b=2")
        assert response.status_code == 422

    def test_null_byte_injection_in_operation(self, test_client):
        """Should reject null byte injection in operation."""
        payload = 'add\x00malicious'
        response = test_client.get(f"/calculate?operation={quote(payload)}&a=1&b=2")
        assert response.status_code == 400


# ========================================================================
# Command injection
# ========================================================================
class TestCommandInjection:
    """Tests for command injection attacks."""

    def test_pipe_injection(self, test_client):
        """Should reject pipe character injection."""
        payload = 'add|cat /etc/passwd'
        response = test_client.get(f"/calculate?operation={quote(payload)}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_semicolon_command_injection(self, test_client):
        """Should reject semicolon command injection."""
        payload = 'add; ls'
        response = test_client.get(f"/calculate?operation={quote(payload)}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_double_ampersand_injection(self, test_client):
        """Should reject && command injection."""
        payload = 'add && rm -rf /'
        response = test_client.get(f"/calculate?operation={quote(payload)}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_backticks_injection(self, test_client):
        """Should reject backticks command injection."""
        response = test_client.get("/calculate?operation=`ls`&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_dollar_parens_injection(self, test_client):
        """Should reject $(command) injection."""
        response = test_client.get("/calculate?operation=$(ls)&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]


# ========================================================================
# Query string manipulation
# ========================================================================
class TestQueryStringManipulation:
    """Tests for query string manipulation attacks."""

    def test_duplicate_operation_params(self, test_client):
        """Should handle duplicate operation parameters (FastAPI uses last value)."""
        response = test_client.get("/calculate?operation=divide&operation=add&a=10&b=2")
        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "add"
        assert data["result"] == 12

    def test_empty_operation_param(self, test_client):
        """Should reject empty operation parameter."""
        response = test_client.get("/calculate?operation=&a=1&b=2")
        # Empty string is valid but not in VALID_OPERATIONS, so returns 400
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_operation_with_only_spaces(self, test_client):
        """Should reject operation with only spaces."""
        response = test_client.get(f"/calculate?operation={quote('   ')}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_url_encoded_operation(self, test_client):
        """Should handle URL-encoded operation."""
        response = test_client.get("/calculate?operation=%61%64%64&a=1&b=2")
        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "add"
        assert data["result"] == 3

    def test_double_encoded_operation(self, test_client):
        """Should reject double-encoded operation."""
        response = test_client.get("/calculate?operation=%2561%2564%2564&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]


# ========================================================================
# Type coercion attacks
# ========================================================================
class TestTypeCoercionAttacks:
    """Tests for malicious type coercion."""

    def test_true_string_in_a(self, test_client):
        """Should reject string 'true' in a (not a number)."""
        response = test_client.get("/calculate?operation=add&a=true&b=2")
        assert response.status_code == 422

    def test_false_string_in_a(self, test_client):
        """Should reject string 'false' in a (not a number)."""
        response = test_client.get("/calculate?operation=add&a=false&b=2")
        assert response.status_code == 422

    def test_null_string_in_a(self, test_client):
        """Should reject string 'null' in a (not a number)."""
        response = test_client.get("/calculate?operation=add&a=null&b=2")
        assert response.status_code == 422

    def test_undefined_string_in_a(self, test_client):
        """Should reject string 'undefined' in a (not a number)."""
        response = test_client.get("/calculate?operation=add&a=undefined&b=2")
        assert response.status_code == 422

    def test_json_object_in_a(self, test_client):
        """Should reject JSON object in a."""
        response = test_client.get('/calculate?operation=add&a={"a":1}&b=2')
        assert response.status_code == 422

    def test_array_in_a(self, test_client):
        """Should reject array in a."""
        response = test_client.get("/calculate?operation=add&a=[1,2,3]&b=2")
        assert response.status_code == 422


# ========================================================================
# Regex injection
# ========================================================================
class TestRegexInjection:
    """Tests for regex injection attacks."""

    def test_regex_pattern_in_operation(self, test_client):
        """Should reject regex pattern in operation."""
        response = test_client.get("/calculate?operation=/add/&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_regex_special_chars_in_operation(self, test_client):
        """Should reject regex special characters in operation."""
        response = test_client.get("/calculate?operation=add.*&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_regex_pattern_in_a(self, test_client):
        """Should reject regex pattern in a."""
        response = test_client.get("/calculate?operation=add&a=/123/&b=2")
        assert response.status_code == 422


# ========================================================================
# Format string attacks
# ========================================================================
class TestFormatStringAttacks:
    """Tests for format string attacks."""

    def test_format_specifiers_in_operation(self, test_client):
        """Should reject format specifiers in operation."""
        response = test_client.get("/calculate?operation=%s%s%s&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_n_format_specifier_in_operation(self, test_client):
        """Should reject %n format specifier in operation."""
        response = test_client.get("/calculate?operation=add%n&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_format_specifiers_in_a(self, test_client):
        """Should reject format specifiers in a."""
        response = test_client.get("/calculate?operation=add&a=%d&b=2")
        assert response.status_code == 422


# ========================================================================
# HTTP Parameter Pollution (HPP)
# ========================================================================
class TestHTTPParameterPollution:
    """Tests for HTTP Parameter Pollution attacks."""

    def test_duplicate_operation_params(self, test_client):
        """Should handle duplicate operation parameters (FastAPI uses last value)."""
        response = test_client.get("/calculate?operation=divide&operation=add&a=10&b=2")
        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "add"
        assert data["result"] == 12

    def test_duplicate_a_params(self, test_client):
        """Should handle duplicate a parameters (FastAPI uses last value)."""
        response = test_client.get("/calculate?operation=add&a=5&a=10&b=2")
        assert response.status_code == 200
        data = response.json()
        assert data["a"] == 10.0

    def test_duplicate_b_params(self, test_client):
        """Should handle duplicate b parameters (FastAPI uses last value)."""
        response = test_client.get("/calculate?operation=add&a=5&b=2&b=10")
        assert response.status_code == 200
        data = response.json()
        assert data["b"] == 10.0


# ========================================================================
# Case and formatting variations
# ========================================================================
class TestVariations:
    """Tests for case and formatting variations."""

    def test_camelcase_operation(self, test_client):
        """Should reject camelCase operation."""
        response = test_client.get("/calculate?operation=Add&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_mixed_case_operation(self, test_client):
        """Should reject mixed case operation."""
        response = test_client.get("/calculate?operation=aDd&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_underscore_operation(self, test_client):
        """Should reject operation with underscore."""
        response = test_client.get("/calculate?operation=add_operation&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_dash_operation(self, test_client):
        """Should reject operation with dash."""
        response = test_client.get("/calculate?operation=add-operation&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]

    def test_space_operation(self, test_client):
        """Should reject operation with space."""
        response = test_client.get(f"/calculate?operation={quote('add operation')}&a=1&b=2")
        assert response.status_code == 400
        assert "Opération inconnue" in response.json()["detail"]
