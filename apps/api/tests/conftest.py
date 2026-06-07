"""Shared test fixtures.

The downstream HTTP client is replaced with an in-process mock so tests
exercise the api code paths (including the downstream-error normalization)
without needing a real downstream service running.
"""

import httpx
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services import downstream as ds_module


class MockDownstream:
    def __init__(self):
        self._responses: dict[tuple[str, str], httpx.Response] = {}

    def expect(self, method: str, path: str, response: httpx.Response) -> None:
        self._responses[(method.upper(), path)] = response

    def _handler(self, request: httpx.Request) -> httpx.Response:
        key = (request.method, request.url.path)
        if key in self._responses:
            return self._responses[key]
        return httpx.Response(
            404,
            json={"detail": f"unmocked downstream call: {key[0]} {key[1]}"},
        )

    def as_client(self) -> httpx.AsyncClient:
        transport = httpx.MockTransport(self._handler)
        return httpx.AsyncClient(transport=transport, base_url="http://mocked-downstream")


@pytest.fixture
def mock_downstream():
    mock = MockDownstream()
    original = ds_module._client
    ds_module._client = mock.as_client()
    yield mock
    ds_module._client = original


@pytest.fixture
def client():
    return TestClient(app)
