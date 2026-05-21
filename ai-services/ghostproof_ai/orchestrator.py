from __future__ import annotations

from uuid import uuid4

from ghostproof_ai.contracts import AnalysisInput, MediaType, ModalityResult, ScanReport
from ghostproof_ai.explainability.engine import ExplanationEngine
from ghostproof_ai.models.registry import ModelRegistry
from ghostproof_ai.pipelines.audio import AudioClonePipeline
from ghostproof_ai.pipelines.image import ImageDetectionPipeline
from ghostproof_ai.pipelines.text import TextDetectionPipeline
from ghostproof_ai.pipelines.video import VideoDeepfakePipeline
from ghostproof_ai.risk.scoring import RiskScorer
from ghostproof_ai.utils import stable_hash


class DetectionOrchestrator:
    def __init__(self, registry: ModelRegistry | None = None) -> None:
        registry = registry or ModelRegistry()
        self.pipelines = {
            MediaType.IMAGE: ImageDetectionPipeline(registry),
            MediaType.VIDEO: VideoDeepfakePipeline(registry),
            MediaType.AUDIO: AudioClonePipeline(registry),
            MediaType.TEXT: TextDetectionPipeline(registry),
        }
        self.scorer = RiskScorer()
        self.explainer = ExplanationEngine()

    async def analyze(self, scan_input: AnalysisInput) -> ScanReport:
        results = await self._run_pipelines(scan_input)
        authenticity, ai_probability, confidence, risk_level = self.scorer.score(results)
        evidence = self.explainer.flatten_evidence(results)
        content_hash = stable_hash(
            {
                "media_type": scan_input.media_type.value,
                "source_url": scan_input.source_url,
                "content": scan_input.content,
                "metadata": scan_input.metadata,
            }
        )
        report_hash = stable_hash(
            {
                "content_hash": content_hash,
                "risk_level": risk_level.value,
                "authenticity_score": authenticity,
                "ai_probability": ai_probability,
                "evidence": [item.model_dump(mode="json") for item in evidence],
            }
        )

        return ScanReport(
            scan_id=f"scan_{uuid4().hex}",
            media_type=scan_input.media_type,
            risk_level=risk_level,
            authenticity_score=authenticity,
            ai_probability=ai_probability,
            confidence=confidence,
            summary=self.explainer.summarize(results, risk_level),
            modality_scores={result.media_type.value: result for result in results},
            evidence=evidence,
            content_hash=content_hash,
            tamper_hash=report_hash,
        )

    async def _run_pipelines(self, scan_input: AnalysisInput) -> list[ModalityResult]:
        if scan_input.media_type != MediaType.MULTIMODAL:
            pipeline = self.pipelines[scan_input.media_type]
            return [await pipeline.analyze(scan_input)]

        modality_inputs = scan_input.metadata.get("modalities", {})
        results: list[ModalityResult] = []
        for media_type, pipeline in self.pipelines.items():
            payload = modality_inputs.get(media_type.value)
            if payload is None:
                continue
            nested_input = AnalysisInput(
                media_type=media_type,
                source_url=payload.get("source_url", scan_input.source_url),
                content=payload.get("content"),
                metadata=payload.get("metadata", {}),
                options=scan_input.options,
            )
            results.append(await pipeline.analyze(nested_input))
        return results
