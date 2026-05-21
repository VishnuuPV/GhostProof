from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from ghostproof_ai.contracts import AnalysisInput, ScanReport


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobRecord(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    scan_input: AnalysisInput
    report: ScanReport | None = None
    error: str | None = None


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}

    def create(self, scan_input: AnalysisInput) -> JobRecord:
        job = JobRecord(
            job_id=f"job_{uuid4().hex}",
            status=JobStatus.PENDING,
            scan_input=scan_input,
        )
        self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> JobRecord | None:
        return self._jobs.get(job_id)

    def update(
        self,
        job_id: str,
        status: JobStatus,
        report: ScanReport | None = None,
        error: str | None = None,
    ) -> JobRecord | None:
        job = self._jobs.get(job_id)
        if not job:
            return None
        updated = job.model_copy(
            update={
                "status": status,
                "updated_at": datetime.now(UTC),
                "report": report,
                "error": error,
            }
        )
        self._jobs[job_id] = updated
        return updated


job_store = InMemoryJobStore()
