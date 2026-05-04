"""Async job management for prediction requests.

Jobs are created immediately, processed in the background, and polled for status/result.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PredictionJob:
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    signal_name: Optional[str] = None
    original_data: Optional[List[float]] = field(default_factory=list)


class JobStore:
    _instance: Optional["JobStore"] = None

    def __init__(self) -> None:
        self._jobs: Dict[str, PredictionJob] = {}
        self._lock = asyncio.Lock()

    async def create_job(
        self,
        config: Optional[Dict[str, Any]] = None,
        signal_name: Optional[str] = None,
        original_data: Optional[List[float]] = None,
    ) -> PredictionJob:
        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        job = PredictionJob(
            job_id=job_id,
            status=JobStatus.PENDING,
            created_at=now,
            updated_at=now,
            config=config,
            signal_name=signal_name,
            original_data=original_data or [],
        )
        async with self._lock:
            self._jobs[job_id] = job
        logger.info(f"Job created: {job_id}")
        return job

    async def get_job(self, job_id: str) -> Optional[PredictionJob]:
        async with self._lock:
            return self._jobs.get(job_id)

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        async with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return False
            job.status = status
            job.updated_at = datetime.now(timezone.utc)
            if result is not None:
                job.result = result
            if error_message is not None:
                job.error_message = error_message
            logger.info(f"Job {job_id} status updated to {status.value}")
            return True

    async def list_jobs(self) -> List[PredictionJob]:
        async with self._lock:
            return sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)


_job_store: Optional[JobStore] = None


def get_job_store() -> JobStore:
    global _job_store
    if _job_store is None:
        _job_store = JobStore()
    return _job_store


async def create_job(
    config: Optional[Dict[str, Any]] = None,
    signal_name: Optional[str] = None,
    original_data: Optional[List[float]] = None,
) -> PredictionJob:
    store = get_job_store()
    return await store.create_job(config=config, signal_name=signal_name, original_data=original_data)


async def get_job(job_id: str) -> Optional[PredictionJob]:
    store = get_job_store()
    return await store.get_job(job_id)


async def update_job_status(
    job_id: str,
    status: JobStatus,
    result: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
) -> bool:
    store = get_job_store()
    return await store.update_job_status(job_id, status, result, error_message)


async def list_jobs() -> List[PredictionJob]:
    store = get_job_store()
    return await store.list_jobs()
