"""Shared test fixtures for the downstream service."""

import pytest
from fastapi.testclient import TestClient

from src.data.store import simulation_state
from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_simulation():
    """Ensure each test starts with simulation_state in 'normal' mode."""
    yield
    simulation_state["mode"] = "normal"
