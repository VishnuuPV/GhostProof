from __future__ import annotations

from ghostproof_ai.contracts import MediaType, ModalityResult, RiskLevel
from ghostproof_ai.utils import clamp


DEFAULT_WEIGHTS: dict[MediaType, float] = {
    MediaType.IMAGE: 0.35,
    MediaType.VIDEO: 0.45,
    MediaType.AUDIO: 0.40,
    MediaType.TEXT: 0.25,
}


class RiskScorer:
    def __init__(self, weights: dict[MediaType, float] | None = None) -> None:
        self.weights = weights or DEFAULT_WEIGHTS

    def score(self, results: list[ModalityResult]) -> tuple[float, float, float, RiskLevel]:
        if not results:
            return 100.0, 0.0, 0.0, RiskLevel.LOW

        weighted_sum = 0.0
        weight_total = 0.0
        confidence_sum = 0.0

        for result in results:
            base_weight = self.weights.get(result.media_type, 0.25)
            weight = base_weight * max(result.confidence, 0.15)
            weighted_sum += result.ai_probability * weight
            confidence_sum += result.confidence * base_weight
            weight_total += weight

        ai_probability = clamp(weighted_sum / max(weight_total, 1e-6))
        confidence = clamp(confidence_sum / max(sum(self.weights.get(r.media_type, 0.25) for r in results), 1e-6))
        authenticity = round((1.0 - ai_probability) * 100, 2)
        return authenticity, round(ai_probability, 4), round(confidence, 4), self._level(ai_probability, confidence)

    @staticmethod
    def _level(ai_probability: float, confidence: float) -> RiskLevel:
        adjusted = ai_probability * (0.72 + 0.28 * confidence)
        if adjusted >= 0.82:
            return RiskLevel.CRITICAL
        if adjusted >= 0.62:
            return RiskLevel.HIGH
        if adjusted >= 0.34:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
