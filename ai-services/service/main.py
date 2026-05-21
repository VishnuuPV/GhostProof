from __future__ import annotations

from fastapi import FastAPI

from ghostproof_ai import DetectionOrchestrator
from ghostproof_ai.contracts import AnalysisInput, ScanReport

app = FastAPI(
    title="GhostProof AI Service",
    version="0.1.0",
    description="Synthetic media inference service for GhostProof.",
)
orchestrator = DetectionOrchestrator()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "ghostproof-ai"}


@app.post("/infer", response_model=ScanReport)
async def infer(scan_input: AnalysisInput) -> ScanReport:
    return await orchestrator.analyze(scan_input)
