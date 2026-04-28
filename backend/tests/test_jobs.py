"""Tests for jobs module.

This test suite covers:
- Job creation with unique IDs
- Job retrieval by ID
- Job status transitions
- Job store concurrency
- Job listing
"""

import asyncio

import pytest
import pytest_asyncio

from app.jobs import (
    JobStatus,
    PredictionJob,
    JobStore,
    create_job,
    get_job,
    update_job_status,
    list_jobs,
)


@pytest_asyncio.fixture
async def job_store():
    """Create a fresh JobStore for each test."""
    return JobStore()


class TestJobCreation:
    """Tests for create_job function."""

    @pytest.mark.asyncio
    async def test_create_job_returns_pending(self, job_store):
        """create_job returns job with PENDING status."""
        job = await job_store.create_job()
        assert job.status == JobStatus.PENDING

    @pytest.mark.asyncio
    async def test_create_job_generates_uuid(self, job_store):
        """create_job generates a valid UUID4."""
        job = await job_store.create_job()
        assert len(job.job_id) == 36
        assert job.job_id.count("-") == 4

    @pytest.mark.asyncio
    async def test_create_job_stores_in_store(self, job_store):
        """create_job stores job in JobStore."""
        job = await job_store.create_job()
        retrieved = await job_store.get_job(job.job_id)
        assert retrieved is not None
        assert retrieved.job_id == job.job_id

    @pytest.mark.asyncio
    async def test_create_job_with_config(self, job_store):
        """create_job accepts and stores config."""
        config = {"context_size": 512, "prediction_length": 96}
        job = await job_store.create_job(config=config)
        assert job.config == config


class TestJobRetrieval:
    """Tests for get_job function."""

    @pytest.mark.asyncio
    async def test_get_job_returns_job(self, job_store):
        """get_job returns the correct job."""
        created = await job_store.create_job()
        retrieved = await job_store.get_job(created.job_id)
        assert retrieved is not None
        assert retrieved.job_id == created.job_id
        assert retrieved.status == created.status

    @pytest.mark.asyncio
    async def test_get_job_returns_none_for_missing(self, job_store):
        """get_job returns None for non-existent ID."""
        result = await job_store.get_job("non-existent-id")
        assert result is None


class TestJobStatusUpdates:
    """Tests for update_job_status function."""

    @pytest.mark.asyncio
    async def test_update_status_changes_status(self, job_store):
        """update_job_status changes the status."""
        job = await job_store.create_job()
        await job_store.update_job_status(job.job_id, JobStatus.PROCESSING)
        updated = await job_store.get_job(job.job_id)
        assert updated.status == JobStatus.PROCESSING

    @pytest.mark.asyncio
    async def test_update_status_changes_timestamp(self, job_store):
        """update_job_status updates the updated_at timestamp."""
        job = await job_store.create_job()
        original_updated = job.updated_at
        await asyncio.sleep(0.01)
        await job_store.update_job_status(job.job_id, JobStatus.PROCESSING)
        updated = await job_store.get_job(job.job_id)
        assert updated.updated_at > original_updated

    @pytest.mark.asyncio
    async def test_update_status_stores_result(self, job_store):
        """update_job_status stores forecast result."""
        job = await job_store.create_job()
        result = {"forecast": [1.0, 2.0, 3.0], "metadata": {"input_points": 100}}
        await job_store.update_job_status(job.job_id, JobStatus.COMPLETED, result=result)
        updated = await job_store.get_job(job.job_id)
        assert updated.result == result

    @pytest.mark.asyncio
    async def test_update_status_stores_error(self, job_store):
        """update_job_status stores error message."""
        job = await job_store.create_job()
        await job_store.update_job_status(
            job.job_id, JobStatus.FAILED, error_message="Model error"
        )
        updated = await job_store.get_job(job.job_id)
        assert updated.error_message == "Model error"

    @pytest.mark.asyncio
    async def test_update_status_returns_false_for_missing(self, job_store):
        """update_job_status returns False for non-existent job."""
        result = await job_store.update_job_status(
            "non-existent", JobStatus.PROCESSING
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_status_transitions_pending_to_completed(self, job_store):
        """Job transitions PENDING -> PROCESSING -> COMPLETED correctly."""
        job = await job_store.create_job()
        assert job.status == JobStatus.PENDING

        await job_store.update_job_status(job.job_id, JobStatus.PROCESSING)
        job = await job_store.get_job(job.job_id)
        assert job.status == JobStatus.PROCESSING

        await job_store.update_job_status(
            job.job_id, JobStatus.COMPLETED, result={"forecast": [1.0]}
        )
        job = await job_store.get_job(job.job_id)
        assert job.status == JobStatus.COMPLETED
        assert job.result is not None

    @pytest.mark.asyncio
    async def test_status_transitions_pending_to_failed(self, job_store):
        """Job transitions PENDING -> PROCESSING -> FAILED correctly."""
        job = await job_store.create_job()
        assert job.status == JobStatus.PENDING

        await job_store.update_job_status(job.job_id, JobStatus.PROCESSING)
        job = await job_store.get_job(job.job_id)
        assert job.status == JobStatus.PROCESSING

        await job_store.update_job_status(
            job.job_id, JobStatus.FAILED, error_message="Prediction failed"
        )
        job = await job_store.get_job(job.job_id)
        assert job.status == JobStatus.FAILED
        assert job.error_message == "Prediction failed"


class TestJobStoreConcurrency:
    """Tests for concurrent access to JobStore."""

    @pytest.mark.asyncio
    async def test_concurrent_job_creation(self, job_store):
        """JobStore handles concurrent create_job calls safely."""
        tasks = [job_store.create_job() for _ in range(100)]
        jobs = await asyncio.gather(*tasks)

        job_ids = [j.job_id for j in jobs]
        assert len(set(job_ids)) == 100

        for job in jobs:
            stored = await job_store.get_job(job.job_id)
            assert stored is not None
            assert stored.job_id == job.job_id

    @pytest.mark.asyncio
    async def test_concurrent_status_updates(self, job_store):
        """JobStore handles concurrent status updates safely."""
        job = await job_store.create_job()

        async def update_loop(status, count):
            for _ in range(count):
                await job_store.update_job_status(job.job_id, status)

        await asyncio.gather(
            update_loop(JobStatus.PROCESSING, 10),
            update_loop(JobStatus.COMPLETED, 1),
        )

        final = await job_store.get_job(job.job_id)
        assert final.status == JobStatus.COMPLETED


class TestJobList:
    """Tests for list_jobs function."""

    @pytest.mark.asyncio
    async def test_list_jobs_returns_all_jobs(self, job_store):
        """list_jobs returns all jobs."""
        for i in range(5):
            await job_store.create_job()
        jobs = await job_store.list_jobs()
        assert len(jobs) == 5

    @pytest.mark.asyncio
    async def test_list_jobs_sorted_by_created_at(self, job_store):
        """list_jobs returns jobs sorted by created_at descending."""
        import time

        job1 = await job_store.create_job()
        await asyncio.sleep(0.01)
        job2 = await job_store.create_job()

        jobs = await job_store.list_jobs()
        assert jobs[0].job_id == job2.job_id
        assert jobs[1].job_id == job1.job_id


class TestModuleLevelFunctions:
    """Tests for module-level convenience functions."""

    @pytest.mark.asyncio
    async def test_module_create_job(self):
        """Module-level create_job works."""
        job = await create_job()
        assert job.status == JobStatus.PENDING

    @pytest.mark.asyncio
    async def test_module_get_job(self):
        """Module-level get_job works."""
        created = await create_job()
        retrieved = await get_job(created.job_id)
        assert retrieved is not None
        assert retrieved.job_id == created.job_id

    @pytest.mark.asyncio
    async def test_module_update_job_status(self):
        """Module-level update_job_status works."""
        job = await create_job()
        result = await update_job_status(job.job_id, JobStatus.COMPLETED, result={"test": True})
        assert result is True
        updated = await get_job(job.job_id)
        assert updated.status == JobStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_module_list_jobs(self):
        """Module-level list_jobs works."""
        await create_job()
        await create_job()
        jobs = await list_jobs()
        assert len(jobs) >= 2
