"""Integration tests for prediction API endpoints.

This test suite covers:
- POST /predict/file: CSV file upload with config
- POST /predict/data: JSON data submission
- GET /predict/status/{job_id}: Job status polling
- GET /predict/result/{job_id}: Result retrieval
- Error handling and validation
"""

from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.jobs import JobStatus


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from app.main import app

    return TestClient(app)


@pytest.fixture
def sample_csv():
    """Generate a simple CSV file content."""
    lines = ["value"]
    for i in range(100):
        lines.append(f"{i * 0.5}")
    return "\n".join(lines).encode("utf-8")


@pytest.fixture
def mock_model():
    """Create a mock ForecastingModel."""
    model = MagicMock()
    model.fit = MagicMock()
    model.predict = MagicMock(return_value={"forecast": np.array([1.0, 2.0, 3.0]), "prediction_length": 3})
    return model


class TestPredictFileEndpoint:
    """Tests for POST /predict/file endpoint."""

    def test_upload_csv_returns_job_id(self, client, sample_csv, mock_model):
        """Upload CSV file returns job_id and status."""
        with patch("app.routers.predict.get_model", return_value=mock_model):
            with patch("app.routers.predict._run_prediction_task", new_callable=AsyncMock):
                response = client.post(
                    "/predict/file",
                    files={"file": ("test.csv", sample_csv, "text/csv")},
                    data={"context_size": 512, "prediction_length": 96},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "processing"

    def test_upload_with_custom_config(self, client, sample_csv, mock_model):
        """Upload with custom context_size and prediction_length."""
        with patch("app.routers.predict.get_model", return_value=mock_model):
            with patch("app.routers.predict._run_prediction_task", new_callable=AsyncMock):
                response = client.post(
                    "/predict/file",
                    files={"file": ("test.csv", sample_csv, "text/csv")},
                    data={"context_size": 256, "prediction_length": 48, "frequency": "D"},
                )

        assert response.status_code == status.HTTP_200_OK

    def test_upload_invalid_csv_returns_400(self, client, mock_model):
        """Upload invalid CSV returns 400."""
        with patch("app.routers.predict.get_model", return_value=mock_model):
            response = client.post(
                "/predict/file",
                files={"file": ("test.csv", b"not a valid csv", "text/csv")},
                data={"context_size": 512, "prediction_length": 96},
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_missing_file_returns_422(self, client, mock_model):
        """Upload missing file returns 422."""
        with patch("app.routers.predict.get_model", return_value=mock_model):
            response = client.post(
                "/predict/file",
                data={"context_size": 512, "prediction_length": 96},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_model_not_loaded_returns_503(self, client, sample_csv):
        """Model not loaded returns 503."""
        with patch("app.routers.predict.get_model", return_value=None):
            response = client.post(
                "/predict/file",
                files={"file": ("test.csv", sample_csv, "text/csv")},
                data={"context_size": 512, "prediction_length": 96},
            )

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


class TestPredictDataEndpoint:
    """Tests for POST /predict/data endpoint."""

    def test_post_data_returns_job_id(self, client, mock_model):
        """Post raw data returns job_id."""
        with patch("app.routers.predict.get_model", return_value=mock_model):
            with patch("app.routers.predict._run_prediction_task", new_callable=AsyncMock):
                response = client.post(
                    "/predict/data",
                    json={"data": [1.0, 2.0, 3.0, 4.0, 5.0], "context_size": 5, "prediction_length": 3},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "processing"

    def test_post_data_with_custom_config(self, client, mock_model):
        """Post data with custom config."""
        with patch("app.routers.predict.get_model", return_value=mock_model):
            with patch("app.routers.predict._run_prediction_task", new_callable=AsyncMock):
                response = client.post(
                    "/predict/data",
                    json={"data": [1.0, 2.0, 3.0], "context_size": 3, "prediction_length": 2, "frequency": "H"},
                )

        assert response.status_code == status.HTTP_200_OK

    def test_post_empty_array_returns_400(self, client, mock_model):
        """Post empty data array returns 400."""
        with patch("app.routers.predict.get_model", return_value=mock_model):
            response = client.post(
                "/predict/data",
                json={"data": [], "context_size": 512, "prediction_length": 96},
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_model_not_loaded_returns_503(self, client):
        """Model not loaded returns 503."""
        with patch("app.routers.predict.get_model", return_value=None):
            response = client.post(
                "/predict/data",
                json={"data": [1.0, 2.0, 3.0], "context_size": 512, "prediction_length": 96},
            )

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


class TestJobStatusEndpoint:
    """Tests for GET /predict/status/{job_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_status_of_existing_job(self, client):
        """Get status of existing job returns status."""
        from app.jobs import create_job

        job = await create_job()

        response = client.get(f"/predict/status/{job.job_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["job_id"] == job.job_id
        assert data["status"] == "pending"

    def test_get_status_of_nonexistent_job_returns_404(self, client):
        """Get status of non-existent job returns 404."""
        response = client.get("/predict/status/nonexistent-job-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestJobResultEndpoint:
    """Tests for GET /predict/result/{job_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_result_of_completed_job(self, client):
        """Get result of completed job returns forecast and metadata."""
        from app.jobs import create_job, update_job_status

        job = await create_job()
        await update_job_status(
            job.job_id,
            JobStatus.COMPLETED,
            result={"forecast": [1.0, 2.0, 3.0], "metadata": {"input_points": 100}},
        )

        response = client.get(f"/predict/result/{job.job_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["job_id"] == job.job_id
        assert data["status"] == "completed"
        assert data["forecast"] == [1.0, 2.0, 3.0]
        assert "metadata" in data

    @pytest.mark.asyncio
    async def test_get_result_of_processing_job_returns_202(self, client):
        """Get result of processing job returns 202."""
        from app.jobs import create_job

        job = await create_job()

        response = client.get(f"/predict/result/{job.job_id}")

        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["status"] == "processing"

    @pytest.mark.asyncio
    async def test_get_result_of_failed_job_returns_500(self, client):
        """Get result of failed job returns 500 with error."""
        from app.jobs import create_job, update_job_status

        job = await create_job()
        await update_job_status(job.job_id, JobStatus.FAILED, error_message="Model error")

        response = client.get(f"/predict/result/{job.job_id}")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_get_result_of_nonexistent_job_returns_404(self, client):
        """Get result of non-existent job returns 404."""
        response = client.get("/predict/result/nonexistent-job-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestEndToEndFlow:
    """End-to-end integration tests."""

    def test_full_flow_upload_status_result(self, client, sample_csv, mock_model):
        """Full flow: upload CSV -> poll status -> get result."""
        with patch("app.routers.predict.get_model", return_value=mock_model):
            with patch("app.routers.predict._run_prediction_task", new_callable=AsyncMock) as mock_task:
                upload_response = client.post(
                    "/predict/file",
                    files={"file": ("test.csv", sample_csv, "text/csv")},
                    data={"context_size": 512, "prediction_length": 96},
                )

        assert upload_response.status_code == status.HTTP_200_OK
        job_id = upload_response.json()["job_id"]

        status_response = client.get(f"/predict/status/{job_id}")
        assert status_response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_response_format_matches_spec(self, client):
        """Response format matches D-03 specification."""
        from app.jobs import create_job, update_job_status

        job = await create_job()
        await update_job_status(
            job.job_id,
            JobStatus.COMPLETED,
            result={
                "forecast": [1.2, 1.3, 1.4],
                "metadata": {
                    "computation_time_ms": 245,
                    "model_used": "TimesFM2p5",
                    "input_points": 1024,
                    "prediction_length": 96,
                },
            },
        )

        response = client.get(f"/predict/result/{job.job_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "job_id" in data
        assert "status" in data
        assert "forecast" in data
        assert "metadata" in data
        assert data["forecast"] == [1.2, 1.3, 1.4]
        assert data["metadata"]["model_used"] == "TimesFM2p5"
