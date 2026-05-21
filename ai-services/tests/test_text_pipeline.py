import pytest

from ghostproof_ai.contracts import AnalysisInput, MediaType
from ghostproof_ai.pipelines.text import TextDetectionPipeline


@pytest.mark.asyncio
async def test_text_pipeline_returns_explainable_result() -> None:
    text = (
        "This product improves safety and improves trust. "
        "This product improves safety and improves trust. "
        "The system provides clear evidence and provides clear evidence. "
    ) * 6
    result = await TextDetectionPipeline().analyze(
        AnalysisInput(media_type=MediaType.TEXT, content=text)
    )

    assert result.media_type == MediaType.TEXT
    assert 0 <= result.ai_probability <= 1
    assert result.evidence
    assert result.reasons
