from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelHandle:
    name: str
    version: str
    path: Path | None
    backend: str
    available: bool


class ModelRegistry:
    """Minimal artifact registry. Production registry should verify signatures."""

    def __init__(self, artifact_dir: str | Path = "models/artifacts") -> None:
        self.artifact_dir = Path(artifact_dir)

    def resolve(self, name: str, backend: str = "onnx") -> ModelHandle:
        candidates = [
            self.artifact_dir / f"{name}.onnx",
            self.artifact_dir / f"{name}.pt",
            self.artifact_dir / f"{name}.safetensors",
        ]
        for path in candidates:
            if path.exists():
                return ModelHandle(
                    name=name,
                    version=path.stem,
                    path=path,
                    backend=backend,
                    available=True,
                )
        return ModelHandle(
            name=name,
            version="heuristic-fallback-v1",
            path=None,
            backend="heuristic",
            available=False,
        )
