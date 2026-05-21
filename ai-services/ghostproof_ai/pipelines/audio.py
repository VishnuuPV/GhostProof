from __future__ import annotations

from ghostproof_ai.contracts import AnalysisInput, Evidence, MediaType, ModalityResult
from ghostproof_ai.pipelines.base import BasePipeline
from ghostproof_ai.utils import clamp, safe_float


class AudioClonePipeline(BasePipeline):
    media_type = MediaType.AUDIO

    async def analyze(self, scan_input: AnalysisInput) -> ModalityResult:
        model = self.registry.resolve("audio-spoofing")
        metadata = scan_input.metadata

        duration = safe_float(metadata.get("duration"))
        harmonic_signal = safe_float(metadata.get("syntheticHarmonicsScore"))
        prosody_signal = safe_float(metadata.get("prosodyFlatnessScore"))
        speaker_mismatch = safe_float(metadata.get("speakerMismatchScore"))
        sample_rate = safe_float(metadata.get("sampleRate"))

        ai_probability = clamp(
            0.17
            + 0.34 * harmonic_signal
            + 0.27 * prosody_signal
            + 0.30 * speaker_mismatch
            + (0.05 if sample_rate and sample_rate < 22050 else 0.0)
        )
        confidence = clamp(
            0.30
            + (0.18 if duration > 4 else 0.0)
            + (0.24 if max(harmonic_signal, prosody_signal, speaker_mismatch) > 0 else 0.0)
        )

        reasons: list[str] = []
        evidence: list[Evidence] = []

        if harmonic_signal > 0.45:
            reasons.append("synthetic harmonic structure")
            evidence.append(
                Evidence(
                    code="AUDIO_SYNTHETIC_HARMONICS",
                    title="Synthetic harmonic structure",
                    description="Spectral harmonics are unusually regular for natural speech.",
                    modality=self.media_type,
                    severity=harmonic_signal,
                    location={"score": harmonic_signal},
                )
            )
        if prosody_signal > 0.45:
            reasons.append("flat prosody pattern")
            evidence.append(
                Evidence(
                    code="AUDIO_FLAT_PROSODY",
                    title="Flat prosody",
                    description="Pitch and energy variation are lower than expected for expressive speech.",
                    modality=self.media_type,
                    severity=prosody_signal,
                    location={"score": prosody_signal},
                )
            )
        if speaker_mismatch > 0.45:
            reasons.append("speaker verification mismatch")
            evidence.append(
                Evidence(
                    code="AUDIO_SPEAKER_MISMATCH",
                    title="Speaker mismatch",
                    description="Voice embedding does not align with supplied speaker reference.",
                    modality=self.media_type,
                    severity=speaker_mismatch,
                    location={"score": speaker_mismatch},
                )
            )

        if not reasons:
            reasons.append("no strong cloned-voice indicators detected")
            evidence.append(
                Evidence(
                    code="AUDIO_SPECTROGRAM_REQUIRED",
                    title="Spectrogram scan recommended",
                    description="Metadata-only audio scan has limited confidence without waveform features.",
                    modality=self.media_type,
                    severity=0.20,
                    recommendation="Use async audio upload for mel-spectrogram analysis.",
                )
            )

        return ModalityResult(
            media_type=self.media_type,
            ai_probability=round(ai_probability, 4),
            authenticity_score=round((1.0 - ai_probability) * 100, 2),
            confidence=round(confidence, 4),
            reasons=reasons,
            evidence=evidence,
            features={
                "duration": duration,
                "sample_rate": sample_rate or None,
                "synthetic_harmonics": harmonic_signal,
                "prosody_flatness": prosody_signal,
                "speaker_mismatch": speaker_mismatch,
                "model_backend": model.backend,
            },
            model_version=model.version,
        )
