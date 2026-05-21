from __future__ import annotations

from ghostproof_ai.contracts import AnalysisInput, Evidence, MediaType, ModalityResult
from ghostproof_ai.pipelines.base import BasePipeline
from ghostproof_ai.utils import clamp, safe_float


class VideoDeepfakePipeline(BasePipeline):
    media_type = MediaType.VIDEO

    async def analyze(self, scan_input: AnalysisInput) -> ModalityResult:
        model = self.registry.resolve("video-temporal-forensics")
        metadata = scan_input.metadata
        duration = safe_float(metadata.get("duration"))
        frame_count = int(safe_float(metadata.get("sampledFrames") or 0))
        has_audio = bool(metadata.get("hasAudio", True))

        temporal_signal = safe_float(metadata.get("temporalInstabilityScore"))
        lip_sync_signal = safe_float(metadata.get("lipSyncMismatchScore"))
        face_warp_signal = safe_float(metadata.get("faceWarpScore"))

        supplied_signal = max(temporal_signal, lip_sync_signal, face_warp_signal)
        coverage = clamp(frame_count / max(scan_input.options.max_frames, 1))
        confidence = clamp(0.28 + 0.34 * coverage + (0.16 if supplied_signal else 0.0))

        ai_probability = clamp(
            0.18
            + 0.34 * temporal_signal
            + 0.30 * lip_sync_signal
            + 0.32 * face_warp_signal
            + (0.10 if duration > 0 and frame_count == 0 else 0.0)
            + (0.06 if not has_audio else 0.0)
        )

        evidence: list[Evidence] = []
        reasons: list[str] = []
        timestamps: list[dict[str, float | str]] = []

        if temporal_signal > 0.45:
            reasons.append("frame-to-frame temporal instability")
            evidence.append(
                Evidence(
                    code="VIDEO_TEMPORAL_INSTABILITY",
                    title="Temporal instability",
                    description="Frame consistency signal indicates possible face or scene synthesis drift.",
                    modality=self.media_type,
                    severity=temporal_signal,
                    location={"score": temporal_signal},
                )
            )
        if lip_sync_signal > 0.45:
            reasons.append("lip synchronization mismatch")
            evidence.append(
                Evidence(
                    code="VIDEO_LIP_SYNC_MISMATCH",
                    title="Lip-sync mismatch",
                    description="Mouth motion and audio timing appear inconsistent.",
                    modality=self.media_type,
                    severity=lip_sync_signal,
                    location={"score": lip_sync_signal},
                )
            )
        if face_warp_signal > 0.45:
            reasons.append("localized face warping indicators")
            evidence.append(
                Evidence(
                    code="VIDEO_FACE_WARP",
                    title="Face warping indicator",
                    description="Face-region geometry appears unstable across sampled frames.",
                    modality=self.media_type,
                    severity=face_warp_signal,
                    location={"score": face_warp_signal},
                )
            )

        if duration > 0:
            for fraction in (0.25, 0.5, 0.75):
                timestamps.append(
                    {
                        "timestamp": round(duration * fraction, 2),
                        "score": round(max(supplied_signal, ai_probability * 0.72), 3),
                        "label": "candidate review segment",
                    }
                )

        if frame_count == 0:
            reasons.append("video requires backend frame extraction for high-confidence result")
            evidence.append(
                Evidence(
                    code="VIDEO_FRAME_SAMPLING_REQUIRED",
                    title="Frame sampling unavailable",
                    description="Browser submitted metadata only. Frame extraction worker should rescan for heatmaps.",
                    modality=self.media_type,
                    severity=0.25,
                    recommendation="Submit video through async job endpoint.",
                )
            )

        if not reasons:
            reasons.append("no strong temporal deepfake indicators detected")

        return ModalityResult(
            media_type=self.media_type,
            ai_probability=round(ai_probability, 4),
            authenticity_score=round((1.0 - ai_probability) * 100, 2),
            confidence=round(confidence, 4),
            reasons=reasons,
            evidence=evidence,
            manipulated_timestamps=timestamps,
            features={
                "duration": duration,
                "sampled_frames": frame_count,
                "has_audio": has_audio,
                "temporal_instability": temporal_signal,
                "lip_sync_mismatch": lip_sync_signal,
                "face_warp": face_warp_signal,
                "model_backend": model.backend,
            },
            model_version=model.version,
        )
