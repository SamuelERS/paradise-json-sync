"""
Health Endpoint Tests / Tests del Endpoint de Salud
===================================================

Tests for the health check endpoint.
Tests para el endpoint de verificación de salud.
"""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /api/health endpoint."""

    def test_health_check_returns_200(self):
        """Health check returns 200 OK."""
        response = client.get("/api/health")

        assert response.status_code == 200

    def test_health_check_returns_healthy_status(self):
        """Health check returns healthy status."""
        response = client.get("/api/health")
        data = response.json()

        assert data["status"] == "healthy"

    def test_health_check_includes_version(self):
        """Health check includes version."""
        response = client.get("/api/health")
        data = response.json()

        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_health_check_includes_timestamp(self):
        """Health check includes timestamp."""
        response = client.get("/api/health")
        data = response.json()

        assert "timestamp" in data

    def test_health_check_includes_services(self):
        """Health check includes services status."""
        response = client.get("/api/health")
        data = response.json()

        assert "services" in data
        assert data["services"]["storage"] == "ok"
        assert data["services"]["processing"] == "ok"


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_returns_200(self):
        """Root endpoint returns 200 OK."""
        response = client.get("/")

        assert response.status_code == 200

    def test_root_returns_api_info(self):
        """Root endpoint returns API info."""
        response = client.get("/")
        data = response.json()

        assert "message" in data
        assert "version" in data
        assert "docs" in data
