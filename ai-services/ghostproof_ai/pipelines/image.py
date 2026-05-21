from __future__ import annotations

import io
from typing import Any

from ghostproof_ai.contracts import AnalysisInput, Evidence, MediaType, ModalityResult
from ghostproof_ai.pipelines.base import BasePipeline
from ghostproof_ai.utils import clamp, decode_data_url, safe_float


class ImageDetectionPipeline(BasePipeline):
    media_type = MediaType.IMAGE

    async def analyze(self, scan_input: AnalysisInput) -> ModalityResult:
        model = self.registry.resolve("image-forensics")
        metadata = scan_input.metadata
        image_bytes = decode_data_url(scan_input.content)
        features: dict[str, Any] = {
            "source_url_present": bool(scan_input.source_url),
            "model_backend": model.backend,
            "model_available": model.available,
        }

        evidence: list[Evidence] = []
        reasons: list[str] = []
        artifact_signal = 0.0
        confidence = 0.35
        suspicious_regions: list[dict[str, Any]] = []

        if image_bytes:
            pixel_features = self._extract_pixel_features(image_bytes)
            features.update(pixel_features)
            artifact_signal += 0.34 * pixel_features.get("frequency_artifact_score", 0.0)
            artifact_signal += 0.18 * pixel_features.get("low_texture_score", 0.0)
            confidence += 0.28

            if pixel_features.get("frequency_artifact_score", 0.0) > 0.55:
                reasons.append("frequency-domain artifact pattern")
                evidence.append(
                    Evidence(
                        code="IMAGE_FREQUENCY_ARTIFACT",
                        title="Frequency artifact cluster",
                        description="Fourier energy distribution suggests synthetic or heavily generated texture.",
                        modality=self.media_type,
                        severity=pixel_features["frequency_artifact_score"],
                        location={"region": "global_frequency_spectrum"},
                    )
                )
                suspicious_regions.append(
                    {
                        "x": 0.18,
                        "y": 0.16,
                        "width": 0.64,
                        "height": 0.58,
                        "score": round(pixel_features["frequency_artifact_score"], 3),
                        "label": "global frequency anomaly",
                    }
                )
        else:
            evidence.append(
                Evidence(
                    code="IMAGE_REMOTE_ONLY",
                    title="Remote image metadata scan",
                    description="Image bytes were not supplied; scan used URL and DOM metadata only.",
                    modality=self.media_type,
                    severity=0.22,
                    recommendation="Enable explicit image upload for pixel-level heatmaps.",
                )
            )

        metadata_signal = self._metadata_signal(metadata)
        features.update(metadata_signal["features"])
        artifact_signal += metadata_signal["score"] * 0.28
        confidence += metadata_signal["confidence"]
        evidence.extend(metadata_signal["evidence"])
        reasons.extend(metadata_signal["reasons"])

        dimension_score = self._dimension_signal(metadata)
        artifact_signal += dimension_score * 0.16
        if dimension_score > 0.45:
            reasons.append("unusual generated-asset dimensions")
            evidence.append(
                Evidence(
                    code="IMAGE_DIMENSION_PATTERN",
                    title="Generated asset dimensions",
                    description="Image dimensions match common AI-generation export patterns.",
                    modality=self.media_type,
                    severity=dimension_score,
                    location={
                        "width": metadata.get("naturalWidth") or metadata.get("width"),
                        "height": metadata.get("naturalHeight") or metadata.get("height"),
                    },
                )
            )

        ai_probability = clamp(0.16 + artifact_signal)
        confidence = clamp(confidence)

        if not reasons:
            reasons.append("no strong image synthesis indicators detected")

        return ModalityResult(
            media_type=self.media_type,
            ai_probability=round(ai_probability, 4),
            authenticity_score=round((1.0 - ai_probability) * 100, 2),
            confidence=round(confidence, 4),
            reasons=reasons,
            evidence=evidence,
            suspicious_regions=suspicious_regions,
            features=features,
            model_version=model.version,
        )

    def _extract_pixel_features(self, image_bytes: bytes) -> dict[str, float]:
        try:
            import numpy as np
            from PIL import Image
        except Exception:
            return {
                "pixel_analysis_available": 0.0,
                "frequency_artifact_score": 0.0,
                "low_texture_score": 0.0,
            }

        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                gray = image.convert("L").resize((256, 256))
                array = np.asarray(gray, dtype=np.float32) / 255.0
        except Exception:
            return {
                "pixel_analysis_available": 0.0,
                "frequency_artifact_score": 0.0,
                "low_texture_score": 0.0,
            }

        spectrum = np.fft.fftshift(np.fft.fft2(array))
        magnitude = np.log1p(np.abs(spectrum))
        center = magnitude[96:160, 96:160].mean()
        outer = np.concatenate(
            [
                magnitude[:64, :].ravel(),
                magnitude[-64:, :].ravel(),
                magnitude[:, :64].ravel(),
                magnitude[:, -64:].ravel(),
            ]
        ).mean()
        frequency_ratio = float(outer / max(center, 1e-6))
        frequency_artifact_score = clamp((frequency_ratio - 0.78) / 0.55)

        dx = np.abs(np.diff(array, axis=1)).mean()
        dy = np.abs(np.diff(array, axis=0)).mean()
        texture_energy = float((dx + dy) / 2)
        low_texture_score = clamp((0.035 - texture_energy) / 0.035)

        return {
            "pixel_analysis_available": 1.0,
            "frequency_ratio": round(frequency_ratio, 5),
            "frequency_artifact_score": round(frequency_artifact_score, 4),
            "texture_energy": round(texture_energy, 5),
            "low_texture_score": round(low_texture_score, 4),
        }

    def _metadata_signal(self, metadata: dict[str, Any]) -> dict[str, Any]:
        evidence: list[Evidence] = []
        reasons: list[str] = []
        score = 0.0
        confidence = 0.0

        has_exif = bool(metadata.get("exif") or metadata.get("cameraMake") or metadata.get("cameraModel"))
        if not has_exif:
            score += 0.30
            confidence += 0.08
            reasons.append("missing camera lineage metadata")
            evidence.append(
                Evidence(
                    code="IMAGE_METADATA_ABSENT",
                    title="Missing capture metadata",
                    description="No camera lineage metadata was supplied by the browser or source.",
                    modality=self.media_type,
                    severity=0.38,
                )
            )

        software = str(metadata.get("software") or metadata.get("generator") or "").lower()
        if any(marker in software for marker in ["stable diffusion", "midjourney", "dall-e", "firefly"]):
            score += 0.56
            confidence += 0.26
            reasons.append("generator metadata present")
            evidence.append(
                Evidence(
                    code="IMAGE_GENERATOR_METADATA",
                    title="Generator metadata",
                    description="Metadata names known image-generation software.",
                    modality=self.media_type,
                    severity=0.92,
                    location={"software": software},
                )
            )

        return {
            "score": clamp(score),
            "confidence": confidence,
            "reasons": reasons,
            "evidence": evidence,
            "features": {"has_exif": has_exif, "software": software or None},
        }

    @staticmethod
    def _dimension_signal(metadata: dict[str, Any]) -> float:
        width = safe_float(metadata.get("naturalWidth") or metadata.get("width"))
        height = safe_float(metadata.get("naturalHeight") or metadata.get("height"))
        if width <= 0 or height <= 0:
            return 0.0
        common_generated_sizes = {(512, 512), (768, 768), (1024, 1024), (1536, 1024), (1024, 1536)}
        if (int(width), int(height)) in common_generated_sizes:
            return 0.62
        if width == height and width >= 512:
            return 0.34
        return 0.0
