from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from ghostproof_ai.contracts import Evidence


class ScanHistoryItem(BaseModel):
    scan_id: str
    media_type: str
    risk_level: str
    authenticity_score: float
    ai_probability: float
    confidence: float
    summary: str
    source_url: str | None = None
    evidence: list[Evidence] = []
    content_hash: str
    tamper_hash: str
    created_at: datetime
