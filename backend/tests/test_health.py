"""Tests for the /health endpoint."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """Test that GET /health returns HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_has_status_key(self, client: TestClient) -> None:
        """Test that health response contains 'status' key."""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_response_has_model_loaded_key(self, client: TestClient) -> None:
        """Test that health response contains 'model_loaded' key."""
        response = client.get("/health")
        data = response.json()

        assert "model_loaded" in data

    def test_health_model_not_loaded_initially(self, client: TestClient) -> None:
        """Test that model_loaded is False when model not loaded (torch unavailable)."""
        response = client.get("/health")
        data = response.json()

        # Without torch, model won't be loaded
        assert "model_loaded" in data
        # Initial state is False since no model loaded in test
        assert data["model_loaded"] is False

    def test_health_with_mocked_loaded_model(self, client: TestClient) -> None:
        """Test health endpoint when model is mocked as loaded."""
        # Patch the global _model to simulate loaded model
        from app import main

        # Store original
        original_model = main._model

        try:
            # Create mock model
            mock_model = type("MockModel", (), {"model": {"loaded": True}})()
            main._model = mock_model

            response = client.get("/health")
            data = response.json()

            assert response.status_code == 200
            assert data["status"] == "healthy"
            assert data["model_loaded"] is True
        finally:
            # Restore original
            main._model = original_model

    def test_health_returns_json_content_type(self, client: TestClient) -> None:
        """Test that health endpoint returns JSON content type."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_health_response_body_structure(self, client: TestClient) -> None:
        """Test that health response has correct JSON structure."""
        response = client.get("/health")
        data = response.json()

        # Should have exactly these keys
        expected_keys = {"status", "model_loaded"}
        assert set(data.keys()) == expected_keys
