from __future__ import annotations

import math
import re
from collections import Counter

from ghostproof_ai.contracts import AnalysisInput, Evidence, MediaType, ModalityResult
from ghostproof_ai.pipelines.base import BasePipeline
from ghostproof_ai.utils import clamp


WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]{1,}")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?")


class TextDetectionPipeline(BasePipeline):
    media_type = MediaType.TEXT

    async def analyze(self, scan_input: AnalysisInput) -> ModalityResult:
        text = scan_input.content or ""
        tokens = [token.lower() for token in WORD_RE.findall(text)]
        sentences = [s.strip() for s in SENTENCE_RE.findall(text) if s.strip()]

        if len(tokens) < 20:
            return ModalityResult(
                media_type=self.media_type,
                ai_probability=0.12,
                authenticity_score=88.0,
                confidence=0.22,
                reasons=["insufficient text for stable authorship analysis"],
                evidence=[
                    Evidence(
                        code="TEXT_TOO_SHORT",
                        title="Limited text sample",
                        description="Text sample is too short for reliable AI-text detection.",
                        modality=self.media_type,
                        severity=0.18,
                        recommendation="Scan a longer passage or full article.",
                    )
                ],
                features={"tokens": len(tokens), "sentences": len(sentences)},
            )

        counts = Counter(tokens)
        unique = len(counts)
        total = len(tokens)
        probabilities = [count / total for count in counts.values()]
        entropy = -sum(p * math.log2(p) for p in probabilities)
        normalized_entropy = entropy / max(math.log2(unique + 1), 1.0)

        sentence_lengths = [len(WORD_RE.findall(sentence)) for sentence in sentences] or [total]
        mean_len = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((length - mean_len) ** 2 for length in sentence_lengths) / len(sentence_lengths)
        burstiness = math.sqrt(variance) / max(mean_len, 1.0)

        repeated_phrases = self._repeated_ngrams(tokens, n=3)
        repetition_ratio = sum(count - 1 for count in repeated_phrases.values()) / max(total, 1)
        predictability = 1.0 - normalized_entropy

        low_burstiness_signal = clamp((0.28 - burstiness) / 0.28)
        repetition_signal = clamp(repetition_ratio * 7.5)
        predictability_signal = clamp((predictability - 0.12) / 0.35)
        uniform_sentence_signal = clamp((1.0 / max(len(set(sentence_lengths)), 1)) * 2.0)

        ai_probability = clamp(
            0.14
            + 0.34 * low_burstiness_signal
            + 0.28 * repetition_signal
            + 0.24 * predictability_signal
            + 0.10 * uniform_sentence_signal
        )
        confidence = clamp(0.34 + min(total, 700) / 1400 + len(sentences) / 80)

        evidence: list[Evidence] = []
        reasons: list[str] = []

        if low_burstiness_signal > 0.45:
            reasons.append("low burstiness across sentence lengths")
            evidence.append(
                Evidence(
                    code="TEXT_LOW_BURSTINESS",
                    title="Uniform sentence rhythm",
                    description="Sentence lengths vary less than expected for natural prose.",
                    modality=self.media_type,
                    severity=low_burstiness_signal,
                    location={"burstiness": round(burstiness, 4)},
                )
            )
        if repetition_signal > 0.35:
            reasons.append("repeated phrase pattern")
            top_phrase = " ".join(max(repeated_phrases, key=repeated_phrases.get))
            evidence.append(
                Evidence(
                    code="TEXT_REPETITION",
                    title="Repeated phrasing",
                    description=f"Phrase recurrence is elevated around: {top_phrase}",
                    modality=self.media_type,
                    severity=repetition_signal,
                    location={"ngram": top_phrase},
                )
            )
        if predictability_signal > 0.40:
            reasons.append("high lexical predictability")
            evidence.append(
                Evidence(
                    code="TEXT_PREDICTABILITY",
                    title="Predictable token distribution",
                    description="Lexical entropy is lower than expected for varied human writing.",
                    modality=self.media_type,
                    severity=predictability_signal,
                    location={"normalized_entropy": round(normalized_entropy, 4)},
                )
            )

        if not reasons:
            reasons.append("no strong synthetic text indicators detected")

        return ModalityResult(
            media_type=self.media_type,
            ai_probability=round(ai_probability, 4),
            authenticity_score=round((1.0 - ai_probability) * 100, 2),
            confidence=round(confidence, 4),
            reasons=reasons,
            evidence=evidence,
            features={
                "tokens": total,
                "sentences": len(sentences),
                "unique_terms": unique,
                "normalized_entropy": round(normalized_entropy, 4),
                "burstiness": round(burstiness, 4),
                "repetition_ratio": round(repetition_ratio, 4),
            },
        )

    @staticmethod
    def _repeated_ngrams(tokens: list[str], n: int) -> dict[tuple[str, ...], int]:
        if len(tokens) < n:
            return {}
        grams = Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))
        return {gram: count for gram, count in grams.items() if count > 1}
