from __future__ import annotations

from ghostproof_ai.contracts import Evidence, ModalityResult, RiskLevel


class ExplanationEngine:
    def summarize(self, results: list[ModalityResult], risk_level: RiskLevel) -> str:
        evidence = self.flatten_evidence(results)
        if not evidence:
            return "No high-severity synthetic-media indicators were detected in available signals."

        top = sorted(evidence, key=lambda item: item.severity, reverse=True)[:3]
        reason_text = "; ".join(item.title.lower() for item in top)
        return f"{risk_level.value.title()} risk driven by {reason_text}."

    @staticmethod
    def flatten_evidence(results: list[ModalityResult]) -> list[Evidence]:
        items: list[Evidence] = []
        for result in results:
            items.extend(result.evidence)
        return sorted(items, key=lambda item: item.severity, reverse=True)
