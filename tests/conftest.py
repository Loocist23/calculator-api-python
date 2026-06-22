"""
Pytest configuration and fixtures for Calculator API tests
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.main import app  # noqa: E402


@pytest.fixture
def calculator():
    """Fixture providing a Calculator instance for unit tests."""
    from src.calculator import Calculator

    return Calculator()


@pytest.fixture
def test_client():
    """Fixture providing a FastAPI test client for integration tests."""
    return TestClient(app)


@pytest.fixture
def server_base_url():
    """Base URL for the test server."""
    return "http://127.0.0.1:8000"
