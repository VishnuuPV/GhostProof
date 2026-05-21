from ghostproof_ai.contracts import MediaType, ModalityResult, RiskLevel
from ghostproof_ai.risk.scoring import RiskScorer


def test_risk_engine_combines_confident_modalities() -> None:
    scorer = RiskScorer()
    authenticity, ai_probability, confidence, risk_level = scorer.score(
        [
            ModalityResult(
                media_type=MediaType.IMAGE,
                ai_probability=0.84,
                authenticity_score=16,
                confidence=0.92,
            ),
            ModalityResult(
                media_type=MediaType.TEXT,
                ai_probability=0.64,
                authenticity_score=36,
                confidence=0.80,
            ),
        ]
    )

    assert authenticity < 35
    assert ai_probability > 0.70
    assert confidence > 0.80
    assert risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
