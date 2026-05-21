from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    MULTIMODAL = "multimodal"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PrivacyMode(str, Enum):
    STANDARD = "standard"
    STRICT = "strict"
    LOCAL_ONLY = "local_only"


class Evidence(BaseModel):
    code: str
    title: str
    description: str
    modality: MediaType
    severity: float = Field(ge=0.0, le=1.0)
    location: dict[str, Any] = Field(default_factory=dict)
    recommendation: str | None = None


class ModalityResult(BaseModel):
    media_type: MediaType
    ai_probability: float = Field(ge=0.0, le=1.0)
    authenticity_score: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    suspicious_regions: list[dict[str, Any]] = Field(default_factory=list)
    manipulated_timestamps: list[dict[str, Any]] = Field(default_factory=list)
    features: dict[str, Any] = Field(default_factory=dict)
    model_version: str = "heuristic-fallback-v1"


class AnalysisOptions(BaseModel):
    explain: bool = True
    privacy_mode: PrivacyMode = PrivacyMode.STANDARD
    max_frames: int = Field(default=16, ge=1, le=96)
    enable_remote_fetch: bool = False


class AnalysisInput(BaseModel):
    media_type: MediaType
    source_url: str | None = None
    content: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    options: AnalysisOptions = Field(default_factory=AnalysisOptions)


class ScanReport(BaseModel):
    scan_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    media_type: MediaType
    risk_level: RiskLevel
    authenticity_score: float = Field(ge=0.0, le=100.0)
    ai_probability: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    modality_scores: dict[str, ModalityResult]
    evidence: list[Evidence] = Field(default_factory=list)
    content_hash: str
    tamper_hash: str | None = None
