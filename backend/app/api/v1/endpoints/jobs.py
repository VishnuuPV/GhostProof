from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.services.inference_client import InferenceClient
from app.services.job_store import JobRecord, JobStatus, job_store
from ghostproof_ai.contracts import AnalysisInput

router = APIRouter()


@router.post("/jobs", response_model=JobRecord, status_code=202)
async def create_job(scan_input: AnalysisInput, background_tasks: BackgroundTasks) -> JobRecord:
    job = job_store.create(scan_input)
    background_tasks.add_task(_run_job, job.job_id, scan_input)
    return job


@router.get("/jobs/{job_id}", response_model=JobRecord)
async def get_job(job_id: str) -> JobRecord:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job


async def _run_job(job_id: str, scan_input: AnalysisInput) -> None:
    job_store.update(job_id, status=JobStatus.RUNNING)
    try:
        report = await InferenceClient().analyze(scan_input)
    except Exception as exc:
        job_store.update(job_id, status=JobStatus.FAILED, error=str(exc))
        return
    job_store.update(job_id, status=JobStatus.COMPLETED, report=report)
