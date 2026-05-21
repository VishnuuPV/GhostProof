from __future__ import annotations

from abc import ABC, abstractmethod

from ghostproof_ai.contracts import AnalysisInput, MediaType, ModalityResult
from ghostproof_ai.models.registry import ModelRegistry


class BasePipeline(ABC):
    media_type: MediaType

    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or ModelRegistry()

    @abstractmethod
    async def analyze(self, scan_input: AnalysisInput) -> ModalityResult:
        raise NotImplementedError
