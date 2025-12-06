"""
Smoke tests to verify the app starts and serves basic endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app import app


@pytest.fixture
def client():
    """Create a test client for the app."""
    return TestClient(app)


class TestAppSmoke:
    """Smoke tests for app startup and basic functionality."""

    def test_app_starts_and_serves_frontend(self, client: TestClient):
        """Verify app starts without errors and serves HTML at root."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_health_endpoint_returns_200(self, client: TestClient):
        """Verify health endpoint works."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["db_ok"] is True

    def test_config_household_profile_returns_200(self, client: TestClient):
        """Verify config API is accessible."""
        response = client.get("/api/config/household-profile")
        assert response.status_code == 200

    def test_removed_dishes_endpoint_returns_404(self, client: TestClient):
        """Verify scaffolding endpoint is removed."""
        response = client.get("/api/dishes?ingredient=test")
        assert response.status_code == 404

    def test_removed_hello_endpoint_returns_404(self, client: TestClient):
        """Verify old hello endpoint is removed."""
        response = client.get("/api/hello")
        assert response.status_code == 404
