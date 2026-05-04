"""Prediction API endpoints.

Provides:
- POST /predict/file: Upload CSV file with config
- POST /predict/data: Submit raw time series data with config
- GET /predict/status/{job_id}: Poll job status
- GET /predict/result/{job_id}: Get forecast result
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.csv_processor import CSVValidationError, parse_csv
from app.jobs import JobStatus, create_job, get_job, list_jobs, update_job_status
from app.prediction_service import PredictionConfig, run_prediction
from app.state import get_model

logger = logging.getLogger(__name__)

router = APIRouter()


class PredictDataRequest(BaseModel):
    data: List[float]
    context_size: int = 512
    prediction_length: int = 96
    frequency: str = "auto"
    signal_name: Optional[str] = None


class JobResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    created_at: str
    updated_at: str


class JobResultResponse(BaseModel):
    job_id: str
    status: str
    forecast: Optional[List[float]] = None
    metadata: Optional[dict] = None


class JobSummaryResponse(BaseModel):
    job_id: str
    status: str
    created_at: str
    updated_at: str
    signal_name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ReapplyRequest(BaseModel):
    context_size: int = 512
    prediction_length: int = 96
    frequency: str = "auto"


class OriginalDataResponse(BaseModel):
    job_id: str
    signal_name: Optional[str] = None
    data: List[float]


async def _run_prediction_task(
    job_id: str,
    data: np.ndarray,
    config: PredictionConfig,
    model: Any,
) -> None:
    try:
        await update_job_status(job_id, JobStatus.PROCESSING)
        result = await run_prediction(data, config, model)
        await update_job_status(
            job_id,
            JobStatus.COMPLETED,
            result={
                "forecast": result.forecast.tolist(),
                "metadata": result.metadata,
            },
        )
    except Exception as e:
        logger.error(f"Prediction failed for job {job_id}: {e}")
        await update_job_status(job_id, JobStatus.FAILED, error_message=str(e))


@router.post("/file", response_model=JobResponse)
async def predict_file(
    file: UploadFile = File(...),
    context_size: int = Form(512),
    prediction_length: int = Form(96),
    frequency: str = Form("auto"),
    column_index: Optional[int] = Form(None),
    column_name: Optional[str] = Form(None),
) -> JobResponse:
    model = get_model()
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")

    try:
        parse_result = parse_csv(content, column_index, column_name)
    except CSVValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    config = PredictionConfig(
        context_size=context_size,
        prediction_length=prediction_length,
        frequency=frequency,
    )

    job = await create_job(
        config={"context_size": context_size, "prediction_length": prediction_length, "frequency": frequency},
        signal_name=file.filename,
        original_data=parse_result.data.tolist(),
    )

    asyncio.create_task(_run_prediction_task(job.job_id, parse_result.data, config, model))

    return JobResponse(job_id=job.job_id, status="processing")


@router.post("/data", response_model=JobResponse)
async def predict_data(request: PredictDataRequest) -> JobResponse:
    model = get_model()
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if not request.data:
        raise HTTPException(status_code=400, detail="Data array cannot be empty")

    try:
        config = PredictionConfig(
            context_size=request.context_size,
            prediction_length=request.prediction_length,
            frequency=request.frequency,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    data = np.array(request.data)

    job = await create_job(
        config={"context_size": request.context_size, "prediction_length": request.prediction_length, "frequency": request.frequency},
        signal_name=request.signal_name,
        original_data=request.data,
    )

    asyncio.create_task(_run_prediction_task(job.job_id, data, config, model))

    return JobResponse(job_id=job.job_id, status="processing")


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str) -> JobStatusResponse:
    job = await get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
    )


@router.get("/result/{job_id}")
async def get_result(job_id: str) -> JobResultResponse:
    job = await get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == JobStatus.COMPLETED:
        return JobResultResponse(
            job_id=job.job_id,
            status=job.status.value,
            forecast=job.result.get("forecast") if job.result else None,
            metadata=job.result.get("metadata") if job.result else None,
        )
    elif job.status == JobStatus.FAILED:
        raise HTTPException(
            status_code=500,
            detail=job.error_message or "Prediction failed",
        )
    else:
        return JobResultResponse(
            job_id=job.job_id,
            status=job.status.value,
        )


@router.get("/jobs", response_model=List[JobSummaryResponse])
async def list_all_jobs() -> List[JobSummaryResponse]:
    jobs = await list_jobs()
    return [
        JobSummaryResponse(
            job_id=job.job_id,
            status=job.status.value,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
            signal_name=job.signal_name,
            config=job.config,
        )
        for job in jobs
    ]


@router.post("/reapply/{job_id}", response_model=JobResponse)
async def reapply_prediction(job_id: str, request: ReapplyRequest) -> JobResponse:
    model = get_model()
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    existing_job = await get_job(job_id)
    if existing_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if not existing_job.original_data or len(existing_job.original_data) == 0:
        raise HTTPException(status_code=400, detail="Original data not available for this job")

    config = PredictionConfig(
        context_size=request.context_size,
        prediction_length=request.prediction_length,
        frequency=request.frequency,
    )

    data = np.array(existing_job.original_data)

    new_job = await create_job(
        config={
            "context_size": request.context_size,
            "prediction_length": request.prediction_length,
            "frequency": request.frequency,
        },
        signal_name=existing_job.signal_name,
        original_data=existing_job.original_data,
    )

    asyncio.create_task(_run_prediction_task(new_job.job_id, data, config, model))

    return JobResponse(job_id=new_job.job_id, status="processing")


@router.get("/data/{job_id}", response_model=OriginalDataResponse)
async def get_original_data(job_id: str) -> OriginalDataResponse:
    job = await get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if not job.original_data or len(job.original_data) == 0:
        raise HTTPException(status_code=404, detail="Original data not available for this job")

    return OriginalDataResponse(
        job_id=job.job_id,
        signal_name=job.signal_name,
        data=job.original_data,
    )
