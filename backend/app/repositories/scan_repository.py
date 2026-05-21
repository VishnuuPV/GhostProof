from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models import ScanRecord
from app.schemas.history import ScanHistoryItem
from ghostproof_ai.contracts import ScanReport
from ghostproof_ai.utils import stable_hash


class ScanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, report: ScanReport, source_url: str | None = None) -> ScanRecord:
        previous = self.db.scalars(
            select(ScanRecord).order_by(desc(ScanRecord.created_at)).limit(1)
        ).first()
        previous_hash = previous.tamper_hash if previous else None
        tamper_hash = stable_hash(
            {
                "previous_hash": previous_hash,
                "report_hash": report.tamper_hash,
                "scan_id": report.scan_id,
            }
        )
        record = ScanRecord(
            id=report.scan_id,
            media_type=report.media_type.value,
            risk_level=report.risk_level.value,
            authenticity_score=report.authenticity_score,
            ai_probability=report.ai_probability,
            confidence=report.confidence,
            summary=report.summary,
            source_url=source_url,
            content_hash=report.content_hash,
            tamper_hash=tamper_hash,
            previous_hash=previous_hash,
            report_json=report.model_dump(mode="json"),
            created_at=report.created_at,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def recent(self, limit: int = 25) -> list[ScanHistoryItem]:
        records = self.db.scalars(
            select(ScanRecord).order_by(desc(ScanRecord.created_at)).limit(limit)
        ).all()
        return [
            ScanHistoryItem(
                scan_id=record.id,
                media_type=record.media_type,
                risk_level=record.risk_level,
                authenticity_score=record.authenticity_score,
                ai_probability=record.ai_probability,
                confidence=record.confidence,
                summary=record.summary,
                source_url=record.source_url,
                evidence=record.report_json.get("evidence", []),
                content_hash=record.content_hash,
                tamper_hash=record.tamper_hash,
                created_at=record.created_at,
            )
            for record in records
        ]
