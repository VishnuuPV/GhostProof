from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.scan_repository import ScanRepository
from app.services.inference_client import InferenceClient
from ghostproof_ai.contracts import AnalysisInput, ScanReport

router = APIRouter()


@router.post("/analyze", response_model=ScanReport)
async def analyze(scan_input: AnalysisInput, db: Session = Depends(get_db)) -> ScanReport:
    client = InferenceClient()
    report = await client.analyze(scan_input)
    ScanRepository(db).save(report=report, source_url=scan_input.source_url)
    return report
