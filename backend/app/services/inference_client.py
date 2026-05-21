from __future__ import annotations

import httpx

from app.core.config import settings
from ghostproof_ai import DetectionOrchestrator
from ghostproof_ai.contracts import AnalysisInput, ScanReport


class InferenceClient:
    def __init__(self) -> None:
        self.local_orchestrator = DetectionOrchestrator()

    async def analyze(self, scan_input: AnalysisInput) -> ScanReport:
        if settings.inference_mode == "remote":
            return await self._remote_analyze(scan_input)
        return await self.local_orchestrator.analyze(scan_input)

    async def _remote_analyze(self, scan_input: AnalysisInput) -> ScanReport:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.ai_service_url}/infer",
                json=scan_input.model_dump(mode="json"),
            )
            response.raise_for_status()
            return ScanReport.model_validate(response.json())
