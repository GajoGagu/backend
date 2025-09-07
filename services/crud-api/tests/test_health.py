import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_endpoint(self, client):
        """Test basic health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_healthz_endpoint(self, client):
        """Test healthz endpoint."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True

    def test_readyz_endpoint(self, client):
        """Test readyz endpoint."""
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True

    def test_health_endpoints_consistency(self, client):
        """Test that all health endpoints return consistent responses."""
        endpoints = ["/health", "/healthz", "/readyz"]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/json"
