"""
CORS Middleware Tests / Pruebas del Middleware CORS
====================================================

Tests for CORS configuration and middleware.
Pruebas para la configuración y middleware CORS.
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


class TestCORSConfiguration:
    """Tests for CORS middleware configuration."""

    @pytest.fixture
    def client(self):
        """Test client for the FastAPI app."""
        return TestClient(app)

    def test_cors_allows_localhost_5173(self, client):
        """Test that CORS allows requests from localhost:5173 (Vite dev server)."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

    def test_cors_allows_localhost_3000(self, client):
        """Test that CORS allows requests from localhost:3000."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_cors_allows_production_origin(self, client):
        """Test that CORS allows requests from production domain."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "https://paradise-json-sync.com",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "https://paradise-json-sync.com"

    def test_cors_rejects_unknown_origin(self, client):
        """Test that CORS rejects requests from unknown origins."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://malicious-site.com",
                "Access-Control-Request-Method": "GET",
            },
        )

        # Should not include Access-Control-Allow-Origin for unknown origins
        allow_origin = response.headers.get("access-control-allow-origin")
        assert allow_origin is None or allow_origin != "http://malicious-site.com"


class TestCORSMethods:
    """Tests for allowed CORS methods."""

    @pytest.fixture
    def client(self):
        """Test client for the FastAPI app."""
        return TestClient(app)

    def test_cors_allows_get_method(self, client):
        """Test that CORS allows GET method."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        allow_methods = response.headers.get("access-control-allow-methods", "")
        assert "GET" in allow_methods

    def test_cors_allows_post_method(self, client):
        """Test that CORS allows POST method."""
        response = client.options(
            "/api/upload",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )

        allow_methods = response.headers.get("access-control-allow-methods", "")
        assert "POST" in allow_methods

    def test_cors_allows_options_method(self, client):
        """Test that CORS allows OPTIONS method (preflight)."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "OPTIONS",
            },
        )

        allow_methods = response.headers.get("access-control-allow-methods", "")
        assert "OPTIONS" in allow_methods


class TestCORSHeaders:
    """Tests for allowed CORS headers."""

    @pytest.fixture
    def client(self):
        """Test client for the FastAPI app."""
        return TestClient(app)

    def test_cors_allows_content_type_header(self, client):
        """Test that CORS allows Content-Type header."""
        response = client.options(
            "/api/upload",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        allow_headers = response.headers.get("access-control-allow-headers", "")
        assert "content-type" in allow_headers.lower()

    def test_cors_allows_authorization_header(self, client):
        """Test that CORS allows Authorization header."""
        response = client.options(
            "/api/upload",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization",
            },
        )

        allow_headers = response.headers.get("access-control-allow-headers", "")
        assert "authorization" in allow_headers.lower()

    def test_cors_allows_accept_header(self, client):
        """Test that CORS allows Accept header."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Accept",
            },
        )

        allow_headers = response.headers.get("access-control-allow-headers", "")
        assert "accept" in allow_headers.lower()


class TestCORSCredentials:
    """Tests for CORS credentials support."""

    @pytest.fixture
    def client(self):
        """Test client for the FastAPI app."""
        return TestClient(app)

    def test_cors_allows_credentials(self, client):
        """Test that CORS allows credentials."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        allow_credentials = response.headers.get("access-control-allow-credentials")
        assert allow_credentials == "true"


class TestCORSActualRequests:
    """Tests for CORS on actual requests (not preflight)."""

    @pytest.fixture
    def client(self):
        """Test client for the FastAPI app."""
        return TestClient(app)

    def test_cors_headers_on_actual_get_request(self, client):
        """Test CORS headers are present on actual GET request."""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:5173"},
        )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

    def test_cors_headers_on_actual_post_request(self, client):
        """Test CORS headers are present on actual POST request."""
        response = client.post(
            "/api/upload",
            headers={"Origin": "http://localhost:5173"},
            files=[],  # Empty files list
        )

        # May return error due to no files, but CORS headers should be present
        assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


class TestCORSEndpoints:
    """Tests for CORS on different endpoints."""

    @pytest.fixture
    def client(self):
        """Test client for the FastAPI app."""
        return TestClient(app)

    def test_cors_on_health_endpoint(self, client):
        """Test CORS on /api/health endpoint."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_on_upload_endpoint(self, client):
        """Test CORS on /api/upload endpoint."""
        response = client.options(
            "/api/upload",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_on_process_endpoint(self, client):
        """Test CORS on /api/process endpoint."""
        response = client.options(
            "/api/process",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_on_status_endpoint(self, client):
        """Test CORS on /api/status endpoint."""
        response = client.options(
            "/api/status/test-job-id",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_on_download_endpoint(self, client):
        """Test CORS on /api/download endpoint."""
        response = client.options(
            "/api/download/excel/test-job-id",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers

    def test_cors_on_root_endpoint(self, client):
        """Test CORS on root endpoint."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
