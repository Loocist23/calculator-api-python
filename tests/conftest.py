"""
Pytest configuration and fixtures for Calculator API tests
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import app


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
